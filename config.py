import os

BOT_TOKEN        = os.getenv("BOT_TOKEN")
POSTGRES_HOST    = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT    = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB      = os.getenv("POSTGRES_DB", "postdb")
POSTGRES_USER    = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mysecretpassword")

DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
