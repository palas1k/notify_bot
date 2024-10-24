from typing import TypeVar

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Cancel, Button
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.infra.postgres.gateways import UserGateway

T = TypeVar('T')


class RegistrationStateGroup(StatesGroup):
    name = State()
    last_name = State()
    check = State()


async def input_name(
        message: Message,
        widget: ManagedTextInput[T],
        dialog_manager: DialogManager,
        data: T,
):
    dialog_manager.dialog_data['name'] = data
    await dialog_manager.switch_to(RegistrationStateGroup.last_name)


async def input_last_name(
        message: Message,
        widget: ManagedTextInput[T],
        dialog_manager: DialogManager,
        data: T,
):
    dialog_manager.dialog_data['last_name'] = data
    await dialog_manager.switch_to(RegistrationStateGroup.check)


@inject
async def save_user(
        query: CallbackQuery, widget: Button, dialog_manager: DialogManager, user_gateway: FromDishka[UserGateway]):
    name = dialog_manager.dialog_data['name']
    last_name = dialog_manager.dialog_data['last_name']
    async with user_gateway.session.begin():
        await user_gateway.create(
            name=name,
            last_name=last_name,
            telegram_id=str(query.from_user.id),
        )
    await query.answer('Вы зарегистрировались!')
    await dialog_manager.done()


async def error(
        message: Message,
        widget: ManagedTextInput[T],
        dialog_manager: DialogManager,
        error: ValueError,
):
    dialog_manager.dialog_data['error'] = error
    await message.answer('Введите текст')


main_window = Dialog(
    Window(
        Const('Регистрация в боте: \n'
              'Введите Имя'),
        TextInput(
            type_factory=str,
            on_error=error,
            on_success=input_name,
            id='input_name',
        ),
        Cancel(Const("Нет"), id="back"),
        state=RegistrationStateGroup.name
    ),
    Window(
        Const('Введите фамилию'),
        TextInput(
            type_factory=str,
            on_error=error,
            on_success=input_last_name,
            id='input_last_name',
        ),
        Cancel(Const("Нет"), id="back"),
        state=RegistrationStateGroup.last_name,
    ),
    Window(
        Format('Все верно? \n'
               'Имя: {dialog_data[name]} \n'
               'Фамилия: {dialog_data[last_name]}'),
        Button(Const("Сохранить!"), on_click=save_user, id='save_user'),
        Cancel(Const("Нет"), id="back"),
        state=RegistrationStateGroup.check,
    )
)
