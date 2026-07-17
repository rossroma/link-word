import time
import logging
from collections import defaultdict
from app.models.schemas import ErrorCode

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """限流异常。"""
    def __init__(self, error_code: ErrorCode = ErrorCode.RATE_LIMITED):
        self.error_code = error_code
        super().__init__(error_code.value)


class RateLimiter:
    """
    双层限流：
    1. Session 级别：单局最多 50 次猜测，两次间隔 ≥ 1 秒
    2. IP 级别：单 IP 每分钟最多 60 次
    """

    MAX_GUESSES_PER_SESSION = 50
    MIN_INTERVAL_SECONDS = 0.3
    MAX_PER_IP_PER_MINUTE = 300

    def __init__(self):
        self._ip_requests: dict[str, list[float]] = defaultdict(list)

    def check_session(self, guess_count: int, last_guess_at: float | None) -> None:
        """检查 session 级别的限制。"""
        # 次数上限
        if guess_count >= self.MAX_GUESSES_PER_SESSION:
            raise RateLimitExceeded(ErrorCode.RATE_LIMITED)

        # 间隔限制
        if last_guess_at is not None:
            elapsed = time.time() - last_guess_at
            if elapsed < self.MIN_INTERVAL_SECONDS:
                raise RateLimitExceeded(ErrorCode.RATE_LIMITED)

    def check_ip(self, client_ip: str) -> None:
        """检查 IP 级别的限制。"""
        now = time.time()
        requests = self._ip_requests[client_ip]

        # 清理超过 1 分钟的旧记录
        self._ip_requests[client_ip] = [
            t for t in requests if now - t < 60
        ]

        if len(self._ip_requests[client_ip]) >= self.MAX_PER_IP_PER_MINUTE:
            raise RateLimitExceeded(ErrorCode.RATE_LIMITED)

        self._ip_requests[client_ip].append(now)

    def record_guess(self, client_ip: str) -> None:
        """记录一次猜测请求。"""
        self._ip_requests[client_ip].append(time.time())

    def remaining_guesses(self, guess_count: int) -> int:
        return max(0, self.MAX_GUESSES_PER_SESSION - guess_count)


# 全局单例
rate_limiter = RateLimiter()