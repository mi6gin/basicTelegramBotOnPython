from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.engine import Base


class Ticket(Base):
    """
    Таблица обращений (тикетов) пользователей в поддержку к Нихао-тян.
    """
    __tablename__ = "tickets"

    # Уникальный идентификатор обращения
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Telegram ID пользователя, создавшего тикет
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))
    
    # Текст обращения
    message: Mapped[str] = mapped_column(String(1000))
    
    # Статус тикета: 'open' или 'closed'
    status: Mapped[str] = mapped_column(String(20), default="open")
    
    # Дата и время создания тикета
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Отношение к модели пользователя User
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<Ticket id={self.id} user_id={self.user_id} status={self.status}>"
