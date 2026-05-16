from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.parser import fetch_products
from bot.database import get_all_product_ids, add_product, get_all_users
import logging
from aiogram import Bot

async def check_for_new_products(bot: Bot):
    logging.info("Checking for new products on dry-fruits.uz...")
    products = await fetch_products()
    
    if not products:
        return
        
    existing_ids = set(get_all_product_ids())
    
    new_products = []
    for p in products:
        if p['id'] not in existing_ids:
            new_products.append(p)
            add_product(p)
            
    if new_products:
        logging.info(f"Found {len(new_products)} new products!")
        users = get_all_users()
        for p in new_products:
            text = f"🚨 **Новый товар на сайте!**\n\n"
            text += f"📦 **Название:** {p['title']}\n"
            if p['description']:
                text += f"ℹ️ **Описание:** {p['description']}\n"
            text += f"\n🔗 [Перейти на сайт](https://dry-fruits.uz)"
            
            for user_id in users:
                try:
                    if p['image']:
                        await bot.send_photo(chat_id=user_id, photo=p['image'], caption=text, parse_mode="Markdown")
                    else:
                        await bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
                except Exception as e:
                    logging.error(f"Failed to send message to {user_id}: {e}")

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    # Проверять сайт каждые 10 минут
    scheduler.add_job(check_for_new_products, "interval", minutes=10, args=[bot])
    scheduler.start()
    return scheduler
