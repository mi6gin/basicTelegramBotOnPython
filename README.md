# 🌸 Шаблон Telegram-бота «Нихао-тян» (Aiogram 3.x + SQLAlchemy 2.0 Async)

Высококачественный, профессионально структурированный и готовый к продакшну шаблон (boilerplate) для быстрой разработки масштабируемых Telegram-ботов на Python. 

Шаблон спроектирован по современным стандартам веб-разработки: с разделением ответственности, слоем репозиториев (Repository Pattern), автоматическим управлением сессиями БД через middlewares и готовым набором функций для обычных пользователей и администраторов.

---

## 🛠️ Стек технологий
* **Язык программирования:** Python 3.10+
* **Фреймворк Bot API:** [Aiogram 3.4.1](https://github.com/aiogram/aiogram) (современный асинхронный фреймворк)
* **ORM (Связующее ПО с БД):** [SQLAlchemy 2.0](https://github.com/sqlalchemy/sqlalchemy) (асинхронный декларативный стиль)
* **Драйвер базы данных:** [aiosqlite](https://github.com/nbraud/aiosqlite) (асинхронный драйвер SQLite; для PostgreSQL достаточно заменить строку подключения на `asyncpg`)
* **Конфигурация:** [Pydantic Settings 2.2.1](https://github.com/pydantic/pydantic-settings) (валидация типов и автоматическая загрузка из `.env` файлов)
* **Логирование:** Стандартный Python `logging` с автоматической ротацией файлов (`RotatingFileHandler` до 5 файлов по 5 МБ каждый)

---

## 🚀 Все фичи шаблона: Что под капотом и как это работает

### 1. Автоматический жизненный цикл сессии БД (`DbSessionMiddleware`)
Вам больше не нужно вручную открывать и закрывать сессии базы данных (`AsyncSessionLocal`) в каждом хендлере или городить конструкции `async with`.
* **Как это работает:** В файле `middlewares/db_session_mw.py` реализована прослойка, которая открывает транзакцию СУБД в начале обработки любого события от Telegram (Message, CallbackQuery) и автоматически закрывает её (с commit или rollback при ошибке) после завершения работы хендлера.
* **Использование в коде:** В любом хендлере или фильтре вы можете просто объявить аргумент `session: AsyncSession`, и aiogram сам подставит туда активную сессию:
  ```python
  @router.message()
  async def my_handler(message: Message, session: AsyncSession):
      # сессия уже открыта и готова к работе
      users = await UserRepository.get_all(session)
  ```

### 2. Авторегистрация и бесшовная проверка банов (`BanMiddleware`)
Каждый входящий пользователь автоматически обрабатывается до того, как его сообщение попадет в хендлер.
* **Авторегистрация:** Если пользователя еще нет в базе данных, мидлварь `middlewares/ban_mw.py` автоматически создает запись в таблице `users`, заполняя его Telegram ID, имя, фамилию и юзернейм.
* **Блокировки (Бан):** Если в базе данных у пользователя стоит флаг `is_banned = True`, мидлварь прерывает выполнение цепочки, отправляет пользователю уведомление о блокировке и не пускает его дальше.
* **Объект `db_user` в хендлерах:** Мидлварь автоматически помещает объект пользователя SQLAlchemy из БД в контекст данных. В хендлере вам достаточно указать аргумент `db_user: User`:
  ```python
  @router.message(Command("my_cmd"))
  async def cmd_my(message: Message, db_user: User):
      await message.answer(f"Привет, твоя роль в БД: {db_user.role}")
  ```

### 3. Защита от флуда (`ThrottlingMiddleware`)
Для защиты от спама и перегрузки сервера реализован Anti-flood фильтр в `middlewares/throttling_mw.py`.
* **Принцип работы:** Использует быстрый кэш в оперативной памяти с автоматической очисткой старых записей. Если пользователь отправляет сообщения чаще, чем задано в конфиге `THROTTLING_DELAY`, бот просто игнорирует его сообщения.

### 4. Двухуровневая защита административной зоны (`IsAdmin`)
Защита админ-панели реализована с помощью кастомного фильтра `filters/is_admin.py`.
* **Статический админ:** Проверяется соответствие ID списку `ADMIN_IDS` из `.env`.
* **Динамический админ:** Проверяется колонка `role == 'admin'` в базе данных.
* **Безопасность:** В файле `routers/admin/__init__.py` фильтр `IsAdmin()` повешен **на весь роутер целиком**. Это гарантирует, что ни один разработчик случайно не забудет защитить новый админский хендлер — защита работает на уровне всего пакета.

### 5. Полноценная панель администратора
Включает в себя готовые инструменты для администрирования:
* **Интерактивная статистика:** По нажатию кнопки СУБД рассчитывает общее число пользователей, количество заблокированных и число открытых тикетов в реальном времени.
* **Безопасный массовый вещатель (Рассылка):** Админ может отправить любое сообщение (текст, фото, видео, стикер, анимацию). Бот рассылает его всем пользователям из БД с помощью метода `copy_to` (сохраняющим все разметки и медиафайлы). Если пользователь заблокировал бота, операция не упадет с ошибкой, а бот просто зафиксирует это в счетчике ошибок доставки.
* **Инструмент блокировки:** Позволяет ввести Telegram ID пользователя и переключить его флаг бана (`is_banned`). Реализованы защитные проверки: нельзя заблокировать самого себя, и нельзя заблокировать другого администратора.

### 6. Умные цепочки состояний (FSM)
* **Onboarding при старте:** При отправке `/start` бот проверяет, заполнено ли БИО пользователя. Если нет — запускается FSM-сценарий принудительной первичной настройки (сбор имени и описания). Без этого пользователь не попадет в главное меню.
* **Техподдержка:** Пользователь заполняет тикет. Обращение сохраняется в таблице `tickets` с привязкой по внешнему ключу (`ForeignKey`) к пользователю.

---

## 📂 Подробная файловая структура
```
nihao-chan-bot/
│
├── bot.py                      # Точка входа. Создание объектов Bot, Dispatcher, регистрация middlewares и роутеров.
├── .env.example                # Шаблон файла конфигурации.
├── requirements.txt            # Зависимости Python проекта.
│
├── config/
│   └── settings.py             # Настройки Pydantic Settings (чтение .env, приведение типов).
│
├── database/                   # Работа с данными (SQLAlchemy 2.0 Async).
│   ├── engine.py               # Конфигурация СУБД, AsyncSessionLocal, автосоздание таблиц при запуске.
│   ├── models/
│   │   ├── user.py             # Определение таблицы пользователей (users).
│   │   └── ticket.py           # Определение таблицы тикетов поддержки (tickets).
│   └── repository/
│       ├── user_repo.py        # Запросы к пользователям (CRUD, бан, статистика).
│       └── ticket_repo.py      # Запросы к тикетам (создание, закрытие, статистика).
│
├── filters/                    # Кастомные фильтры aiogram.
│   ├── is_admin.py             # Проверка прав администратора (из config или БД).
│   └── is_private.py           # Проверка, что чат с ботом является личным (Private).
│
├── keyboards/                  # Кнопки и меню.
│   ├── inline/
│   │   ├── user_menu.py        # Главное меню пользователя.
│   │   ├── profile.py          # Меню управления профилем.
│   │   └── admin_panel.py      # Меню панели администратора.
│   └── reply/
│       └── cancel.py           # Кнопка "Отмена" для выхода из FSM-состояний.
│
├── middlewares/                # Прослойки обработки событий.
│   ├── db_session_mw.py        # Инжектирование сессии БД.
│   ├── ban_mw.py               # Проверка бана и авторегистрация (предоставляет db_user).
│   ├── throttling_mw.py        # Ограничение частоты сообщений (Anti-flood).
│   └── logging_mw.py           # Логирование текста и нажатий кнопок.
│
├── routers/                    # Слой хендлеров (маршрутизация).
│   ├── __init__.py             # Объединение всех роутеров бота.
│   ├── user/                   # Зона пользователя.
│   │   ├── __init__.py         # Сборщик роутеров юзера.
│   │   ├── start.py            # /start, /help, /about и onboarding FSM.
│   │   ├── profile.py          # Просмотр и редактирование профиля.
│   │   ├── catalog.py          # Пример вложенных меню (Каталог образов).
│   │   └── support.py          # Создание обращения в поддержку.
│   └── admin/                  # Зона администратора (защищена IsAdmin).
│       ├── __init__.py         # Сборщик роутеров админа.
│       ├── panel.py            # Точка входа в админку (/admin).
│       ├── users.py            # Блокировка/разблокировка пользователей по ID.
│       ├── mailing.py          # Создание массовой рассылки.
│       └── stats.py            # Отображение статистики из БД.
│
├── states/                     # Группы состояний FSM (Finite State Machine).
│   ├── registration.py         # Состояния onboarding-а.
│   ├── profile.py              # Состояния редактирования профиля.
│   └── support.py              # Состояния создания обращения.
│
└── utils/                      # Дополнительные инструменты.
    ├── logger.py               # Конфигурация логирования (консоль + файл с ротацией).
    └── validators.py           # Простые валидаторы ввода (длина, регулярные выражения).
```

---

## 🏁 Быстрый старт: Как запустить бота с нуля

### 1. Клонирование и установка зависимостей
```bash
git clone https://github.com/mi6gin/basicTelegramBotOnPython.git
cd basicTelegramBotOnPython

# Создаем виртуальное окружение
python -m venv venv

# Активируем виртуальное окружение
source venv/bin/activate  # Для macOS/Linux
venv\Scripts\activate     # Для Windows

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 2. Настройка конфигурационного файла
Создайте файл `.env` на основе примера:
```bash
cp .env.example .env
```
Откройте созданный файл `.env` в текстовом редакторе и настройте параметры:
* `BOT_TOKEN` — ваш токен бота от официального бота [@BotFather](https://t.me/BotFather).
* `ADMIN_IDS` — ваш численный Telegram ID (можно узнать у [@userinfobot](https://t.me/userinfobot)). Можно указать несколько через запятую: `12345,67890`.
* `DB_URL` — строка подключения. По умолчанию используется локальный SQLite файл `sqlite+aiosqlite:///nihao_chan.db`.
* `THROTTLING_DELAY` — задержка антифлуда в секундах (например, `0.8`).

> [!WARNING]
> **Меры безопасности проекта:** 
> Файл `.env` содержит реальные конфиденциальные данные (секретный токен Telegram-бота, пароли СУБД) и **ни в коем случае не должен добавляться в Git-репозиторий** (он автоматически скрыт в `.gitignore`).
> Файл шаблона `.env.example` предназначен только для демонстрации структуры настроек. Никогда не заполняйте `.env.example` вашими настоящими секретами и токенами перед отправкой коммитов в Git!


### 3. Первый запуск
```bash
python bot.py
```
*Что произойдет при первом запуске:*
1. Бот автоматически создаст файл базы данных `nihao_chan.db` в корне.
2. SQLAlchemy выполнит миграцию и создаст таблицы `users` и `tickets`.
3. Создастся директория `logs/`, и запишется первый лог в `logs/bot.log`.
4. Бот очистит накопившиеся за время отключения сообщения от пользователей (`drop_pending_updates`) и начнет опрашивать сервера Telegram.

---

## 🧑‍💻 Инструкция по разработке: Как расширять шаблон

### Как добавить новую таблицу в базу данных?
1. В папке `database/models/` создайте новый файл, например `item.py`:
   ```python
   from sqlalchemy import String, Integer
   from sqlalchemy.orm import Mapped, mapped_column
   from database.engine import Base

   class Item(Base):
       __tablename__ = "items"

       id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
       name: Mapped[str] = mapped_column(String(100))
       price: Mapped[int] = mapped_column(Integer)
   ```
2. Откройте [database/engine.py](file:///Users/mi6ruhgunn/PycharmProjects/basicTelegramBotOnPython/database/engine.py). В функции `init_db` импортируйте вашу новую модель, чтобы SQLAlchemy увидел её метаданные при старте:
   ```python
   # Внутри функции init_db():
   from database.models.item import Item
   ```

### Как написать новый метод для работы с БД (Репозиторий)?
1. В папке `database/repository/` создайте файл `item_repo.py`:
   ```python
   from sqlalchemy import select
   from sqlalchemy.ext.asyncio import AsyncSession
   from database.models.item import Item

   class ItemRepository:
       @staticmethod
       async def get_expensive_items(session: AsyncSession, min_price: int):
           query = select(Item).where(Item.price >= min_price)
           result = await session.execute(query)
           return result.scalars().all()
   ```

### Как добавить новый хендлер (обработчик сообщений)?
1. Создайте файл хендлеров, например в `routers/user/store.py`:
   ```python
   from aiogram import Router, F
   from aiogram.types import Message
   from sqlalchemy.ext.asyncio import AsyncSession
   from database.repository.item_repo import ItemRepository

   router = Router(name="user_store")

   @router.message(F.text == "🛍️ Магазин")
   async def show_store(message: Message, session: AsyncSession):
       items = await ItemRepository.get_expensive_items(session, min_price=100)
       await message.answer(f"В магазине {len(items)} дорогих товаров!")
   ```
2. Подключите ваш новый роутер в сборщик роутеров пользователя [routers/user/\_\_init\_\_.py](file:///Users/mi6ruhgunn/PycharmProjects/basicTelegramBotOnPython/routers/user/__init__.py):
   ```python
   from .store import router as store_router
   
   # Внутри router.include_routers:
   router.include_routers(
       ...,
       store_router
   )
   ```

### Как добавить новую цепочку FSM?
1. Опишите состояния в новой группе состояний в `states/`:
   ```python
   from aiogram.fsm.state import StatesGroup, State

   class StoreOrderStates(StatesGroup):
       waiting_for_address = State()
   ```
2. В хендлере установите состояние:
   ```python
   await state.set_state(StoreOrderStates.waiting_for_address)
   ```
3. Ловите ввод пользователя с фильтром по состоянию:
   ```python
   @router.message(StoreOrderStates.waiting_for_address)
   async def process_address(message: Message, state: FSMContext):
       address = message.text
       await state.update_data(address=address)
       await state.clear()
       await message.answer("Заказ оформлен!")
   ```
