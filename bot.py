import asyncio
from aiogram import types
from config import ALLOWED_UPDATES

# Импортируем роутеры
from data.chat_storage_json import update_chats_cache
from handlers.start import start_router
from handlers.group_selection import group_router
from handlers.pricing import pricing_router
from handlers.contact_manager import contact_router
from handlers.chat_handler import chat_router
from handlers.chat_flow import flow_router
from handlers.confirmations import confirmations_router
from handlers.file import file_router
from handlers.back_to_handlers import back_to_router

from handlers.fallback_handler import fallback_router

from common.bot_cmds_list import set_bot_commands

from loader import bot, dp  # вот теперь отсюда

async def main():

    update_chats_cache()
    
    # Регистрируем роутеры
    dp.include_router(start_router)
    dp.include_router(group_router)
    dp.include_router(pricing_router)
    dp.include_router(contact_router)
    dp.include_router(chat_router)
    dp.include_router(file_router)
    dp.include_router(flow_router)
    dp.include_router(confirmations_router)
    dp.include_router(back_to_router)

    dp.include_router(fallback_router)

    print("\nБот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await set_bot_commands()
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == "__main__":
    asyncio.run(main())