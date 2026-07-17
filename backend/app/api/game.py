from fastapi import APIRouter, Request
from app.core.game_controller import (
    create_game,
    make_guess,
    get_history,
    give_up,
)
from app.models.schemas import (
    GuessRequest,
    GameCreatedResponse,
    GuessResponse,
    ErrorResponse,
    ErrorCode,
    HistoryResponse,
    GameOverResponse,
)

router = APIRouter(prefix="/api/game", tags=["game"])


def _get_client_ip(request: Request) -> str:
    """获取客户端 IP。"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post(
    "/new",
    response_model=GameCreatedResponse | ErrorResponse,
    responses={
        200: {"description": "游戏创建成功"},
        500: {"model": ErrorResponse},
    },
)
async def new_game(request: Request):
    """创建新游戏。"""
    try:
        return create_game()
    except Exception:
        return ErrorResponse(error_code=ErrorCode.INTERNAL_ERROR)


@router.post(
    "/{session_id}/guess",
    response_model=GuessResponse,
    responses={
        200: {"description": "猜测结果"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
    },
)
async def guess(session_id: str, body: GuessRequest, request: Request):
    """提交猜测。"""
    client_ip = _get_client_ip(request)
    return make_guess(session_id, body.word, client_ip)


@router.get(
    "/{session_id}/history",
    response_model=HistoryResponse | ErrorResponse,
    responses={
        200: {"description": "猜测历史"},
        404: {"model": ErrorResponse},
    },
)
async def history(session_id: str):
    """获取猜测历史。"""
    return get_history(session_id)


@router.post(
    "/{session_id}/giveup",
    response_model=GameOverResponse | ErrorResponse,
    responses={
        200: {"description": "已放弃"},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def giveup(session_id: str):
    """放弃游戏。"""
    return give_up(session_id)