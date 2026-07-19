from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.repository.user_repo import UserRepository
from database.repository.ticket_repo import TicketRepository
from filters.is_private import IsPrivate
from filters.is_admin import IsAdmin
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name="admin_stats")


@router.callback_query(F.data == "admin_stats", IsPrivate(), IsAdmin())
async def show_stats(callback: CallbackQuery, session: AsyncSession):
    """
    Отображает административную статистику по базе данных бота.
    """
    await callback.answer()
    
    # Считаем количество записей в таблицах
    total_users = await UserRepository.get_total_count(session)
    banned_users = await UserRepository.get_banned_count(session)
    open_tickets = await TicketRepository.get_open_count(session)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Панель управления", callback_data="admin_panel_entry")
    
    await callback.message.edit_text(
        f"📊 **Статистика бота Нихао-тян**\n\n"
        f"┣ Всего пользователей в БД: `{total_users}`\n"
        f"┣ Заблокированных пользователей: `{banned_users}`\n"
        f"┗ Открытых тикетов в техподдержку: `{open_tickets}`",
        reply_markup=builder.as_markup()
    )
