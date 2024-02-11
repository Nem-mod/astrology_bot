from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.natal_chart.callbacks import GendersCallback, Genders


def get_select_gender_buttons() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("Male"),
        callback_data=GendersCallback(
            gender=Genders.MALE,
            id="10cba086-f44b-4201-8852-2eac88866775"
        )
    )

    keyboard_builder.button(
        text=_("Female"),
        callback_data=GendersCallback(
            gender=Genders.FEMALE,
            id="da3d635c-44a7-4aac-b30a-ba3e21a3128d"
        )
    )

    keyboard_builder.button(
        text=_("⬅️ Back"),
        callback_data="/cancel_select_gender"
    )

    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()
