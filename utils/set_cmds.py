from loader import bot
from aiogram.types import BotCommand


async def set_commands():
    return await bot.set_my_commands(
        [
            BotCommand(command='start', description='Начало ↩️'),
            BotCommand(command='profile', description='Профиль 🏡')
        ]
    )