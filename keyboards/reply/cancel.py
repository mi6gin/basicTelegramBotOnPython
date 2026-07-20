from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup
from aiogram_i18n import I18nContext


def get_cancel_keyboard(i18n: I18nContext) -> ReplyKeyboardMarkup:
    """
    Возвращает Reply-клавиатуру с одной кнопкой 'Отмена' для выхода из FSM-состояний.
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text=i18n.get("btn-cancel"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
