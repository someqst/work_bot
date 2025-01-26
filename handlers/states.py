from aiogram.fsm.state import StatesGroup, State


class Employeer(StatesGroup):
    insert_location = State()
    insert_work_time = State()
    insert_price = State()
    insert_title = State()
    insert_description = State()


class Worker(StatesGroup):
    work_info = State()
    work_done = State()



class EveryOne(StatesGroup):
    change_location = State()
    change_about = State()
    chat_st = State()


class UserCreation(StatesGroup):
    select_role = State()
    enter_location = State()
    enter_about = State()


class Admin(StatesGroup):
    give_emp_balance = State()