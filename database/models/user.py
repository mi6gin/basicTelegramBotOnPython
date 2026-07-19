from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database.engine import Base


class User(Base):
    """
    Таблица пользователей бота Нихао-тян.
    """
    __tablename__ = "users"

    # Telegram ID является уникальным первичным ключом (BigInteger для поддержки длинных ID)
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    
    # Имя пользователя Telegram без знака @
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Имя пользователя
    first_name: Mapped[str] = mapped_column(String(64))
    
    # Фамилия пользователя
    last_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Краткая биография/описание профиля (заполняется в FSM)
    bio: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    
    # Роль пользователя: 'user' или 'admin'
    role: Mapped[str] = mapped_column(String(20), default="user")
    
    # Флаг блокировки пользователя
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Дата и время регистрации пользователя в боте
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"<User id={self.telegram_id} username={self.username} role={self.role}>"
