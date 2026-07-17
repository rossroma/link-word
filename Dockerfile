FROM python:3.12-slim

WORKDIR /app

# 系统依赖（使用阿里云镜像加速）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# CPU 版 PyTorch（体积小，避免 CUDA 依赖）
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu

# Python 依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 后端代码
COPY backend/app/ ./app/

# 前端静态文件
COPY frontend/ ./static/

# 模型缓存目录
RUN mkdir -p /app/models

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]