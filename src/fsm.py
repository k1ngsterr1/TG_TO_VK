from aiogram.fsm.state import State, StatesGroup


class FSM(StatesGroup):
    wait_tg_channels = State()
    wait_vk_token = State()
    wait_vk_groups = State()
    wait_post_choice = State()
    
