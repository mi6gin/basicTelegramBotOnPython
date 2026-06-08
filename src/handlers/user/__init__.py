from aiogram import Router
from . import start

router = Router()

# Регистрируем хендлеры в роутер модуля
start.setup(router)
