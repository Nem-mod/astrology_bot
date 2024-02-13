from datetime import datetime

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n.types import BotCommand
from aiogram.utils.i18n import gettext as _, FSMI18nMiddleware

from db import MongoDbService
from keyboards.user import get_locales_buttons
from keyboards.user.callbacks import SetLocalesCallback
from services import ClickUpService
from services.ClickUp.ClickUp import CRM_CUSTOM_FIELDS
from states import NatalStates


async def callback_start(message: types.message.Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    crm_id = state_data.get("crm_record_id")
    if not crm_id == None:
        return
    try:
        record = await ClickUpService.add_to_crm(
            telegram=message.from_user.username,
            client_name=f"{message.from_user.full_name} ID:{message.from_user.id}"
        )
        dt = datetime.now().timestamp() * 1000
        await ClickUpService.update_task_custom_field(
            task_id=record["id"],
            field_id=CRM_CUSTOM_FIELDS.REGISTRATION_DATE,
            value=dt
        )
        await ClickUpService.update_task_custom_field(
            task_id=record["id"],
            field_id=CRM_CUSTOM_FIELDS.NATAL_COUNT,
            value="0"
        )
        await state.update_data({"natal_count": "0"})
        await state.update_data({"crm_record_id": record["id"]})

        mongo_client = MongoDbService()
        await mongo_client.insert_user({
            "user_id": message.from_user.id,
            "crm_id": record["id"],
            "natal_count": 0
        })

    except Exception as err:
        print(err)
        return

    buttons = get_locales_buttons()
    await message.answer(
        text=_("Please choose your language 🌐"),
        reply_markup=buttons
    )


async def callback_select_language(
        callback_query: types.CallbackQuery,
        state: FSMContext,
        callback_data: SetLocalesCallback,
        i18n_middleware: FSMI18nMiddleware,
        bot: Bot
):
    await i18n_middleware.set_locale(state, callback_data.locale)

    await state.set_state(NatalStates.get_name)
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("Start calculation"),
        callback_data="/start_natal_calc"
    )
    await callback_query.message.answer(
        text=_("Hello, I'm the Virtual Astrologer. I'll create your natal chart and interpret it using birth data and "
               "the current positions of the planets in the sky. Then you can ask me anything you're curious about!"),
        reply_markup=keyboard_builder.as_markup()
    )

    state_data = await state.get_data()
    try:
        await ClickUpService.update_task_custom_field(
            task_id=state_data["crm_record_id"],
            field_id=CRM_CUSTOM_FIELDS.LANGUAGE,
            value=callback_data.crm_field_id
        )
        mongo_client = MongoDbService()

        await mongo_client.update_user(
            user_id=callback_query.from_user.id,
            data={
                "$set": {
                    "locale": callback_data.locale
                }
            },
        )

    except Exception as err:
        print(err)

    await bot.set_my_commands(
        commands=[
            BotCommand(command="/calculate", description=_("Calculate Natal chart")),
        ],
        scope=BotCommandScopeChat(chat_id=callback_query.from_user.id)
    )
