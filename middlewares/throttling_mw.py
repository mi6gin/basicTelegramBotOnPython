import time
from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from config.settings import settings


class ThrottlingMiddleware(BaseMiddleware):
    """
    Мидлварь для ограничения частоты запросов от одного пользователя (Anti-flood).
    Использует кэш в памяти с автоматической очисткой.
    """

    def __init__(self, limit: float = settings.throttling_delay):
        super().__init__()
        self.limit = limit
        self.caches: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Применяем троттлинг только к сообщениям
        if not isinstance(event, Message):
            return await handler(event, data)

        user = event.from_user
        if not user:
            return await handler(event, data)

        user_id = user.id
        now = time.time()

        # Очистка памяти при переполнении кэша
        if len(self.caches) > 10000:
            self.caches = {
                uid: ts for uid, ts in self.caches.items() 
                if now - ts < self.limit
            }

        if user_id in self.caches:
            delta = now - self.caches[user_id]
            if delta < self.limit:
                # Превышен лимит запросов — игнорируем сообщение
                # При желании можно отправить сообщение пользователю:
                # await event.answer("Не пишите так часто, Нихао-тян не успевает отвечать!")
                return

        # Обновляем время последнего запроса и запускаем обработчик
        self.caches[user_id] = now
        return await handler(event, data)
