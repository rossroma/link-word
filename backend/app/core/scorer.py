import logging
import math
import random
from dataclasses import dataclass

import numpy as np

from app.config import config

logger = logging.getLogger(__name__)


# ── 校准状态（全局单例）──────────────────────────────────────

@dataclass
class CalibrationState:
    """启动时采样计算的余弦相似度分布统计量。"""
    noise_mean: float       # 随机词对余弦相似度的均值 μ
    noise_std: float        # 随机词对余弦相似度的标准差 σ
    center: float           # sigmoid 中心偏移（以 σ 为单位）
    k: float                # sigmoid 陡峭度

    def is_ready(self) -> bool:
        return self.noise_std > 0


_calibration: CalibrationState | None = None


def get_calibration() -> CalibrationState | None:
    return _calibration


# ── 余弦相似度 ────────────────────────────────────────────────

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """计算两个 L2 归一化向量的余弦相似度。"""
    va = np.array(a)
    vb = np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))


# ── 统计校准（方案 B：z-score + sigmoid）─────────────────────

def estimate_noise_floor(
    word_bank: list[dict],
    sample_size: int | None = None,
) -> CalibrationState:
    """
    从词库中随机采样词汇，计算所有词对的余弦相似度分布。

    返回 CalibrationState，包含 μ（均值）和 σ（标准差）。
    采样 100 个词 → 4950 个词对 → 统计量足够稳定。
    """
    if sample_size is None:
        sample_size = config.CALIBRATION_SAMPLE_SIZE

    # 从词库中随机选词（去重）
    all_words = list({w["word"] for w in word_bank})
    if len(all_words) < sample_size:
        sample_size = len(all_words)
        logger.warning(
            f"Word bank has only {len(all_words)} unique words, "
            f"using all for calibration"
        )

    sampled = random.sample(all_words, sample_size)

    # 嵌入所有采样词（延迟导入避免循环依赖）
    from app.core.embedding import embed

    logger.info(f"Embedding {sample_size} words for calibration...")
    embeddings = np.array([embed(w) for w in sampled])  # (N, 512)

    # 计算所有词对的 L2 归一化余弦相似度
    # embeddings 已经是 L2 归一化的，所以点积 = 余弦相似度
    sim_matrix = embeddings @ embeddings.T  # (N, N)

    # 取上三角（排除对角线 self-similarity=1.0）
    triu_indices = np.triu_indices(sample_size, k=1)
    similarities = sim_matrix[triu_indices]  # N*(N-1)/2 个值

    noise_mean = float(np.mean(similarities))
    noise_std = float(np.std(similarities))

    state = CalibrationState(
        noise_mean=noise_mean,
        noise_std=noise_std,
        center=config.CALIBRATION_SIGMOID_CENTER,
        k=config.CALIBRATION_SIGMOID_K,
    )

    logger.info(
        f"Calibration done: μ={noise_mean:.4f}, σ={noise_std:.4f}, "
        f"center={state.center}σ, k={state.k}, "
        f"pairs={len(similarities)}, "
        f"range=[{noise_mean - 3*noise_std:.4f}, {noise_mean + 3*noise_std:.4f}]"
    )

    return state


def set_calibration(state: CalibrationState) -> None:
    """设置全局校准状态（在启动时调用）。"""
    global _calibration
    _calibration = state


def calibrate_score(cosine_sim: float) -> int:
    """
    将余弦相似度映射到 0–99 的整数分数。

    优先使用启动时统计校准（sigmoid），
    回退到线性映射（兼容旧配置）。
    """
    if _calibration and _calibration.is_ready():
        return _calibrate_sigmoid(cosine_sim)
    return _calibrate_linear(cosine_sim)


def _calibrate_sigmoid(cosine_sim: float) -> int:
    """
    z-score + sigmoid 映射。

    公式:
        z = (cos_sim - (μ + center × σ)) / σ
        score = 99 / (1 + exp(-z × k))

    含义:
        - 余弦相似度处于「随机词对均值」→ 低分
        - 余弦相似度高于均值 center 个标准差 → 50 分（sigmoid 中点）
        - 余弦相似度越高，分数增长越快（sigmoid 陡峭区）
    """
    cal = _calibration
    if cal.noise_std <= 0:
        return _calibrate_linear(cosine_sim)

    # z-score: 相对于「随机均值 + 偏移」的标准化距离
    z = (cosine_sim - (cal.noise_mean + cal.center * cal.noise_std)) / cal.noise_std

    # sigmoid 映射到 [0, 99]
    try:
        score = 99.0 / (1.0 + math.exp(-z * cal.k))
    except OverflowError:
        # z 过大或过小导致 exp 溢出
        return 99 if z > 0 else 0

    return max(0, min(99, round(score)))


def _calibrate_linear(cosine_sim: float) -> int:
    """
    线性映射（回退方案）。

    将余弦相似度按配置的 [MIN_SIM, MAX_SIM] 区间线性拉伸到 0–99。
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


# ── 公开接口 ──────────────────────────────────────────────────

def score_guess(
    target_embedding: list[float],
    guess_word: str,
    guess_embedding: list[float],
) -> int:
    """
    计算猜测词的分数。

    返回:
    - 100: 精确匹配（由调用方处理）
    - 0-99: 语义相似度分数
    """
    sim = cosine_similarity(target_embedding, guess_embedding)
    return calibrate_score(sim)