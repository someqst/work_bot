from aiogram import Router
from loader import db
from aiogram.types import Message
from aiogram.filters import CommandStart
from data.buttons import build_start_kb
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if user:
        await state.clear()
        kb = (await build_start_kb(False, user.role)).adjust(1)
        return await message.answer('Выберите действие', reply_markup=kb.as_markup())
    
    kb = (await build_start_kb(True)).adjust(1)
    return await message.answer('Выберите вашу роль', reply_markup=kb.as_markup())
