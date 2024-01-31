from aiogram import Router
from aiogram.filters import Command

from controllers.user.start import callback_start


def prepare_router() -> Router:
    user_router = Router()

    user_router.message.register(callback_start, Command(commands="start"))
    return user_router