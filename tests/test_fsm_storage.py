import pytest
from unittest.mock import MagicMock, AsyncMock
from aiogram.fsm.storage.base import StorageKey
from database.fsm_storage import SQLAlchemyStorage
from database.models.fsm_state import FSMStateModel
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_sqlalchemy_storage_state_operations():
    """Тест записи и чтения FSM состояний и временных данных в SQLAlchemyStorage."""
    # 1. Готовим заглушки сессии и сессион-мейкера
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.add = MagicMock()
    
    session_maker = MagicMock()
    session_maker.return_value.__aenter__ = AsyncMock(return_value=session)
    session_maker.return_value.__aexit__ = AsyncMock()
    
    storage = SQLAlchemyStorage(session_maker)
    key = StorageKey(bot_id=1, chat_id=2, user_id=3, destiny='default')
    
    # 2. Имитируем, что записи в БД изначально нет (set_state должен создать новую модель)
    mock_result_empty = MagicMock()
    mock_result_empty.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_result_empty
    
    await storage.set_state(key, "TestState")
    
    # Должна добавиться новая запись в БД и выполниться коммит
    session.add.assert_called_once()
    session.commit.assert_called_once()
    
    # 3. Имитируем, что запись в БД уже существует
    mock_record = FSMStateModel(key="1:2:3:default", state="TestState", data="{}")
    mock_result_exists = MagicMock()
    mock_result_exists.scalar_one_or_none.return_value = mock_record
    session.execute.return_value = mock_result_exists
    
    # Проверяем получение состояния (get_state)
    retrieved_state = await storage.get_state(key)
    assert retrieved_state == "TestState"
    
    # Проверяем запись данных (set_data)
    session.add.reset_mock()
    session.commit.reset_mock()
    await storage.set_data(key, {"foo": "bar"})
    
    # Данные должны обновиться в существующей записи в виде JSON
    assert mock_record.data == '{"foo": "bar"}'
    session.commit.assert_called_once()
    session.add.assert_not_called()  # Модель уже существует в сессии, add не нужен
    
    # Проверяем получение данных (get_data)
    retrieved_data = await storage.get_data(key)
    assert retrieved_data == {"foo": "bar"}
