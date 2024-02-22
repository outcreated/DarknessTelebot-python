from aiogram.fsm.state import StatesGroup, State


class Registered(StatesGroup):
    register_state = State()
