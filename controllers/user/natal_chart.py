import re
from datetime import datetime, timedelta

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler_di import ContextSchedulerDecorator
from aiogram.utils.i18n import gettext as _

from controllers.user.utils import create_telegraph_article, form_not_completed
from db import MongoDbService
from keyboards.natal_chart import get_geonames_buttons, get_select_gender_buttons, get_buy_buttons
from keyboards.natal_chart.callbacks import GeoNameCallback, GendersCallback
from keyboards.user import get_proceed_buttons
from services import ClickUpService
from services.ClickUp.ClickUp import CRM_CUSTOM_FIELDS
from states import NatalStates

from utils import TelegraphHelper

# TODO: refactor check availability
async def check_natal_chart_is_available(state_data, user_id) -> bool:
    try:
        crm_record = await ClickUpService.get_record(state_data["crm_record_id"])
        crm_status = crm_record["status"]["status"].strip()
        mongo_client = MongoDbService()
        user = await mongo_client.get_user(user_id)
    except:
        return False

    if (
            int(user["natal_chart_left"]) <= 0
            and not (crm_status == "trial"
                or crm_status == "subscription")
    ):
        return False

    return True


async def callback_start_calculation(callback_query: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    is_available = await check_natal_chart_is_available(state_data, callback_query.from_user.id)
    if not is_available:
        buttons = get_buy_buttons()
        await callback_query.message.answer(
            text=_("Looks like you enjoy chatting with me!\n\n❓Questions and suggestions? Write to @maginoid"),
            reply_markup=buttons
        )
        return

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("⬅️ Back"),
        callback_data="/cancel_creating_natal_chart"
    )
    await callback_query.message.answer(
        text=_("What is your name?"),
        reply_markup=keyboard_builder.as_markup()
    )


async def handle_calculate(message: types.message.Message, state: FSMContext):
    state_data = await state.get_data()
    is_available = await check_natal_chart_is_available(state_data, message.from_user.id)
    if not is_available:
        buttons = get_buy_buttons()
        await message.answer(
            text=_("Looks like you enjoy chatting with me!\n\n❓Questions and suggestions? Write to @maginoid"),
            reply_markup=buttons
        )
        return

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("⬅️ Back"),
        callback_data="/cancel_creating_natal_chart"
    )
    await message.answer(
        text=_("What is your name?"),
        reply_markup=keyboard_builder.as_markup()
    )


async def handle_get_name(message: types.message.Message, state: FSMContext,
                          apscheduler: ContextSchedulerDecorator) -> None:
    await state.update_data({"name": message.text})
    state_data = await state.get_data()
    try:
        await ClickUpService.update_task_custom_field(
            task_id=state_data["crm_record_id"],
            field_id=CRM_CUSTOM_FIELDS.NATAL_NAME,
            value=f"{message.text}"
        )
        await ClickUpService.update_task_custom_status(task_id=state_data["crm_record_id"], value="filling form")
    except Exception as err:
        print(err)

    buttons = get_select_gender_buttons()
    await state.set_state(NatalStates.ignore)
    await message.answer(
        text=_("Choose your gender"),
        reply_markup=buttons
    )

    job = apscheduler.add_job(
        form_not_completed,
        trigger="date",
        run_date=datetime.now() + timedelta(minutes=30),
        kwargs={
            "chat_id": message.from_user.id,
            "crm_record_id": state_data["crm_record_id"]
        }
    )
    await state.update_data({"scheduler_job_id": job.id})


async def callback_get_gender(
        callback_query: types.CallbackQuery,
        state: FSMContext,
        callback_data: GendersCallback,
):
    await state.update_data(gender=callback_data.gender)
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

    state_data = await state.get_data()
    try:
        await ClickUpService.update_task_custom_field(
            state_data["crm_record_id"],
            CRM_CUSTOM_FIELDS.SEX,
            callback_data.id,
        )

    except Exception as err:
        print(err)


async def handle_birthday(message: types.message.Message, state: FSMContext):
    date_regex = r"^(0?[1-9]|[12]\d|3[01])\.(0?[1-9]|1[012])\.(\d{4})$"
    if not re.match(date_regex, message.text):
        await message.answer(_("Inputted value is invalid, correct format is DD.MM.YYYY"))
        return
    date = datetime.strptime(message.text, "%d.%m.%Y")

    await state.update_data({
        "birth_year": date.year,
        "birth_month": date.month,
        "birth_day": date.day
    })

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
    await message.answer(
        text=_("What time were you born? Type a time in 24 hours format HH:mm. For example: 23:20.  If you don't "
               "know, select 'I don't know exact time' we will use default time."),
        reply_markup=keyboard_builder.as_markup()
    )

    await state.set_state(NatalStates.get_birthtime)

    state_data = await state.get_data()
    try:
        timestamp = date.timestamp() * 1000
        await ClickUpService.update_task_custom_field(
            state_data["crm_record_id"],
            CRM_CUSTOM_FIELDS.BIRTHDAY,
            timestamp
        )

    except Exception as err:
        print(err)


