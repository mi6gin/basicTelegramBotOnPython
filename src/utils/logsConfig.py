import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import os
from aiogram.types import Message

class SafeFormatter(logging.Formatter):
    def format(self, record):
        record.username = getattr(record, "username", "SYSTEM")
        record.user_id = getattr(record, "user_id", "-")
        record.chat_id = getattr(record, "chat_id", "-")
        return super().format(record)

logger = logging.getLogger(__name__)


def log_message(message: Message):
    if message.photo:
        caption = f" с подписью: '{message.caption}'" if message.caption else " без подписи"
        content_info = f"Отправлена фотография{caption}"

    elif message.video:
        caption = f" с подписью: '{message.caption}'" if message.caption else " без подписи"
        content_info = f"Отправлено видео{caption}"

    elif message.document:
        caption = f" с подписью: '{message.caption}'" if message.caption else " без подписи"
        content_info = f"Отправлен документ ({message.document.file_name}){caption}"

    elif message.text:
        content_info = message.text
    else:
        content_info = f"Отправлен другой тип медиа (type: {message.content_type})"

    logger.info(
        content_info,
        extra={
            "username": message.from_user.username or message.from_user.full_name,
            "user_id": message.from_user.id,
            "chat_id": message.chat.id,
        }
    )

def init_logger():
    os.makedirs("logs", exist_ok=True)

    log_format = (
        "%(asctime)s | "
        "[%(username)s -- %(user_id)s] | "
        "[ChatId -- %(chat_id)s] : "
        "%(message)s"
    )

    date_format = "%d.%m.%Y (%H:%M:%S)"

    formatter = SafeFormatter(fmt=log_format, datefmt=date_format)

    file_handler = TimedRotatingFileHandler(
        "logs/NihaoTyan.log",
        when="midnight",
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)