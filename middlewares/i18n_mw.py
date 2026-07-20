from typing import Any, Dict, Optional
from aiogram_i18n.managers.base import BaseManager
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore
from aiogram.types import User as TelegramUser
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import User
from database.repository.user_repo import UserRepository
from config.settings import settings


class DBLocaleManager(BaseManager):
    """
    Кастомный менеджер локализации, работающий с базой данных (Unit of Work).
    """

    def __init__(self, default_locale: str = "ru"):
        super().__init__(default_locale=default_locale)

    async def get_locale(
        self,
        db_user: Optional[User] = None,
        event_from_user: Optional[TelegramUser] = None,
        **kwargs: Any
    ) -> str:
        # 1. Если пользователь уже авторизован и у него есть язык в БД
        if db_user and db_user.language:
            return db_user.language
            
        # 2. Если пользователя нет в БД, пробуем определить язык по его настройкам в Telegram
        if event_from_user and event_from_user.language_code:
            lang = event_from_user.language_code.split("-")[0]
            if lang in ("ru", "en"):
                return lang
                
        # 3. Дефолтный язык
        return self.default_locale

    async def set_locale(
        self,
        locale: str,
        db_user: Optional[User] = None,
        session: Optional[AsyncSession] = None,
        **kwargs: Any
    ) -> None:
        # Устанавливаем язык пользователю в БД (коммит произойдет автоматически в конце middleware)
        if db_user and session:
            await UserRepository.update_language(session, db_user.telegram_id, locale)


# Настраиваем ядро локализации на Fluent (.ftl файлы)
i18n_middleware = I18nMiddleware(
    core=FluentRuntimeCore(path="locales"),
    default_locale="ru",
    manager=DBLocaleManager(default_locale="ru")
)
