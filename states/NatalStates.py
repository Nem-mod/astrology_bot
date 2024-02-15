from aiogram.fsm.state import StatesGroup, State


class NatalStates(StatesGroup):
    get_name = State()
    get_gender = State()
    get_birthday = State()
    get_birthtime = State()
    get_birth_city = State()
    ignore = State()
