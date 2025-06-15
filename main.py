from db.db import create_tables
from bot.telegram_bot import start_bot

if __name__ == "__main__":
    print("🔥 Iniciando Bot Multi-Nicho...")
    create_tables()
    print("✅ Tabelas criadas/verificadas")
    start_bot()
