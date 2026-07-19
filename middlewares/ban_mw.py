from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from database.repository.user_repo import UserRepository


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
            # Получаем или создаем пользователя в БД
            db_user = await UserRepository.get_or_create(
                session=session,
                telegram_id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name
            )

            # Если пользователь заблокирован — прерываем обработку
            if db_user.is_banned:
                if isinstance(event, Message):
                    await event.answer(
                        "К сожалению, вы заблокированы в системе Нихао-тян. ❌\n"
                        "Свяжитесь с администрацией, если это ошибка."
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "Вы заблокированы! Доступ ограничен.",
                        show_alert=True
                    )
                return  # Прерываем выполнение цепочки обработчиков

            # Передаем объект пользователя дальше в хендлеры и другие middleware
            data["db_user"] = db_user

        return await handler(event, data)
