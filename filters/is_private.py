from typing import Union
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery


class IsPrivate(Filter):
    """
    Фильтр для проверки того, что сообщение или нажатие кнопки произошло в личном чате с ботом.
    Предотвращает вызовы команд личного кабинета в группах и супергруппах.
    """

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        if isinstance(event, Message):
            return event.chat.type == "private"
        elif isinstance(event, CallbackQuery):
            # Проверяем чат сообщения, к которому прикреплена inline-кнопка
            return event.message.chat.type == "private" if event.message else False
        return False
