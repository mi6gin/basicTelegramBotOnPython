from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from keyboards.inline.admin_panel import get_admin_panel_keyboard
from filters.is_private import IsPrivate
from filters.is_admin import IsAdmin
from utils.logger import logger

router = Router(name="admin_panel")


@router.message(Command("admin"), IsPrivate(), IsAdmin())
async def cmd_admin(message: Message):
    """
    Обработчик команды /admin.
    Показывает панель администратора с кнопками управления.
    """
    logger.info(f"Admin {message.from_user.id} accessed admin panel via command")
    await message.answer(
        "⚙️ **Панель управления Нихао-тян**\n\n"
        "Вы вошли с правами администратора. Выберите действие:",
        reply_markup=get_admin_panel_keyboard()
    )


@router.callback_query(F.data == "admin_panel_entry", IsPrivate(), IsAdmin())
async def callback_admin(callback: CallbackQuery):
    """
    Показывает панель администратора по нажатию inline-кнопки.
    """
    await callback.answer()
    await callback.message.edit_text(
        "⚙️ **Панель управления Нихао-тян**\n\n"
        "Вы вошли с правами администратора. Выберите действие:",
        reply_markup=get_admin_panel_keyboard()
    )
