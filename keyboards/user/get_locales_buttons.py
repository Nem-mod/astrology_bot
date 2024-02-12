from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.user.callbacks import SetLocalesCallback, AvailebleLocales


def get_locales_buttons() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="🇺🇸English",
        callback_data=SetLocalesCallback(
            locale=AvailebleLocales.en,
            crm_field_id="15416836-993c-44b5-88df-4c4f0cfade43"
        )
    )

    keyboard_builder.button(
        text="🇺🇦Українська",
        callback_data=SetLocalesCallback(
            locale=AvailebleLocales.uk,
            crm_field_id="1462db7b-5d9b-4e5d-90a8-6409553ade58"
        )
    )

    keyboard_builder.button(
        text="🇷🇺Русский",
        callback_data=SetLocalesCallback(
            locale=AvailebleLocales.ru,
            crm_field_id="8b72928b-e21a-4197-acec-e76b46ccb8e1"

        )
    )

    return keyboard_builder.as_markup()
