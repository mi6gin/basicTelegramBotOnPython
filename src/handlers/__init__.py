from aiogram import Router
from .user import router as user_router
from .error import setup as setup_errors

def get_handlers_router() -> Router:
    router = Router()
    
    # Подключаем роутеры модулей
    router.include_router(user_router)
    
    # Настройка специфичных вещей, например, ошибок
    setup_errors(router)
    
    return router
