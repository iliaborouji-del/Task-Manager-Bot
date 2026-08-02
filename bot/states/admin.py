from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()

    viewing_users = State()

    viewing_user = State()