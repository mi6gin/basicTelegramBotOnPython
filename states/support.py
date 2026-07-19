from aiogram.fsm.state import StatesGroup, State


class SupportStates(StatesGroup):
    """
    Состояния FSM для отправки обращения (тикета) в службу поддержки.
    """
    # Ожидание ввода текста обращения от пользователя
    waiting_for_ticket_message = State()
