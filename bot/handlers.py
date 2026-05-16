from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from bot.database import add_user, get_products, get_products_count, search_products, get_search_count
from bot.keyboards import get_main_menu, get_pagination_keyboard

router = Router()

class SearchState(StatesGroup):
    waiting_for_query = State()
    search_query = State() # храним поисковой запрос пользователя

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handler for the /start command"""
    await state.clear()
    add_user(message.chat.id)
    
    await message.answer(
        "👋 Привет! Я бот для мониторинга сайта *dry-fruits.uz*.\n\n"
        "Я успешно запомнил ваш чат. Теперь каждые 10 минут я буду проверять сайт на наличие новых товаров "
        "и присылать вам уведомления!\n\n"
        "Воспользуйтесь меню ниже, чтобы просмотреть каталог или найти нужный товар.",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "📦 Все товары")
async def show_all_products(message: Message, state: FSMContext):
    await state.clear()
    count = get_products_count()
    if count == 0:
        await message.answer("Товаров пока нет в базе. Подождите первого обновления с сайта.")
        return
        
    products = get_products(limit=1, offset=0)
    if products:
        p = products[0]
        text = f"📦 **{p['title']}**\n\n"
        if p['description']:
            text += f"ℹ️ {p['description']}\n"
        text += f"\nТовар 1 из {count}"
        
        kb = get_pagination_keyboard(0, count, is_search=0)
        
        if p['image']:
            await message.answer_photo(photo=p['image'], caption=text, parse_mode="Markdown", reply_markup=kb)
        else:
            await message.answer(text, parse_mode="Markdown", reply_markup=kb)

@router.message(F.text == "🔍 Поиск товара")
async def start_search(message: Message, state: FSMContext):
    await message.answer("Введите название товара (например, 'дыня' или 'инжир'):")
    await state.set_state(SearchState.waiting_for_query)

@router.message(SearchState.waiting_for_query, F.text)
async def process_search(message: Message, state: FSMContext):
    query = message.text
    count = get_search_count(query)
    
    if count == 0:
        await message.answer(f"По запросу '{query}' ничего не найдено 😔\nПопробуйте другой запрос или посмотрите 'Все товары'.")
        await state.clear()
        return
        
    await state.update_data(search_query=query)
    await state.set_state(SearchState.search_query) # Переводим в состояние хранения запроса
    
    products = search_products(query, limit=1, offset=0)
    if products:
        p = products[0]
        text = f"🔍 **Результаты поиска:** '{query}'\n\n"
        text += f"📦 **{p['title']}**\n\n"
        if p['description']:
            text += f"ℹ️ {p['description']}\n"
        text += f"\nРезультат 1 из {count}"
        
        kb = get_pagination_keyboard(0, count, is_search=1)
        
        if p['image']:
            await message.answer_photo(photo=p['image'], caption=text, parse_mode="Markdown", reply_markup=kb)
        else:
            await message.answer(text, parse_mode="Markdown", reply_markup=kb)

@router.callback_query(F.data.startswith("page_"))
async def process_pagination(callback: CallbackQuery, state: FSMContext):
    _, is_search_str, offset_str = callback.data.split("_")
    is_search = int(is_search_str)
    offset = int(offset_str)
    
    if is_search == 1:
        data = await state.get_data()
        query = data.get("search_query", "")
        count = get_search_count(query)
        products = search_products(query, limit=1, offset=offset)
        prefix = f"🔍 **Результаты поиска:** '{query}'\n\n"
    else:
        count = get_products_count()
        products = get_products(limit=1, offset=offset)
        prefix = ""
        
    if not products:
        await callback.answer("Ошибка при загрузке товара.", show_alert=True)
        return
        
    p = products[0]
    text = prefix + f"📦 **{p['title']}**\n\n"
    if p['description']:
        text += f"ℹ️ {p['description']}\n"
    text += f"\nТовар {offset + 1} из {count}"
    
    kb = get_pagination_keyboard(offset, count, is_search=is_search)
    
    if p['image']:
        try:
            await callback.message.delete()
            await callback.message.answer_photo(photo=p['image'], caption=text, parse_mode="Markdown", reply_markup=kb)
        except:
            pass
    else:
        try:
            await callback.message.delete()
            await callback.message.answer(text, parse_mode="Markdown", reply_markup=kb)
        except:
            pass
            
    await callback.answer()
