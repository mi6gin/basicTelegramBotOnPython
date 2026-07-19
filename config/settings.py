from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, field_validator
from typing import List


class Settings(BaseSettings):
    """
    Класс конфигурации бота Нихао-тян.
    Загружает переменные окружения или данные из .env файла.
    """
    # Токен бота, получаемый от @BotFather (обернут в SecretStr для безопасности)
    bot_token: SecretStr
    
    # Список Telegram ID администраторов бота
    admin_ids: List[int] = []

    # URL подключения к базе данных (по умолчанию SQLite)
    db_url: str = "sqlite+aiosqlite:///nihao_chan.db"
    
    # Настройки антифлуда (троттлинга) в секундах
    throttling_delay: float = 0.8

    # Настройки для загрузки переменных окружения
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        """
        Валидатор для разбора списка ID администраторов.
        Позволяет передавать их через запятую в .env: ADMIN_IDS=12345,67890
        """
        if isinstance(v, str):
            if not v.strip():
                return []
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v


# Создаем глобальный объект настроек
settings = Settings()
