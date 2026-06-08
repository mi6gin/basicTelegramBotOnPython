from aiogram import types, Router
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, session: AsyncSession):
    # Пример: сессия уже доступна здесь благодаря DbSessionMiddleware
    # Можно выполнять запросы: await session.execute(...)
    
    await message.reply(
        f"Здравствуйте, {message.from_user.full_name}!"
    )

def setup(r: Router):
    # В данном шаблоне мы используем подключение роутера в handlers/__init__.py
    # Но для совместимости с текущей структурой setup() можно оставить
    r.include_router(router)
