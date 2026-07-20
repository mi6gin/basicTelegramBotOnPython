from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from database.repository.user_repo import UserRepository
from config.settings import settings


class BanMiddleware(BaseMiddleware):
    """
    Мидлварь для проверки блокировки пользователя и автоматического
    создания/получения записи пользователя из базы данных.
    Добавляет объект `db_user` в аргументы хендлеров.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        session = data.get("session")
        tg_user = data.get("event_from_user")

        if session and tg_user:
            # Определяем роль пользователя на основе конфигурации ADMIN_IDS
            role = "admin" if tg_user.id in settings.admin_ids else None

            # Получаем или создаем пользователя в БД
            db_user = await UserRepository.get_or_create(
                session=session,
                telegram_id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                role=role
            )

            # Если пользователь заблокирован — прерываем обработку
            if db_user.is_banned:
                from middlewares.i18n_mw import i18n_middleware
                # Определяем локаль
                locale = db_user.language or (tg_user.language_code.split("-")[0] if tg_user.language_code else "ru")
                if locale not in ("ru", "en"):
                    locale = "ru"

                if isinstance(event, Message):
                    try:
                        msg = i18n_middleware.core.get("err-banned-message", locale)
                    except Exception:
                        msg = "Unfortunately, you are banned in the Nihao-chan system. ❌" if locale == "en" else "К сожалению, вы заблокированы в системе Нихао-тян. ❌"
                    await event.answer(msg)
                elif isinstance(event, CallbackQuery):
                    try:
                        msg = i18n_middleware.core.get("err-banned-callback", locale)
                    except Exception:
                        msg = "You are banned! Access denied." if locale == "en" else "Вы заблокированы! Доступ ограничен."
                    await event.answer(msg, show_alert=True)
                return  # Прерываем выполнение цепочки обработчиков

            # Передаем объект пользователя дальше в хендлеры и другие middleware
            data["db_user"] = db_user

        return await handler(event, data)
