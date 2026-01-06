from aiogram import Router, Bot

from src.core.notifier import Notifier
from src.settings import Config


async def on_startup(bot: Bot):
    me = await bot.get_me()
    bot_username = f"@{me.username}" if me.username else me.full_name

    for admin in Config.ADMIN_ID:
        await Notifier.notify(admin, f"Бот {bot_username} запущен")


def setup(r: Router):
    r.startup.register(on_startup)
