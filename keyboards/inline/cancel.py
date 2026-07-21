from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram_i18n import I18nContext


def get_cancel_inline_keyboard(i18n: I18nContext, callback_data: str = "cancel_state") -> InlineKeyboardMarkup:
    """
    Возвращает inline-клавиатуру с одной кнопкой "Отмена" для выхода из FSM-состояний.
    Идеально заменяет громоздкие reply-кнопки на красивые интерактивные кнопки под сообщением.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.get("btn-cancel"), callback_data=callback_data)
    return builder.as_markup()
