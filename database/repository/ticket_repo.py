from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from database.models.ticket import Ticket
from typing import List, Optional


class TicketRepository:
    """
    Репозиторий для работы с обращениями в поддержку (tickets).
    Все методы асинхронны и работают в контексте переданной сессии.
    """

    @staticmethod
    async def create(session: AsyncSession, user_id: int, message: str) -> Ticket:
        """
        Создает новое обращение в поддержку.
        """
        ticket = Ticket(
            user_id=user_id,
            message=message,
            status="open"
        )
        session.add(ticket)
        await session.commit()
        await session.refresh(ticket)
        return ticket

    @staticmethod
    async def get_by_id(session: AsyncSession, ticket_id: int) -> Optional[Ticket]:
        """
        Получает обращение по его ID (с подгрузкой данных пользователя).
        """
        query = (
            select(Ticket)
            .options(joinedload(Ticket.user))
            .where(Ticket.id == ticket_id)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_open(session: AsyncSession) -> List[Ticket]:
        """
        Возвращает список всех открытых обращений.
        """
        query = (
            select(Ticket)
            .options(joinedload(Ticket.user))
            .where(Ticket.status == "open")
            .order_by(Ticket.created_at.desc())
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_user(session: AsyncSession, user_id: int) -> List[Ticket]:
        """
        Возвращает обращения конкретного пользователя.
        """
        query = select(Ticket).where(Ticket.user_id == user_id).order_by(Ticket.created_at.desc())
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def close(session: AsyncSession, ticket_id: int) -> bool:
        """
        Закрывает обращение (устанавливает статус 'closed').
        """
        query = (
            update(Ticket)
            .where(Ticket.id == ticket_id)
            .values(status="closed")
        )
        result = await session.execute(query)
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def get_open_count(session: AsyncSession) -> int:
        """
        Возвращает общее количество открытых обращений.
        """
        query = select(func.count()).select_from(Ticket).where(Ticket.status == "open")
        result = await session.execute(query)
        return result.scalar() or 0
