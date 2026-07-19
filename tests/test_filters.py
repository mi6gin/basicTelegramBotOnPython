import pytest
from unittest.mock import MagicMock, patch
from filters.is_admin import IsAdmin
from filters.is_private import IsPrivate
from database.models.user import User


@pytest.mark.asyncio
async def test_is_admin_from_settings():
    """Проверка того, что пользователь признается админом по ID из настроек."""
    event = MagicMock()
    event.from_user.id = 11111

    filter_instance = IsAdmin()
    with patch("filters.is_admin.settings") as mock_settings:
        mock_settings.admin_ids = [11111]
        result = await filter_instance(event, db_user=None)
        assert result is True


@pytest.mark.asyncio
async def test_is_admin_from_db():
    """Проверка того, что пользователь признается админом по его роли из БД."""
    event = MagicMock()
    event.from_user.id = 22222

    db_user = MagicMock(spec=User)
    db_user.role = "admin"

    filter_instance = IsAdmin()
    with patch("filters.is_admin.settings") as mock_settings:
        mock_settings.admin_ids = [11111]  # Другой ID
        result = await filter_instance(event, db_user=db_user)
        assert result is True


@pytest.mark.asyncio
async def test_is_not_admin():
    """Проверка того, что обычный пользователь не проходит фильтр IsAdmin."""
    event = MagicMock()
    event.from_user.id = 33333

    db_user = MagicMock(spec=User)
    db_user.role = "user"

    filter_instance = IsAdmin()
    with patch("filters.is_admin.settings") as mock_settings:
        mock_settings.admin_ids = [11111]
        result = await filter_instance(event, db_user=db_user)
        assert result is False


from aiogram.types import Message, CallbackQuery


@pytest.mark.asyncio
async def test_is_private_chat():
    """Проверка того, что личный чат (private) проходит фильтр IsPrivate."""
    event = MagicMock(spec=Message)
    event.chat = MagicMock()
    event.chat.type = "private"

    filter_instance = IsPrivate()
    result = await filter_instance(event)
    assert result is True


@pytest.mark.asyncio
async def test_is_not_private_chat():
    """Проверка того, что групповой чат не проходит фильтр IsPrivate."""
    event = MagicMock(spec=Message)
    event.chat = MagicMock()
    event.chat.type = "group"

    filter_instance = IsPrivate()
    result = await filter_instance(event)
    assert result is False

