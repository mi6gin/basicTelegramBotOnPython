import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message
from middlewares.throttling_mw import ThrottlingMiddleware
from middlewares.ban_mw import BanMiddleware
from database.repository.user_repo import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_throttling_middleware_block_spam():
    """Тест троттлинг-мидлвари: первое сообщение проходит, второе блокируется (спам)."""
    middleware = ThrottlingMiddleware(limit=1.0)
    handler = AsyncMock(return_value="handler_response")

    # Создаем mock-сообщение
    message = MagicMock(spec=Message)
    message.from_user = MagicMock()
    message.from_user.id = 12345

    data = {}

    # Первый запрос — должен успешно пройти в обработчик
    res1 = await middleware(handler, message, data)
    assert res1 == "handler_response"
    assert handler.call_count == 1

    # Второй мгновенный запрос — должен заблокироваться (handler не должен вызваться повторно)
    res2 = await middleware(handler, message, data)
    assert res2 is None
    assert handler.call_count == 1  # Счетчик вызовов остался прежним
    
    
@pytest.mark.asyncio
async def test_ban_middleware_allows_active_user(db_session: AsyncSession):
    """Проверяет, что BanMiddleware регистрирует активного юзера и пропускает его дальше."""
    middleware = BanMiddleware()
    handler = AsyncMock(return_value="allowed")
    
    message = MagicMock(spec=Message)
    tg_user = MagicMock()
    tg_user.id = 77701
    tg_user.username = "active_guy"
    tg_user.first_name = "Alex"
    tg_user.last_name = "Smith"
    
    message.from_user = tg_user
    
    data = {
        "session": db_session,
        "event_from_user": tg_user
    }
    
    result = await middleware(handler, message, data)
    assert result == "allowed"
    assert handler.call_count == 1
    
    # Объект db_user должен быть добавлен в data
    assert "db_user" in data
    assert data["db_user"].telegram_id == 77701
    assert data["db_user"].is_banned is False


@pytest.mark.asyncio
async def test_ban_middleware_blocks_banned_user(db_session: AsyncSession):
    """Проверяет, что BanMiddleware блокирует забаненного юзера и не пускает его в хендлер."""
    user_id = 77702
    
    # 1. Сначала регистрируем и баним пользователя в тестовой БД
    await UserRepository.get_or_create(db_session, user_id, first_name="BadGuy")
    await UserRepository.set_ban_status(db_session, user_id, is_banned=True)
    
    middleware = BanMiddleware()
    handler = AsyncMock(return_value="should_not_run")
    
    message = AsyncMock(spec=Message)
    tg_user = MagicMock()
    tg_user.id = user_id
    tg_user.username = "banned_guy"
    tg_user.first_name = "BadGuy"
    tg_user.last_name = None
    
    message.from_user = tg_user
    message.answer = AsyncMock() # Mock ответа пользователю
    
    data = {
        "session": db_session,
        "event_from_user": tg_user
    }
    
    result = await middleware(handler, message, data)
    assert result is None # Запрос отклонен
    assert handler.call_count == 0 # Обработчик не вызывался
    
    # Сообщение о блокировке должно быть отправлено пользователю
    message.answer.assert_called_once()
    assert "заблокированы" in message.answer.call_args[0][0]
