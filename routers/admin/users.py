from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database.repository.user_repo import UserRepository
from keyboards.inline.admin_panel import get_admin_panel_keyboard
from keyboards.reply.cancel import get_cancel_keyboard
from filters.is_private import IsPrivate
from filters.is_admin import IsAdmin
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger

router = Router(name="admin_users")


class AdminUserManageStates(StatesGroup):
    """
    Состояния FSM для управления пользователями администратором.
    """
    # Ожидание ввода Telegram ID целевого пользователя
    waiting_for_target_id = State()


@router.callback_query(F.data == "admin_users_manage", IsPrivate(), IsAdmin())
async def start_manage_users(callback: CallbackQuery, state: FSMContext):
    """
    Запускает FSM для смены статуса бана пользователя.
    """
    await callback.answer()
    await callback.message.answer(
        "👥 **Управление доступом пользователей**\n\n"
        "Отправьте Telegram ID пользователя, которого вы хотите заблокировать или разблокировать:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminUserManageStates.waiting_for_target_id)


@router.message(AdminUserManageStates.waiting_for_target_id, IsPrivate(), IsAdmin())
async def process_ban_unban(message: Message, state: FSMContext, session: AsyncSession):
    """
    Принимает ID пользователя, находит его в БД и инвертирует его флаг бана (is_banned).
    """
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Действие отменено.",
            reply_markup=get_admin_panel_keyboard()
        )
        return

    input_text = message.text.strip()
    
    # Валидируем ввод Telegram ID (должно быть числом)
    if not input_text.isdigit():
        await message.answer("Ошибка! Telegram ID должен состоять только из цифр. Попробуйте еще раз:")
        return
        
    target_id = int(input_text)
    
    # Предотвращаем самоблокировку
    if target_id == message.from_user.id:
        await message.answer("Вы не можете заблокировать самого себя!")
        await state.clear()
        await message.answer("Панель администратора:", reply_markup=get_admin_panel_keyboard())
        return

    # Получаем пользователя из БД
    target_user = await UserRepository.get_by_id(session, target_id)
    
    if not target_user:
        await message.answer(f"Пользователь с ID `{target_id}` не найден в базе данных бота.")
        await state.clear()
        await message.answer("Панель администратора:", reply_markup=get_admin_panel_keyboard())
        return

    # Предотвращаем бан других админов
    if target_user.role == "admin":
        await message.answer("Вы не можете заблокировать другого администратора!")
        await state.clear()
        await message.answer("Панель администратора:", reply_markup=get_admin_panel_keyboard())
        return

    # Переключаем статус бана
    new_ban_status = not target_user.is_banned
    await UserRepository.set_ban_status(session, target_id, new_ban_status)
    
    status_text = "заблокирован ❌" if new_ban_status else "разблокирован  активен"
    logger.warning(f"Admin {message.from_user.id} changed ban status of user {target_id} to {new_ban_status}")
    
    await state.clear()
    await message.answer(
        f"Пользователь {target_user.first_name} (`{target_id}`) теперь **{status_text}**.",
        reply_markup=get_admin_panel_keyboard()
    )
