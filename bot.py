import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config.settings import settings
from database.engine import init_db, AsyncSessionLocal
from middlewares.db_session_mw import DbSessionMiddleware
from middlewares.ban_mw import BanMiddleware
from middlewares.throttling_mw import ThrottlingMiddleware
from middlewares.logging_mw import LoggingMiddleware
from routers import get_main_router
from utils.logger import logger


async def set_bot_commands(bot: Bot):
    """
    Устанавливает базовое меню команд в интерфейсе Telegram.
    """
    commands = [
        BotCommand(command="start", description="Запустить бота / Меню 🌸"),
        BotCommand(command="help", description="Показать справку ℹ️"),
        BotCommand(command="about", description="О Нихао-тян ✨")
    ]
    await bot.set_my_commands(commands)


async def main():
    """
    Основная функция запуска бота Нихао-тян.
    """
    logger.info("Запуск бота Нихао-тян...")

    # 1. Инициализация базы данных (создание таблиц)
    await init_db()

    # 2. Инициализация бота и диспетчера.
    # Настраиваем HTML разметку сообщений по умолчанию для красивого форматирования.
    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # 3. Регистрация Middleware (прослоек).
    # Порядок регистрации критически важен:
    # 1) Сессия БД — открывает транзакцию и передает ее в следующие слои.
    # 2) Баны — проверяет статус блокировки и регистрирует новых пользователей.
    # 3) Антифлуд (Троттлинг) — защищает бот от спам-сообщений.
    # 4) Логирование — записывает поступающие события в логи.
    dp.update.outer_middleware(DbSessionMiddleware(AsyncSessionLocal))
    dp.update.outer_middleware(BanMiddleware())
    dp.message.outer_middleware(ThrottlingMiddleware())
    dp.update.outer_middleware(LoggingMiddleware())

    # 4. Подключение общего роутера хендлеров
    dp.include_router(get_main_router())

    # 5. Установка команд меню
    await set_bot_commands(bot)

    # 6. Пропуск накопившихся обновлений перед стартом (drop_pending_updates)
    await bot.delete_webhook(drop_pending_updates=True)

    # 7. Запуск polling-а
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Критическая ошибка при работе бота: {e}", exc_info=True)
    finally:
        # Корректное закрытие сессий при завершении
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот Нихао-тян остановлен пользователем.")
        sys.exit(0)
