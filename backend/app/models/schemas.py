from pydantic import BaseModel, Field
from enum import Enum


class GameStatus(str, Enum):
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"
    ABANDONED = "abandoned"


class ErrorCode(str, Enum):
    """所有可能的错误码——严格枚举，不允许自由文本。"""
    EMPTY_INPUT = "EMPTY_INPUT"
    TOO_LONG = "TOO_LONG"
    INVALID_CHARS = "INVALID_CHARS"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    GAME_ALREADY_ENDED = "GAME_ALREADY_ENDED"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# ─── 请求模型 ────────────────────────────────────────────


class GuessRequest(BaseModel):
    word: str = Field(..., min_length=1, max_length=10)


class NewGameRequest(BaseModel):
    difficulty: str | None = Field(default=None, pattern="^(easy|medium|hard)$")


# ─── 响应模型（5 种枚举类型）─────────────────────────────


class GameCreatedResponse(BaseModel):
    """类型 5: 新游戏创建成功。"""
    type: str = Field("game_created", frozen=True)
    session_id: str
    max_guesses: int
    status: GameStatus


class GuessPlayingResponse(BaseModel):
    """类型 1: 猜测成功，分数 < 100，游戏继续。"""
    type: str = Field("guess_result", frozen=True)
    score: int = Field(..., ge=0, le=99)
    guess_count: int = Field(..., ge=1)
    status: GameStatus


class GuessWonResponse(BaseModel):
    """类型 2: 猜中，分数 = 100，游戏胜利。"""
    type: str = Field("guess_result", frozen=True)
    score: int = Field(100, frozen=True)
    guess_count: int = Field(..., ge=1)
    status: GameStatus
    target_word: str


class GuessLostResponse(BaseModel):
    """类型 3: 次数耗尽，游戏失败。"""
    type: str = Field("guess_result", frozen=True)
    score: int = Field(..., ge=0, le=99)
    guess_count: int
    status: GameStatus
    target_word: str


class ErrorResponse(BaseModel):
    """类型 4: 错误响应。error_code 是枚举值，不是自由文本。"""
    type: str = Field("error", frozen=True)
    error_code: ErrorCode


class GameOverResponse(BaseModel):
    """放弃游戏时的响应。"""
    type: str = Field("game_over", frozen=True)
    status: GameStatus
    target_word: str
    guess_count: int


class GuessHistoryItem(BaseModel):
    word: str
    score: int
    guess_number: int


class HistoryResponse(BaseModel):
    session_id: str
    status: GameStatus
    max_guesses: int
    guesses: list[GuessHistoryItem]


# ─── 联合类型（API 路由使用）─────────────────────────────


# POST /guess 可能返回的 4 种类型
GuessResponse = (
    GuessPlayingResponse
    | GuessWonResponse
    | GuessLostResponse
    | ErrorResponse
)