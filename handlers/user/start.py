from aiogram import Router, F
from loader import db
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from data.buttons import build_start_kb
from aiogram.fsm.context import FSMContext
from handlers.states import UserCreation


router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    await message.delete()
    user = await db.get_user(message.from_user.id)
    if user:
        kb = (await build_start_kb(False, user.role)).adjust(1)
        return await message.answer('Выберите действие', reply_markup=kb.as_markup())
    
    kb = (await build_start_kb(True)).adjust(1)
    await db.create_user(message.from_user.id, message.from_user.username)
    await state.set_state(UserCreation.select_role)
    return await message.answer('Выберите вашу роль', reply_markup=kb.as_markup())

