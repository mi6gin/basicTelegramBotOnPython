from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config.settings import settings
from utils.logger import logger

# Создаем асинхронный движок для подключения к БД
engine = create_async_engine(
    url=settings.db_url,
    echo=False,  # Можно включить True для отладки SQL-запросов
    future=True
)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """
    Базовый декларативный класс для моделей SQLAlchemy.
    """
    pass


async def init_db():
    """
    Создает все таблицы базы данных, если они еще не существуют.
    """
    try:
        logger.info("Инициализация базы данных...")
        async with engine.begin() as conn:
            # Импортируем модели перед созданием таблиц, чтобы они зарегистрировались в Base.metadata
            from database.models.user import User
            from database.models.ticket import Ticket
            
            await conn.run_sync(Base.metadata.create_all)
        logger.info("База данных успешно инициализирована.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}", exc_info=True)
        raise e
