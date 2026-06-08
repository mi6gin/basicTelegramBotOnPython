from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as AiogramUser
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

from src.core.models import User

class UserManagementMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: AiogramUser | None = data.get("event_from_user")
        session: AsyncSession = data.get("session")

        if user and session:
            # Логика Upsert пользователя
            stmt = insert(User).values(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                created_at=datetime.datetime.now()
            )

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
        
        return await handler(event, data)
