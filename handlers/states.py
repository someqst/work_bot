from aiogram.fsm.state import StatesGroup, State


class Employeer(StatesGroup):
    insert_location = State()
    insert_work_time = State()
    insert_price = State()
    insert_title = State()
    insert_description = State()
