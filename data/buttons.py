from loader import db
from database.models import Work
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton




async def build_start_kb(first_log_in: bool, role: str | None = None) -> InlineKeyboardBuilder:
    start_kb = InlineKeyboardBuilder()
    if first_log_in:
        start_kb.button(text='Работник', callback_data='im_worker')
        start_kb.button(text='Работодатель', callback_data='im_employeer')
        return start_kb
    
    if role == 'worker':
        start_kb.button(text='Посмотреть доступные объявления', callback_data='check_available_works')
        start_kb.button(text='Перейти в профиль', callback_data='profile_call')
        return start_kb
    
    if role == 'employeer':
        start_kb.button(text='Разместить объявление', callback_data='add_work')
        start_kb.button(text='Перейти в профиль', callback_data='profile_call')
        return start_kb
    

async def build_profile_kb(user_id, role: str) -> InlineKeyboardBuilder:
    profile_kb = InlineKeyboardBuilder()
    
    if role == 'worker':
        jobs = await db.select_worker_jobs(user_id)
        profile_kb.button(text='Изменить настройки ⚙️', callback_data='edit_user_settings')
        profile_kb.button(text='Вывод средств 💰', callback_data='profile_call')
        profile_kb.button(text=f'Активные работы ({len(jobs)})', callback_data='get_my_jobs_wrk')
        return profile_kb
    
    if role == 'employeer':
        jobs = await db.select_employeer_jobs(user_id)
        profile_kb.button(text='Изменить настройки ⚙️', callback_data='edit_user_settings')
        profile_kb.button(text='Пополнить баланс 💰', callback_data='profile_call')
        profile_kb.button(text=f'Мои объявления ({len(jobs)})', callback_data='get_my_jobs_emp')
        return profile_kb
    

async def build_jobs_kb(user_id, role: str) -> InlineKeyboardBuilder:
    jobs_kb = InlineKeyboardBuilder()

    if role == 'employeer':
        jobs = await db.select_employeer_jobs(user_id)
        role = 'employeer'
    else:
        jobs = await db.select_worker_jobs(user_id)
        role = 'worker'

    if jobs:
        for job in jobs:
            jobs_kb.button(text=f'{job.title[:30]}... - {job.price}', callback_data=f'{role}_select_{job.id}')
    jobs_kb.adjust(1)

    jobs_kb.row(InlineKeyboardButton(text=f'Назад ◀️', callback_data=f'profile_call'))
    return jobs_kb


async def build_works_kb(works: list[Work]) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    for work in works:
        kb.button(text=f'{work.title[:30]}... - {work.price}', callback_data=f'wrk_{work.id}')
    kb.adjust(1)
    return kb


async def build_ok_kb(work_id) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text='Взять на выполнение ✅', callback_data=f'ok_{work_id}')
    return kb


async def build_approve_kb(work_id, worker_id) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text='Принять ✅', callback_data=f'app_{work_id}_{worker_id}')
    return kb


async def build_check_kb(work_id, employeer_id) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text='Уточнить детали ❔', callback_data=f'qst_{work_id}_{employeer_id}')
    kb.button(text='Готово ✅', callback_data=f'done_{work_id}_{employeer_id}')
    kb.adjust(1)
    return kb


async def build_chat_kb(owner_id, worker_id, role) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    # role - это кому
    if role == 'employeer':
        kb.button(text='Войти в чат', callback_data=f'join_emp_{owner_id}_{worker_id}')
    else:
        kb.button(text='Войти в чат', callback_data=f'join_wrk_{owner_id}_{worker_id}')
    return kb


async def build_done_work_kb(work_id) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text='Отлично ✅', callback_data=f'approve_{work_id}')
    kb.button(text='Уточнить детали ❔', callback_data=f'ask_worker_{work_id}')
    kb.button(text='Отменить ❌', callback_data=f'declince_{work_id}')
    kb.adjust(1)
    return kb


async def build_support_kb(work_id) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text='Подтвердить отмену', callback_data=f'des_ok_{work_id}')
    kb.button(text='Отдать деньги исполнителю', callback_data=f'des_no_{work_id}')
    kb.adjust(1)
    return kb


select_role = InlineKeyboardBuilder()
select_role.button(text='Работодатель', callback_data='im_employeer')
select_role.button(text='Работник', callback_data='im_worker')
select_role.adjust(1)


change_job_kb = InlineKeyboardBuilder()
change_job_kb.button(text='Локация', callback_data='change_location_emp')
change_job_kb.button(text='Время работы', callback_data='change_work_time_emp')
change_job_kb.button(text='Цена', callback_data='change_work_price_emp')
change_job_kb.button(text='Заголовок', callback_data='change_work_title_emp')
change_job_kb.button(text='Описание', callback_data='change_work_descriprion_emp')
change_job_kb.button(text='Разместить ✅', callback_data='publish_work_emp')
change_job_kb.adjust(1)


settings_kb = InlineKeyboardBuilder()
settings_kb.button(text='Изменить роль', callback_data='change_role')
settings_kb.button(text='Изменить локацию', callback_data='change_location')
settings_kb.button(text='Изменить описание профиля', callback_data='change_about')
settings_kb.adjust(1)


online_work = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Онлайн')]])
online_work.resize_keyboard = True

remove_reply_kb = ReplyKeyboardRemove()


admin_kb = InlineKeyboardBuilder()
admin_kb.button(text='Выдать баланс employeer', callback_data='give_money_employeer')


