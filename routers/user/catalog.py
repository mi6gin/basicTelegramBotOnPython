from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext
from filters.is_private import IsPrivate

router = Router(name="user_catalog")

# Моковые данные каталога с поддержкой ключей локализации
CATALOG_ITEMS = {
    "theme_classic": {
        "title_key": "catalog-classic-title",
        "desc_key": "catalog-classic-desc",
        "rating": "⭐️ 4.9/5",
    },
    "theme_sakura": {
        "title_key": "catalog-sakura-title",
        "desc_key": "catalog-sakura-desc",
        "rating": "⭐️ 5.0/5",
    },
    "theme_cyberpunk": {
        "title_key": "catalog-cyberpunk-title",
        "desc_key": "catalog-cyberpunk-desc",
        "rating": "⭐️ 4.8/5",
    }
}


@router.callback_query(F.data == "user_catalog", IsPrivate())
async def show_catalog(callback: CallbackQuery, i18n: I18nContext):
    """
    Показывает список доступных товаров/тем в каталоге.
    """
    await callback.answer()
    
    builder = InlineKeyboardBuilder()
    for item_id, item_data in CATALOG_ITEMS.items():
        builder.button(text=i18n.get(item_data["title_key"]), callback_data=f"catalog_view_{item_id}")
        
    builder.button(text=i18n.get("btn-back-to-menu"), callback_data="back_to_menu")
    builder.adjust(1)
    
    await callback.message.edit_text(
        i18n.get("catalog-title"),
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.startswith("catalog_view_"), IsPrivate())
async def show_catalog_item(callback: CallbackQuery, i18n: I18nContext):
    """
    Показывает карточку конкретного товара/темы с детальным описанием.
    """
    await callback.answer()
    
    item_id = callback.data.replace("catalog_view_", "")
    item_data = CATALOG_ITEMS.get(item_id)
    
    if not item_data:
        await callback.message.answer(i18n.get("err-item-not-found"))
        return
        
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.get("btn-back-to-catalog"), callback_data="user_catalog")
    builder.adjust(1)
    
    # Получаем локализованные значения
    title = i18n.get(item_data["title_key"])
    description = i18n.get(item_data["desc_key"])
    
    text = i18n.get(
        "catalog-item-detail",
        title=title,
        description=description,
        rating=item_data["rating"]
    )
    
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup()
    )
