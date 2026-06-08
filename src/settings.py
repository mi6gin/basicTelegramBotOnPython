from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    # Pydantic автоматически подтянет эти переменные из .env или окружения
    bot_token: SecretStr
    admin_ids: list[int]

    # Настройка для загрузки из файла
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Создаем экземпляр конфига
config = Settings()
