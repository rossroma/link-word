import numpy as np
from app.config import config


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """计算两个向量的余弦相似度。"""
    va = np.array(a)
    vb = np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))


def calibrate_score(cosine_sim: float) -> int:
    """
    将余弦相似度映射到 0–99 的整数分数。

    使用经验阈值进行线性拉伸，确保分数在 0–99 区间内均匀分布。
    """
    if cosine_sim <= config.SCORE_MIN_SIM:
        return 0
    if cosine_sim >= config.SCORE_MAX_SIM:
        return 99

    normalized = (cosine_sim - config.SCORE_MIN_SIM) / (
        config.SCORE_MAX_SIM - config.SCORE_MIN_SIM
    )
    score = round(normalized * 99)
    return max(0, min(99, score))


def score_guess(target_embedding: list[float], guess_word: str, guess_embedding: list[float]) -> int:
    """
    计算猜测词的分数。

    返回:
    - 100: 精确匹配
    - 0-99: 语义相似度分数
    """
    sim = cosine_similarity(target_embedding, guess_embedding)
    return calibrate_score(sim)