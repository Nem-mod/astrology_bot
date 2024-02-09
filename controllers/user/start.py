import pprint
from datetime import datetime, timedelta
from enum import Enum

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler_di import ContextSchedulerDecorator
from kerykeion import AstrologicalSubject
from aiogram.utils.i18n import gettext as _
from data.config import config
from keyboards.natal_chart import SimpleTimeChooser, get_geonames_buttons
from keyboards.natal_chart.SimpleCalendar import SimpleCalendar
from keyboards.natal_chart.callbacks import CalendarCallback, TimeChooserCallback, GeoNameCallback
from services.OpenAI import OpenAIService
from states import NatalStates
from telegraph.aio import Telegraph

from utils.create_table_chart import create_table_chart


async def callback_start(message: types.message.Message) -> None:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("Start calculation"),
        callback_data="/start_natal_calc"
    )
    await message.answer(
        text=_("Welcome message.\n\nWe do not share your data with third parties."),
        reply_markup=keyboard_builder.as_markup()
    )


async def callback_start_calculation(callback_query: types.CallbackQuery, state: FSMContext,
                                     apscheduler: ContextSchedulerDecorator):
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


async def handle_get_name(message: types.message.Message, state: FSMContext,
                          apscheduler: ContextSchedulerDecorator) -> None:
    await state.update_data({"name": message.text})
    calendar = await SimpleCalendar.start_calendar(datetime(year=2004, month=1, day=1))
    await message.answer(
        text=_("When were you born? Select date and time."),
        reply_markup=calendar
    )
    await state.set_state(NatalStates.get_birth_year)


async def callback_calendar(callback_query: types.CallbackQuery, state: FSMContext, callback_data: CalendarCallback):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    current_datetime = datetime.now()
    if not selected or date > current_datetime - timedelta(days=365):
        return
    # await callback_query.message.answer(str(date))
    date: datetime = date

    await state.update_data({
        "birth_year": date.year,
        "birth_month": date.month,
        "birth_day": date.day
    })

    # await state.set_state(NatalStates.get_birth_hour)
    time_chooser = await SimpleTimeChooser.start_time_chooser(hour=12, minute=0)
    await callback_query.message.edit_text(text=_(
        "What time were you born? Choose a time. If you don't know, select "
        "<b>I don't know exact time</b> we will use default time."),
        reply_markup=time_chooser
    )


async def callback_time_chooser(callback_query: types.CallbackQuery, state: FSMContext,
                                callback_data: TimeChooserCallback):
    selected, hour, minute = await SimpleTimeChooser().process_selection(callback_query, callback_data)
    if not selected:
        return
    await state.update_data({
        "birth_hour": hour,
        "birth_minute": minute,
    })

    await callback_query.message.edit_text(_("Write the city and country of birth, for example: Nikolaev, Ukraine."))
    await state.set_state(NatalStates.get_birth_city)


async def handle_birth_city(message: types.message.Message, state: FSMContext):
    buttons = await get_geonames_buttons(message.text)
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

    poll_options = [
        _("Strengths & Weaknesses"),
        _("Career & Realization"),
        _("Mission"),
        _("Relationships"),
        _("Harmony & Balance"),
        _("Finances"),
        _("Blog Topics"),
        _("Success Story"),
    ]
    await callback_query.message.answer_poll(
        options=poll_options,
        allows_multiple_answers=True,
        question=_("Choose topics that interest you (at least one):"),
        is_anonymous=False
    )


