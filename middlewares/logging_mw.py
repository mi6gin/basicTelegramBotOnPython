from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from utils.logger import logger


class LoggingMiddleware(BaseMiddleware):
    """
    Мидлварь для логирования входящих обновлений (сообщений и нажатий кнопок).
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        user_info = f"User(id={user.id}, username={user.username})" if user else "Unknown User"

        if isinstance(event, Message):
            if event.text:
                logger.info(f"{user_info} sent text message: '{event.text}'")
            elif event.contact:
                logger.info(f"{user_info} shared contact: '{event.contact.phone_number}'")
            else:
                logger.info(f"{user_info} sent message with content_type: {event.content_type}")
        
        elif isinstance(event, CallbackQuery):
            logger.info(f"{user_info} clicked inline button with callback_data: '{event.data}'")

        # Передаем управление следующему обработчику
        return await handler(event, data)
