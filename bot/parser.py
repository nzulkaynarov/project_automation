import aiohttp
from bs4 import BeautifulSoup
import logging

URL = "https://dry-fruits.uz"

async def fetch_products():
    """Fetches the website and returns a list of dictionaries with product data."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as response:
                response.raise_for_status()
                html = await response.text()
    except Exception as e:
        logging.error(f"Error fetching {URL}: {e}")
        return []

    soup = BeautifulSoup(html, 'html.parser')
    products = []
    
    # В Tilda товары часто лежат в блоках с классом t994__item-wrapper
    items = soup.find_all('div', class_='t994__item-wrapper')
    
    for item in items:
        title_tag = item.find('div', class_='t994__title')
        descr_tag = item.find('div', class_='t994__descr')
        img_tag = item.find('div', class_='t994__bgimg')
        
        if not title_tag:
            continue
            
        title = title_tag.get_text(strip=True)
        descr = descr_tag.get_text(strip=True) if descr_tag else ""
        
        # Извлекаем URL картинки
        img_url = ""
        if img_tag:
            if img_tag.has_attr('data-original'):
                img_url = img_tag['data-original']
            elif img_tag.has_attr('style'):
                style = img_tag['style']
                if "url(" in style:
                    start = style.find("url('") + 5
                    end = style.find("')", start)
                    if start != 4 and end != -1:
                        img_url = style[start:end]
        
        products.append({
            'id': title, # Используем название как уникальный ID
            'title': title,
            'description': descr,
            'image': img_url
        })
        
    return products
