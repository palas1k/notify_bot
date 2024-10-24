from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Group, Start
from aiogram_dialog.widgets.text import Const

from src.presentation.aiogram.dialogs.scores import ScoreStateGroup
from src.presentation.aiogram.dialogs.user_registration import RegistrationStateGroup


class MainStateGroup(StatesGroup):
    main = State()


main_window = Dialog(
    Window(
        Const("Меню"),
        Group(
            Start(Const("Ввести результаты"), id='input', state=ScoreStateGroup.get_scores),
            Start(Const('Посмотреть результаты'), id='view', state=ScoreStateGroup.view_scores),
        ),
        state=MainStateGroup.main
    )
)
