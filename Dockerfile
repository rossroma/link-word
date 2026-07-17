FROM python:3.12-slim

WORKDIR /app

# Python 依赖（无需编译工具，全部预编译 wheel ~15MB）
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 后端代码
COPY backend/app/ ./app/

# ONNX 模型文件（91.5MB，已预导出，无需下载）
COPY model_files/ ./model_files/

# 前端静态文件
COPY frontend/ ./static/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]