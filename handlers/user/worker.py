from pytz import timezone
from aiogram import F, Router
from datetime import datetime, timedelta
from aiogram.types import Message, CallbackQuery
from loader import db, bot
from aiogram.fsm.context import FSMContext
from handlers.states import Worker
from data.buttons import (build_works_kb, build_ok_kb,
                          build_approve_kb, build_chat_kb,
                          build_done_work_kb, build_jobs_kb, build_check_kb)


router = Router()


@router.callback_query(F.data == 'check_available_works')
async def check_available_works(call: CallbackQuery):
    await call.answer()
    user = await db.get_user(call.from_user.id)

    works = await db.select_opened_works_by_location(user.location)

    if works:
        kb = await build_works_kb(works)
        return await bot.send_message(call.from_user.id, 'Доступные работы:', reply_markup=kb.as_markup())
    
    return await bot.send_message(call.from_user.id, 'Нет активных работ *в вашей локации*\nВы можете изменить вашу локацию в /profile\n\n*Чтобы искать везде - сделайте "не важно".*',
                                  parse_mode='Markdown')


@router.callback_query(F.data.startswith('wrk_'))
async def get_work_by_kb(call: CallbackQuery, state: FSMContext):
    await call.answer()
    work = await db.get_work_by_id((call.data).removeprefix('wrk_'))

    if not work:
        return await bot.send_message(call.from_user.id, 'Работа была удалена')
    
    await bot.send_message(call.from_user.id, 
f'''
*{work.title}*

ЦЕНА: *{work.price}*
ВРЕМЯ НА ВЫПОЛНЕНИЕ: *{work.work_time} ч.*

_{work.description}_
''', reply_markup=(await build_ok_kb(work.id)).as_markup(), parse_mode='Markdown')
    await state.set_state(Worker.work_info)
    await state.update_data(work_title = work.title, work_id = str(work.id), work_owner = work.owner)


@router.callback_query(Worker.work_info, F.data.startswith('ok_'))
async def get_work_for_done(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    await bot.send_message(call.from_user.id, "Ожидайте, если работодатель одобрит вашу кандидатуру, мы дадим вам знать")

    data = await state.get_data()
    work_owner = data.get('work_owner')
    work_title = data.get('work_title')
    work_id = data.get('work_id')
     
    worker = await db.get_user(call.from_user.id)
    
    await bot.send_message(work_owner, 
f'''
Пользователь хочет выполнить вашу работу
*{work_title}*

Информация о пользователе:
UserName: {f"@{worker.username}" if worker.username else 'Нет'}
Описание работника:
_{worker.about or 'Нет'}_
''', parse_mode='Markdown', reply_markup=(await build_approve_kb(work_id, worker.id)).as_markup())
    await state.clear()


# ----- Уточнение деталей по работе -----
@router.callback_query(F.data.startswith('qst_'))
async def ask_question(call: CallbackQuery):
    await call.answer()

    owner = int((call.data).split('_')[2])
    work_id = (call.data).split('_')[1]

    work = await db.get_work_by_id(work_id)
    if not work:
        return await bot.send_message(call.from_user.id, 'Работа была удалена.')

    await bot.send_message(call.from_user.id, 'Отправили запрос на связь с работодателем')
    await bot.send_message(owner, f'С вами хотят связаться по заданию *{work.title}*',
                           reply_markup=(await build_chat_kb(owner, call.from_user.id, 'employeer')).as_markup(), parse_mode='Markdown')
    

# ------- Работа окончена ----------
@router.callback_query(F.data.startswith('done_'))
async def work_done(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Worker.work_done)
    await state.update_data(employeer = int((call.data).split('_')[2]))
    await state.update_data(work_id = (call.data).split('_')[1])
    await bot.send_message(call.from_user.id, 'Пришлите доказательства работы ❗️архивом❗️, чтобы поддержка смогла проверить информацию при спорной ситуации.')

    
@router.message(Worker.work_done, F.document)
async def send_done_archive(message: Message, state: FSMContext):
    data = await state.get_data()

    await bot.send_document(data.get('employeer'), document=message.document.file_id, caption=
'''
Ваша задача выполнена!
Вы можете принять задачу, тогда средства с вашего счета будут списаны и отправлены работнику, либо отменить задачу.
Если вы отмените задачу, поддержка проверит ее на факт выполнения и сделает вердикт о том, отменить ли задачу или начислить работнику деньги.
''', reply_markup=(await build_done_work_kb(data.get('work_id'))).as_markup())


# -------- Вход в чат с работником -----------
@router.callback_query(F.data.startswith('join_wrk_'))
async def join_chat_emp(call: CallbackQuery):
    await call.answer()
    employeer = int((call.data).split('_')[2])
    await bot.send_message(call.from_user.id, 'Если заходите выйти из чата, напишите /exit')
    await db.create_chat(call.from_user.id, employeer)
    
    try:
        await bot.send_message(employeer, 'Исполнитель вошел в диалог. Если захотите выйти из чата, пишите /exit')
    except:
        await bot.send_message(call.from_user.id, 'Сообщение не отправилось работнику. Он не зайдет.')


# ----- Работник смотрит свои работы -------
@router.callback_query(F.data == 'get_my_jobs_wrk')
async def get_my_jobs_emp(call: CallbackQuery):
    await call.answer()
    kb = await build_jobs_kb(call.from_user.id, 'worker')
    await call.message.edit_text('Выберите работу', reply_markup=kb.as_markup())



@router.callback_query(F.data.startswith('worker_select_'))
async def select_job(call: CallbackQuery):
    await call.answer()
    work_info = await db.get_work_by_id((call.data).split("_")[2])
    work_process_info = await db.get_work_process_by_id((call.data).split("_")[2])

    remain_time: timedelta = (work_process_info.end_time - datetime.now(timezone('Europe/Moscow')).replace(tzinfo=None))
    
    kb = await build_check_kb(work_info.id, work_info.owner)
    if work_info.status == 'in_progress':
        remain_time_text = f"Осталось времени: {int(remain_time.total_seconds() // 3600)} ч, {int(remain_time.total_seconds() % 3600 // 60)} мин"
    else:
        remain_time_text = ''

    try:
        await bot.send_message(call.from_user.id,
f'''
Ты выбрал работу {work_info.id}

*{work_info.title}*

{remain_time_text}

_{work_info.description}_
''', parse_mode='Markdown', reply_markup=kb.as_markup())
    except:
        await bot.send_message(call.from_user.id,
f'''
{work_info.title}

{remain_time_text}

Описание:
{work_info.description}
''', reply_markup=kb.as_markup())