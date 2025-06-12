Aqui está um esqueleto inicial para seu projeto de bot de clonagem agendada para Telegram, usando Python, SQLite e as bibliotecas sugeridas.

````plaintext
ClonagemAgendada/
│
├── main.py
├── requirements.txt
├── config.py
│
├── db/
│   └── db.py
│
├── bot/
│   ├── telegram_bot.py
│   ├── scheduler.py
│   └── caption_generator.py
│
└── utils/
    └── helpers.py
````

---

### **1. requirements.txt**

````plaintext
python-telegram-bot==20.8
APScheduler==3.10.4
sqlite3
requests
````

---

### **2. config.py**

````python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
CANAL_FONTE_ID = -1001234567890
CANAIS_DESTINO = [
    -1001111111111,
    -1002222222222,
    -1003333333333,
    -1004444444444,
    -1005555555555,
    -1006666666666,
]
SCHEDULE_HOURS = 2  # Intervalo em horas
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
````

---

### **3. db/db.py**

````python
import sqlite3

def connect():
    return sqlite3.connect("clonagem.db")

def create_tables():
    conn = connect()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id_post TEXT PRIMARY KEY,
            media_type TEXT,
            media_file_id TEXT,
            caption TEXT,
            timestamp DATETIME
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS envios (
            id_envio INTEGER PRIMARY KEY AUTOINCREMENT,
            id_post TEXT,
            canal_destino INTEGER,
            data_envio DATETIME,
            FOREIGN KEY(id_post) REFERENCES posts(id_post)
        )
    """)
    conn.commit()
    conn.close()
````

---

### **4. bot/telegram_bot.py**

````python
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from db.db import connect
from config import TELEGRAM_BOT_TOKEN, CANAL_FONTE_ID

async def handle_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Lógica para salvar novo post no banco
    pass

def start_bot():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Chat(CANAL_FONTE_ID), handle_new_post))
    app.run_polling()
````

---

### **5. bot/scheduler.py**

````python
from apscheduler.schedulers.background import BackgroundScheduler
from bot.telegram_bot import send_scheduled_posts

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_scheduled_posts, 'interval', hours=2)
    scheduler.start()
````

---

### **6. bot/caption_generator.py**

````python
def generate_caption(media_info):
    # Integração com Gemini API para gerar legenda personalizada
    return "Legenda gerada"
````

---

### **7. utils/helpers.py**

````python
def log(msg):
    print(f"[LOG] {msg}")
````

---

### **8. main.py**

````python
from db.db import create_tables
from bot.telegram_bot import start_bot
from bot.scheduler.py import start_scheduler

if __name__ == "__main__":
    create_tables()
    start_scheduler()
    start_bot()
````

---

Esse esqueleto cobre a estrutura básica. Você pode expandir cada módulo conforme a lógica do seu projeto evoluir. Se quiser exemplos de implementação para cada função, só pedir!