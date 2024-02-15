from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.natal_chart.callbacks import OrderCallback, OrderTypes


def get_buy_buttons() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("📄 Buy 10 analyses for $10"),
        callback_data=OrderCallback(
            amount=10,
            cost=10,
            type=OrderTypes.NATAL_CHARTS,
            description=_("📄 10 analyses")
        )
    )
    keyboard_builder.button(
        text=_("📄 Buy 30 analyses for $25"),
        callback_data=OrderCallback(
            amount=30,
            cost=25,
            type=OrderTypes.NATAL_CHARTS,
            description=_("📄 30 analyses")
        )
    )
    keyboard_builder.button(
        text=_("📄 Buy 1000 analyses for $150"),
        callback_data=OrderCallback(
            amount=1000,
            cost=150,
            type=OrderTypes.NATAL_CHARTS,
            description=_("📄 1000 analyses")
        )
    )

    keyboard_builder.button(
        text=_("💬 Buy 100 questions for $5"),
        callback_data=OrderCallback(
            amount=100,
            cost=5,
            type=OrderTypes.QUESTIONS,
            description=_("💬 100 questions")
        )
    )

    keyboard_builder.button(
        text=_("🎁 Donation"),
        callback_data="/ignore"
    )

    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()
