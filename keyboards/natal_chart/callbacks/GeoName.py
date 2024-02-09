from enum import Enum
from aiogram.filters.callback_data import CallbackData

class GeoNameActions(str, Enum):
    choose = "choose"

class GeoNameCallback(CallbackData, prefix="sch"):
    action: GeoNameActions
    address: str
    lat: float
    lng: float
