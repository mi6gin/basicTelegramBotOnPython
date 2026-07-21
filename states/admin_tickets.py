from aiogram.fsm.state import StatesGroup, State


class AdminTicketStates(StatesGroup):
    """
    Состояния FSM для ответов администратора на тикеты пользователей.
    """
    # Ожидание ввода текста ответа пользователю
    waiting_for_reply = State()
