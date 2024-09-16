from aiogram import Bot, Dispatcher
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka as setup_dishka_aiogram
from loguru import logger

from src.config import get_config, Config
from src.infra.loguru import setup_logging
from src.main.di import DishkaProvider
from src.main.telegram import setup_aiogram


def app() -> tuple[Bot, Dispatcher]:
    config: Config = get_config()
    setup_logging(config.logging)

    container = make_async_container(DishkaProvider(config=config))
    logger.info("INIT aiogram")

    bot, dp = setup_aiogram(config)
    setup_dishka_aiogram(container, router=dp, auto_inject=True)
    logger.info("Initializer")
    return bot, dp
