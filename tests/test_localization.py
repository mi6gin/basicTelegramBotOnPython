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


@pytest.mark.asyncio
async def test_all_code_keys_exist_in_locales():
    """
    Сканирует исходный код проекта на наличие вызовов i18n.get('key')
    и проверяет, что каждый найденный ключ присутствует во всех локалях.
    Предотвращает опечатки и синтаксические ошибки Fluent.
    """
    import os
    import re
    
    key_pattern = re.compile(r'i18n\.get\(\s*["\']([^"\']+)["\']')
    keys_in_code = set()
    
    # Обходим файлы проекта, исключая виртуальное окружение, тесты и миграции
    for root, _, files in os.walk("."):
        if any(ignored in root for ignored in (".venv", ".git", "tests", "alembic")):
            continue
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for match in key_pattern.finditer(content):
                        keys_in_code.add(match.group(1))
                        
    core = FluentRuntimeCore(path="locales")
    await core.startup()
    
    for locale in ("ru", "en"):
        translator = core.get_translator(locale)
        translator_keys = set(translator._messages.keys())
        
        for key in keys_in_code:
            assert key in translator_keys, (
                f"Ключ '{key}', вызываемый в коде, отсутствует в файле локализации {locale}/messages.ftl! "
                f"Возможно, допущена опечатка или в файле локализации есть синтаксическая ошибка."
            )

