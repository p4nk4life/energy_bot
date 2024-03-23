from aiogram.fsm.state import State, StatesGroup

class Dialog_admin(StatesGroup):
    usr_to_adm = State()
    adm_to_usr = State()