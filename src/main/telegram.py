from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from dishka import FromDishka
from loguru import logger
from redis.asyncio import Redis

from src.config import Config
from src.infra.postgres.gateways import TaskGateway
from src.presentation.aiogram.middleware.check_user import CheckUserMiddleware
from src.presentation.aiogram.routes.main import router as main_router
from src.presentation.aiogram.dialogs.tasks_crud import main_window as tasks_window


def setup_aiogram(config: Config) -> tuple[Bot, Dispatcher]:
    bot = Bot(config.telegram.token)
    storage = RedisStorage(
        (Redis.from_url(config.redis.dsn)), key_builder=DefaultKeyBuilder(with_destiny=True)
    )
    dp = Dispatcher(storage=storage)
    setup_dialogs(dp)
    dp.include_routers(main_router,
                       tasks_window
                       )
    dp.message.middleware(CheckUserMiddleware())
    dp.callback_query.middleware(CheckUserMiddleware())

    return bot, dp
