from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Update
from loguru import logger

from src.config import get_config

cfg = get_config()


class CheckUserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ):
        if event.from_user.id != cfg.telegram.main_chat_id:
            return await event.message.answer('ты не имеешь права о ты не имеешь права')
        return await handler(event, data)
