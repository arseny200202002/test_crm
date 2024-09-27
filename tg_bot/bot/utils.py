from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from asgiref.sync import async_to_sync

from .config import API_TOKEN


async def async_send_message(chat_id: int, message: str) -> None:
    async with Bot(API_TOKEN) as bot:
        await bot.send_message(chat_id, message, parse_mode=ParseMode.HTML)


send_message = async_to_sync(async_send_message)
