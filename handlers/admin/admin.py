from aiogram import F, Router
from aiogram.filters import Command
from data.config import admins
from loader import db
from aiogram.types import Message, CallbackQuery
from data.buttons import admin_kb
from handlers.states import Admin
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(Command('admin'), F.from_user.id.in_(admins))
async def admin_cmd(message: Message):
    await message.answer('Выберите действие', reply_markup=admin_kb.as_markup())


# ----- Выдача баланса -------

@router.callback_query(F.data == 'give_money_employeer')
async def give_emp_money(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите username или user_id')
    await state.set_state(Admin.give_emp_balance)


@router.message(Admin.give_emp_balance, F.text)
async def enter_information(message: Message, state: FSMContext):
    data = await state.get_data()

    if not data.get('user_info'):
        await state.update_data(user_info = message.text)
        return await message.answer('Введите, сколько хотите положить денег на баланс')
    
    user_info: str = data.get('user_info')
    if user_info.isdigit():
        user = await db.get_user(int(user_info))
    else:
        if '@' in user_info:
            user_info = user_info.removeprefix('@')
        user = await db.get_user_by_username(user_info)
    
    if not user:
        await state.clear()
        return await message.answer('Пользователь не был найден')
    
    try:
        await db.update_employeer_balance(user.id, int(message.text))
        await message.answer('Баланс успешно выдан')
    except Exception as e:
        await message.answer('Ошибка')
    await state.clear()

