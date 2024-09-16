import datetime
from typing import TypeVar, Any

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ChatEvent
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import CalendarConfig, ManagedCalendar, Button, Cancel, Select, ScrollingGroup, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from loguru import logger

from src.infra.postgres.gateways import TaskGateway
from src.presentation.aiogram.widgets import CustomCalendar

T = TypeVar('T')


class TasksStateGroup(StatesGroup):
    new_task = State()
    input_date = State()
    save_new_task = State()
    all_tasks = State()
    retrieve = State()
    delete_task = State()


async def text_handler(
        message: Message,
        widget: ManagedTextInput[T],
        dialog_manager: DialogManager,
        data: T,
):
    dialog_manager.dialog_data["text"] = data
    await dialog_manager.switch_to(TasksStateGroup.input_date)


async def on_reservation_date_selected(
        event: ChatEvent,
        widget: ManagedCalendar,
        dialog_manager: DialogManager,
        selected_date: datetime.date,
):
    dialog_manager.dialog_data["date"] = selected_date.strftime(
        "%d-%m-%Y"
    )
    await dialog_manager.switch_to(TasksStateGroup.save_new_task)


@inject
async def save_task(
        query: CallbackQuery, widget: Button, dialog_manager: DialogManager, task_gateway: FromDishka[TaskGateway]):
    date = dialog_manager.dialog_data["date"]
    text = dialog_manager.dialog_data["text"]
    async with task_gateway.session.begin():
        await task_gateway.create_task(
            text=text,
            day=datetime.datetime.strptime(date, "%d-%m-%Y"),
        )
    await query.answer("Вы записались!")
    await dialog_manager.done()


@inject
async def done_task(
        query: CallbackQuery, widget: Button, dialog_manager: DialogManager, task_gateway: FromDishka[TaskGateway]):
    task_id = dialog_manager.dialog_data['note']
    async with task_gateway.session.begin():
        await task_gateway.update_task_status(task_id)

    await query.answer('Выполнено')
    await dialog_manager.done()


@inject
async def notes_getter(dialog_manager: DialogManager,
                       task_gateway: FromDishka[TaskGateway],
                       **_):
    result = await task_gateway.get_all_tasks()
    notes = []
    for item in result:
        notes.append([item.id, item.text[:15], item.date.strftime("%d-%m-%Y")])
    return {"notes": notes, "count": len(notes)}


async def note_selected(
        callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item: str
):
    dialog_manager.dialog_data["note"] = item
    await dialog_manager.switch_to(TasksStateGroup.retrieve)

@inject
async def delete_task(
        query: CallbackQuery, widget: Button, dialog_manager: DialogManager, task_gateway: FromDishka[TaskGateway]):
    task_id = dialog_manager.dialog_data['note']
    logger.info(task_id)
    async with task_gateway.session.begin():
        await task_gateway.delete_by_id(task_id)

    await query.answer('Удалено')
    await dialog_manager.done()


main_window = Dialog(
    Window(
        Const('Введите текст\n'
              'для новой заметки'),
        TextInput(
            on_success=text_handler,
            id='new_task',
        ),
        Cancel(Const("Нет"), id="back"),
        state=TasksStateGroup.new_task,
    ),
    Window(
        Const('Выберите дату'),
        CustomCalendar(
            "reservation_date",
            id="reservation_date",
            config=CalendarConfig(
                min_date=datetime.date.today(),
                max_date=datetime.date.today() + datetime.timedelta(days=365),
            ),
            on_click=on_reservation_date_selected,
        ),
        Cancel(Const("Нет"), id="back"),
        state=TasksStateGroup.input_date
    ),
    Window(
        Format(
            "Напоминание: {dialog_data[text]}\n Дата: {dialog_data[date]}?"
        ),
        Button(Const("Да"), on_click=save_task, id="save_reg"),
        Cancel(Const("Нет"), id="back"),
        state=TasksStateGroup.save_new_task,
    ),
    Window(
        Const('Мои напоминалки'),
        ScrollingGroup(
            Select(
                Format("{item[1]} дата {item[2]}"),
                id="notes_list",
                item_id_getter=lambda item: item[0],
                items="notes",
                on_click=note_selected,
            ),
            id='notes_list_group',
            width=1,
            height=10,
        ),
        Cancel(Const("Назад"), id="back"),
        state=TasksStateGroup.all_tasks,
        getter=notes_getter,
    ),
    Window(
        Const('Хотите:'),
        SwitchTo(
            Const('Удалить?'),
            id='delete',
            state=TasksStateGroup.delete_task
        ),
        Button(
            Const('Выполнить'),
            on_click=done_task,
            id='done_task'
        ),
        Cancel(Const('Назад'), id='back'),
        state=TasksStateGroup.retrieve
    ),
    Window(
        Const('Удалить?'),
        Button(Const('Да'), on_click=delete_task, id='delete_task'),
        Cancel(Const('Нет'), id='back'),
        state=TasksStateGroup.delete_task
    )
)
