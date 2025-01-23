from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from loader import db


async def build_start_kb(first_log_in: bool, role: str | None = None) -> InlineKeyboardBuilder:
    start_kb = InlineKeyboardBuilder()
    if first_log_in:
        start_kb.button(text='Работник', callback_data='im_employeer')
        start_kb.button(text='Работодатель', callback_data='im_worker')
        return start_kb
    
    if role == 'worker':
        start_kb.button(text='Посмотреть доступные объявления', callback_data='check_available_works')
        start_kb.button(text='Перейти в профиль', callback_data='go_profile')
        return start_kb
    
    if role == 'employeer':
        start_kb.button(text='Разместить объявление', callback_data='add_work')
        start_kb.button(text='Перейти в профиль', callback_data='go_profile')
        return start_kb
    

async def build_profile_kb(user_id, role: str) -> InlineKeyboardBuilder:
    profile_kb = InlineKeyboardBuilder()
    
    if role == 'worker':
        profile_kb.button(text='Изменить настройки', callback_data='check_available_works')
        profile_kb.button(text='Вывод средств', callback_data='go_profile')
        return profile_kb
    
    if role == 'employeer':
        jobs = await db.select_employeer_jobs(user_id)
        profile_kb.button(text='Изменить настройки', callback_data='add_work')
        profile_kb.button(text='Пополнить баланс', callback_data='go_profile')
        profile_kb.button(text=f'Мои объявления ({len(jobs)})', callback_data='get_my_jobs_emp')
        return profile_kb
    

async def build_jobs_kb(user_id) -> InlineKeyboardBuilder:
    jobs_kb = InlineKeyboardBuilder()
    jobs = await db.select_employeer_jobs(user_id)
    
    if jobs:
        for job in jobs:
            jobs_kb.button(text=f'{job.title[:6]}... - {job.price}', callback_data=f'jb_{job.id}')

    jobs_kb.row(InlineKeyboardButton(text=f'Назад ◀️', callback_data=f'profile_call'))
    return jobs_kb

    




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


