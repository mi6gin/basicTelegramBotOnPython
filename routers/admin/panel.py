import os
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from keyboards.inline.admin_panel import get_admin_panel_keyboard
from filters.is_private import IsPrivate
from filters.is_admin import IsAdmin
from aiogram_i18n import I18nContext
from utils.logger import logger, LOG_FILE

router = Router(name="admin_panel")


@router.message(Command("admin"), IsPrivate(), IsAdmin())
async def cmd_admin(message: Message, i18n: I18nContext):
    """
    Обработчик команды /admin.
    Показывает панель администратора с кнопками управления.
    """
    logger.info(f"Admin {message.from_user.id} accessed admin panel via command")
    await message.answer(
        i18n.get("admin-panel-title"),
        reply_markup=get_admin_panel_keyboard(i18n)
    )


@router.callback_query(F.data == "admin_panel_entry", IsPrivate(), IsAdmin())
async def callback_admin(callback: CallbackQuery, i18n: I18nContext):
    """
    Показывает панель администратора по нажатию inline-кнопки.
    """
    await callback.answer()
    await callback.message.edit_text(
        i18n.get("admin-panel-title"),
        reply_markup=get_admin_panel_keyboard(i18n)
    )


@router.callback_query(F.data == "admin_get_logs", IsPrivate(), IsAdmin())
async def get_logs_file(callback: CallbackQuery, i18n: I18nContext):
    """
    Отправляет файл логов администратору в виде документа.
    """
    await callback.answer()
    
    if not os.path.exists(LOG_FILE):
        await callback.message.answer(i18n.get("err-logs-not-found"))
        return
        
    try:
        # Отправляем файл документа
        document = FSInputFile(path=LOG_FILE, filename="bot.log")
        await callback.message.answer_document(
            document=document,
            caption=i18n.get("admin-logs-caption")
        )
    except Exception as e:
        logger.error(f"Error sending log file to admin: {e}", exc_info=True)
        await callback.message.answer(f"❌ Error sending logs: {e}")
