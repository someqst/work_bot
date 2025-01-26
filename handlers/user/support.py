from aiogram import F, Router
from aiogram.types import CallbackQuery
from loader import db, bot


router = Router()


@router.callback_query(F.data.startswith('des_ok_'))
async def declince_work(call: CallbackQuery):
    await call.answer()
    work_process = await db.get_work_process_by_id((call.data).split('_')[2])

    await db.delete_worker_from_work(work_process.worker, work_process.id)
    await bot.send_message(work_process.worker, 'Решением поддержки ваша работа была аннулирована.')


@router.callback_query(F.data.startswith('des_no_'))
async def declince_work_no(call: CallbackQuery):
    await call.answer()
    work_process = await db.get_work_process_by_id((call.data).split('_')[2])
    work = await db.get_work_by_id((call.data).split('_')[2])

    await db.update_worker_balance(work_process.worker, work.price)
    await db.close_work(work.id)

    await bot.send_message(work_process.worker, f'Ваша работа не была отменена.\n{work.price} начислены на ваш счет')
