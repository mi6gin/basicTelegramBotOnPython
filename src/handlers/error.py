import traceback
from datetime import datetime
from typing import Any

from aiogram import Router
from aiogram.types import BufferedInputFile, ErrorEvent
from aiogram.handlers import ErrorHandler as _BaseHandler

from src.settings import Config


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

        for admin_id in Config.ADMIN_ID:
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
        user = getattr(self.event_data.update.message, "from_user", None)
        return getattr(user, "username", "unknown") or "no_username"


def setup(r: Router):
    r.errors.register(ErrorHandler)