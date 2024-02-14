from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.user.callbacks import SetLocalesCallback, AvailebleLocales


def get_proceed_buttons() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("📄 Perform another analysis"),
        callback_data="/start_natal_calc"
    )

    keyboard_builder.button(
        text=_("🤖 Free chat with the Virtual Astrologer"),
        callback_data="/chat_with_va"
    )

    return keyboard_builder.as_markup()
