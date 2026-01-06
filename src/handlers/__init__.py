from aiogram import Router

from . import on_startup, error

def setup(r: Router):
    error.setup(r)
    on_startup.setup(r)