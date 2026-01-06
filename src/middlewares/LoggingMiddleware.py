from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            from src.utils.logsConfig import log_message
            log_message(event)

        # Передаем управление дальше к хендлерам
        return await handler(event, data)