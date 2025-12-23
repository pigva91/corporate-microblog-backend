import os

from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from app.config import settings
from app.routes import router

media_dir = settings.media_folder
os.makedirs(media_dir, exist_ok=True)

app = FastAPI(
    title="Сервис микроблогов API",
    description="""
        API для корпоративного сервиса микроблогов (аналог Twitter).
        Основные возможности:
        - Добавить/удалить твит (с медиа)
        - Поставить/убрать лайк
        - Зафолловить/отписаться от пользователя
        - Получить ленту твитов
        - Профили пользователей
        - Загрузка медиа
    """,
    version="1.0.0",
)

app.include_router(router, prefix="/api")
app.mount("/media", StaticFiles(directory=media_dir), name="media")
app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "result": False,
            "error_type": type(exc).__name__,
            "error_message": exc.detail,
        },
    )
