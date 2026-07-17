FROM python:3.12-slim

WORKDIR /app

# 使用阿里云 pip 镜像（国内加速下载）
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set global.trusted-host mirrors.aliyun.com

# Python 依赖（全部从阿里云镜像下载，含 CPU 版 torch）
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --default-timeout=300 --retries=5 -r requirements.txt

# 后端代码
COPY backend/app/ ./app/

# 前端静态文件
COPY frontend/ ./static/

# 模型缓存目录
RUN mkdir -p /app/models

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]