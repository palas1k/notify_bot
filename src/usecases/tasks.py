import datetime

from aiogram import Bot
from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import get_config
from src.infra.celery import app, celery_event_loop
from src.infra.postgres.gateways import TaskGateway

cfg = get_config()

bot = Bot(cfg.telegram.token)

engine = create_async_engine(cfg.database.dsn, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def send_my_tasks():
    task_gateway = TaskGateway(async_session())
    async with task_gateway.session.begin():
        tasks = await task_gateway.get_today_task()
        for task in tasks:
            await bot.send_message(chat_id=cfg.telegram.main_chat_id, text=task.text)
            if task.counter == 4:
                await task_gateway.update_task_status(task.id)
            else:
                await task_gateway.update_task_counter(task.id)


@app.task
def every_day() -> None:
    celery_event_loop.run_until_complete(send_my_tasks())
