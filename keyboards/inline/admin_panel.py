from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру панели администратора.
    Включает разделы статистики, рассылки, управления пользователями и возврата в меню.
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📊 Статистика", callback_data="admin_stats")
    builder.button(text="📣 Создать рассылку", callback_data="admin_mailing")
    builder.button(text="👥 Управление", callback_data="admin_users_manage")
    builder.button(text="🔙 Главное меню", callback_data="back_to_menu")
    
    # 2 кнопки в первом ряду, затем по 1 кнопке
    builder.adjust(2, 1, 1)
    
    return builder.as_markup()
