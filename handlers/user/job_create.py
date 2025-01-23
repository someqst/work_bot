from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from loader import bot, db
from aiogram.fsm.context import FSMContext
from handlers.states import Employeer
from data.buttons import change_job_kb


router = Router()


@router.callback_query(F.data == 'add_work')
async def add_work(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await bot.send_message(call.from_user.id, 'Введите локацию')
    await state.set_state(Employeer.insert_location)


@router.message(Employeer.insert_location, F.text)
async def enter_location(message: Message, state: FSMContext):
    await state.update_data(location = message.text)

    if await is_changeble(state, message.from_user.id):
        return

    await message.answer('Если вы ввели что-то неверно, в конце заполнения можно будет изменить\n\nВведите время выполнения в часах')
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
    await state.update_data(price = message.text)

    if await is_changeble(state, message.from_user.id):
        return

    await message.answer('Введите заголовок, который увидит работник')
    await state.set_state(Employeer.insert_title)


@router.message(Employeer.insert_title, F.text)
async def enter_title(message: Message, state: FSMContext):
    await state.update_data(title = message.text)

    if await is_changeble(state, message.from_user.id):
        return

    await message.answer('Введите полное описание, не более 4096 символов')
    await state.set_state(Employeer.insert_description)


@router.message(Employeer.insert_description, F.text)
async def enter_description(message: Message, state: FSMContext):
    await state.update_data(description = message.text)

    await message.answer('Хотите ли вы что-нибудь поменять?', reply_markup=change_job_kb.as_markup())


@router.callback_query(F.data == 'publish_work_emp')
async def publish_work_emp(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    
    location = data.get('location')
    work_time = int(data.get('work_time'))
    price = int(data.get('price'))
    title = data.get('title')
    description = data.get('description')

    await db.create_work(call.from_user.id, location, work_time, price, title, description)
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

# def is_changeble(func):
#     async def wrapper(*args, **kwargs):
#         state: FSMContext = kwargs.get('state')
#         if (await state.get_data()).get('description'):
#             await func(*args, **kwargs)
#     return wrapper

