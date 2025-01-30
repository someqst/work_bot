from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from loader import db, bot
from data.buttons import settings_kb, online_work, remove_reply_kb
from handlers.states import EveryOne
from aiogram.fsm.context import FSMContext

router = Router()


@router.callback_query(F.data == 'edit_user_settings')
async def edit_user_settings(call: CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, 'Что вы хотите изменить?', reply_markup=settings_kb.as_markup())


# --------- Изменение локации ----------
@router.callback_query(F.data == 'change_location')
async def change_location(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await bot.send_message(call.from_user.id, 'Введите локацию', reply_markup=online_work)
    await state.set_state(EveryOne.change_location)


@router.message(EveryOne.change_location, F.text)
async def enter_location(message: Message, state: FSMContext):
    await message.answer('Локация успешно изменена', reply_markup=remove_reply_kb)
    if (message.text).isdigit():
        return await message.answer('Введите название населенного пункта')
    await state.clear()
    await db.change_user_location(message.from_user.id, (message.text).lower())


# ------------ Выбор новой роли (работодатель | работник) ---------
@router.callback_query(F.data == 'change_role')
async def change_role(call: CallbackQuery):
    await call.answer()
    
    user = await db.get_user(call.from_user.id)
    if user.role == 'employeer':
        await db.change_user_role(call.from_user.id, 'worker')
        await bot.send_message(call.from_user.id, 'Вы не сможете видеть ваши работы и статус их выполнения. Чтобы вернуть все как было, снова поменяйте роль!')
    else:
        await db.change_user_role(call.from_user.id, 'employeer')
        await bot.send_message(call.from_user.id, 'Ваша роль успешно изменена')


# ----------- Изменение about -------------
@router.callback_query(F.data == 'change_about')
async def change_about(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(EveryOne.change_about)
    await bot.send_message(call.from_user.id, 'Введите новое описание профиля. (не более 3500 символов)')


@router.message(EveryOne.change_about, F.text)
async def change_about_text(message: Message, state: FSMContext):
    if len(message.text) > 3500:
        return await message.answer('Вы ввели более 3500 символов')
    
    await state.clear()
    await db.change_user_about(message.from_user.id, message.text)
    return await message.answer('Описание успешно изменено')
