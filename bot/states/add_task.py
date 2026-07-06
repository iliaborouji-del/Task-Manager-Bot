from aiogram.fsm.state import State, StatesGroup

class AddTaskStates(StatesGroup):

    title = State()
    
    description = State()
    
    priority = State()
    
    deadline = State()
    
    status = State()
    
class Deadline(StatesGroup):
    year = State()
    
    month = State()
    
    day = State()
    
    time = State()