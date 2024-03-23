from aiogram.fsm.state import State, StatesGroup

class Elements(StatesGroup):
    add_element_id = State()
    add_element_name = State()
    add_element_desc = State()
    add_element_desc_2 = State()
    remove_element = State()
    add_element_user = State()
    existed_element_id = State()
    remove_element_by_id = State()
