from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.models.user import User
from database.repository.user_repo import UserRepository
from keyboards.inline.profile import get_profile_keyboard
from keyboards.reply.cancel import get_cancel_keyboard
from states.profile import ProfileStates
from filters.is_private import IsPrivate
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger

router = Router(name="user_profile")


def format_profile_text(user: User) -> str:
    """
    Форматирует текст профиля для отправки пользователю.
    """
    username_str = f"@{user.username}" if user.username else "не установлен"
    reg_date = user.registered_at.strftime("%d.%m.%Y в %H:%M")
    bio_str = user.bio if user.bio else "Не указано ℹ️"
    
    return (
        f"👤 **Ваш профиль Нихао-тян**\n\n"
        f"┣ **Имя:** {user.first_name}\n"
        f"┣ **Юзернейм:** {username_str}\n"
        f"┣ **Telegram ID:** `{user.telegram_id}`\n"
        f"┣ **Роль:** `{user.role}`\n"
        f"┣ **Дата регистрации:** {reg_date}\n\n"
        f"📝 **БИО:** {bio_str}"
    )


@router.callback_query(F.data == "user_profile", IsPrivate())
async def show_profile(callback: CallbackQuery, db_user: User):
    """
    Показывает карточку профиля пользователя.
    """
    await callback.answer()
    await callback.message.edit_text(
        text=format_profile_text(db_user),
        reply_markup=get_profile_keyboard()
    )


@router.callback_query(F.data == "edit_profile_bio", IsPrivate())
async def start_edit_bio(callback: CallbackQuery, state: FSMContext):
    """
    Запускает процесс редактирования БИО пользователя с использованием FSM.
    """
    await callback.answer()
    await callback.message.answer(
        "Напишите ваше новое БИО (описание профиля, до 150 символов):",
        reply_markup=get_cancel_keyboard()
    )
    # Сохраняем ID сообщения профиля, чтобы потом отредактировать его или удалить
    await state.update_data(profile_msg_id=callback.message.message_id)
    await state.set_state(ProfileStates.waiting_for_new_bio)


@router.message(ProfileStates.waiting_for_new_bio, IsPrivate())
async def process_new_bio(message: Message, state: FSMContext, session: AsyncSession, db_user: User):
    """
    Обрабатывает ввод нового БИО. Валидирует длину и сохраняет в БД.
    """
    if message.text == "❌ Отмена":
        await state.clear()
        # Повторно показываем профиль
        await message.answer(
            text="Изменение отменено.\n\n" + format_profile_text(db_user),
            reply_markup=get_profile_keyboard()
        )
        return

    new_bio = message.text.strip()
    if len(new_bio) > 150:
        await message.answer(
            f"Описание слишком длинное! Уложитесь в 150 символов (сейчас: {len(new_bio)})."
        )
        return

    # Обновляем био в базе данных
    await UserRepository.update_bio(session, db_user.telegram_id, new_bio)
    
    await state.clear()
    
    # Отправляем сообщение об успехе и актуальный профиль
    await message.answer(
        "✨ Ваше БИО успешно обновлено! ✨\n\n" + format_profile_text(db_user),
        reply_markup=get_profile_keyboard()
    )
