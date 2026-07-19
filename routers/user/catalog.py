from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.is_private import IsPrivate

router = Router(name="user_catalog")

# Моковые данные каталога
CATALOG_ITEMS = {
    "theme_classic": {
        "title": "🌸 Нихао-тян Классическая",
        "description": "Стандартная тема Нихао-тян. Любит зеленый чай, вежлива и всегда готова помочь вам с кодом.",
        "rating": "⭐️ 4.9/5",
    },
    "theme_sakura": {
        "title": "💮 Нихао-тян Сакура",
        "description": "Весенняя нежная тема Нихао-тян. Окружена лепестками сакуры и вдохновляет на создание красивого софта.",
        "rating": "⭐️ 5.0/5",
    },
    "theme_cyberpunk": {
        "title": "⚡ Нихао-тян Киберпанк",
        "description": "Неоновая хакерская тема Нихао-тян. Пишет скрипты на ассемблере, носит киберимпланты и слушает синтвейв.",
        "rating": "⭐️ 4.8/5",
    }
}


@router.callback_query(F.data == "user_catalog", IsPrivate())
async def show_catalog(callback: CallbackQuery):
    """
    Показывает список доступных товаров/тем в каталоге.
    """
    await callback.answer()
    
    builder = InlineKeyboardBuilder()
    for item_id, item_data in CATALOG_ITEMS.items():
        builder.button(text=item_data["title"], callback_data=f"catalog_view_{item_id}")
        
    builder.button(text="🔙 Главное меню", callback_data="back_to_menu")
    builder.adjust(1)
    
    await callback.message.edit_text(
        "📂 **Каталог образов Нихао-тян**\n\n"
        "Выберите интересующий образ, чтобы узнать подробности:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.startswith("catalog_view_"), IsPrivate())
async def show_catalog_item(callback: CallbackQuery):
    """
    Показывает карточку конкретного товара/темы с детальным описанием.
    """
    await callback.answer()
    
    item_id = callback.data.split("_")[-1]
    item_data = CATALOG_ITEMS.get(f"theme_{item_id}")
    
    if not item_data:
        await callback.message.answer("К сожалению, образ не найден.")
        return
        
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад в каталог", callback_data="user_catalog")
    builder.adjust(1)
    
    text = (
        f"**{item_data['title']}**\n\n"
        f"📝 **Описание:** {item_data['description']}\n\n"
        f"📊 **Популярность:** {item_data['rating']}"
    )
    
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup()
    )
