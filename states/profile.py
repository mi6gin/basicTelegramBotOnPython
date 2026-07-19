from aiogram.fsm.state import StatesGroup, State


class ProfileStates(StatesGroup):
    """
    Состояния FSM для редактирования профиля пользователя.
    """
    # Ожидание ввода новой биографии (описания)
    waiting_for_new_bio = State()
