import logging
from app.core.validator import validate_guess, ValidationError
from app.core.embedding import embed
from app.core.scorer import score_guess
from app.core.session import session_manager, GameSession
from app.core.word_picker import WordPicker
from app.core.rate_limiter import rate_limiter, RateLimitExceeded
from app.data.word_loader import load_word_bank
from app.config import config
from app.models.schemas import (
    GameStatus,
    ErrorCode,
    GameCreatedResponse,
    GuessPlayingResponse,
    GuessWonResponse,
    GuessLostResponse,
    ErrorResponse,
    GameOverResponse,
    HistoryResponse,
    GuessHistoryItem,
)

logger = logging.getLogger(__name__)

# 全局选词器（启动时初始化）
_word_picker: WordPicker | None = None


def get_word_picker() -> WordPicker:
    global _word_picker
    if _word_picker is None:
        word_bank = load_word_bank()
        _word_picker = WordPicker(word_bank)
    return _word_picker


def create_game(player_id: str | None = None) -> GameCreatedResponse:
    """创建新游戏。"""
    picker = get_word_picker()
    chosen = picker.pick(player_id)

    target_word = chosen["word"]
    target_embedding = embed(target_word)

    session = session_manager.create(target_word, target_embedding)

    return GameCreatedResponse(
        session_id=session.session_id,
        max_guesses=config.MAX_GUESSES,
        status=GameStatus.PLAYING,
    )


def make_guess(
    session_id: str,
    raw_word: str,
    client_ip: str = "unknown",
) -> (
    GuessPlayingResponse
    | GuessWonResponse
    | GuessLostResponse
    | ErrorResponse
):
    """
    处理一次猜测请求。

    返回类型严格限定为 4 种：
    - GuessPlayingResponse: 猜测成功，继续游戏
    - GuessWonResponse: 猜中
    - GuessLostResponse: 次数耗尽
    - ErrorResponse: 错误
    """
    # 1. 输入校验（结构性约束，不用关键词匹配）
    try:
        word = validate_guess(raw_word)
    except ValidationError as e:
        return ErrorResponse(error_code=e.error_code)

    # 2. 会话校验
    session = session_manager.get(session_id)
    if session is None:
        return ErrorResponse(error_code=ErrorCode.SESSION_NOT_FOUND)

    if session.status != GameStatus.PLAYING:
        return ErrorResponse(error_code=ErrorCode.GAME_ALREADY_ENDED)

    # 3. 限流检查
    try:
        rate_limiter.check_session(session.guess_count(), session.last_guess_at)
        rate_limiter.check_ip(client_ip)
    except RateLimitExceeded:
        return ErrorResponse(error_code=ErrorCode.RATE_LIMITED)

    # 4. 精确匹配检查
    if word == session.target_word:
        guess_count = session.add_guess(word, 100)
        session.status = GameStatus.WON
        return GuessWonResponse(
            score=100,
            guess_count=guess_count,
            status=GameStatus.WON,
            target_word=session.target_word,
        )

    # 5. 计算语义相似度
    guess_embedding = embed(word)
    score = score_guess(session.target_embedding, word, guess_embedding)

    # 6. 记录猜测
    guess_count = session.add_guess(word, score)

    # 7. 检查是否耗尽次数
    if guess_count >= config.MAX_GUESSES:
        session.status = GameStatus.LOST
        return GuessLostResponse(
            score=score,
            guess_count=guess_count,
            status=GameStatus.LOST,
            target_word=session.target_word,
        )

    # 8. 游戏继续
    return GuessPlayingResponse(
        score=score,
        guess_count=guess_count,
        status=GameStatus.PLAYING,
    )


def get_history(session_id: str) -> HistoryResponse | ErrorResponse:
    """获取猜测历史。"""
    session = session_manager.get(session_id)
    if session is None:
        return ErrorResponse(error_code=ErrorCode.SESSION_NOT_FOUND)

    items = [
        GuessHistoryItem(
            word=g["word"],
            score=g["score"],
            guess_number=i + 1,
        )
        for i, g in enumerate(session.guesses)
    ]

    return HistoryResponse(
        session_id=session.session_id,
        status=session.status,
        max_guesses=config.MAX_GUESSES,
        guesses=items,
    )


def give_up(session_id: str) -> GameOverResponse | ErrorResponse:
    """放弃游戏。"""
    session = session_manager.get(session_id)
    if session is None:
        return ErrorResponse(error_code=ErrorCode.SESSION_NOT_FOUND)

    if session.status != GameStatus.PLAYING:
        return ErrorResponse(error_code=ErrorCode.GAME_ALREADY_ENDED)

    session.status = GameStatus.ABANDONED

    return GameOverResponse(
        status=GameStatus.ABANDONED,
        target_word=session.target_word,
        guess_count=session.guess_count(),
    )