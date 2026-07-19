import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Определяем пути для логов
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "bot.log"


def setup_logger(name: str = "nihao_chan") -> logging.Logger:
    """
    Настраивает и возвращает экземпляр логгера с выводом в консоль и файл.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Проверяем, чтобы обработчики не дублировались при повторном вызове
    if not logger.handlers:
        # Формат логирования
        log_format = logging.Formatter(
            fmt="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Вывод в консоль
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        # Вывод в файл с ротацией (максимум 5 файлов по 5 МБ каждый)
        file_handler = RotatingFileHandler(
            filename=LOG_FILE,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(log_format)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

    return logger


# Экспортируем основной логгер
logger = setup_logger()
