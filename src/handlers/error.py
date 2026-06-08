import traceback
from datetime import datetime
from typing import Any

from aiogram import Router
from aiogram.types import BufferedInputFile, ErrorEvent
from aiogram.handlers import ErrorHandler as _BaseHandler

from src.settings import config


class ErrorHandler(_BaseHandler):
    @property
    def event_data(self) -> ErrorEvent:
        if not isinstance(self.event, ErrorEvent):
            raise ValueError(f"Expected ErrorEvent, got {type(self.event)}")
        return self.event

    async def handle(self) -> Any:
        # Используем обычный цикл вместо list comprehension
        file = self._traceback_file
        caption = self._caption

        for admin_id in config.admin_ids:
            await self.bot.send_document(
                chat_id=admin_id,
                document=file,
                caption=caption
            )

    @property
    def _traceback_file(self) -> BufferedInputFile:
        exc_text = traceback.format_exception(
            type(self.event_data.exception),
            self.event_data.exception,
            self.event_data.exception.__traceback__
        )
        file_content = "".join(exc_text).encode("utf-8")
        return BufferedInputFile(file_content, filename="traceback.txt")

    @property
    def _caption(self) -> str:
        exc_msg = str(self.event_data.exception)
        username = self._try_get_username()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return (
            f"❌ <b>Error:</b> {exc_msg}\n"
            f"👤 <b>User:</b> @{username}\n"
            f"📅 <b>Date:</b> {date}"
        )

    def _try_get_username(self) -> str:
        update = self.event_data.update
        user = None
        if update.message:
            user = update.message.from_user
        elif update.callback_query:
            user = update.callback_query.from_user
        elif update.inline_query:
            user = update.inline_query.from_user
        
        if user:
            return user.username or user.full_name or "no_username"
        return "unknown"


def setup(r: Router):
    r.errors.register(ErrorHandler)