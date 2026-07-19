from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру для страницы профиля с возможностью редактирования БИО и возврата в меню.
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📝 Изменить БИО", callback_data="edit_profile_bio")
    builder.button(text="🔙 Главное меню", callback_data="back_to_menu")
    
    builder.adjust(1)
    
    return builder.as_markup()
