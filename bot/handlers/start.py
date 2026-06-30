from aiogram import filters, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from states.start import BotStates
from keyboards.start import markup, start_text

router = Router()

@router.message(filters.CommandStart)
async def start(message: Message, state: FSMContext):
    await message.answer(text=start_text, reply_markup=markup)
    await state.set_state(BotStates.waiting_for_main_menu_button)