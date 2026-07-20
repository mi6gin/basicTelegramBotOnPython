# Этап 1: Сборка зависимостей
FROM python:3.9-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установка необходимых пакетов для компиляции некоторых Python-библиотек (если потребуется)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Устанавливаем зависимости в локальную директорию пользователя
RUN pip install --no-cache-dir --user -r requirements.txt


# Этап 2: Финальный легковесный образ для рантайма
FROM python:3.9-slim as runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Добавляем путь к локальным бинарникам пользователя в PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Создаем безопасного non-root пользователя
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Копируем установленные библиотеки из этапа сборки
COPY --from=builder /root/.local /home/appuser/.local

# Копируем исходный код проекта с назначением прав нашему пользователю
COPY --chown=appuser:appuser . .

# Создаем папки для хранения БД и логов, чтобы при монтировании томов не возникало проблем с правами доступа
RUN mkdir -p data logs

# Запуск миграций Alembic перед стартом основного процесса бота
CMD ["/bin/sh", "-c", "alembic upgrade head && python bot.py"]
