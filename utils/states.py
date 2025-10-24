from aiogram.fsm.state import State, StatesGroup

class UserState(StatesGroup):
    choosing_city = State()
    waiting_for_initial_text = State()
    in_chat_with_manager = State()

class ManagerState(StatesGroup):
    in_chat_with_user = State()
    viewing_queue = State()
    manager_active_with = ""