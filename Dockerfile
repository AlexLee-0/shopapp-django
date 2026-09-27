# syntax=docker/dockerfile:1

# ---------- Этап 1: сборка зависимостей ----------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.0.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

# Копируем только манифесты — чтобы слой кэшировался
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости в СИСТЕМНЫЙ Python (venv отключён)
RUN poetry install --no-root --only main --no-ansi


# ---------- Этап 2: финальный образ ----------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Копируем установленные пакеты из builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем код проекта
COPY . .

# Создаём папки для медиа и статики
RUN mkdir -p /app/uploads /app/staticfiles

EXPOSE 8000

# Команда запуска через gunicorn
CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]