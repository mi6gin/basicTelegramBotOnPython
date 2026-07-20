import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# Определяем пути для логов
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "bot.log"


class ColorFormatter(logging.Formatter):
    """
    Кастомный форматировщик логов для консоли с поддержкой ANSI цветов.
    """
    GREY = "\x1b[38;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: GREY + "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s" + RESET,
        logging.INFO: GREEN + "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s" + RESET,
        logging.WARNING: YELLOW + "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s" + RESET,
        logging.ERROR: RED + "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s" + RESET,
        logging.CRITICAL: BOLD_RED + "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s" + RESET,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.GREY)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logger(name: str = "nihao_chan") -> logging.Logger:
    """
    Настраивает и возвращает экземпляр логгера с выводом в консоль (цвета) и файл (по дням).
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Проверяем, чтобы обработчики не дублировались при повторном вызове
    if not logger.handlers:
        # Вывод в консоль (с цветным форматированием)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColorFormatter())
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        # Стандартный плоский формат для файла
        file_format = logging.Formatter(
            fmt="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Вывод в файл с посуточной ротацией (каждый день в полночь, хранение за 30 дней)
        file_handler = TimedRotatingFileHandler(
            filename=LOG_FILE,
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        file_handler.setFormatter(file_format)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

    return logger


# Экспортируем основной логгер
logger = setup_logger()
