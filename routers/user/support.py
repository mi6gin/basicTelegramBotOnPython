from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
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
async def start_support_ticket(callback: CallbackQuery, state: FSMContext):
    """
    Запускает процесс создания тикета поддержки (FSM).
    """
    await callback.answer()
    await callback.message.answer(
        "✍️ **Обращение к Нихао-тян**\n\n"
        "Опишите вашу проблему или задайте вопрос одним сообщением.\n"
        "Мы постараемся ответить как можно быстрее!",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(SupportStates.waiting_for_ticket_message)


@router.message(SupportStates.waiting_for_ticket_message, IsPrivate())
async def process_ticket_message(
    message: Message, 
    state: FSMContext, 
    session: AsyncSession, 
    db_user: User
):
    """
    Обрабатывает ввод сообщения для поддержки. Создает тикет в БД.
    """
    if message.text == "❌ Отмена":
        await state.clear()
        is_admin_user = await IsAdmin()(message, db_user)
        await message.answer(
            "Отправка тикета отменена.",
            reply_markup=get_user_menu_keyboard(is_admin=is_admin_user)
        )
        return

    ticket_text = message.text.strip()
    if len(ticket_text) < 10 or len(ticket_text) > 1000:
        await message.answer(
            "Описание тикета должно быть от 10 до 1000 символов.\n"
            "Пожалуйста, сформулируйте вопрос корректно."
        )
        return

    # Создаем тикет в БД
    ticket = await TicketRepository.create(session, db_user.telegram_id, ticket_text)
    
    await state.clear()
    logger.info(f"User {db_user.telegram_id} created support ticket #{ticket.id}")
    
    is_admin_user = await IsAdmin()(message, db_user)
    await message.answer(
        f"✅ **Тикет #{ticket.id} успешно отправлен!**\n\n"
        f"Нихао-тян получила твое сообщение. Скоро мы свяжемся с тобой!",
        reply_markup=get_user_menu_keyboard(is_admin=is_admin_user)
    )
