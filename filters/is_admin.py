from typing import Union, Optional
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from config.settings import settings
from database.models.user import User


class IsAdmin(Filter):
    """
    Фильтр для проверки прав администратора.
    Проверяет Telegram ID по списку ADMIN_IDS в настройках или роль в БД.
    """

    async def __call__(self, event: Union[Message, CallbackQuery], db_user: Optional[User] = None) -> bool:
        user_id = event.from_user.id
        
        # 1. Проверка по жестко заданным ID в конфигурационном файле
        if user_id in settings.admin_ids:
            return True
            
        # 2. Проверка по роли в базе данных (если db_user успешно прокинут)
        if db_user and db_user.role == "admin":
            return True
            
        return False
