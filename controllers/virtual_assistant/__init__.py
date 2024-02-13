from aiogram import Router
from . import chat
def prepare_router() -> Router:
    virtual_assistant = Router()
    virtual_assistant.callback_query.register(chat.callback_start_chat, lambda c: c.data == "/chat_with_va")
    return virtual_assistant
