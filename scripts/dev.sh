#!/bin/bash
# dev.sh — 开发环境一键启动脚本

set -e

echo "🚀 Link Word — 开发环境启动"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 需要安装 Docker"
    exit 1
fi

# 如果使用国内 HuggingFace 镜像
if [ -z "$HF_ENDPOINT" ]; then
    echo "💡 提示：国内环境可设置 HF_ENDPOINT=https://hf-mirror.com 加速模型下载"
    echo "   export HF_ENDPOINT=https://hf-mirror.com"
    echo ""
fi

# 启动
echo "📦 构建并启动容器..."
docker compose up -d --build

echo ""
echo "⏳ 等待后端就绪（首次启动需下载模型，约 95MB，请耐心等待）..."
echo "   查看日志: docker compose logs -f backend"

# 等待后端健康检查
for i in $(seq 1 30); do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo ""
        echo "✅ 后端就绪！"
        echo "🎮 打开浏览器访问: http://localhost:3000"
        echo ""
        echo "📋 常用命令:"
        echo "   查看日志: docker compose logs -f backend"
        echo "   停止服务: docker compose down"
        echo "   API 文档: http://localhost:8000/api/docs"
        exit 0
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "⚠️  后端启动超时，请查看日志: docker compose logs backend"
echo "   首次启动模型下载可能需要较长时间"