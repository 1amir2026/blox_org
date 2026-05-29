from aiogram.fsm.state import State, StatesGroup

class ProfileStates(StatesGroup):
    choosing_design = State()
    choosing_light_color = State()
    choosing_bg_color = State()
    waiting_for_skin = State()