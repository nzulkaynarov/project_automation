import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.handlers import router
from bot.database import init_db
from bot.scheduler import setup_scheduler

# Setup logging
logging.basicConfig(level=logging.INFO)

async def main():
    # Load environment variables
    load_dotenv()
    
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token or bot_token == "your_bot_token_here":
        logging.error("BOT_TOKEN is not set in .env file.")
        return

    # Initialize SQLite database
    init_db()

    # Initialize bot and dispatcher
    bot = Bot(token=bot_token)
    dp = Dispatcher()

    # Include routers
    dp.include_router(router)

    # Start background scheduler
    setup_scheduler(bot)

    # Start polling
    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
