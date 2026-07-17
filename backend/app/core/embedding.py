import logging
import os
from typing import Optional

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

logger = logging.getLogger(__name__)

# 模型文件路径（自动探测：向上查找 model_files/ 目录）
def _find_model_dir() -> str:
    path = os.getenv("MODEL_FILES_DIR", "")
    if path and os.path.isdir(path):
        return path
    # 从当前文件位置向上查找 model_files/
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        candidate = os.path.join(d, "model_files")
        if os.path.isdir(candidate):
            return candidate
        d = os.path.dirname(d)
    raise FileNotFoundError("Cannot find model_files/ directory")

_MODEL_DIR = _find_model_dir()
_ONNX_PATH = os.path.join(_MODEL_DIR, "model.onnx")
_TOKENIZER_PATH = os.path.join(_MODEL_DIR, "tokenizer.json")

# 全局实例（懒加载）
_session: Optional[ort.InferenceSession] = None
_tokenizer: Optional[Tokenizer] = None


def _get_session() -> ort.InferenceSession:
    global _session
    if _session is None:
        logger.info(f"Loading ONNX model: {_ONNX_PATH}")
        _session = ort.InferenceSession(
            _ONNX_PATH,
            providers=["CPUExecutionProvider"],
        )
        logger.info("ONNX model loaded")
    return _session


def _get_tokenizer() -> Tokenizer:
    global _tokenizer
    if _tokenizer is None:
        logger.info(f"Loading tokenizer: {_TOKENIZER_PATH}")
        _tokenizer = Tokenizer.from_file(_TOKENIZER_PATH)
        logger.info("Tokenizer loaded")
    return _tokenizer


def get_model() -> str:
    """兼容旧接口，返回模型标识。"""
    _get_session()
    _get_tokenizer()
    return "bge-small-zh-v1.5 (ONNX)"


def embed(word: str) -> list[float]:
    """将中文词汇转为向量（ONNX 推理 + mean pooling + L2 归一化）。"""
    session = _get_session()
    tokenizer = _get_tokenizer()

    encoded = tokenizer.encode(word)
    input_ids = np.array([encoded.ids], dtype=np.int64)
    attention_mask = np.array([encoded.attention_mask], dtype=np.int64)

    outputs = session.run(
        None,
        {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        },
    )

    # Mean pooling：对 token 维度取平均（用 attention_mask 排除 padding）
    hidden = outputs[0]  # shape: (1, seq_len, hidden_dim)
    mask = attention_mask[:, :, None]  # shape: (1, seq_len, 1)
    pooled = (hidden * mask).sum(axis=1) / mask.sum(axis=1)  # shape: (1, hidden_dim)

    # L2 归一化
    norm = np.linalg.norm(pooled, axis=1, keepdims=True)
    pooled = pooled / norm

    return pooled[0].tolist()