from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='start chat with bot'
        ),
        BotCommand(
            command='exchange_prices',
            description='Currency exchange prices'
        ),
        BotCommand(
            command='cryptocurrency_info',
            description='Cryptocurrency info'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
