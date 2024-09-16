import logging

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import CalendarScope
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarScopeView,
    CalendarDaysView,
    CalendarMonthView,
    CalendarYearsView,
    Calendar,
)
from aiogram_dialog.widgets.text import Format, Case


def date_selector(fieldname: str):
    def selector(data: dict, case: Case, dialog_manager: DialogManager):
        return data["date"].strftime("%d/%m/%Y") in data["data"]["dialog_data"].get(
            fieldname, []
        )

    return selector


class CustomCalendar(Calendar):
    def __init__(self, reserved_dates_fieldname: str, **kwargs):
        self.fieldname = reserved_dates_fieldname
        super().__init__(**kwargs)

    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                self.config,
                date_text=Case(
                    {True: Format("✅ {date: %d}"), False: Format("{date: %d}")},
                    selector=date_selector(self.fieldname),
                ),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                self.config,
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
                self.config,
            ),
        }
