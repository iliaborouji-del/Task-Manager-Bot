from aiogram import filters, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.states.start import BotStates
from bot.keyboards.start import create_main_menu_keyboard, start_text

router = Router()

@router.message(filters.CommandStart)
async def start(message: Message, state: FSMContext):
    await message.answer(text=start_text, reply_markup=create_main_menu_keyboard())
    await state.set_state(BotStates.waiting_for_main_menu_button)