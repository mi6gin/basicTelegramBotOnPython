import json
from typing import Dict, Any, Optional
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from sqlalchemy import select
from database.models.fsm_state import FSMStateModel


class SQLAlchemyStorage(BaseStorage):
    """
    Кастомное хранилище FSM состояний на базе SQLAlchemy (SQLite).
    Позволяет сохранять FSM состояния и временные данные пользователей в БД,
    чтобы они не терялись при перезапусках бота.
    """
    def __init__(self, session_maker):
        self.session_maker = session_maker

    def _get_db_key(self, key: StorageKey) -> str:
        # Уникальный ключ FSM для конкретного контекста чата и пользователя
        return f"{key.bot_id}:{key.chat_id}:{key.user_id}:{key.destiny}"

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        db_key = self._get_db_key(key)
        # Получаем строку состояния
        state_str = state.state if hasattr(state, "state") else state
        
        async with self.session_maker() as session:
            query = select(FSMStateModel).where(FSMStateModel.key == db_key)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            
            if record:
                record.state = state_str
            else:
                record = FSMStateModel(key=db_key, state=state_str, data="{}")
                session.add(record)
                
            await session.commit()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        db_key = self._get_db_key(key)
        
        async with self.session_maker() as session:
            query = select(FSMStateModel).where(FSMStateModel.key == db_key)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            return record.state if record else None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        db_key = self._get_db_key(key)
        data_str = json.dumps(data)
        
        async with self.session_maker() as session:
            query = select(FSMStateModel).where(FSMStateModel.key == db_key)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            
            if record:
                record.data = data_str
            else:
                record = FSMStateModel(key=db_key, state=None, data=data_str)
                session.add(record)
                
            await session.commit()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        db_key = self._get_db_key(key)
        
        async with self.session_maker() as session:
            query = select(FSMStateModel).where(FSMStateModel.key == db_key)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record and record.data:
                try:
                    return json.loads(record.data)
                except ValueError:
                    return {}
            return {}

    async def close(self) -> None:
        # Сессии закрываются автоматически внутри контекстного менеджера,
        # поэтому метод закрытия пустой.
        pass
