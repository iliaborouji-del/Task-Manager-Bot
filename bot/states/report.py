from aiogram.fsm.state import State, StatesGroup

class ReportState(StatesGroup):
    waiting_for_date_range = State()