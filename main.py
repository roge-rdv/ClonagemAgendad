from db.db import create_tables
from bot.telegram_bot import start_bot
from bot.scheduler import start_scheduler

if __name__ == "__main__":
    create_tables()
    start_scheduler()
    start_bot()
