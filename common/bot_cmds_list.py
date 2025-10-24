from aiogram.types import BotCommand
from aiogram import types
from config import MANAGER_IDS
from loader import bot


public = [
    BotCommand(command="start", description="Начать"),
    BotCommand(command="contact_manager", description="Связаться с менеджером"),
]

manager = [
    BotCommand(command="start", description="Начать"),
    BotCommand(command="admin", description="Для админов"),
    BotCommand(command="my_status", description="Мой статус онлайн и с кем")
]


async def set_bot_commands():
    # Общие команды для всех пользователей
    await bot.set_my_commands(public, scope=types.BotCommandScopeAllPrivateChats())

    # Персональные команды для админов
    for manager_id in MANAGER_IDS:
        await bot.set_my_commands(manager, scope=types.BotCommandScopeChat(chat_id=manager_id))