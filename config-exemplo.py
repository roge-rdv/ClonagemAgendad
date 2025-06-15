# ⚙️ CONFIGURAÇÃO DO BOT MULTI-NICHO
# 
# 📋 INSTRUÇÕES:
# 1. Copie este arquivo para config.py
# 2. Configure seu token do bot
# 3. Ajuste os IDs dos canais se necessário
# 4. NÃO COMMITE o config.py no Git!

# 🤖 TOKEN DO BOT
# Obtenha em: https://t.me/botfather
TELEGRAM_BOT_TOKEN = "SEU_TOKEN_AQUI"

# 🎯 MAPEAMENTO ORGANIZADO POR NICHO
# Cada nicho tem seu canal fonte e destino específico
CANAL_MAPPINGS = {
    'novin': {
        'fonte': -1002557461071,      # Canal de onde PEGA o conteúdo
        'destino': -1002574788580,    # Canal onde POSTA o conteúdo
        'caption_file': 'novin'       # Arquivo de legendas (captions/novin.py)
    },
    'leaks': {
        'fonte': -1002515987008,
        'destino': -1002651133010,
        'caption_file': 'leaks'       # Arquivo de legendas (captions/leaks.py)
    },
    'latinas': {
        'fonte': -1002783680178,
        'destino': -1002707898874,
        'caption_file': 'latinas'     # Arquivo de legendas (captions/latinas.py)
    },
    'coroas': {
        'fonte': -1002786777796,
        'destino': -1002765829939,
        'caption_file': 'coroas'      # Arquivo de legendas (captions/coroas.py)
    },
    'ourovip': {
        'fonte': -1002769718349,
        'destino': -1002870159887,
        'caption_file': 'gold'        # Arquivo de legendas (captions/gold.py)
    },
    'backdoor': {
        'fonte': -1002870192830,
        'destino': -1002759274414,
        'caption_file': 'backdoor'    # Arquivo de legendas (captions/backdoor.py)
    }
}

# 📋 LISTAS AUTOMÁTICAS (NÃO MEXER)
# Geradas automaticamente a partir do mapeamento acima
CANAIS_FONTE = [mapping['fonte'] for mapping in CANAL_MAPPINGS.values()]
CANAIS_DESTINO = [mapping['destino'] for mapping in CANAL_MAPPINGS.values()]

# ⚙️ CONFIGURAÇÕES LEGADAS (COMPATIBILIDADE)
# Mantidas para funcionar com código antigo
CANAL_FONTE_ID = CANAIS_FONTE[0] if CANAIS_FONTE else -1002758088813
SCHEDULE_HOURS = 4  # Usado pelo scheduler antigo

# 🔧 FUNÇÕES AUXILIARES (NÃO MEXER)

def get_nicho_by_fonte(canal_fonte_id):
    """Retorna o nicho baseado no canal fonte."""
    for nicho, config in CANAL_MAPPINGS.items():
        if config['fonte'] == canal_fonte_id:
            return nicho
    return None

def get_destino_by_fonte(canal_fonte_id):
    """Retorna canal destino baseado no canal fonte."""
    for nicho, config in CANAL_MAPPINGS.items():
        if config['fonte'] == canal_fonte_id:
            return config['destino']
    return None

def get_caption_file_by_fonte(canal_fonte_id):
    """Retorna arquivo de caption baseado no canal fonte."""
    for nicho, config in CANAL_MAPPINGS.items():
        if config['fonte'] == canal_fonte_id:
            return config['caption_file']
    return 'pt_br'  # fallback padrão

# 📝 COMO OBTER OS IDs DOS CANAIS:
# 
# 1. Adicione @userinfobot no seu canal
# 2. Encaminhe uma mensagem do canal para o bot
# 3. O bot retornará o ID (ex: -1002574788580)
# 
# ATENÇÃO: IDs de canais sempre começam com -100 !

# 🤖 COMO OBTER O TOKEN DO BOT:
# 
# 1. Fale com @BotFather no Telegram
# 2. Use o comando /newbot
# 3. Escolha um nome e username para seu bot
# 4. Copie o token que ele fornecer
# 5. Cole aqui no TELEGRAM_BOT_TOKEN

# ⚠️ IMPORTANTE:
# 
# - O bot precisa ser ADMINISTRADOR nos canais fonte (para ler mensagens)
# - O bot precisa ser ADMINISTRADOR nos canais destino (para enviar mensagens)
# - Nunca compartilhe seu token! Mantenha em segredo!
# - Use este arquivo apenas como exemplo, trabalhe sempre com config.py
