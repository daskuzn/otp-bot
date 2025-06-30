# ---------- base image ----------
FROM python:3.13.3-slim AS runtime

# ––– системные библиотеки (для asyncpg) –––
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# ––– создаём пользователя без root-прав –––
RUN useradd -m bot
USER bot
WORKDIR /app

# ––– устанавливаем зависимости слоем (кеш) –––
COPY --chown=bot:bot requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt  # :contentReference[oaicite:1]{index=1}

# ––– копируем исходники –––
COPY --chown=bot:bot . .

# ––– важные переменные окружения –––
ENV PYTHONUNBUFFERED=1 \
    TZ=UTC

CMD ["python", "app.py"]
