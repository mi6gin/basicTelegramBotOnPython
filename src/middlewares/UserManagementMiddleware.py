from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as AiogramUser

from src.core.database import get_async_session, upsert_user


class UserManagementMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        
        # Получаем объект пользователя из данных события
        user: AiogramUser | None = data.get("event_from_user")

        if user:
            # Получаем асинхронную сессию
            async with await get_async_session() as session:
                # Подготавливаем данные для сохранения
                user_data = {
                    "user_id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
                # Вызываем функцию для добавления/обновления пользователя
                await upsert_user(session, user_data)
        
        # Передаем управление следующему обработчику
        return await handler(event, data)
