from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def get_user_menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """
    Возвращает главное меню пользователя с кнопками Профиля, Каталога и Поддержки.
    Если пользователь является администратором, добавляет кнопку 'Админ-панель'.
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем основные кнопки
    builder.button(text="👤 Мой профиль", callback_data="user_profile")
    builder.button(text="📂 Каталог", callback_data="user_catalog")
    builder.button(text="✍️ Написать Нихао-тян (Поддержка)", callback_data="user_support")
    
    # Условная кнопка для администратора
    if is_admin:
        builder.button(text="⚙️ Панель управления", callback_data="admin_panel_entry")
        
    # Размещаем по 1 кнопке в ряд
    builder.adjust(1)
    
    return builder.as_markup()
