import asyncio
from datetime import datetime
from pytz import timezone
from loader import db, bot


async def delete_works():
    time_now = datetime.now(timezone('Europe/Moscow')).replace(tzinfo=None)

    works = await db.select_expired_works(time_now)
    if works:
        sended = 0
        for work in works:
            if sended >= 30:
                await asyncio.sleep(1.5)
                sended = 0
            try:
                await bot.send_message(work.worker, f'Вы не успели сдать работу {work.title}. Она была отменена.')
                await bot.send_message(work.owner, f'Вашу работу "{work.title}" не успели выполнить в срок. Она снова помещена в статус "активна"')
                await db.delete_expired_work(work.id)
                sended += 2
            except Exception as e:
                print(e)
    