from typing import TypeVar, Any

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel
from aiogram_dialog.widgets.text import Format, Const
from asyncpg import UniqueViolationError
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.errors import UniqueError, NotFoundError
from src.infra.postgres.gateways import ScoreGateway

T = TypeVar('T')


class ScoreStateGroup(StatesGroup):
    get_scores = State()
    input_score = State()
    check_inputs = State()
    view_scores = State()


@inject
async def scores_getter(score_gateway: FromDishka[ScoreGateway],
                        dialog_manager: DialogManager,
                        **kwargs: Any):
    user_id = str(dialog_manager.event.from_user.id)
    async with score_gateway.session.begin():
        try:
            result = await score_gateway.get_by_telegram_id(user_id)
        except NotFoundError:
            result = await score_gateway.create(telegram_id=str(user_id))

    dialog_manager.dialog_data['input_score'] = result.scores
    result = list(result.scores.items())
    return {'scores': result, 'count': len(result)}


async def subject_selected(
        query: CallbackQuery, widget: Select, dialog_manager: DialogManager, subject: str
):
    dialog_manager.dialog_data['subject'] = subject

    await dialog_manager.switch_to(ScoreStateGroup.input_score)


async def error(
        message: Message,
        widget: ManagedTextInput[T],
        dialog_manager: DialogManager,
        error: ValueError,
):
    dialog_manager.dialog_data['error'] = error
    await message.answer('Введите число')


@inject
async def input_score(
        message: Message,
        widget: ManagedTextInput[T],
        dialog_manager: DialogManager,
        data: T,
        score_gateway: FromDishka[ScoreGateway],
        **kwargs: Any
):
    subject = dialog_manager.dialog_data['subject']
    input_score = dialog_manager.dialog_data['input_score']
    input_score[subject] = data
    async with score_gateway.session.begin():
        await score_gateway.update(telegram_id=str(dialog_manager.event.from_user.id),
                                   data={'scores': input_score})

    await dialog_manager.event.answer('Готово!')
    await dialog_manager.done()


main_window = Dialog(
    Window(
        Const('Выберите предмет'),
        ScrollingGroup(
            Select(
                Format("Предмет: {item[0]} Бал: {item[1]}"),
                item_id_getter=lambda item: item[0],
                items="scores",
                id="select_scores",
                on_click=subject_selected,
            ),
            width=1,
            height=10,
            id="opts_list_pager",
        ),
        Cancel(Const("Нет"), id="back"),
        getter=scores_getter,
        state=ScoreStateGroup.get_scores,
    ),
    Window(
        Const('Введите балл по предмету'),
        TextInput(
            type_factory=int,
            on_error=error,
            on_success=input_score,
            id="input_score",
        ),
        Cancel(Const("Нет"), id="back"),
        state=ScoreStateGroup.input_score,
    ),
    Window(
        Format("Ваши баллы! \n"
               "{dialog_data[input_score]}"),
        Cancel(Const("Нет"), id="back"),
        getter=scores_getter,
        state=ScoreStateGroup.view_scores,
    )
)
