from enum import IntEnum, Enum

from aiogram.filters.callback_data import CallbackData

class OrderTypes(str, Enum):
    NATAL_CHARTS = "nt",
    QUESTIONS = "vaq"

class OrderCallback(CallbackData, prefix="sch"):
    amount: int
    cost: int
    type: OrderTypes

