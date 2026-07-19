from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import User
from typing import List, Optional


class UserRepository:
    """
    Репозиторий для работы с таблицей пользователей (users).
    Все методы асинхронны и работают в контексте переданной сессии.
    """

    @staticmethod
    async def get_by_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
        """
        Получает пользователя по его Telegram ID.
        """
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()


    @staticmethod
    async def get_or_create(
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: str = "",
        last_name: Optional[str] = None,
        role: str = "user"
    ) -> User:
        """
        Возвращает пользователя, если он существует, иначе создает нового.
        """
        user = await UserRepository.get_by_id(session, telegram_id)
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            # Обновляем username, first_name и last_name, если они изменились
            updated = False
            if user.username != username:
                user.username = username
                updated = True
            if user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if user.last_name != last_name:
                user.last_name = last_name
                updated = True
            
            if updated:
                await session.commit()
                await session.refresh(user)
        
        return user

    @staticmethod
    async def update_bio(session: AsyncSession, telegram_id: int, bio: str) -> Optional[User]:
        """
        Обновляет описание/биографию профиля пользователя.
        """
        query = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(bio=bio)
            .returning(User)
        )
        result = await session.execute(query)
        await session.commit()
        return result.scalar_one_or_none()

    @staticmethod
    async def set_ban_status(session: AsyncSession, telegram_id: int, is_banned: bool) -> bool:
        """
        Устанавливает статус бана пользователя (True - забанить, False - разбанить).
        """
        user = await UserRepository.get_by_id(session, telegram_id)
        if user:
            user.is_banned = is_banned
            await session.commit()
            return True
        return False

    @staticmethod
    async def get_all(session: AsyncSession) -> List[User]:
        """
        Возвращает список всех зарегистрированных пользователей.
        """
        query = select(User)
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_total_count(session: AsyncSession) -> int:
        """
        Возвращает общее количество пользователей.
        """
        query = select(func.count()).select_from(User)
        result = await session.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def get_banned_count(session: AsyncSession) -> int:
        """
        Возвращает количество забаненных пользователей.
        """
        query = select(func.count()).select_from(User).where(User.is_banned == True)
        result = await session.execute(query)
        return result.scalar() or 0
