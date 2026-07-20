import pytest
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore


@pytest.mark.asyncio
async def test_localization_startup_and_completeness():
    """
    Интеграционный тест: проверяет запуск локализации, наличие обязательных языков
    и симметричность ключей перевода (чтобы в английском переводе не забыли ни один ключ из русского).
    """
    # 1. Загружаем локализацию по реальному пути проекта
    core = FluentRuntimeCore(path="locales")
    await core.startup()

    # 2. Проверяем, что языки загрузились
    assert "ru" in core.available_locales, "Русский язык ('ru') отсутствует в загруженных локалях."
    assert "en" in core.available_locales, "Английский язык ('en') отсутствует в загруженных локалях."

    # 3. Извлекаем переводчики для каждого языка
    ru_translator = core.get_translator("ru")
    en_translator = core.get_translator("en")

    # 4. Получаем все ключи сообщений
    ru_keys = set(ru_translator._messages.keys())
    en_keys = set(en_translator._messages.keys())

    assert len(ru_keys) > 0, "Файл локализации ru/messages.ftl пуст."
    assert len(en_keys) > 0, "Файл локализации en/messages.ftl пуст."

    # 5. Проверяем симметрию ключей (каждый ключ в ru должен быть в en, и наоборот)
    missing_in_en = ru_keys - en_keys
    missing_in_ru = en_keys - ru_keys

    assert not missing_in_en, f"Следующие ключи присутствуют в ru/messages.ftl, но пропущены в en/messages.ftl: {missing_in_en}"
    assert not missing_in_ru, f"Следующие ключи присутствуют в en/messages.ftl, но пропущены в ru/messages.ftl: {missing_in_ru}"


@pytest.mark.asyncio
async def test_localization_rendering():
    """
    Тест рендеринга сообщений: проверяет корректность отдачи текстов на разных языках и работу переменных.
    """
    core = FluentRuntimeCore(path="locales")
    await core.startup()

    # Проверка получения базовой кнопки
    btn_ru = core.get("btn-profile", "ru")
    btn_en = core.get("btn-profile", "en")
    assert btn_ru == "👤 Мой профиль"
    assert btn_en == "👤 My Profile"

    # Проверка интерполяции переменных ($name, $id, etc.)
    welcome_ru = core.get("welcome-text-start", "ru", name="Аня")
    welcome_en = core.get("welcome-text-start", "en", name="Anna")
    assert "Аня" in welcome_ru
    assert "Anna" in welcome_en
