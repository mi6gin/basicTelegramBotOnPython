from aiogram import Router

from . import start

def setup(r: Router):
    start.setup(r)