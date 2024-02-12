from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, FSMI18nMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.natal_chart import get_select_gender_buttons
from states import NatalStates


async def callback_back_from_select_name(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

async def callback_back_from_gender(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(NatalStates.get_name)
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("⬅️ Back"),
        callback_data="/cancel_creating_natal_chart"
    )
    await callback_query.message.answer(
        text=_("What is your name?"),
        reply_markup=keyboard_builder.as_markup()
    )


async def callback_back_from_birthday(callback_query: types.CallbackQuery, state: FSMContext):
    buttons = get_select_gender_buttons()
    await state.set_state(NatalStates.ignore)
    await callback_query.message.answer(
        text=_("Choose your gender"),
        reply_markup=buttons
    )

async def callback_back_fom_birhttime(
        callback_query: types.CallbackQuery,
        state: FSMContext,
):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("⬅️ Back"),
        callback_data="/cancel_get_birthday"
    )
    await callback_query.message.answer(
        text=_("Enter the day, month and year of your birth in the format DD.MM.YYYY. For example: 31.12.1990"),
        reply_markup=keyboard_builder.as_markup()
    )
    await state.set_state(NatalStates.get_birthday)


async def callback_back_from_birth_city(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("I dont know exact time"),
        callback_data="/set_default_birthtime"
    )
    keyboard_builder.button(
        text=_("⬅️ Back"),
        callback_data="/cancel_get_birthtime"
    )
    keyboard_builder.adjust(1)
    await callback_query.message.answer(
        text=_("What time were you born? Type a time in 24 hours format HH:mm. For example: 23:20.  If you don't "
               "know, select 'I don't know exact time' we will use default time."),
        reply_markup=keyboard_builder.as_markup()
    )

    await state.set_state(NatalStates.get_birthtime)
