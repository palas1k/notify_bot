from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from src.presentation.aiogram.dialogs.tasks_crud import TasksStateGroup

router = Router()


@router.message(Command('new_task'))
async def new_task_handler(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(TasksStateGroup.new_task, mode=StartMode.RESET_STACK)


@router.message(Command('my_tasks'))
async def my_task_handler(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(TasksStateGroup.all_tasks)
