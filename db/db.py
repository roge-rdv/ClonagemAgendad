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
            timestamp DATETIME,
            media_group_id TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS envios (
            id_envio INTEGER PRIMARY KEY AUTOINCREMENT,
            id_post TEXT,
            canal_destino INTEGER,
            data_envio DATETIME,
            media_group_id TEXT,
            FOREIGN KEY(id_post) REFERENCES posts(id_post)
        )
    """)
    conn.commit()
    conn.close()
