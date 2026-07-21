from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram_i18n import I18nContext

from database.repository.ticket_repo import TicketRepository
from keyboards.inline.admin_panel import get_admin_panel_keyboard
from filters.is_private import IsPrivate
from filters.is_admin import IsAdmin

router = Router(name="admin_tickets")


@router.callback_query(F.data.startswith("admin_tickets_view_"), IsPrivate(), IsAdmin())
async def view_open_tickets(
    callback: CallbackQuery, 
    session: AsyncSession, 
    i18n: I18nContext, 
    state: FSMContext
):
    """
    Позволяет администратору просматривать все открытые обращения по очереди (пагинация).
    """
    await state.clear()
    await callback.answer()
    
    # Парсим текущий индекс из callback_data
    try:
        index = int(callback.data.replace("admin_tickets_view_", ""))
    except ValueError:
        index = 0

    tickets = await TicketRepository.get_all_open(session)
    
    if not tickets:
        builder = InlineKeyboardBuilder()
        builder.button(text=i18n.get("btn-admin-panel"), callback_data="admin_panel_entry")
        await callback.message.edit_text(
            i18n.get("admin-tickets-empty"),
            reply_markup=builder.as_markup()
        )
        return

    # Корректируем индекс
    if index < 0:
        index = 0
    elif index >= len(tickets):
        index = len(tickets) - 1

    ticket = tickets[index]
    
    # Форматируем данные пользователя
    user_name = ticket.user.first_name if ticket.user else i18n.get("profile-username-empty")
    username_str = ticket.user.username if (ticket.user and ticket.user.username) else i18n.get("profile-username-empty")
    date_str = ticket.created_at.strftime("%d.%m.%Y в %H:%M")

    text = i18n.get(
        "admin-tickets-title",
        id=str(ticket.id),
        status=ticket.status,
        name=user_name,
        user_id=str(ticket.user_id),
        username=username_str,
        date=date_str,
        message=ticket.message
    )

    # Строим клавиатуру пагинации и управления
    builder = InlineKeyboardBuilder()
    
    # 1. Кнопка закрытия текущего тикета
    builder.button(text=i18n.get("btn-ticket-close"), callback_data=f"admin_ticket_close_{ticket.id}_{index}")
    
    # 2. Кнопки пагинации
    row_count = 0
    if index > 0:
        builder.button(text=i18n.get("btn-ticket-prev"), callback_data=f"admin_tickets_view_{index-1}")
        row_count += 1
        
    builder.button(text=f"{index+1}/{len(tickets)}", callback_data="noop")
    row_count += 1
    
    if index < len(tickets) - 1:
        builder.button(text=i18n.get("btn-ticket-next"), callback_data=f"admin_tickets_view_{index+1}")
        row_count += 1

    # 3. Кнопка возврата в админку
    builder.button(text=i18n.get("btn-admin-panel"), callback_data="admin_panel_entry")
    
    builder.adjust(1, row_count, 1)
    
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.startswith("admin_ticket_close_"), IsPrivate(), IsAdmin())
async def close_ticket_callback(
    callback: CallbackQuery, 
    session: AsyncSession, 
    i18n: I18nContext,
    state: FSMContext
):
    """
    Закрывает тикет поддержки и обновляет просмотр.
    """
    # callback_data: admin_ticket_close_{ticket_id}_{current_index}
    parts = callback.data.split("_")
    ticket_id = int(parts[3])
    index = int(parts[4])
    
    # Закрываем тикет в БД
    success = await TicketRepository.close(session, ticket_id)
    if success:
        await callback.answer(i18n.get("support-cancel"), show_alert=True)
    else:
        await callback.answer("Ошибка при закрытии", show_alert=True)

    # Загружаем оставшиеся открытые тикеты
    tickets = await TicketRepository.get_all_open(session)
    
    if not tickets:
        builder = InlineKeyboardBuilder()
        builder.button(text=i18n.get("btn-admin-panel"), callback_data="admin_panel_entry")
        await callback.message.edit_text(
            i18n.get("admin-tickets-empty"),
            reply_markup=builder.as_markup()
        )
        return

    # Корректируем индекс для следующего просмотра
    if index >= len(tickets):
        index = len(tickets) - 1
        
    # Перенаправляем на просмотр оставшихся
    builder = InlineKeyboardBuilder()
    builder.button(text="⏳ Обновление...", callback_data="noop")
    await callback.message.edit_text("⏳ Обновление списка...", reply_markup=builder.as_markup())
    
    # Запускаем просмотр заново
    callback.data = f"admin_tickets_view_{index}"
    await view_open_tickets(callback, session, i18n, state)
