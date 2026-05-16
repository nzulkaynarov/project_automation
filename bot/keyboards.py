from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu():
    """Главное меню бота"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📦 Все товары"),
                KeyboardButton(text="🔍 Поиск товара")
            ]
        ],
        resize_keyboard=True
    )
    return kb

def get_pagination_keyboard(current_offset: int, total_count: int, is_search: int = 0):
    """Клавиатура для перелистывания товаров"""
    builder = InlineKeyboardBuilder()
    
    # Кнопка 'Назад'
    if current_offset > 0:
        builder.button(text="⬅️ Назад", callback_data=f"page_{is_search}_{current_offset - 1}")
        
    # Кнопка 'Вперед'
    if current_offset < total_count - 1:
        builder.button(text="Вперед ➡️", callback_data=f"page_{is_search}_{current_offset + 1}")
        
    builder.adjust(2) # Кнопки в один ряд
    return builder.as_markup()
