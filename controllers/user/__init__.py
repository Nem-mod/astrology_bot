from aiogram import Router, F
from aiogram.filters import Command

from controllers.user import start
from keyboards.natal_chart.callbacks import CalendarCallback, TimeChooserCallback, GeoNameCallback, GeoNameActions
from states import NatalStates


def prepare_router() -> Router:
    user_router = Router()

    user_router.message.register(start.callback_start, Command(commands="start"))
    user_router.callback_query.register(start.callback_start_calculation, lambda c: c.data == "/start_natal_calc")

    user_router.message.register(start.handle_get_name, NatalStates.get_name)
    user_router.callback_query.register(start.callback_calendar, CalendarCallback.filter())
    user_router.callback_query.register(start.callback_time_chooser, TimeChooserCallback.filter())
    user_router.message.register(start.handle_birth_city, NatalStates.get_birth_city)
    user_router.callback_query.register(start.callback_chose_city, GeoNameCallback.filter(F.action == GeoNameActions.choose ))
    user_router.poll.register(start.handle_poll)
    user_router.poll_answer.register(start.handle_poll_answer)
    # user_router.message.register(start.handle_get_birth_day, NatalStates.get_birth_day)

    # user_router.message.register(start.handle_get_birth_city, NatalStates.get_birth_city)

    return user_router
