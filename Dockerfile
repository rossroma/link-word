FROM python:3.12-slim

WORKDIR /app

# 使用阿里云 pip 镜像源（服务器在国内，需要加速）
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set global.trusted-host mirrors.aliyun.com

# Python 依赖（~40MB，阿里云内网下载极快）
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