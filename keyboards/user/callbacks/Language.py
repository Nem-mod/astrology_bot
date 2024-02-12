from enum import Enum

from aiogram.filters.callback_data import CallbackData


class AvailebleLocales(str, Enum):
    uk = "uk"
    ru = "ru"
    en = "en"


class SetLocalesCallback(CallbackData, prefix="loc"):
    locale: AvailebleLocales
    crm_field_id: str