from aiogram import Bot, Dispatcher

from src.middlewares.LoggingMiddleware import LoggingMiddleware
from src.middlewares.UserManagementMiddleware import UserManagementMiddleware
from src.middlewares.DbSessionMiddleware import DbSessionMiddleware
from src.settings import config
from src.core.notifier import Notifier
from src.core.database import init_db, AsyncSessionLocal
from src.handlers import get_handlers_router
from src.utils.logsConfig import init_logger
from src.utils.botCommands import set_commands

async def start_bot():
    # 1. Инициализация БД
    await init_db()
    
    # 2. Логирование
    init_logger()
    
    # 3. Бот и Диспетчер
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    # 4. Регистрация Middlewares
    # Важно: DbSessionMiddleware должен идти первым, чтобы сессия была доступна в других middleware
    dp.update.outer_middleware(DbSessionMiddleware(AsyncSessionLocal))
    dp.update.outer_middleware(UserManagementMiddleware())
    dp.message.outer_middleware(LoggingMiddleware())

    # 5. Регистрация роутеров (все хендлеры теперь в одном главном роутере)
    main_router = get_handlers_router()
    dp.include_router(main_router)

    # 6. Дополнительные настройки
    await set_commands(bot)
    await Notifier.setup(bot)
    
    # 7. Запуск
    await dp.start_polling(bot)
