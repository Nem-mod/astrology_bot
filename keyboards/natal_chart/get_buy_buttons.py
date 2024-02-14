from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_buy_buttons() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("📄 Buy 10 analyses for $10"),
        callback_data="/ignore"
    )
    keyboard_builder.button(
        text=_("📄 Buy 30 analyses for $25"),
        callback_data="/ignore"
    )
    keyboard_builder.button(
        text=_("📄 Buy 1000 analyses for $150"),
        callback_data="/ignore"
    )
    keyboard_builder.button(
        text=_("💬 Buy 100 questions for $5"),
        callback_data="/ignore"
    )

    keyboard_builder.button(
        text=_("🎁 Donation"),
        callback_data="/ignore"
    )

    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()
