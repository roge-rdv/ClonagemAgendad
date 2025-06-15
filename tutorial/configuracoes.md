# ⚙️ Configurações Avançadas do Bot

## 🔧 config.py - Configuração Principal

### Token do Bot
```python
TELEGRAM_BOT_TOKEN = "1234567890:ABC-DEFghijklmnopqrstuvwxyz"
```
**Como obter:**
1. Fale com [@BotFather](https://t.me/botfather)
2. `/newbot`
3. Escolha nome e username
4. Copie o token

### Mapeamento de Canais
```python
CANAL_MAPPINGS = {
    'novin': {
        'fonte': -1002557461071,      # Canal de onde pega
        'destino': -1002574788580,    # Canal onde posta
        'caption_file': 'novin'       # Arquivo de legendas
    },
    # ... outros nichos
}
```

**Como obter IDs dos canais:**
1. Adicione [@userinfobot](https://t.me/userinfobot) no canal
2. Encaminhe uma mensagem do canal para o bot
3. O bot retornará o ID (ex: -1002574788580)

## 🎯 Configurações por Nicho

### Arquivos de Legendas
Cada nicho usa um arquivo específico:

- **novin** → `captions/novin.py` → `ARSENAL_NOVINHAS`
- **leaks** → `captions/leaks.py` → `ARSENAL_LEAKS`
- **latinas** → `captions/latinas.py` → `ARSENAL_LATINAS`
- **coroas** → `captions/coroas.py` → `ARSENAL_COROAS`
- **ourovip** → `captions/gold.py` → `ARSENAL_GOLD`
- **backdoor** → `captions/backdoor.py` → `ARSENAL_BACKDOOR`

### Personalizando Legendas
```python
# captions/novin.py
ARSENAL_NOVINHAS = [
    "🔥 Sua legenda personalizada aqui! 👉 @seubotcta",
    "😈 Outra legenda provocativa! 👉 @seubotcta",
    # ... adicione quantas quiser
]
```

## ⏰ Configurações de Horários

### Scheduler Principal
```python
# bot/scheduler.py
scheduler.add_job(
    send_scheduled_posts,
    trigger=IntervalTrigger(seconds=30),  # Intervalo de verificação
    args=[app],
    id='send_posts',
    replace_existing=True
)
```

**Opções:**
- `seconds=30` - A cada 30 segundos (padrão)
- `minutes=5` - A cada 5 minutos
- `hours=1` - A cada 1 hora

### Horários por Canal
Use comandos do bot:
```bash
# Configuração agressiva (8 posts/dia)
/horariosrapidos agressivo

# Configuração normal (4 posts/dia)
/horariosrapidos normal

# Configuração conservadora (2 posts/dia)
/horariosrapidos conservador

# Sem restrições (posta sempre)
/horariosrapidos livre
```

## 🚦 Rate Limiting

### Configurações Básicas
```python
# bot/rate_limiter.py
class RateLimiter:
    def __init__(self):
        self.max_messages_per_minute = 20   # Máximo por minuto
        self.max_messages_per_hour = 200    # Máximo por hora
        self.min_interval_between_sends = 3  # Segundos entre envios
```

### Perfis de Rate Limiting

**Conservador:**
```python
self.max_messages_per_minute = 10
self.max_messages_per_hour = 100
self.min_interval_between_sends = 5
```

**Balanceado (padrão):**
```python
self.max_messages_per_minute = 20
self.max_messages_per_hour = 200
self.min_interval_between_sends = 3
```

**Agressivo:**
```python
self.max_messages_per_minute = 30
self.max_messages_per_hour = 300
self.min_interval_between_sends = 1
```

## 🏷️ Watermarks (Opcional)

### Configuração Base
```python
# bot/watermark_manager.py
class WatermarkManager:
    def __init__(self):
        self.default_text = "SEU CANAL"
        self.default_position = "bottom-right"
        self.default_opacity = 70
        self.default_size = 20
        self.default_color = "white"
```

### Via Comando
```bash
/configurarwatermark CANAL_ID "Texto" posicao opacidade tamanho cor
```

**Exemplo:**
```bash
/configurarwatermark -1002574788580 "VIP CENTRAL" bottom-right 70 20 white
```

## 📊 Enquetes Automáticas

### Configuração
```python
# bot/poll_manager.py
def set_poll_frequency(self, canal_id, hours=168):  # 168h = 1 semana
```

### Via Comando
```bash
# A cada 24 horas
/configurarenquetes -1002574788580 24

# A cada 1 semana (padrão)
/configurarenquetes -1002574788580 168
```

## 🗄️ Banco de Dados

### Localização
- **Arquivo:** `clonagem.db` (SQLite)
- **Backup:** Automático via cron

### Tabelas Principais
- **posts** - Posts recebidos dos canais fonte
- **envios** - Posts enviados para canais destino
- **mensagens_enviadas** - Controle para deleção
- **canal_schedules** - Horários por canal

### Limpeza Automática
```bash
# Via comando
/limparbanco CONFIRMAR

# Via cron (adicionar ao crontab)
0 3 * * 0 /usr/bin/python3 /caminho/para/cleanup.py
```

## 🔐 Segurança

### Admin ID
```python
# bot/commands.py
BOT_ADMIN_ID = 8169883791  # Seu ID do Telegram
```

**Como obter seu ID:**
1. Fale com [@userinfobot](https://t.me/userinfobot)
2. Copie o número do ID

### Permissões Necessárias
**Nos canais fonte:**
- Bot deve ser ADMIN
- Permissão para LER mensagens

**Nos canais destino:**
- Bot deve ser ADMIN
- Permissão para ENVIAR mensagens
- Permissão para ENVIAR mídias

## 🎛️ Configurações Avançadas

### Smart Scheduler
```python
# bot/smart_scheduler.py
def should_post_now(self, canal_id, current_time=None):
    # Se não há horários configurados, SEMPRE pode postar
    return True  # Mais agressivo
    # return False  # Mais conservador
```

### Caption Generator
```python
# bot/nicho_caption_generator.py
def generate_caption_by_fonte(self, canal_fonte_id, post_data=None):
    # 20% chance de adicionar urgência
    if random.random() < 0.2:  # Mude para 0.5 (50%) ou 0.1 (10%)
        urgencia_extra = [...]
```

## 📝 Variáveis de Ambiente (Opcional)

### Criar .env
```bash
# .env
TELEGRAM_TOKEN=1234567890:ABC-DEF...
ADMIN_ID=8169883791
RATE_LIMIT_MINUTE=20
RATE_LIMIT_HOUR=200
SCHEDULER_INTERVAL=30
```

### Usar no código
```python
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
BOT_ADMIN_ID = int(os.getenv('ADMIN_ID', 8169883791))
```

## 🔄 Configurações por Ambiente

### Desenvolvimento
```python
DEBUG = True
RATE_LIMIT_ENABLED = False
SCHEDULER_INTERVAL = 10  # segundos
```

### Produção
```python
DEBUG = False
RATE_LIMIT_ENABLED = True
SCHEDULER_INTERVAL = 30  # segundos
```

## 📋 Checklist de Configuração

### Inicial
- [ ] Token do bot configurado
- [ ] IDs dos canais corretos
- [ ] Bot é admin nos canais fonte
- [ ] Bot é admin nos canais destino
- [ ] Admin ID configurado

### Personalização
- [ ] Legendas personalizadas
- [ ] Horários configurados
- [ ] Rate limiting ajustado
- [ ] Watermarks configurados (se desejado)
- [ ] Enquetes configuradas (se desejado)

### Produção
- [ ] .env para dados sensíveis
- [ ] Backup automático configurado
- [ ] Logs sendo salvos
- [ ] Monitoramento ativo

---

**💡 Dica:** Sempre teste as configurações com `/debug` e `/statusnichos` antes de colocar em produção!
