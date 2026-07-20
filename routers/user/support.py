from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext

from database.models.user import User
from database.repository.ticket_repo import TicketRepository
from keyboards.reply.cancel import get_cancel_keyboard
from keyboards.inline.user_menu import get_user_menu_keyboard
from states.support import SupportStates
from filters.is_private import IsPrivate
from filters.is_admin import IsAdmin
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger

router = Router(name="user_support")


@router.callback_query(F.data == "user_support", IsPrivate())
async def start_support_ticket(callback: CallbackQuery, state: FSMContext, i18n: I18nContext):
    """
    Запускает процесс создания тикета поддержки (FSM).
    """
    await callback.answer()
    await callback.message.answer(
        i18n.get("support-prompt"),
        reply_markup=get_cancel_keyboard(i18n)
    )
    await state.set_state(SupportStates.waiting_for_ticket_message)


@router.message(SupportStates.waiting_for_ticket_message, IsPrivate())
async def process_ticket_message(
    message: Message, 
    state: FSMContext, 
    session: AsyncSession, 
    db_user: User,
    i18n: I18nContext
):
    """
    Обрабатывает ввод сообщения для поддержки. Создает тикет в БД.
    """
    cancel_text = i18n.get("btn-cancel")
    if message.text == cancel_text or message.text == "❌ Отмена":
        await state.clear()
        is_admin_user = await IsAdmin()(message, db_user)
        await message.answer(
            i18n.get("support-cancel"),
            reply_markup=get_user_menu_keyboard(i18n, is_admin=is_admin_user)
        )
        return

    ticket_text = message.text.strip()
    if len(ticket_text) < 10 or len(ticket_text) > 1000:
        await message.answer(i18n.get("err-ticket-length"))
        return

    # Создаем тикет в БД
    ticket = await TicketRepository.create(session, db_user.telegram_id, ticket_text)
    
    await state.clear()
    logger.info(f"User {db_user.telegram_id} created support ticket #{ticket.id}")
    
    is_admin_user = await IsAdmin()(message, db_user)
    await message.answer(
        i18n.get("support-success", id=str(ticket.id)),
        reply_markup=get_user_menu_keyboard(i18n, is_admin=is_admin_user)
    )
