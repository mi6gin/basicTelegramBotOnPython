from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Возвращает Reply-клавиатуру с одной кнопкой 'Отмена' для выхода из FSM-состояний.
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отмена")
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
