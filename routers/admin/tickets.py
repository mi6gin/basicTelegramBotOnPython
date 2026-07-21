from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram_i18n import I18nContext

from database.repository.ticket_repo import TicketRepository
from keyboards.inline.admin_panel import get_admin_panel_keyboard
from keyboards.inline.cancel import get_cancel_inline_keyboard
from filters.is_private import IsPrivate
from filters.is_admin import IsAdmin
from states.admin_tickets import AdminTicketStates
from utils.logger import logger

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

    # Строим клавиатуру управления
    builder = InlineKeyboardBuilder()
    
    # 1. Кнопки управления текущим тикетом
    builder.button(text=i18n.get("btn-ticket-reply"), callback_data=f"admin_ticket_reply_{ticket.id}_{index}")
    builder.button(text=i18n.get("btn-ticket-close-no-reply"), callback_data=f"admin_ticket_close_no_reply_{ticket.id}_{index}")
    
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
    
    # Разметка рядов: Ответить (1), Закрыть без ответа (1), Пагинация (row_count), Назад (1)
    builder.adjust(1, 1, row_count, 1)
    
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.startswith("admin_ticket_close_no_reply_"), IsPrivate(), IsAdmin())
async def close_ticket_no_reply(
    callback: CallbackQuery, 
    session: AsyncSession, 
    bot: Bot,
    i18n: I18nContext,
    state: FSMContext
):
    """
    Закрывает тикет без отправки текстового ответа.
    Пользователь получает простое сервисное уведомление о закрытии.
    """
    # callback_data: admin_ticket_close_no_reply_{ticket_id}_{current_index}
    parts = callback.data.split("_")
    ticket_id = int(parts[5])
    index = int(parts[6])
    
    # Загружаем тикет для отправки уведомления
    ticket = await TicketRepository.get_by_id(session, ticket_id)
    if not ticket:
        await callback.answer(i18n.get("err-item-not-found"), show_alert=True)
        return
        
    # Закрываем тикет в БД
    await TicketRepository.close(session, ticket_id)
    await callback.answer(i18n.get("support-cancel"), show_alert=True)

    # Уведомляем пользователя на его языке
    locale = ticket.user.language if (ticket.user and ticket.user.language) else "ru"
    try:
        msg_text = i18n.get("user-ticket-closed-simple", locale=locale, id=str(ticket_id))
        await bot.send_message(chat_id=ticket.user_id, text=msg_text)
    except Exception as e:
        logger.warning(f"Failed to notify user {ticket.user_id} about ticket #{ticket_id} closure: {e}")

    # Перенаправляем на просмотр оставшихся
    tickets = await TicketRepository.get_all_open(session)
    if not tickets:
        builder = InlineKeyboardBuilder()
        builder.button(text=i18n.get("btn-admin-panel"), callback_data="admin_panel_entry")
        await callback.message.edit_text(
            i18n.get("admin-tickets-empty"),
            reply_markup=builder.as_markup()
        )
        return

    if index >= len(tickets):
        index = len(tickets) - 1
        
    callback.data = f"admin_tickets_view_{index}"
    await view_open_tickets(callback, session, i18n, state)


@router.callback_query(F.data.startswith("admin_ticket_reply_"), IsPrivate(), IsAdmin())
async def start_ticket_reply(
    callback: CallbackQuery, 
    i18n: I18nContext,
    state: FSMContext
):
    """
    Инициирует процесс отправки ответа пользователю (FSM).
    """
    await callback.answer()
    
    # callback_data: admin_ticket_reply_{ticket_id}_{current_index}
    parts = callback.data.split("_")
    ticket_id = int(parts[3])
    index = int(parts[4])
    
    prompt_msg = await callback.message.edit_text(
        i18n.get("admin-ticket-reply-prompt", id=str(ticket_id)),
        reply_markup=get_cancel_inline_keyboard(i18n, callback_data=f"cancel_ticket_reply_{index}")
    )
    
    await state.set_state(AdminTicketStates.waiting_for_reply)
    await state.update_data(
        ticket_id=ticket_id,
        index=index,
        prompt_msg_id=prompt_msg.message_id
    )


@router.callback_query(F.data.startswith("cancel_ticket_reply_"), IsPrivate(), IsAdmin())
async def cancel_ticket_reply(
    callback: CallbackQuery, 
    session: AsyncSession, 
    i18n: I18nContext,
    state: FSMContext
):
    """
    Отмена ввода ответа. Возвращает к просмотру этого же тикета.
    """
    await state.clear()
    await callback.answer(i18n.get("admin-ticket-reply-cancel"))
    
    index = int(callback.data.replace("cancel_ticket_reply_", ""))
    
    callback.data = f"admin_tickets_view_{index}"
    await view_open_tickets(callback, session, i18n, state)


@router.message(AdminTicketStates.waiting_for_reply, IsPrivate(), IsAdmin())
async def process_ticket_reply(
    message: Message, 
    session: AsyncSession, 
    bot: Bot, 
    state: FSMContext, 
    i18n: I18nContext
):
    """
    Получает ответ администратора, отправляет его пользователю и закрывает обращение.
    """
    data = await state.get_data()
    ticket_id = data.get("ticket_id")
    index = data.get("index")
    prompt_msg_id = data.get("prompt_msg_id")
    
    await state.clear()
    
    # Удаляем сообщение-подсказку с кнопкой отмены
    if prompt_msg_id:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=prompt_msg_id)
        except Exception:
            pass

    ticket = await TicketRepository.get_by_id(session, ticket_id)
    if not ticket:
        await message.answer(i18n.get("err-item-not-found"))
        return

    # Закрываем тикет в БД
    await TicketRepository.close(session, ticket_id)
    await message.answer(i18n.get("support-cancel"))

    # Отправляем ответ пользователю на его языке
    locale = ticket.user.language if (ticket.user and ticket.user.language) else "ru"
    try:
        msg_text = i18n.get("user-ticket-closed-with-reply", locale=locale, id=str(ticket_id), reply=message.text)
        await bot.send_message(chat_id=ticket.user_id, text=msg_text)
    except Exception as e:
        logger.warning(f"Failed to send reply to user {ticket.user_id} for ticket #{ticket_id}: {e}")

    # Возвращаемся к оставшимся тикетам
    tickets = await TicketRepository.get_all_open(session)
    
    if not tickets:
        builder = InlineKeyboardBuilder()
        builder.button(text=i18n.get("btn-admin-panel"), callback_data="admin_panel_entry")
        await message.answer(
            i18n.get("admin-tickets-empty"),
            reply_markup=builder.as_markup()
        )
        return

    if index >= len(tickets):
        index = len(tickets) - 1

    # Создаем фиктивный CallbackQuery, чтобы переиспользовать функцию просмотра
    dummy_callback = CallbackQuery(
        id="0",
        from_user=message.from_user,
        chat_instance="0",
        message=message,  # Новое сообщение админа станет местом вывода
        data=f"admin_tickets_view_{index}"
    )
    
    # Подменяем метод edit_text на answer, чтобы dummy_callback отработал отправкой нового сообщения
    async def mock_edit_text(text, reply_markup=None):
        return await message.answer(text, reply_markup=reply_markup)
        
    dummy_callback.message.edit_text = mock_edit_text
    await view_open_tickets(dummy_callback, session, i18n, state)
