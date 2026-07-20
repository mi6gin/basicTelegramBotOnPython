import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database.repository.user_repo import UserRepository
from keyboards.inline.admin_panel import get_admin_panel_keyboard
from keyboards.reply.cancel import get_cancel_keyboard
from filters.is_private import IsPrivate
from filters.is_admin import IsAdmin
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram_i18n import I18nContext
from utils.logger import logger

router = Router(name="admin_mailing")


class AdminMailingStates(StatesGroup):
    """
    Состояния FSM для проведения массовой рассылки.
    """
    # Ожидание ввода контента для рассылки
    waiting_for_content = State()


@router.callback_query(F.data == "admin_mailing", IsPrivate(), IsAdmin())
async def start_mailing(callback: CallbackQuery, state: FSMContext, i18n: I18nContext):
    """
    Запускает процесс создания рассылки (FSM).
    """
    await callback.answer()
    await callback.message.answer(
        i18n.get("admin-mailing-prompt"),
        reply_markup=get_cancel_keyboard(i18n)
    )
    await state.set_state(AdminMailingStates.waiting_for_content)


@router.message(AdminMailingStates.waiting_for_content, IsPrivate(), IsAdmin())
async def process_mailing_content(
    message: Message, 
    state: FSMContext, 
    session: AsyncSession, 
    bot: Bot,
    i18n: I18nContext
):
    """
    Получает контент рассылки, совершает рассылку по списку пользователей из БД.
    Копирует форматирование и вложения с помощью метода copy_to.
    """
    cancel_text = i18n.get("btn-cancel")
    if message.text == cancel_text or message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            i18n.get("admin-mailing-cancel"),
            reply_markup=get_admin_panel_keyboard(i18n)
        )
        return

    # Загружаем список всех пользователей из базы данных
    users = await UserRepository.get_all(session)
    if not users:
        await message.answer(i18n.get("err-no-users"))
        await state.clear()
        return

    status_msg = await message.answer(i18n.get("admin-mailing-sending"))
    await state.clear()

    success_count = 0
    fail_count = 0

    for user in users:
        # Пропускаем заблокированных в нашей БД
        if user.is_banned:
            continue
            
        try:
            # Метод copy_to идеально дублирует сообщение со всем форматированием
            await message.copy_to(chat_id=user.telegram_id)
            success_count += 1
            # Небольшая задержка, чтобы не превысить лимиты API Telegram (30 сообщений в секунду)
            await asyncio.sleep(0.05)
        except Exception as e:
            # Ошибка возникает, если пользователь заблокировал бота
            logger.debug(f"Failed to send mailing message to {user.telegram_id}: {e}")
            fail_count += 1

    await status_msg.delete()
    
    await message.answer(
        i18n.get(
            "admin-mailing-success",
            success=str(success_count),
            failed=str(fail_count)
        ),
        reply_markup=get_admin_panel_keyboard(i18n)
    )
