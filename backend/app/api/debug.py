from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.embedding import embed
from app.core.scorer import cosine_similarity, calibrate_score
from app.config import config

router = APIRouter(prefix="/api/debug", tags=["debug"])


class CalibrateRequest(BaseModel):
    target_word: str = Field(..., min_length=1, max_length=10)
    words: list[str] = Field(..., min_length=1, max_length=50)


class CalibrateResultItem(BaseModel):
    word: str
    cosine_similarity: float
    normalized: float
    score: int


class CalibrateResponse(BaseModel):
    target_word: str
    results: list[CalibrateResultItem]
    calibration_params: dict


@router.post("/calibrate", response_model=CalibrateResponse)
async def calibrate(body: CalibrateRequest):
    """
    调试端点：返回一组词与目标词的原始余弦相似度 + 校准后分数。
    用于直观评估评分分布，调整校准参数。
    """
    target_embedding = embed(body.target_word)

    results: list[CalibrateResultItem] = []
    for word in body.words:
        guess_embedding = embed(word)
        cos_sim = cosine_similarity(target_embedding, guess_embedding)

        # 计算归一化值（与 calibrate_score 内部逻辑一致）
        if cos_sim <= config.SCORE_MIN_SIM:
            normalized = 0.0
        elif cos_sim >= config.SCORE_MAX_SIM:
            normalized = 1.0
        else:
            normalized = (cos_sim - config.SCORE_MIN_SIM) / (
                config.SCORE_MAX_SIM - config.SCORE_MIN_SIM
            )

        score = calibrate_score(cos_sim)

        results.append(CalibrateResultItem(
            word=word,
            cosine_similarity=round(cos_sim, 6),
            normalized=round(normalized, 4),
            score=score,
        ))

    return CalibrateResponse(
        target_word=body.target_word,
        results=results,
        calibration_params={
            "score_min_sim": config.SCORE_MIN_SIM,
            "score_max_sim": config.SCORE_MAX_SIM,
            "description": "线性映射: score = (cos_sim - min) / (max - min) × 99",
        },
    )