from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.models.user import User
from database.repository.user_repo import UserRepository
from keyboards.inline.user_menu import get_user_menu_keyboard
from keyboards.reply.cancel import get_cancel_keyboard
from states.registration import RegistrationStates
from filters.is_admin import IsAdmin
from filters.is_private import IsPrivate
from utils.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name="user_start")


@router.message(CommandStart(), IsPrivate())
async def cmd_start(message: Message, state: FSMContext, db_user: User):
    """
    Обработчик команды /start.
    Проверяет, заполнена ли биография пользователя.
    Если пуста — начинает диалог знакомства (FSM), иначе показывает главное меню.
    """
    logger.info(f"User {message.from_user.id} triggered /start")
    
    # Если профиль новый и биография еще не заполнена, запускаем FSM
    if not db_user.bio:
        await message.answer(
            f"Нихао, {message.from_user.first_name}! {chr(127800)}\n"
            "Я Нихао-тян, твой интерактивный помощник.\n\n"
            "Давай познакомимся поближе! Напиши, как мне к тебе обращаться?",
            reply_markup=get_cancel_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_name)
    else:
        # Если пользователь уже зарегистрирован, показываем меню
        is_admin_user = await IsAdmin()(message, db_user)
        await message.answer(
            f"Рада видеть тебя снова, {db_user.first_name}! {chr(10024)}\n"
            "Чем я могу помочь тебе сегодня?",
            reply_markup=get_user_menu_keyboard(is_admin=is_admin_user)
        )


@router.message(Command("help"), IsPrivate())
async def cmd_help(message: Message, db_user: User):
    """
    Обработчик команды /help.
    Показывает справочную информацию по доступным командам.
    """
    is_admin_user = await IsAdmin()(message, db_user)
    help_text = (
        "Доступные команды: \n"
        "| /start - Запустить бота и войти в меню\n"
        "| /help - Показать список команд\n"
        "| /about - Информация о Нихао-тян\n"
    )
    if is_admin_user:
        help_text += "| /admin - Войти в панель администратора\n"

    await message.answer(help_text)


@router.message(Command("about"), IsPrivate())
async def cmd_about(message: Message):
    """
    Обработчик команды /about.
    Предоставляет описание проекта.
    """
    await message.answer(
        "✨ **Нихао-тян Бот** — это высококачественный шаблон Telegram-бота,\n"
        "построенный на базе фреймворка Aiogram 3.x и асинхронной СУБД SQLAlchemy 2.0.\n\n"
        "Шаблон поддерживает ролевую модель (пользователь/админ), "
        "FSM-состояния, защиту от спама (Anti-flood) и полноценную СУБД SQLite/PostgreSQL."
    )


# --- FSM Хендлеры Onboarding (Регистрация) ---

@router.message(RegistrationStates.waiting_for_name, IsPrivate())
async def process_name(message: Message, state: FSMContext):
    """
    Получение имени пользователя во время регистрации.
    """
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена. Введите /start для повторной попытки.")
        return

    name = message.text.strip()
    if len(name) < 2 or len(name) > 30:
        await message.answer("Пожалуйста, введите корректное имя (от 2 до 30 символов).")
        return

    await state.update_data(name=name)
    await message.answer(
        f"Очень приятно, {name}! {chr(128140)}\n"
        "Теперь напиши коротко о себе (например, свои интересы или род занятий, до 150 символов):",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_bio)


@router.message(RegistrationStates.waiting_for_bio, IsPrivate())
async def process_bio(message: Message, state: FSMContext, session: AsyncSession, db_user: User):
    """
    Получение био во время регистрации и завершение FSM.
    """
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена. Введите /start для повторной попытки.")
        return

    bio = message.text.strip()
    if len(bio) > 150:
        await message.answer(f"Описание слишком длинное! Уложитесь в 150 символов (сейчас: {len(bio)}).")
        return

    data = await state.get_data()
    name = data.get("name", message.from_user.first_name)

    # Обновляем био и имя (first_name) в базе данных
    db_user.first_name = name
    db_user.bio = bio
    await session.commit()

    await state.clear()
    
    is_admin_user = await IsAdmin()(message, db_user)
    await message.answer(
        "✨ Ура! Профиль успешно настроен! Приятно познакомиться! ✨",
        reply_markup=get_user_menu_keyboard(is_admin=is_admin_user)
    )


# --- Хендлеры возврата в меню ---

@router.callback_query(F.data == "back_to_menu", IsPrivate())
async def process_back_to_menu(callback: CallbackQuery, db_user: User):
    """
    Возврат в главное меню при нажатии inline-кнопки.
    """
    await callback.answer()
    is_admin_user = await IsAdmin()(callback, db_user)
    await callback.message.edit_text(
        f"Главное меню Нихао-тян {chr(127800)}\n"
        "Выберите интересующий вас раздел:",
        reply_markup=get_user_menu_keyboard(is_admin=is_admin_user)
    )
