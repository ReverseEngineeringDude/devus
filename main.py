import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import config
from handlers import common, music

# ... (other imports)

async def main() -> None:
    """
    Initializes and starts the bot.
    """
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Initialize Dispatcher
    dp = Dispatcher()

    # Include routers
    dp.include_router(common.router)
    dp.include_router(music.router)

    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    # The user is using a Linux OS, so the default event loop policy is sufficient
    # and nest_asyncio is not strictly required for this script to run, but it's
    # included in requirements.txt for environments where it might be needed.
    asyncio.run(main())
