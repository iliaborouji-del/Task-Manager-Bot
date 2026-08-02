from aiogram.fsm.state import State, StatesGroup


class CategoriesStates(StatesGroup):
    waiting_for_choose = State()
    
    waiting_for_category_name = State()

    selected_category = State()

    waiting_for_new_category_name = State()

    waiting_for_move_category = State()

    waiting_for_task_category = State()