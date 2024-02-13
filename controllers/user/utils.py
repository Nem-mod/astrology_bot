from pathlib import Path

from aiogram import types, Bot
from kerykeion import AstrologicalSubject
from telegraph import Telegraph

from aiogram.utils.i18n import gettext as _, FSMI18nMiddleware
from data.config import config
from services import OpenAIService, ClickUpService
from utils import TelegraphHelper
from utils.create_table_chart import create_table_chart

async def form_not_completed(bot: Bot, chat_id: str, crm_record_id: str):
    await bot.send_message(
        chat_id=chat_id,
        text=_("Any difficulties? Do you ask your mother your birth time? Do you doubt AstroBot? Keep going, "
               "it will be interesting! Instead of mom, write @maginoid to get help")
    )

    await ClickUpService.update_task_custom_status(task_id=crm_record_id, value="form not completed")


async def create_telegraph_article(state_data: dict, poll_answer: types.PollAnswer) -> tuple[str, str]:

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
        "You must response in HTML format. Use only AVAILEBLE HTML tags\n AVAILABLE HTML tags are <p>, <b>, "
        "<i>. Do not use list tags."
    )

    query_message = _(
        "Perform a detailed astrological analysis of the user's natal chart.  Don't forget to write in your answer  "
        "house numbers when responding.\n"
        "Client: {name}\n"
        "Data: {astro_data}"
    ).format(name=person.name, astro_data=astro_data)

    natal_summary, messages = await openai_service.chat_completion(
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
        prompt=f"Create an image of the user based on the personality description from the natal chart. The image "
               f"format is 9 by width, 16 by height.",
        extra_query=f"Person's gender: {state_data['gender']}\n Astrological analysis: {natal_summary}"
    )

    for image in images:
        image_th_path = await telegraph.upload_file(image)
        html_content += f'<img src="{image_th_path[0]["src"]}">'

    telegraph_response = await telegraph.create_page(
        title=_("Astrological analysis: {name} {zodiac}").format(name=person.name, zodiac=person.sun.emoji),
        html_content=html_content
    )

    for image in images:
        try:
            fp = Path(image)
            fp.unlink()
        except Exception as err:
            print(err)

    return telegraph_response["url"], natal_summary
