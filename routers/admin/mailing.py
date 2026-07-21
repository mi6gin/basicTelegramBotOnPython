import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database.repository.user_repo import UserRepository
from keyboards.inline.admin_panel import get_admin_panel_keyboard
from keyboards.inline.cancel import get_cancel_inline_keyboard
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
    
    prompt_msg = await callback.message.edit_text(
        i18n.get("admin-mailing-prompt"),
        reply_markup=get_cancel_inline_keyboard(i18n, callback_data="cancel_admin_mailing")
    )
    
    await state.set_state(AdminMailingStates.waiting_for_content)
    await state.update_data(prompt_msg_id=prompt_msg.message_id)


@router.callback_query(F.data == "cancel_admin_mailing", IsPrivate(), IsAdmin())
async def process_cancel_mailing(callback: CallbackQuery, state: FSMContext, i18n: I18nContext):
    """
    Отмена рассылки при клике на инлайн-кнопку. Возвращает в админку.
    """
    await callback.answer()
    await state.clear()
    
    await callback.message.edit_text(
        i18n.get("admin-panel-title"),
        reply_markup=get_admin_panel_keyboard(i18n)
    )


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
    """
    # Удаляем сообщение-подсказку с инлайн-кнопкой отмены
    data = await state.get_data()
    prompt_msg_id = data.get("prompt_msg_id")
    if prompt_msg_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_msg_id)
        except Exception:
            pass

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
        if user.is_banned:
            continue
            
        try:
            await message.copy_to(chat_id=user.telegram_id)
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
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
