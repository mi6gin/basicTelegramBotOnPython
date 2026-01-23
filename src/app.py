from aiogram import Bot, Dispatcher

from src.middlewares.LoggingMiddleware import LoggingMiddleware
from src.middlewares.UserManagementMiddleware import UserManagementMiddleware
from src.settings import Config as botConfig
from src.core.notifier import Notifier
from src.core.database import init_db
from src.handlers.user.__init__  import setup as user_startup
from src.handlers.__init__ import setup as on_startup_setup
from src.utils.logsConfig import init_logger
from src.utils.botCommands import set_commands

async def start_bot():
    await init_db()  # Инициализация базы данных
    init_logger()
    bot = Bot(token=botConfig.TOKEN)
    dp = Dispatcher()

    # Регистрация middleware
    dp.update.outer_middleware(UserManagementMiddleware()) # Для всех входящих апдейтов
    dp.message.outer_middleware(LoggingMiddleware())

    user_startup(dp)
    on_startup_setup(dp)
    await set_commands(bot)
    await Notifier.setup(bot)
    await dp.start_polling(bot)