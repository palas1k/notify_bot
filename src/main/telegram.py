from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from redis.asyncio import Redis

from src.config import Config
from src.presentation.aiogram.routes.main import router as main_router
from src.presentation.aiogram.dialogs.user_registration import main_window as users_window
from src.presentation.aiogram.dialogs.scores import main_window as scores_window
from src.presentation.aiogram.dialogs.main_menu import main_window as main_menu


def setup_aiogram(config: Config) -> tuple[Bot, Dispatcher]:
    bot = Bot(config.telegram.token)
    storage = RedisStorage(
        (Redis.from_url(config.redis.dsn)), key_builder=DefaultKeyBuilder(with_destiny=True)
    )
    dp = Dispatcher(storage=storage)
    setup_dialogs(dp)
    dp.include_routers(main_router,
                       users_window,
                       scores_window,
                       main_menu
                       )

    return bot, dp
