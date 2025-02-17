from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from loader import db
from data.buttons import build_profile_kb
from aiogram.filters import Command


router = Router()


# ------ Профиль по команде --------
@router.message(Command('profile'))
async def profile_cmd(message: Message):
    await message.delete()
    user = await db.get_user(message.from_user.id)
    kb = (await build_profile_kb(user.id, user.role)).adjust(1)

    await message.answer(
f'''
Место: *{user.location or "Не задано"}*
Баланс: *{user.balance_deposit if user.role == "employeer" else user.balance_earned}*
{"Выполнeнные задания: " + f"*{user.done_works}*" if user.role == "worker" else ''}
Рейтинг: *?*
Описание: _{user.about if user.about else 'Нет'}_
''', reply_markup=kb.as_markup(), parse_mode='Markdown')


# ------ Профиль по inline клавиатуре --------
@router.callback_query(F.data == 'profile_call')
async def profile_call(call: CallbackQuery):
    await call.answer()
    user = await db.get_user(call.from_user.id)
    kb = (await build_profile_kb(user.id, user.role)).adjust(1)

    await call.message.edit_text(
f'''
Место: *{user.location or "Не задано"}*
Баланс: *{user.balance_deposit if user.role == "employeer" else user.balance_earned}*
{"Выполнeнные задания: " + f"*{user.done_works}*" if user.role == "worker" else ''}
Рейтинг: *?*
Описание: _{user.about if user.about else 'Нет'}_
''', reply_markup=kb.as_markup(), parse_mode='Markdown')
