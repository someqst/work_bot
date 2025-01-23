from aiogram import F, Router
from loader import db, bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from data.buttons import select_role


router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message):
    await db.create_user(message.from_user.id, message.from_user.username)
    await message.answer('Выберите вашу роль', reply_markup=select_role.as_markup())


# Выбор новой роли (работодатель | работник)
@router.callback_query(F.data == 'change_role')
async def change_role(call: CallbackQuery):
    jobs_to_delete = ''
    user_ads = await db.get_user_ads(call.from_user.id)
    if user_ads:
        jobs_to_delete+="Ваши работы удалятся:\n"
        for ad in user_ads:
            jobs_to_delete+=f'*{ad.title}*\n'
        jobs_to_delete+='\n'
        print(jobs_to_delete)
    await bot.send_message(call.from_user.id, f'{jobs_to_delete}Хотите изменить вашу роль?\n', reply_markup=select_role.as_markup(), parse_mode='Markdown')


# @router.callback_query(F.data.in_({'im_employeer', 'im_worker'}))
# async def select_role(call: CallbackQuery):
#     await call.answer()



    