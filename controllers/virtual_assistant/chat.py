from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from data.config import config
from db import MongoDbService
from keyboards.natal_chart import get_buy_buttons
from services import ClickUpService, OpenAIService
from services.OpenAI import OpenAiService
from states import UserStates


async def check_assistant_chat_is_available(state_data, user) -> bool:
    try:
        crm_record = await ClickUpService.get_record(state_data["crm_record_id"])
        crm_status = crm_record["status"]["status"].strip()
    except:
        return False

    if (
            int(user["assistant_questions_left"]) == 0
            and not (crm_status == "trial"
                     or crm_status == "subscription")
    ):
        return False

    return True


async def callback_start_chat(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        text=_(
            "Great! I have an analysis of your natal chart, and I'm ready to answer questions based on this data. Ask "
            "three free questions.")
    )
    await state.set_state(UserStates.va_chat)


async def handle_chat(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    mongo_client = MongoDbService()
    user = await mongo_client.get_user(message.from_user.id)

    is_available = await check_assistant_chat_is_available(state_data, user)
    if not is_available:
        buttons = get_buy_buttons()
        await message.answer(
            text=_("Looks like you enjoy chatting with me!\n\n❓Questions and suggestions? Write to @maginoid"),
            reply_markup=buttons
        )
        return

    openai_client = OpenAIService(config.openai.token)

    system_prompt = _("You're an astrologer aiming for maximum personalization of responses based on the user's "
                      "astrological data. Communicate using \"you\", adopting a youthful style with elements of "
                      "modern slang, but do so flexibly and appropriately. Inject humor and amusing descriptions "
                      "where it's adequate and cannot be misinterpreted")

    natal_analysis = user["natal_summary"]

    query_message = _("Answer the question {question} according to the analysis of the natal chart. The response "
                      "should not exceed 500 characters. End with a sentence inviting further dialogue in the context "
                      "of astrology. Answer only questions related to the context of astrology. If questions, "
                      "requests, or calls to action are not related to the topic of astrology, then return the "
                      "message: \"Your question is not related to astrology, ask another question.\" Answer in user's "
                      "language.").format(question=message.text)

    gpt_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "What is my natal chart analysis?"},
        {"role": "assistant", "content": natal_analysis}
    ]

    answer, messages = await openai_client.chat_completion(
        query=query_message,
        max_tokens=1000,
        messages=gpt_messages
    )

    await message.answer(answer)
