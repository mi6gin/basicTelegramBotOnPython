import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.repository.user_repo import UserRepository
from database.repository.ticket_repo import TicketRepository
from database.models.user import User
from database.models.ticket import Ticket


@pytest.mark.asyncio
async def test_user_repository_get_or_create(db_session: AsyncSession):
    """Тест создания пользователя и получения существующего."""
    telegram_id = 99999
    username = "test_user"
    first_name = "Ivan"

    # 1. Создание нового пользователя
    user = await UserRepository.get_or_create(
        session=db_session,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name
    )
    assert user is not None
    assert user.telegram_id == telegram_id
    assert user.username == username
    assert user.first_name == first_name
    assert user.role == "user"
    assert user.is_banned is False

    # 2. Получение того же пользователя (повторный запрос)
    existing_user = await UserRepository.get_or_create(
        session=db_session,
        telegram_id=telegram_id,
        username=username,
        first_name="Ivan_Updated"  # Попробуем обновить имя
    )
    assert existing_user.telegram_id == telegram_id
    assert existing_user.first_name == "Ivan_Updated"  # Имя обновилось в БД
@pytest.mark.asyncio
async def test_user_repository_ban_status_and_stats(db_session: AsyncSession):
    """Тест переключения бана и корректности статистики по пользователям."""
    u1 = await UserRepository.get_or_create(db_session, 10001, first_name="User1")
    u2 = await UserRepository.get_or_create(db_session, 10002, first_name="User2")

    # Проверяем начальную статистику
    total = await UserRepository.get_total_count(db_session)
    banned = await UserRepository.get_banned_count(db_session)
    assert total == 2
    assert banned == 0

    # Блокируем первого пользователя
    await UserRepository.set_ban_status(db_session, 10001, is_banned=True)
    
    banned_after = await UserRepository.get_banned_count(db_session)
    assert banned_after == 1

    user1 = await UserRepository.get_by_id(db_session, 10001)
    assert user1.is_banned is True


@pytest.mark.asyncio
async def test_ticket_repository_lifecycle(db_session: AsyncSession):
    """Тест полного цикла работы с тикетом техподдержки."""
    # 1. Создаем пользователя, который напишет тикет
    user_id = 77777
    await UserRepository.get_or_create(db_session, user_id, first_name="Bob")

    # 2. Создаем тикет поддержки
    ticket_msg = "У меня не нажимается кнопка каталога!"
    ticket = await TicketRepository.create(db_session, user_id, ticket_msg)
    
    assert ticket is not None
    assert ticket.id is not None
    assert ticket.user_id == user_id
    assert ticket.message == ticket_msg
    assert ticket.status == "open"

    # Проверяем счетчик открытых тикетов
    open_count = await TicketRepository.get_open_count(db_session)
    assert open_count == 1

    # 3. Получаем тикет по ID
    db_ticket = await TicketRepository.get_by_id(db_session, ticket.id)
    assert db_ticket is not None
    assert db_ticket.user.first_name == "Bob"  # Связь подгрузилась

    # 4. Закрываем тикет
    success = await TicketRepository.close(db_session, ticket.id)
    assert success is True

    # Проверяем счетчик открытых тикетов после закрытия
    open_count_after = await TicketRepository.get_open_count(db_session)
    assert open_count_after == 0
