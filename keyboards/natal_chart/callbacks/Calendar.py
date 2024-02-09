from enum import IntEnum

from aiogram.filters.callback_data import CallbackData


class CalendarActions(IntEnum):
    IGNORE = 0
    STEP_BACKWARD_MONTH = 1
    STEP_FORWARD_MONTH = 2
    STEP_BACKWARD_YEAR = 3
    STEP_FORWARD_YEAR = 4
    START = 5
    # SET_YEAR = 4
    # SET_MONTH = 5
    SET_DAY = 6


class CalendarCallback(CallbackData, prefix="sch"):
    action: CalendarActions
    year: int
    month: int
    day: int


