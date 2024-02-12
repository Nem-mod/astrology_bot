from aiogram import Router, F
from aiogram.filters import Command

from controllers.user import start
from controllers.user import back_handlers as back
from keyboards.natal_chart.callbacks import CalendarCallback, TimeChooserCallback, GeoNameCallback, GeoNameActions, \
    GendersCallback
from keyboards.user.callbacks import SetLocalesCallback
from states import NatalStates


def prepare_router() -> Router:
    user_router = Router()

    user_router.message.register(start.callback_start, Command(commands="start"))

    user_router.callback_query.register(start.callback_start_calculation, lambda c: c.data == "/start_natal_calc")
    user_router.callback_query.register(start.callback_select_language, SetLocalesCallback.filter())

    user_router.message.register(start.handle_get_name, NatalStates.get_name)
    user_router.callback_query.register(start.callback_get_gender, GendersCallback.filter())
    user_router.message.register(start.handle_birthday, NatalStates.get_birthday)
    user_router.callback_query.register(start.callback_set_default_birthtime, lambda c: c.data == "/set_default_birthtime")
    user_router.message.register(start.hande_get_birthtime, NatalStates.get_birthtime)

    # user_router.callback_query.register(start.callback_calendar, CalendarCallback.filter())
    # user_router.callback_query.register(start.callback_time_chooser, TimeChooserCallback.filter())
    user_router.message.register(start.handle_birth_city, NatalStates.get_birth_city)
    user_router.callback_query.register(start.callback_chose_city,
                                        GeoNameCallback.filter(F.action == GeoNameActions.choose))
    user_router.poll_answer.register(start.handle_poll_answer)


    # BACK BUTTONS
    user_router.callback_query.register(back.callback_back_from_select_name,
                                        lambda c: c.data == "/cancel_creating_natal_chart")
    user_router.callback_query.register(back.callback_back_from_gender,
                                        lambda c: c.data == "/cancel_select_gender")

    user_router.callback_query.register(back.callback_back_from_birthday,
                                        lambda c: c.data == "/cancel_get_birthday")
    user_router.callback_query.register(back.callback_back_fom_birhttime,
                                        lambda c: c.data == "/cancel_get_birthtime")
    user_router.callback_query.register(back.callback_back_from_birth_city,
                                        lambda c: c.data == "/cancel_get_birth_city")

    return user_router
