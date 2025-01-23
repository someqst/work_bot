from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from loader import bot, db
from aiogram.fsm.context import FSMContext
from handlers.states import Employeer
from data.buttons import build_profile_kb, build_jobs_kb
from aiogram.filters import Command


router = Router()


# ------ Профиль по команде --------
@router.message(Command('profile'))
async def profile_cmd(message: Message):
    user = await db.get_user(message.from_user.id)
    kb = (await build_profile_kb(user.id, user.role)).adjust(1)

    await message.answer(
f'''
Место: {user.location or "Не задано"}
Баланс: {user.balance_deposit if user.role == "employeer" else user.balance_earned}
{"Выполденные задания: " + user.done_works if user.role == "worker" else ''}
Рейтинг: ?
''', reply_markup=kb.as_markup())


# ------ Профиль по inline клавиатуре --------
@router.callback_query(F.data == 'profile_call')
async def profile_call(call: CallbackQuery):
    await call.answer()
    user = await db.get_user(call.from_user.id)
    kb = (await build_profile_kb(user.id, user.role)).adjust(1)

    await call.message.edit_text(
f'''
Место: {user.location or "Не задано"}
Баланс: {user.balance_deposit if user.role == "employeer" else user.balance_earned}
{"Выполденные задания: " + user.done_works if user.role == "worker" else ''}
Рейтинг: ?
''', reply_markup=kb.as_markup())


@router.callback_query(F.data == 'get_my_jobs_emp')
async def get_my_jobs_emp(call: CallbackQuery):
    await call.answer()
    kb = await build_jobs_kb(call.from_user.id)
    await call.message.edit_text('Выберите работу', reply_markup=kb.as_markup())



@router.callback_query(F.data.startswith('jb_'))
async def select_job(call: CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, f'Ты выбрал работу {(call.data).split('_')[1]}')




