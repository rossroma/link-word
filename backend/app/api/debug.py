from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.embedding import embed
from app.core.scorer import (
    cosine_similarity,
    calibrate_score,
    get_calibration,
    _calibrate_linear,
    _calibrate_sigmoid,
)
from app.config import config

router = APIRouter(prefix="/api/debug", tags=["debug"])


class CalibrateRequest(BaseModel):
    target_word: str = Field(..., min_length=1, max_length=10)
    words: list[str] = Field(..., min_length=1, max_length=50)


class CalibrateResultItem(BaseModel):
    word: str
    cosine_similarity: float
    z_score: float | None = None      # z-score（仅 sigmoid 模式）
    linear_score: int                  # 线性映射分数（对照）
    score: int                         # 当前校准分数


class CalibrateResponse(BaseModel):
    target_word: str
    results: list[CalibrateResultItem]
    calibration_params: dict


@router.post("/calibrate", response_model=CalibrateResponse)
async def calibrate(body: CalibrateRequest):
    """
    调试端点：返回一组词与目标词的原始余弦相似度 + 校准后分数。
    同时返回线性映射分数作为对照，方便比较校准效果。
    """
    target_embedding = embed(body.target_word)
    cal = get_calibration()

    results: list[CalibrateResultItem] = []
    for word in body.words:
        guess_embedding = embed(word)
        cos_sim = cosine_similarity(target_embedding, guess_embedding)

        # 线性映射分数（对照）
        linear_score = _calibrate_linear(cos_sim)

        # 当前校准分数
        score = calibrate_score(cos_sim)

        # z-score（仅 sigmoid 模式）
        z_score = None
        if cal and cal.is_ready():
            z_score = round(
                (cos_sim - (cal.noise_mean + cal.center * cal.noise_std))
                / cal.noise_std,
                4,
            )

        results.append(CalibrateResultItem(
            word=word,
            cosine_similarity=round(cos_sim, 6),
            z_score=z_score,
            linear_score=linear_score,
            score=score,
        ))

    # 构建校准参数信息
    if cal and cal.is_ready():
        params = {
            "method": "sigmoid (z-score 统计校准)",
            "noise_mean": round(cal.noise_mean, 4),
            "noise_std": round(cal.noise_std, 4),
            "sigmoid_center": f"μ + {cal.center}σ = {round(cal.noise_mean + cal.center * cal.noise_std, 4)}",
            "sigmoid_k": cal.k,
            "formula": "z = (cos_sim - (μ + center·σ)) / σ, score = 99 / (1 + exp(-z·k))",
            "fallback_linear": {
                "score_min_sim": config.SCORE_MIN_SIM,
                "score_max_sim": config.SCORE_MAX_SIM,
            },
        }
    else:
        params = {
            "method": "linear (统计校准未就绪，使用回退方案)",
            "score_min_sim": config.SCORE_MIN_SIM,
            "score_max_sim": config.SCORE_MAX_SIM,
            "formula": "score = (cos_sim - min) / (max - min) × 99",
        }

    return CalibrateResponse(
        target_word=body.target_word,
        results=results,
        calibration_params=params,
    )