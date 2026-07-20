import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from app.api.game import router as game_router
from app.api.debug import router as debug_router
from app.core.embedding import get_model, embed
from app.data.word_loader import load_word_bank

# 日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Link Word - 猜词游戏",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
)

# CORS（开发环境允许所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(game_router)
app.include_router(debug_router)


@app.on_event("startup")
async def startup():
    """启动时预加载模型和词库。"""
    logger.info("Starting Link Word server...")

    # 预加载词库
    words = load_word_bank()
    logger.info(f"Word bank loaded: {len(words)} words")

    # 预加载模型（ONNX Runtime，秒级加载）
    model = get_model()
    embed("启动预热")
    logger.info(f"Model ready: {model}")


@app.get("/api/health")
async def health():
    """健康检查端点。"""
    from app.core.session import session_manager
    return {
        "status": "ok",
        "active_sessions": session_manager.count(),
    }


# 静态文件服务（生产模式：后端同时提供前端静态资源）
# 必须在所有 API 路由之后 mount，否则 StaticFiles 会拦截 /api/*
_static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(_static_dir):
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")