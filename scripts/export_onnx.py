"""
一次性脚本：将 BAAI/bge-small-zh-v1.5 导出为 ONNX 格式。

运行：python export_onnx.py
输出：model_files/model.onnx + tokenizer 文件
"""

import os
import sys
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

MODEL_NAME = "BAAI/bge-small-zh-v1.5"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model_files")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    # 获取底层 transformer 模型，强制移到 CPU（MPS 不支持 ONNX 导出）
    transformer = model._first_module().auto_model.cpu()
    tokenizer = model.tokenizer

    # 导出 ONNX
    onnx_path = os.path.join(OUTPUT_DIR, "model.onnx")
    print(f"Exporting ONNX to: {onnx_path}")

    dummy = tokenizer("测试文本", return_tensors="pt")
    input_ids = dummy["input_ids"].cpu()
    attention_mask = dummy["attention_mask"].cpu()

    torch.onnx.export(
        transformer,
        (input_ids, attention_mask),
        onnx_path,
        input_names=["input_ids", "attention_mask"],
        output_names=["last_hidden_state"],
        dynamic_axes={
            "input_ids": {0: "batch", 1: "sequence"},
            "attention_mask": {0: "batch", 1: "sequence"},
            "last_hidden_state": {0: "batch", 1: "sequence"},
        },
        opset_version=14,
        do_constant_folding=True,
    )

    # 验证
    import onnxruntime as ort

    session = ort.InferenceSession(onnx_path)
    onnx_out = session.run(
        None,
        {
            "input_ids": input_ids.numpy(),
            "attention_mask": attention_mask.numpy(),
        },
    )[0]

    # PyTorch 输出（CPU 上）
    with torch.no_grad():
        pt_out = transformer(input_ids, attention_mask).last_hidden_state.numpy()

    diff = np.abs(onnx_out - pt_out).max()
    print(f"ONNX vs PyTorch max diff: {diff:.6f}")

    # 保存 tokenizer
    print(f"Saving tokenizer to: {OUTPUT_DIR}")
    tokenizer.save_pretrained(OUTPUT_DIR)

    # 获取输出维度
    dim = onnx_out.shape[-1]
    print(f"\nDone! Embedding dimension: {dim}")
    print(f"Files in {OUTPUT_DIR}/:")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        size_mb = os.path.getsize(os.path.join(OUTPUT_DIR, f)) / (1024 * 1024)
        print(f"  {f}  ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()