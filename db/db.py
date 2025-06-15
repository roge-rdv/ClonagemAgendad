import sqlite3

def connect():
    return sqlite3.connect("clonagem.db")

def create_tables():
    conn = connect()
    c = conn.cursor()
    
    # Cria tabela posts com TODAS as colunas necessárias
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id_post TEXT PRIMARY KEY,
            media_type TEXT,
            media_file_id TEXT,
            caption TEXT,
            timestamp DATETIME,
            media_group_id TEXT,
            canal_fonte INTEGER,
            nicho TEXT
        )
    """)
    
    # Verifica se as colunas novas existem, se não existir, ADICIONA! 🔥
    try:
        c.execute("ALTER TABLE posts ADD COLUMN canal_fonte INTEGER")
        print("✅ Coluna canal_fonte adicionada!")
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    try:
        c.execute("ALTER TABLE posts ADD COLUMN nicho TEXT")
        print("✅ Coluna nicho adicionada!")
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS envios (
            id_envio INTEGER PRIMARY KEY AUTOINCREMENT,
            id_post TEXT,
            canal_destino INTEGER,
            data_envio DATETIME,
            media_group_id TEXT,
            message_id INTEGER,
            deletado BOOLEAN DEFAULT 0,
            nicho TEXT,
            FOREIGN KEY(id_post) REFERENCES posts(id_post)
        )
    """)
    
    # Verifica se as colunas novas existem na tabela envios
    try:
        c.execute("ALTER TABLE envios ADD COLUMN message_id INTEGER")
        print("✅ Coluna message_id adicionada!")
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    try:
        c.execute("ALTER TABLE envios ADD COLUMN deletado BOOLEAN DEFAULT 0")
        print("✅ Coluna deletado adicionada!")
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    try:
        c.execute("ALTER TABLE envios ADD COLUMN nicho TEXT")
        print("✅ Coluna nicho adicionada na tabela envios!")
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    # Tabela pra rastrear mensagens enviadas (pra DELETAR depois! 😈)
    c.execute("""
        CREATE TABLE IF NOT EXISTS mensagens_enviadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            canal_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            tipo_conteudo TEXT,
            nicho TEXT,
            data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
            deletado BOOLEAN DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()
    print("🔥 Todas as tabelas e colunas estão atualizadas!")
