from datetime import datetime, timedelta
from pytz import timezone
from dateutil.relativedelta import relativedelta
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from loader import bot, db
from aiogram.fsm.context import FSMContext
from handlers.states import Employeer, EveryOne
from data.buttons import change_job_kb, online_work, remove_reply_kb, build_check_kb, build_jobs_kb


router = Router()


# ------------ Создание работы ------------
@router.callback_query(F.data == 'add_work')
async def add_work(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await bot.send_message(call.from_user.id, 'Введите локацию', reply_markup=online_work)
    await state.set_state(Employeer.insert_location)


@router.message(Employeer.insert_location, F.text)
async def enter_location(message: Message, state: FSMContext):
    await state.update_data(location = (message.text).lower())

    if await is_changeble(state, message.from_user.id):
        return

    await message.answer('Если вы ввели что-то неверно, в конце заполнения можно будет изменить\n\nВведите время выполнения в часах', reply_markup=remove_reply_kb)
    await state.set_state(Employeer.insert_work_time)


@router.message(Employeer.insert_work_time, F.text)
async def enter_work_time(message: Message, state: FSMContext):
    await state.update_data(work_time = message.text)

    if await is_changeble(state, message.from_user.id):
        return

    await message.answer('Введите цену, которую будете готовы заплатить')
    await state.set_state(Employeer.insert_price)


@router.message(Employeer.insert_price, F.text)
async def enter_price(message: Message, state: FSMContext):
    if not (message.text).isdigit():
        return await message.answer('Введите число')
    
    user = await db.get_user(message.from_user.id)
    
    if int(message.text) > user.balance_deposit:
        return await message.answer('Сначала пополните баланс на нужную сумму.')
    
    await state.update_data(price = message.text)

    if await is_changeble(state, message.from_user.id):
        return

    await message.answer('Введите заголовок, который увидит работник. *Не более 150 символов*', parse_mode='Markdown')
    await state.set_state(Employeer.insert_title)


@router.message(Employeer.insert_title, F.text)
async def enter_title(message: Message, state: FSMContext):
    if len(message.text) > 150:
        return await message.answer('Заголовок должен быть не более 150 символов')
    
    await state.update_data(title = message.text)

    if await is_changeble(state, message.from_user.id):
        return

    await message.answer('Введите полное описание, *не более 3500 символов*', parse_mode='Markdown')
    await state.set_state(Employeer.insert_description)


@router.message(Employeer.insert_description, F.text)
async def enter_description(message: Message, state: FSMContext):
    if len(message.text) > 3500:
        return await message.answer('Описание должно быть не более 3500 символов')
    await state.update_data(description = message.text)

    await message.answer('Хотите ли вы что-нибудь поменять?', reply_markup=change_job_kb.as_markup())


@router.callback_query(F.data == 'publish_work_emp')
async def publish_work_emp(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    data = await state.get_data()
    
    location = data.get('location')
    work_time = int(data.get('work_time'))
    price = int(data.get('price'))
    title = data.get('title')
    description = data.get('description')

    await db.create_work(call.from_user.id, location, work_time, price, title, description)
    await db.get_employeer_deposit(call.from_user.id, price)
    await state.clear()
    return await bot.send_message(call.from_user.id, 'Работа успешно размещена. Посмотреть можно в /profile (перед этим будет оплата, но пока MVP)')


@router.callback_query(F.data.in_({'change_location_emp', 'change_work_time_emp', 'change_work_price_emp',
                                   'change_work_title_emp', 'change_work_descriprion_emp'}))
async def change_work_preferences(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    match call.data:
        case 'change_location_emp':
            await bot.send_message(call.from_user.id, 'Введите локацию')
            await state.set_state(Employeer.insert_location)
        case 'change_work_time_emp':
            await bot.send_message(call.from_user.id, 'Введите время выполнения в часах')
            await state.set_state(Employeer.insert_work_time)
        case 'change_work_price_emp':
            await bot.send_message(call.from_user.id, 'Введите цену, которую будете готовы заплатить')
            await state.set_state(Employeer.insert_price)
        case 'change_work_title_emp':
            await bot.send_message(call.from_user.id, 'Введите заголовок, который увидит работник')
            await state.set_state(Employeer.insert_title)
        case 'change_work_descriprion_emp':
            await bot.send_message(call.from_user.id, 'Введите полное описание, не более 4096 символов')
            await state.set_state(Employeer.insert_description)
        

async def is_changeble(state: FSMContext, user_id):
    if (await state.get_data()).get('description'):
        await bot.send_message(user_id, 'Хотите ли вы что-нибудь поменять?', reply_markup=change_job_kb.as_markup())
        return True
    return False



#------------ Апрув воркера на работу ---------------


@router.callback_query(F.data.startswith('app_'))
async def get_work_for_done(call: CallbackQuery):
    await call.answer()

    work_id = (call.data).split('_')[1]
    worker_id = (call.data).split('_')[2]
    
    work = await db.get_work_by_id(work_id)

    await bot.send_message(worker_id,
f'''Вас приняли на выполнение работы

*{work.title}*

Цена: {work.price}

❗️Если вы не выполните работу за *{work.work_time} ч.*, то она будет отменена автоматически❗️
''', parse_mode='Markdown', reply_markup=(await build_check_kb(work.id, call.from_user.id)).as_markup())
    end_time = (datetime.now(timezone('Europe/Moscow')) + relativedelta(hours=work.work_time)).replace(tzinfo=None)

    await db.set_work_status(work_id, 'in_progress')
    await db.create_work_process(work_id, work.title, end_time, work.price, int(worker_id), call.from_user.id)



# -------- Вход в чат с работником -----------
@router.callback_query(F.data.startswith('join_emp_'))
async def join_chat_emp(call: CallbackQuery, state: FSMContext):
    await call.answer()
    worker = int((call.data).split('_')[3])
    await bot.send_message(call.from_user.id, 'Если заходите выйти из чата, напишите /exit')
    await db.create_chat(call.from_user.id, worker)
    
    try:
        await bot.send_message(worker, 'Работодатель вошел в диалог. Если захотите выйти из чата, пишите /exit')
        await state.set_state(EveryOne.chat_st)
    except:
        await bot.send_message(call.from_user.id, 'Сообщение не отправилось работнику. Он не зайдет.')



# ----- Работодатель смотрит свои работы -------
@router.callback_query(F.data == 'get_my_jobs_emp')
async def get_my_jobs_emp(call: CallbackQuery):
    await call.answer()
    kb = await build_jobs_kb(call.from_user.id, 'employeer')
    await call.message.edit_text('Выберите работу', reply_markup=kb.as_markup())



@router.callback_query(F.data.startswith('employeer_select_'))
async def select_job(call: CallbackQuery):
    await call.answer()
    work_info = await db.get_work_by_id((call.data).split("_")[2])
    work_process_info = await db.get_work_process_by_id((call.data).split("_")[2])
    
    if work_process_info:
        worker = await db.get_user(work_process_info.worker)
        remain_time: timedelta = (work_process_info.end_time - datetime.now(timezone('Europe/Moscow')).replace(tzinfo=None))
    
    await bot.send_message(call.from_user.id,
f'''
*{work_info.title}*

Статус: {"открыта" if work_info.status == 'opened' else "в процессе... ⏱️"}

{"Выполняет @" + worker.username if work_process_info else ''}

{"Осталось времени: " + f"{int(remain_time.total_seconds() // 3600)} ч. " + f"{int(remain_time.total_seconds() % 3600 // 60)} мин" if work_process_info else ''}

''', parse_mode='Markdown')
