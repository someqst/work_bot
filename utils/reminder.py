from loader import db, bot
import asyncio


async def remaind_about_work_1hour():
    works = await db.get_works_for_remind_1hour()

    if not works:
        return
    
    sended = 0
    for work in works:
        if sended >= 30:
            await asyncio.sleep(1.5)
            sended = 0
        try:
            await bot.send_message(work.worker,
f'''❗️Поторопитесь❗️

У вас остался *один час* до сдачи задания

*"{work.title}"*

Закрыть задачу можно по пути:
/profile -> Активные работы

''', parse_mode='Markdown')
            sended += 1
        except:
            pass


async def remaind_about_work_30mins():
    works = await db.get_works_for_remind_30min()

    if not works:
        return
    
    sended = 0
    for work in works:
        if sended >= 30:
            await asyncio.sleep(1.5)
            sended = 0
        try:
            await bot.send_message(work.worker,
f'''❗️Поторопитесь❗️

У вас осталось *30 минут* до сдачи задания

*"{work.title}"*

Закрыть задачу можно по пути:
/profile -> Активные работы

''', parse_mode='Markdown')
            sended += 1
        except:
            pass