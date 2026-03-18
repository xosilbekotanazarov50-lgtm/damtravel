from aiogram import Bot
from .config import BOT_TOKEN, ADMIN_IDS, CHANNEL_ID
from . import language

bot = Bot(token=BOT_TOKEN)

__all__ = ["BOT_TOKEN", "ADMIN_IDS", "CHANNEL_ID", "bot", "language"]
