from aiogram import Router

from states import UserStates
from . import chat
def prepare_router() -> Router:
    virtual_assistant = Router()
    virtual_assistant.callback_query.register(chat.callback_start_chat, lambda c: c.data == "/chat_with_va")
    virtual_assistant.message.register(chat.handle_chat, UserStates.va_chat)
    return virtual_assistant
