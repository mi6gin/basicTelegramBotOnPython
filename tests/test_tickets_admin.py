import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from routers.admin.tickets import view_open_tickets, close_ticket_callback
from routers.user.catalog import select_catalog_item
from database.models.ticket import Ticket
from database.models.user import User


@pytest.mark.asyncio
async def test_view_open_tickets_empty():
    """Тест просмотра тикетов администратором, когда тикетов нет."""
    callback = MagicMock(spec=CallbackQuery)
    callback.data = "admin_tickets_view_0"
    callback.answer = AsyncMock()
    callback.message = MagicMock()
    callback.message.edit_text = AsyncMock()
    
    session = MagicMock(spec=AsyncSession)
    i18n = MagicMock(spec=I18nContext)
    i18n.get = MagicMock(return_value="No tickets")
    state = AsyncMock(spec=FSMContext)

    with patch("database.repository.ticket_repo.TicketRepository.get_all_open", return_value=[]):
        await view_open_tickets(callback, session, i18n, state)
        
        callback.answer.assert_called_once()
        state.clear.assert_called_once()
        callback.message.edit_text.assert_called_once_with("No tickets", reply_markup=ANY)


@pytest.mark.asyncio
async def test_view_open_tickets_success():
    """Тест просмотра тикетов администратором, когда они есть в системе."""
    callback = MagicMock(spec=CallbackQuery)
    callback.data = "admin_tickets_view_0"
    callback.answer = AsyncMock()
    callback.message = MagicMock()
    callback.message.edit_text = AsyncMock()
    
    session = MagicMock(spec=AsyncSession)
    i18n = MagicMock(spec=I18nContext)
    i18n.get = MagicMock(return_value="Ticket template")
    state = AsyncMock(spec=FSMContext)

    mock_ticket = MagicMock(spec=Ticket)
    mock_ticket.id = 4
    mock_ticket.status = "open"
    mock_ticket.user_id = 1234
    mock_ticket.message = "Need help"
    mock_ticket.created_at = MagicMock()
    mock_ticket.user = MagicMock()
    mock_ticket.user.first_name = "Alice"
    mock_ticket.user.username = "alice_test"

    with patch("database.repository.ticket_repo.TicketRepository.get_all_open", return_value=[mock_ticket]):
        await view_open_tickets(callback, session, i18n, state)
        
        callback.answer.assert_called_once()
        state.clear.assert_called_once()
        callback.message.edit_text.assert_called_once()


@pytest.mark.asyncio
async def test_close_ticket_callback():
    """Тест закрытия тикета администратором по кнопке."""
    callback = MagicMock(spec=CallbackQuery)
    callback.data = "admin_ticket_close_4_0"
    callback.answer = AsyncMock()
    callback.message = MagicMock()
    callback.message.edit_text = AsyncMock()
    
    session = MagicMock(spec=AsyncSession)
    i18n = MagicMock(spec=I18nContext)
    i18n.get = MagicMock(return_value="Closed info")
    state = AsyncMock(spec=FSMContext)

    with patch("database.repository.ticket_repo.TicketRepository.close", return_value=True) as mock_close, \
         patch("database.repository.ticket_repo.TicketRepository.get_all_open", return_value=[]):
        await close_ticket_callback(callback, session, i18n, state)
        
        mock_close.assert_called_once_with(session, 4)
        callback.answer.assert_called_once_with("Closed info", show_alert=True)
        callback.message.edit_text.assert_called_once()


@pytest.mark.asyncio
async def test_select_catalog_theme():
    """Тест активации темы пользователем в каталоге."""
    callback = MagicMock(spec=CallbackQuery)
    callback.data = "catalog_select_theme_sakura"
    callback.answer = AsyncMock()
    
    session = MagicMock(spec=AsyncSession)
    db_user = MagicMock(spec=User)
    db_user.telegram_id = 9876
    
    i18n = MagicMock(spec=I18nContext)
    i18n.get = MagicMock(return_value="Sakura Style applied")

    with patch("database.repository.user_repo.UserRepository.set_selected_theme", return_value=True) as mock_set_theme:
        await select_catalog_item(callback, session, db_user, i18n)
        
        mock_set_theme.assert_called_once_with(session, 9876, "theme_sakura")
        callback.answer.assert_called_once_with("Sakura Style applied", show_alert=True)
