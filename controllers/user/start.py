import re
from datetime import datetime, timedelta
from pathlib import Path

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n.types import BotCommand
from apscheduler_di import ContextSchedulerDecorator
from kerykeion import AstrologicalSubject
from aiogram.utils.i18n import gettext as _, FSMI18nMiddleware
from data.config import config
from keyboards.natal_chart import get_geonames_buttons, get_select_gender_buttons
from keyboards.natal_chart.callbacks import GeoNameCallback, GendersCallback
from keyboards.user import get_locales_buttons
from keyboards.user.callbacks import SetLocalesCallback
from services import ClickUpService
from services.ClickUp.ClickUp import CRM_CUSTOM_FIELDS
from services.OpenAI import OpenAIService
from states import NatalStates
from telegraph.aio import Telegraph

from utils import TelegraphHelper
from utils.create_table_chart import create_table_chart


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
    except Exception as err:
        print(err)
        return

    buttons = get_locales_buttons()
    await message.answer(
        text=_("Please choose your language 🌐"),
        reply_markup=buttons
    )


async def callback_start_calculation(callback_query: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    try:
        crm_record = await ClickUpService.get_record(state_data["crm_record_id"])
        crm_status = crm_record["status"]["status"].strip()
    except:
        return

    if (
            not int(state_data["natal_count"]) == 0
            and not (crm_status == "trial"
                     or crm_status == "subscription")
    ):
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
    try:
        crm_record = await ClickUpService.get_record(state_data["crm_record_id"])
        crm_status = crm_record["status"]["status"].strip()
    except:
        return

    if (
            not int(state_data["natal_count"]) == 0
            and not (crm_status == "trial"
                     or crm_status == "subscription")
    ):
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
    except Exception as err:
        print(err)

    await bot.set_my_commands(
        commands=[
            BotCommand(command="/calculate", description=_("Calculate Natal chart")),
        ],
        scope=BotCommandScopeChat(chat_id=callback_query.from_user.id)
    )


async def form_not_completed(bot: Bot, chat_id: str, crm_record_id: str):
    await bot.send_message(
        chat_id=chat_id,
        text=_("Any difficulties? Do you ask your mother your birth time? Do you doubt AstroBot? Keep going, "
               "it will be interesting! Instead of mom, write @maginoid to get help")
    )

    await ClickUpService.update_task_custom_status(task_id=crm_record_id, value="form not completed")


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
    print(state_data["scheduler_job_id"], state_data)
    apscheduler.remove_job(state_data["scheduler_job_id"])
    try:
        await ClickUpService.update_task_custom_status(task_id=state_data["crm_record_id"], value="form completed")
    except Exception as err:
        print(err)

    await bot.send_message(text=_("Calculating takes a bit of time. We answer you when it will be ready"),
                           chat_id=state_data["chat_id"])

    person = AstrologicalSubject(
        name=state_data["name"],
        year=int(state_data["birth_year"]),
        month=int(state_data["birth_month"]),
        day=int(state_data["birth_day"]),
        hour=int(state_data["birth_hour"]),
        city=state_data["birth_city"],
        lat=state_data["lat"],
        lng=state_data["lng"],
        geonames_username="artem.nechaev"
    )

    astro_data = create_table_chart(
        person.planets_list,
        person.first_house,
        person.tenth_house
    )

    openai_service = OpenAIService(
        api_key=config.openai.token
    )

    system_prompt = _(
        "You're an astrologer aiming for maximum personalization of responses based on the user's astrological data. "
        "Communicate using \"you\", adopting a youthful style with elements of modern slang, but do so flexibly and "
        "appropriately. Inject humor and amusing descriptions where it's adequate and cannot be misinterpreted.\n\n"
        "You must response in HTML format. Use only AVAILEBLE HTML tags\n AVAILABLE HTML tags are <p>, <b>, <i>"
    )

    query_message = _(
        "Perform a detailed astrological analysis of the user's natal chart.  Don't forget to write in your answer  "
        "house numbers when responding.\n"
        "Client: {name}\n"
        "Data: {astro_data}"
    ).format(name=person.name, astro_data=astro_data)

    entrance_completion, messages = await openai_service.chat_completion(
        query=query_message,
        system_prompt=system_prompt,
    )

    # RELATIONSHIPS

    telegraph = Telegraph()
    telegraph_helper = TelegraphHelper()
    await telegraph.create_account(short_name='JettAstro')

    html_content = f"{telegraph_helper.HEADER}"

    for id in poll_answer.option_ids:
        temp_comp, tmp_msg = await openai_service.chat_completion(
            telegraph_helper.TOPICS_PROMPTS[id],
            system_prompt=system_prompt,
            messages=messages
        )
        try:
            temp_image = telegraph_helper.TOPIC_IMAGES[id]
            image_th_path = await telegraph.upload_file(temp_image)

            html_content += f'<img src="{image_th_path[0]["src"]}">'
        except:
            pass
        html_content += telegraph_helper.BLOCKQUOTE_LIST[id]
        html_content += (temp_comp)

    images = await openai_service.image_generation(
        prompt=f"Create image that reproduce information of Natal Chart\n {entrance_completion}. Place user expected face in center of image."
    )
    for image in images:
        image_th_path = await telegraph.upload_file(image)
        html_content += f'<img src="{image_th_path[0]["src"]}">'

    telegraph_response = await telegraph.create_page(
        title=_("Astrological analysis: {name} {zodiac}").format(name=person.name, zodiac=person.sun.emoji),
        html_content=html_content
    )

    print(telegraph_response['url'])

    await bot.send_message(
        text=_("We created your transcription of natala chart you can read it there <a href=\"{link}\">link</a>")
        .format(link=telegraph_response["url"]),
        chat_id=state_data["chat_id"]
    )

    await state.set_state()

    for image in images:
        try:
            fp = Path(image)
            fp.unlink()
        except Exception as err:
            print(err)

    try:
        natal_count = int(state_data["natal_count"]) + 1
        await ClickUpService.update_task_custom_field(
            task_id=state_data["crm_record_id"],
            field_id=CRM_CUSTOM_FIELDS.ARTICLE_LINK,
            value=telegraph_response["url"]
        )

        await ClickUpService.update_task_custom_field(
            task_id=state_data["crm_record_id"],
            field_id=CRM_CUSTOM_FIELDS.NATAL_COUNT,
            value=str(natal_count)
        )
        topics_ids = []

        for id in poll_answer.option_ids:
            topics_ids.append(telegraph_helper.TOPICS_CRM_IDS[id])

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
