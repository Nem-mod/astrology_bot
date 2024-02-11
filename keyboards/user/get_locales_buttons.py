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
        )
    )

    keyboard_builder.button(
        text="🇺🇦Українська",
        callback_data=SetLocalesCallback(
            locale=AvailebleLocales.uk,
        )
    )

    keyboard_builder.button(
        text="🇷🇺Русский",
        callback_data=SetLocalesCallback(
            locale=AvailebleLocales.ru,
        )
    )

    return keyboard_builder.as_markup()
