# Шаблон для телеграм-бота на Aiogram 3.x

Базовый модульный шаблон для создания телеграм-ботов. Подготовлен для масштабирования и работы с асинхронной базой данных.

## Стек технологий
*   **Aiogram 3.x**
*   **SQLAlchemy 2.0 (Async)** + **aiosqlite**
*   **Logging** (с ротацией файлов)

## Настройка и запуск

1.  **Клонирование и установка:**
    ```bash
    git clone https://github.com/mi6gin/basicTelegramBotOnPython.git
    cd basicTelegramBotOnPython
    python -m venv venv
    # Активируйте venv и установите зависимости:
    pip install -r requirements.txt
    ```

2.  **Конфигурация:**
    Создайте файл `.env` в корне и укажите:
    ```env
    BOT_TOKEN="ваш_токен"
    ADMIN_ID="id1,id2"
    ```

3.  **Запуск:** `python main.py`

## Структура проекта
*   `src/app.py` — Точка сборки (middlewares, routers, DB init).
*   `src/core/` — Модели БД (`models.py`) и логика подключений (`database.py`).
*   `src/handlers/` — Модульное разделение обработчиков.
*   `src/middlewares/` — Внедрение сессий БД и логирование.
*   `src/utils/` — Вспомогательный код.

---
*Минималистичный boilerplate для разработчиков.*
