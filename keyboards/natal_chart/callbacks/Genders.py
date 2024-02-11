from enum import Enum

from aiogram.filters.callback_data import CallbackData

class Genders(str, Enum):
    MALE = "Male",
    FEMALE = "Female"

class GendersCallback(CallbackData, prefix="gend"):
    gender: Genders
    id: str
