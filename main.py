# main.py
"""
Main entry point for the Telegram bot.

- Initializes logging and configuration.
- Creates and configures the bot and dispatcher using aiogram library.
- Includes the main router with all handlers.
- Removes any existing webhook and starts polling for updates.
- Ensures proper cleanup and shutdown of the bot session.

Run this file directly to start the bot.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode  # For using HTML in messages
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from handlers import router  # Importing the router from handlers.py


async def main():
    if not BOT_TOKEN:
        logging.error("Токен бота не найден. Проверьте переменную окружения TELEGRAM_BOT_TOKEN.")
        raise sys.exit(1)

    bot = Bot(token=BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # Using HTML for hbold
              )

    # Creating a Dispatcher instance to handle updates
    dp = Dispatcher()

    # Connecting the router with our handlers
    dp.include_router(router)

    logging.basicConfig(level=logging.INFO)
    logging.info("Бот запускается...")

    # Remove any existing webhook to ensure the bot can receive updates
    await bot.delete_webhook(drop_pending_updates=True)
    # Start polling for updates
    try:
        await dp.start_polling(bot)
    # Shutting down the bot gracefully
    finally:
        await bot.session.close()
        logging.info("Бот остановлен.")


if __name__ == "__main__":
    asyncio.run(main())
