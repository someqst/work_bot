from aiogram import F, Router
from aiogram.types import CallbackQuery
from loader import db, bot
from data.buttons import (build_chat_kb, build_support_kb)
from data.config import admins


router = Router()


# ------- Работа принята и закончена --------
@router.callback_query(F.data.startswith('approve_'))
async def approve_work(call: CallbackQuery):
    await call.answer()
    await call.message.delete()
    work_process = await db.get_work_process_by_id((call.data).split('_')[1])

    try:
        await bot.send_message(work_process.worker, f'Работа *"{work_process.title}"* подтверждена!\nСредства ({work_process.price}) будут зачислены на ваш счет.',
                               parse_mode='Markdown')
    except:
        pass
    
    await db.update_worker_balance(work_process.worker, work_process.price)
    await db.close_work(work_process.id)
    await bot.send_message(call.from_user.id, 'Работа подтверждена и закрыта. Средства отправлены исполнителю.')


# -------- Обсудить детальки ----------
@router.callback_query(F.data.startswith('ask_worker_'))
async def approve_work(call: CallbackQuery):
    await call.answer()
    work = await db.get_work_process_by_id((call.data).split('_')[2])

    try:
        await bot.send_message(work.worker, f'С вами хотят связаться по заданию *{work.title}*',
                           reply_markup=(await build_chat_kb(call.from_user.id, work.worker, 'worker')).as_markup(), parse_mode='Markdown')
        await bot.send_message(call.from_user.id, 'Отправили запрос на начало чата исполнителю')
    except:
        await bot.send_message(call.from_user.id, 'Не получилось отправить запрос на начало чата исполнителю')


# -------- Отменить работу ----------
@router.callback_query(F.data.startswith('declince_'))
async def approve_work(call: CallbackQuery):
    await call.answer()
    work_process = await db.get_work_process_by_id((call.data).split('_')[1])
    work = await db.get_work_by_id((call.data).split('_')[1])

    try:
        await bot.send_message(work_process.worker, f'Работодатель отменил работу *"{work.title}"*\n\nПроверяем детали', parse_mode='Markdown')
        await bot.send_message(call.from_user.id, 'Отправили отказ исполнителю и поддержке. Ожидайте результат рассмотрения.')
        for admin in admins:
            await bot.send_document(admin, call.message.document.file_id,
                                    caption=f'Отменили работу {work.id}\n\n_{work.description}_',
                                    reply_markup=(await build_support_kb(work.id)).as_markup(), parse_mode='Markdown')
    except Exception as e:
        print(e)
        await bot.send_message(call.from_user.id, 'Не получилось отменить работу')


