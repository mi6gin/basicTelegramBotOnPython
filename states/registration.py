from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    """
    Состояния FSM для процесса регистрации/знакомства с Нихао-тян.
    """
    # Ожидание ввода имени пользователя
    waiting_for_name = State()
    
    # Ожидание ввода биографии/описания
    waiting_for_bio = State()
