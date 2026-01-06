from aiogram import types, Router
from aiogram.filters import Command

async def start(message: types.Message):
    await message.reply(
        "Здравствуйте!"
    )

def setup(r: Router):
    r.message.register(start, Command("start"))