async def handle_poll(poll: types.Poll, bot: Bot, fsm_storage: MemoryStorage, *args, **kwargs):
    # selected_topics = []
    # iter_num_option = 0
    # for option in poll.options:
    #     if option.voter_count > 0:
    #         selected_topics.append({"option": option.text, "id": iter_num_option})
    #     iter_num_option += 1
    #
    # state_data = await state.get_data()
    # person = AstrologicalSubject(
    #     name=state_data["name"],
    #     year=int(state_data["birth_year"]),
    #     month=int(state_data["birth_month"]),
    #     day=int(state_data["birth_day"]),
    #     hour=int(state_data["birth_hour"]),
    #     city=state_data["birth_city"],
    #     lat=state_data["lat"],
    #     lng=state_data["lng"]
    # )
    # astro_data = create_table_chart(
    #     person.planets_list,
    #     person.first_house,
    #     person.tenth_house
    # )
    #
    # openai_service = OpenAIService(
    #     api_key=config.openai.token
    # )
    #
    # system_prompt = _(
    #     "You're an astrologer aiming for maximum personalization of responses based on the user's astrological data. "
    #     "Communicate using \"you\", adopting a youthful style with elements of modern slang, but do so flexibly and "
    #     "appropriately. Inject humor and amusing descriptions where it's adequate and cannot be misinterpreted."
    # )
    #
    # query_message = _(
    #     "Perform a detailed astrological analysis of the user's natal chart.  Don't forget to write in your answer  "
    #     "house numbers when responding.\n"
    #     f"Client: {person.name}\n"
    #     f"Data: {astro_data}"
    # )
    #
    # entrance_completion, messages = await openai_service.chat_completion(
    #     query=query_message,
    #     system_prompt=system_prompt,
    # )
    #
    # topic_prompts = [
    #     _("Describe 5 unique strengths of the User and 3 areas for growth that they should work on. The answer must "
    #       "contain no more than 1000 characters. Add emoji. The answer to this question is based on the analysis of "
    #       "the natal chart."),
    #     _("What fields of activity could the user engage in to fully realize themselves? The answer must contain no "
    #       "more than 1500 characters. Add emoji. The answer to this question is based on the analysis of the natal "
    #       "chart."),
    #     _("What is the User’s mission? How can the User benefit humanity? The answer must contain no more than 1500 "
    #       "characters. Add emoji. The answer to this question is based on the analysis of the natal chart."),
    #     _("With what partner can the User build harmonious relationships? The answer must contain no more than 1000 "
    #       "characters. Add emoji. The answer to this question is based on the analysis of the natal chart."),
    #     _("How can the User achieve harmony and balance in life? Highlight 5 key points. The answer must contain no "
    #       "more than 1000 characters. Add emoji. The answer to this question is based on the analysis of the natal "
    #       "chart."),
    #     _("How can the User achieve financial well-being? Describe one of the most suitable paths for the User. The "
    #       "answer must contain no more than 2000 characters. Add emoji. The answer to this question is based on the "
    #       "analysis of the natal chart. Give some tips for achieving financial prosperity. Give some tips for "
    #       "financial literacy. Consider what financial mistakes a user can make.  Advise what books to read for this "
    #       "purpose."),
    #     _("How should a user express himself on a blog?\n\n"
    #       "Specify Which blog topics are close to the user:\n"
    #       "- Personal blogs,\n"
    #       "- Niche blogs or professional blogs,\n"
    #       "- Corporate and business blogs,\n"
    #       "- Educational blogs,\n"
    #       "- Travel,\n"
    #       "- Fashion and Beauty,\n"
    #       "- Technology and Gadgets,\n"
    #       "- Sports and Fitness,\n"
    #       "- Arts and Culture.\n\n"
    #       "Specify What type of blog is appropriate for the user:\n"
    #       "- Text,\n"
    #       "- photo,\n"
    #       "- video podcasts (youtube or short videos),\n"
    #       "- audio podcasts,\n"
    #       "- microblogging (for example Twitter, but not only)\n"
    #       "Give Recommendations for blog promotion.\n"
    #       " Indicate Which social networks are better suited.\n"
    #       "The answer should be no more than 1500 characters. Add an emoji. The answer to this question is based on "
    #       "analyzing a natal chart.\n"
    #       ),
    #     _("Write the User's success story based on the data from their natal chart. The answer must contain no more "
    #       "than 2000 characters. Add emoji. The answer to this question is based on all previous answers.")
    # ]
    #
    # completions_list = []
    # # RELATIONSHIPS
    # for selected_topic in selected_topics:
    #     temp_comp, tmp_msg = await openai_service.chat_completion(topic_prompts[selected_topic["id"]], system_prompt=system_prompt, messages=messages)
    #     completions_list.append(temp_comp)
    #
    # images = await openai_service.image_generation(
    #     prompt=f"Create image that reproduce information of Natal Chart\n {entrance_completion}"
    # )
    # telegraph = Telegraph()
    # await telegraph.create_account(short_name='JettAstro')
    #
    # html_content = ""
    # for image in images:
    #     image_th_path = await telegraph.upload_file(image)
    #     html_content += f'<img src="{image_th_path[0]["src"]}">'
    #
    # for completion in completions_list:
    #     html_content += (f"<p>{completion}</p>")
    #
    # telegraph_response = await telegraph.create_page(
    #     title=f'{person.name} Описание',
    #     html_content=html_content
    # )
    #
    # print(telegraph_response['url'])
    #
    # await bot.send_message(text=telegraph_response["url"], chat_id=state_data["chat_id"])
    #
    # await state.set_state()
    pass


