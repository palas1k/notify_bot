from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.errors import NotFoundError
from src.infra.postgres.gateways import UserGateway
from src.presentation.aiogram.dialogs.main_menu import MainStateGroup
from src.presentation.aiogram.dialogs.scores import ScoreStateGroup
from src.presentation.aiogram.dialogs.user_registration import RegistrationStateGroup

router = Router()


@router.message(CommandStart())
async def start_menu(message: Message, dialog_manager: DialogManager, user_gateway: FromDishka[UserGateway]):
    await dialog_manager.start(MainStateGroup.main)


@router.message(Command('register'))
async def register_new_user(message: Message, dialog_manager: DialogManager, user_gateway: FromDishka[UserGateway]):
    try:
        await user_gateway.get_user_by_telegram_id(str(message.from_user.id))
        await message.answer('Вы уже зарегистрированы!')
        await dialog_manager.done()
    except NotFoundError as e:
        await dialog_manager.start(RegistrationStateGroup.name, mode=StartMode.RESET_STACK)


@router.message(Command('enter_scores'))
async def enter_scores(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(ScoreStateGroup.get_scores, mode=StartMode.RESET_STACK)


@router.message(Command('view_scores'))
async def view_scores(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(ScoreStateGroup.view_scores, mode=StartMode.RESET_STACK)
