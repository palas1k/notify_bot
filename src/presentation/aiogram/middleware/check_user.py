from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.infra.postgres.gateways import UserGateway


@inject
class CheckUserChannelMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
            user_gateway: FromDishka[UserGateway],
    ) -> Any:
        try:
            await user_gateway.get_user_by_telegram_id(str(event.message.from_user.id))
        except Exception:
            return await event.bot.send_message(
            )
        await handler(event, data)