async def handle_poll_answer(poll_answer: types.PollAnswer, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    person = AstrologicalSubject(
        name=state_data["name"],
        year=int(state_data["birth_year"]),
        month=int(state_data["birth_month"]),
        day=int(state_data["birth_day"]),
        hour=int(state_data["birth_hour"]),
        city=state_data["birth_city"],
        lat=state_data["lat"],
        lng=state_data["lng"]
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
        "appropriately. Inject humor and amusing descriptions where it's adequate and cannot be misinterpreted."
    )

    query_message = _(
        "Perform a detailed astrological analysis of the user's natal chart.  Don't forget to write in your answer  "
        "house numbers when responding.\n"
        f"Client: {person.name}\n"
        f"Data: {astro_data}"
    )

    entrance_completion, messages = await openai_service.chat_completion(
        query=query_message,
        system_prompt=system_prompt,
    )

    topic_prompts = [
        _("Describe 5 unique strengths of the User and 3 areas for growth that they should work on. The answer must "
          "contain no more than 1000 characters. Add emoji. The answer to this question is based on the analysis of "
          "the natal chart."),
        _("What fields of activity could the user engage in to fully realize themselves? The answer must contain no "
          "more than 1500 characters. Add emoji. The answer to this question is based on the analysis of the natal "
          "chart."),
        _("What is the User’s mission? How can the User benefit humanity? The answer must contain no more than 1500 "
          "characters. Add emoji. The answer to this question is based on the analysis of the natal chart."),
        _("With what partner can the User build harmonious relationships? The answer must contain no more than 1000 "
          "characters. Add emoji. The answer to this question is based on the analysis of the natal chart."),
        _("How can the User achieve harmony and balance in life? Highlight 5 key points. The answer must contain no "
          "more than 1000 characters. Add emoji. The answer to this question is based on the analysis of the natal "
          "chart."),
        _("How can the User achieve financial well-being? Describe one of the most suitable paths for the User. The "
          "answer must contain no more than 2000 characters. Add emoji. The answer to this question is based on the "
          "analysis of the natal chart. Give some tips for achieving financial prosperity. Give some tips for "
          "financial literacy. Consider what financial mistakes a user can make.  Advise what books to read for this "
          "purpose."),
        _("How should a user express himself on a blog?\n\n"
          "Specify Which blog topics are close to the user:\n"
          "- Personal blogs,\n"
          "- Niche blogs or professional blogs,\n"
          "- Corporate and business blogs,\n"
          "- Educational blogs,\n"
          "- Travel,\n"
          "- Fashion and Beauty,\n"
          "- Technology and Gadgets,\n"
          "- Sports and Fitness,\n"
          "- Arts and Culture.\n\n"
          "Specify What type of blog is appropriate for the user:\n"
          "- Text,\n"
          "- photo,\n"
          "- video podcasts (youtube or short videos),\n"
          "- audio podcasts,\n"
          "- microblogging (for example Twitter, but not only)\n"
          "Give Recommendations for blog promotion.\n"
          " Indicate Which social networks are better suited.\n"
          "The answer should be no more than 1500 characters. Add an emoji. The answer to this question is based on "
          "analyzing a natal chart.\n"
          ),
        _("Write the User's success story based on the data from their natal chart. The answer must contain no more "
          "than 2000 characters. Add emoji. The answer to this question is based on all previous answers.")
    ]

    completions_list = []
    # RELATIONSHIPS
    for id in poll_answer.option_ids:
        temp_comp, tmp_msg = await openai_service.chat_completion(
            topic_prompts[id],
            system_prompt=system_prompt,
            messages=messages
        )
        completions_list.append(temp_comp)

    images = await openai_service.image_generation(
        prompt=f"Create image that reproduce information of Natal Chart\n {entrance_completion}"
    )
    telegraph = Telegraph()
    await telegraph.create_account(short_name='JettAstro')

    html_content = ""
    for image in images:
        image_th_path = await telegraph.upload_file(image)
        html_content += f'<img src="{image_th_path[0]["src"]}">'

    for completion in completions_list:
        html_content += (f"<p>{completion}</p>")

    telegraph_response = await telegraph.create_page(
        title=f'{person.name} Описание',
        html_content=html_content
    )

    print(telegraph_response['url'])

    await bot.send_message(text=telegraph_response["url"], chat_id=state_data["chat_id"])

    await state.set_state()


async def handle_get_birth_citydd(message: types.message.Message, state: FSMContext, bot: Bot) -> None:
    await message.answer("Немного подождите")
    state_data = await state.get_data()
    birth_city = message.text

    person = AstrologicalSubject(
        name=state_data["name"],
        year=int(state_data["birth_year"]),
        month=int(state_data["birth_month"]),
        day=int(state_data["birth_day"]),
        hour=int(state_data["birth_hour"]),
        city=birth_city
    )

    astro_data = create_table_chart(person.planets_list, person.first_house, person.tenth_house)
    openai_service = OpenAIService(
        api_key=config.openai.token
    )

    system_prompt = (
        "Ты виртуальный астролог. Отвечай на вопросы опираясь на контекст астрологических данных пользователя. "
        "Обращайся на \"ты\". Не говори \"вы\". Твой стиль молодежный, немного с современный сленгом. Добавляй иногда "
        "юмор и смешные описания или ситуации.")

    query_message = (
        "Выполни астрологический анализ натальной карты для пользователя. Учти положение Солнца, Луны, Меркурия, "
        "Венеры, Марса, Юпитера, Сатурна, Урана, Нептуна, Плутона, Хирона, Лилит, Селены, Восходящего и Нисходящего "
        "узлов, Парса Фортуны, Вертекса, а также Асцендента.  Учти взаимодействия и аспекты между планетами, "
        "положение планет в знаках задиака и домах.\n"
        f"Пользователь: {person.name}\n"
        f"Дата: {astro_data}"
    )
    print(system_prompt)
    print(query_message)
    query_completion = await openai_service.chat_completion(
        query=query_message,
        system_prompt=system_prompt,
    )

    images = await openai_service.image_generation(
        prompt=f"Create image that reproduce information of Natal Chart\n {query_completion}"
    )

    print(images)

    telegraph = Telegraph()
    await telegraph.create_account(short_name='JettAstro')

    html_content = ""
    for image in images:
        image_th_path = await telegraph.upload_file(image)
        html_content += f'<img src="{image_th_path[0]["src"]}">'

    html_content += (
        f"<p>Here is your natal Chart</p>"
        f"<p>{query_completion}</p>"
    )

    telegraph_response = await telegraph.create_page(
        title=f'{person.name} Описание',
        html_content=html_content
    )

    print(telegraph_response['url'])

    await message.answer(telegraph_response["url"])

    await state.set_state()
