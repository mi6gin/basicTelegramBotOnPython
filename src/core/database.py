import datetime
from sqlalchemy import create_engine, Column, BigInteger, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.dialects.sqlite import insert

# --- Настройка SQLAlchemy ---
DB_URL = "sqlite+aiosqlite:///./main.db"  # Путь к файлу вашей БД
Base = declarative_base()

# Асинхронный движок
async_engine = create_async_engine(DB_URL)

# Асинхронная сессия
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# --- Модель пользователя ---
class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}')>"

# --- Функции для работы с БД ---
async def init_db():
    """Инициализирует базу данных и создает таблицы."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncSession:
    """Возвращает асинхронную сессию."""
    return AsyncSessionLocal()

async def upsert_user(session: AsyncSession, user_data: dict):
    """
    Добавляет нового пользователя или обновляет существующего.
    Поле created_at не обновляется при наличии пользователя.
    """
    
    # Запрос на вставку
    stmt = insert(User).values(
        user_id=user_data['user_id'],
        username=user_data.get('username'),
        first_name=user_data['first_name'],
        last_name=user_data.get('last_name'),
        created_at=datetime.datetime.now()
    )

    # Указание, что делать при конфликте (если user_id уже существует)
    # Здесь мы обновляем поля, которые могли измениться
    do_update_stmt = stmt.on_conflict_do_update(
        index_elements=['user_id'],
        set_={
            'username': stmt.excluded.username,
            'first_name': stmt.excluded.first_name,
            'last_name': stmt.excluded.last_name
        }
    )
    
    await session.execute(do_update_stmt)
    await session.commit()
