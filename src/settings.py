import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = list(map(int, os.getenv("ADMIN_ID", "").split(",")))