async def callback_set_default_birthtime(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data({
        "birth_hour": 12,
        "birth_minute": 0,
    })

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("⬅️ Back"),
        callback_data="/cancel_get_birth_city"
    )
    await callback_query.message.answer(
        text=_("Write the city and country of birth, for example: Nikolaev, Ukraine."),
        reply_markup=keyboard_builder.as_markup()

    )

    await state.set_state(NatalStates.get_birth_city)

    state_data = await state.get_data()
    try:
        await ClickUpService.update_task_custom_field(
            state_data["crm_record_id"],
            CRM_CUSTOM_FIELDS.BIRTHTIME,
            "12:00"
        )

    except Exception as err:
        print(err)


async def hande_get_birthtime(message: types.message.Message, state: FSMContext):
    date_regex = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
    if not re.match(date_regex, message.text):
        await message.answer(_("Inputted value is invalid, correct format is HH:MM"))
        return

    split_data = message.text.split(':')
    await state.update_data({
        "birth_hour": int(split_data[0]),
        "birth_minute": int(split_data[1]),
    })

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("⬅️ Back"),
        callback_data="/cancel_get_birth_city"
    )

    await message.answer(
        text=_("Write the city and country of birth, for example: Nikolaev, Ukraine."),
        reply_markup=keyboard_builder.as_markup()

    )
    await state.set_state(NatalStates.get_birth_city)

    state_data = await state.get_data()
    try:
        await ClickUpService.update_task_custom_field(
            state_data["crm_record_id"],
            CRM_CUSTOM_FIELDS.BIRTHTIME,
            message.text
        )

    except Exception as err:
        print(err)


async def handle_birth_city(message: types.message.Message, state: FSMContext):
    buttons = await get_geonames_buttons(message.text)
    if not buttons:
        await message.answer(_("No locations has found. Write location correctly"))
        return
    await message.answer(
        text=_("<b>Confirm your place of birth:</b>"),
        reply_markup=buttons
    )


async def callback_chose_city(callback_query: types.CallbackQuery, state: FSMContext, callback_data: GeoNameCallback):
    await state.update_data(
        {
            "birth_city": callback_data.address,
            "lat": callback_data.lat,
            "lng": callback_data.lng,
            "chat_id": callback_query.from_user.id
        }
    )

    await callback_query.message.edit_text(
        _("You location {location_name} confirmed").format(location_name=callback_data.address)
    )

    poll_options = TelegraphHelper().TOPICS

    await callback_query.message.answer_poll(
        options=poll_options,
        allows_multiple_answers=True,
        question=_("Choose topics that interest you (at least one):"),
        is_anonymous=False
    )

    state_data = await state.get_data()
    try:
        await ClickUpService.update_task_custom_field(
            task_id=state_data["crm_record_id"],
            field_id=CRM_CUSTOM_FIELDS.LOCATION,
            value=callback_data.address)
    except Exception as err:
        print(err)


async def handle_poll_answer(poll_answer: types.PollAnswer, state: FSMContext, bot: Bot,
                             apscheduler: ContextSchedulerDecorator):
    state_data = await state.get_data()
    try:
        apscheduler.remove_job(state_data["scheduler_job_id"])
    except:
        pass
    try:
        await ClickUpService.update_task_custom_status(task_id=state_data["crm_record_id"], value="form completed")
    except Exception as err:
        print(err)

    await bot.send_message(text="⏳",
                           chat_id=state_data["chat_id"])

    await bot.send_message(text=_("Calculating the natal chart. It will take 2 min..."),
                           chat_id=state_data["chat_id"])

    telegraph_link, natal_summary = await create_telegraph_article(state_data, poll_answer)

    await bot.send_message(
        text=_("Your analysis is ready. Click the link below👇\n") + f"{telegraph_link}",
        chat_id=state_data["chat_id"]
    )

    await state.set_state()

    try:
        natal_count = int(state_data["natal_count"]) + 1
        await ClickUpService.update_task_custom_field(
            task_id=state_data["crm_record_id"],
            field_id=CRM_CUSTOM_FIELDS.NATAL_COUNT,
            value=str(natal_count)
        )

        await ClickUpService.update_task_custom_field(
            task_id=state_data["crm_record_id"],
            field_id=CRM_CUSTOM_FIELDS.ARTICLE_LINK,
            value=telegraph_link
        )

        topics_ids = []

        for id in poll_answer.option_ids:
            topics_ids.append(TelegraphHelper.TOPICS_CRM_IDS[id])

        await ClickUpService.update_task_custom_field(
            task_id=state_data["crm_record_id"],
            field_id=CRM_CUSTOM_FIELDS.TOPICS,
            value=topics_ids
        )

        await ClickUpService.update_task_custom_status(
            task_id=state_data["crm_record_id"],
            value="article ready"
        )

    except Exception as err:
        print(err)

    try:
        mongo_client = MongoDbService()
        await mongo_client.update_user(
            user_id=state_data["chat_id"],
            data={
                "$inc": {
                    "natal_chart_left": -1
                },
                "$set": {
                    "natal_summary": natal_summary
                }
            }
        )

    except Exception as err:
        print(err)

    proceed_buttons = get_proceed_buttons()
    await bot.send_message(
        text=_("Shall we continue our conversation?"),
        chat_id=state_data["chat_id"],
        reply_markup=proceed_buttons
    )
