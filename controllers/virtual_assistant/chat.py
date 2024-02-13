from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from states import UserStates


async def callback_start_chat(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        text=_("Great! I have an analysis of your natal chart, and I'm ready to answer questions based on this data. Ask three free questions.")
    )
    await state.set_state(UserStates.va_chat)