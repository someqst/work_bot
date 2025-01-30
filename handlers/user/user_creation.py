from aiogram import Router, F
from loader import db, bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.states import UserCreation
from data.buttons import online_work, remove_reply_kb, build_start_kb


router = Router()


@router.callback_query(UserCreation.select_role, F.data.in_({'im_employeer', 'im_worker'}))
async def select_first_role(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    await state.update_data(role = (call.data).removeprefix('im_'))

    await state.set_state(UserCreation.enter_location)
    return await bot.send_message(call.from_user.id, 'Выберите локацию', reply_markup=online_work)


@router.message(UserCreation.enter_location, F.text)
async def location_entering(message: Message, state: FSMContext):
    if '/start' in (message.text) or '/profile' in (message.text):
        return await message.answer('Вам обязательно нужно ввести локацию.')
    
    await state.update_data(location = (message.text).lower())
    role = (await state.get_data()).get('role')

    await state.set_state(UserCreation.enter_about)
    if role == 'worker': 
        return await message.answer('Напишите немного о себе\n\nВаши навыки\nВаши компетенции. Не более 3500 символов', reply_markup=remove_reply_kb)
    return await message.answer('Напишите немного о вашей компании.\n\nВаше предложение\nВаша цель', reply_markup=remove_reply_kb)


@router.message(UserCreation.enter_about, F.text)
async def about_entering(message: Message, state: FSMContext):
    if '/start' in (message.text) or '/profile' in (message.text):
        return await message.answer('Вам обязательно нужно ввести описание.')

    if len(message.text) > 3500:
        return await message.answer('Вы ввели более 3500 символов.')
    
    data = await state.get_data()
    await state.clear()
    
    await db.create_user(message.from_user.id, message.from_user.username, data.get('location'), data.get('role'), message.text)
    await message.answer('Ваш профиль успешно создан', reply_markup=(await build_start_kb(False, data.get('role'))).adjust(1).as_markup())