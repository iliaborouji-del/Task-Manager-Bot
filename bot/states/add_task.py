from aiogram.fsm.state import State, StatesGroup

class AddTaskStates(StatesGroup):

    title = State()
    
    description = State()
    
    category = State()
    
    priority = State()
    
    deadline = State()
    
    status = State()
    
    waiting_for_category = State()
    
class Deadline(StatesGroup):
    year = State()
    
    month = State()
    
    day = State()
    
    time = State()