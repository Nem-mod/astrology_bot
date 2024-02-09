from enum import IntEnum

from aiogram.filters.callback_data import CallbackData


class TimeChooserActions(IntEnum):
    IGNORE = 0
    STEP_HOUR_T = 1
    STEP_HOUR_B = 2
    STEP_MINUTE_T = 3
    STEP_MINUTE_B = 4
    CONFIRM = 5
    CONTINUE = 6

class TimeChooserCallback(CallbackData, prefix="sch"):
    action: TimeChooserActions
    hour: int
    minute: int
