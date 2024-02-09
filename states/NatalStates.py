from aiogram.fsm.state import StatesGroup, State


class NatalStates(StatesGroup):
    get_name = State()
    get_birth_year = State()
    get_birth_month = State()
    get_birth_day = State()
    get_birth_hour = State()
    get_birth_city = State()
