import time
import uuid
import logging
from datetime import datetime
from app.config import config
from app.models.schemas import GameStatus

logger = logging.getLogger(__name__)


class GameSession:
    """单个游戏会话。"""

    def __init__(self, target_word: str, target_embedding: list[float]):
        self.session_id = str(uuid.uuid4())
        self.target_word = target_word
        self.target_embedding = target_embedding
        self.guesses: list[dict] = []
        self.status = GameStatus.PLAYING
        self.created_at = datetime.utcnow()
        self.last_guess_at: float | None = None

    def add_guess(self, word: str, score: int) -> int:
        """记录一次猜测，返回猜测次数。"""
        self.guesses.append({
            "word": word,
            "score": score,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.last_guess_at = time.time()
        return len(self.guesses)

    def guess_count(self) -> int:
        return len(self.guesses)

    def is_expired(self) -> bool:
        elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        return elapsed > config.SESSION_TTL_SECONDS


class SessionManager:
    """会话管理器（内存存储）。"""

    def __init__(self):
        self._sessions: dict[str, GameSession] = {}

    def create(self, target_word: str, target_embedding: list[float]) -> GameSession:
        session = GameSession(target_word, target_embedding)
        self._sessions[session.session_id] = session
        self._cleanup_expired()
        logger.info(f"Session created: {session.session_id}")
        return session

    def get(self, session_id: str) -> GameSession | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if session.is_expired():
            self._sessions.pop(session_id, None)
            return None
        return session

    def remove(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def _cleanup_expired(self) -> None:
        expired = [
            sid for sid, s in self._sessions.items()
            if s.is_expired()
        ]
        for sid in expired:
            self._sessions.pop(sid, None)
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")

    def count(self) -> int:
        return len(self._sessions)


# 全局单例
session_manager = SessionManager()