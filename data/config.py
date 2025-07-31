from utils.postgres_db import DB
import os



BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
KEY_DOMAIN = os.getenv("KEY_DOMAIN")

DP_PORT = 5432
DB_USER="postgres"
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = "railway"

DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

db: DB = DB(
    DB_HOST, DB_PORT, DB_USER,
    DP_PASSWORD, DB_NAME
)

BAD_SYMBOLS = ['+', '(', '-', ')', ' '] # не трогать

SESSIONS_STORAGE = "sessions"
os.makedirs(SESSIONS_STORAGE, exist_ok=True)
