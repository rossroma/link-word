import logging
from sentence_transformers import SentenceTransformer
from app.config import config

logger = logging.getLogger(__name__)

# 全局模型实例（懒加载）
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """获取或初始化 Embedding 模型（单例）。"""
    global _model
    if _model is None:
        logger.info(f"Loading model: {config.MODEL_NAME}")
        _model = SentenceTransformer(
            config.MODEL_NAME,
            cache_folder=config.MODEL_CACHE_DIR,
        )
        logger.info(f"Model loaded. Dim: {_model.get_sentence_embedding_dimension()}")
    return _model


def embed(word: str) -> list[float]:
    """将中文词汇转为向量。"""
    model = get_model()
    vec = model.encode(word, normalize_embeddings=True)
    return vec.tolist()