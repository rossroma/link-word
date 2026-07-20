import os


class Config:
    """应用配置，从环境变量读取。"""

    # 词库路径
    WORD_BANK_PATH: str = os.getenv(
        "WORD_BANK_PATH", "/app/word_bank/all.json"
    )

    # Embedding 模型
    MODEL_NAME: str = os.getenv(
        "MODEL_NAME", "BAAI/bge-small-zh-v1.5"
    )
    MODEL_CACHE_DIR: str = os.getenv(
        "MODEL_CACHE_DIR", "/app/models"
    )

    # 游戏参数
    MAX_GUESSES: int = int(os.getenv("MAX_GUESSES", "50"))
    MIN_GUESS_INTERVAL_SECONDS: float = float(
        os.getenv("MIN_GUESS_INTERVAL_SECONDS", "1.0")
    )

    # 会话
    SESSION_TTL_SECONDS: int = int(
        os.getenv("SESSION_TTL_SECONDS", "3600")  # 1 小时
    )

    # 分数校准
    SCORE_MIN_SIM: float = float(os.getenv("SCORE_MIN_SIM", "0.15"))
    SCORE_MAX_SIM: float = float(os.getenv("SCORE_MAX_SIM", "0.90"))

    # 统计校准（方案 B：启动时采样 + sigmoid 映射）
    CALIBRATION_SAMPLE_SIZE: int = int(
        os.getenv("CALIBRATION_SAMPLE_SIZE", "100")
    )
    CALIBRATION_SIGMOID_CENTER: float = float(
        os.getenv("CALIBRATION_SIGMOID_CENTER", "1.5")
    )
    CALIBRATION_SIGMOID_K: float = float(
        os.getenv("CALIBRATION_SIGMOID_K", "1.2")
    )

    # 选词器
    WORD_COOLDOWN_MINUTES: int = int(
        os.getenv("WORD_COOLDOWN_MINUTES", "10")
    )
    PLAYER_AVOID_RECENT: int = int(
        os.getenv("PLAYER_AVOID_RECENT", "10")
    )


config = Config()