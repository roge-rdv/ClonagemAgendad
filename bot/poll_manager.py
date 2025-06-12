import random
from db.db import connect
from datetime import datetime, timedelta

class PollManager:
    def __init__(self):
        self.create_poll_table()
        # Enquetes específicas para nicho +18
        self.adult_polls = [
            {
                "question": "🔥 Que tipo de conteúdo você prefere ver mais?",
                "options": ["📸 Fotos exclusivas", "🎥 Vídeos premium", "📱 Stories íntimos", "💬 Conversas VIP"],
                "anonymous": True
            },
            {
                "question": "⏰ Qual o melhor horário para receber conteúdo exclusivo?",
                "options": ["🌅 Manhã (8h-12h)", "☀️ Tarde (12h-18h)", "🌙 Noite (18h-22h)", "🌃 Madrugada (22h-2h)"],
                "anonymous": True
            },
            {
                "question": "💎 Que benefício VIP te interessa mais?",
                "options": ["🎬 Conteúdo sem censura", "💬 Chat privado", "🎁 Conteúdo personalizado", "⭐ Acesso antecipado"],
                "anonymous": True
            },
            {
                "question": "🎯 Como você prefere interagir com o conteúdo?",
                "options": ["👀 Só visualizar", "❤️ Curtir e reagir", "💬 Comentar ativamente", "📤 Compartilhar favoritos"],
                "anonymous": True
            },
            {
                "question": "🔞 Qual estilo de legenda te chama mais atenção?",
                "options": ["😈 Provocativo/Ousado", "💎 Exclusivo/VIP", "🔥 Direto ao ponto", "😏 Misterioso/Sugestivo"],
                "anonymous": True
            },
            {
                "question": "📊 Com que frequência você gostaria de receber conteúdo premium?",
                "options": ["🚀 Várias vezes ao dia", "📅 Uma vez por dia", "📆 Algumas vezes por semana", "🎯 Qualidade > Quantidade"],
                "anonymous": True
            },
            {
                "question": "💰 Qual fator mais influencia sua decisão de virar VIP?",
                "options": ["🎁 Conteúdo exclusivo", "💸 Preço acessível", "⭐ Qualidade garantida", "👥 Comunidade ativa"],
                "anonymous": True
            },
            {
                "question": "🎨 Que tipo de personalização você valoriza mais?",
                "options": ["🏷️ Conteúdo marcado", "🎯 Recomendações personalizadas", "💬 Mensagens customizadas", "🎪 Experiência única"],
                "anonymous": True
            }
        ]
    
    def create_poll_table(self):
        """Cria tabela para rastrear enquetes enviadas."""
        conn = connect()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS polls_sent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                canal_id INTEGER NOT NULL,
                poll_question TEXT NOT NULL,
                poll_id TEXT,
                data_envio DATETIME,
                ativo BOOLEAN DEFAULT 1
            )
        """)
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS poll_config (
                canal_id INTEGER PRIMARY KEY,
                frequency_hours INTEGER DEFAULT 168,
                ativo BOOLEAN DEFAULT 1,
                last_poll_sent DATETIME
            )
        """)
        conn.commit()
        conn.close()
    
    def set_poll_frequency(self, canal_id, hours=168):
        """Define frequência de enquetes para um canal (padrão: 1 semana)."""
        conn = connect()
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO poll_config (canal_id, frequency_hours, ativo, last_poll_sent)
            VALUES (?, ?, 1, ?)
        """, (canal_id, hours, datetime.now()))
        conn.commit()
        conn.close()
    
    def should_send_poll(self, canal_id):
        """Verifica se deve enviar enquete para o canal."""
        conn = connect()
        c = conn.cursor()
        c.execute("""
            SELECT frequency_hours, last_poll_sent FROM poll_config
            WHERE canal_id = ? AND ativo = 1
        """, (canal_id,))
        result = c.fetchone()
        conn.close()
        
        if not result:
            return False
        
        frequency_hours, last_sent = result
        if not last_sent:
            return True
        
        last_sent_dt = datetime.fromisoformat(last_sent)
        next_poll_time = last_sent_dt + timedelta(hours=frequency_hours)
        
        return datetime.now() >= next_poll_time
    
    def get_random_poll(self):
        """Retorna uma enquete aleatória."""
        return random.choice(self.adult_polls)
    
    def record_poll_sent(self, canal_id, poll_question, poll_id=None):
        """Registra que uma enquete foi enviada."""
        conn = connect()
        c = conn.cursor()
        c.execute("""
            INSERT INTO polls_sent (canal_id, poll_question, poll_id, data_envio)
            VALUES (?, ?, ?, ?)
        """, (canal_id, poll_question, poll_id, datetime.now()))
        
        # Atualiza último envio na configuração
        c.execute("""
            UPDATE poll_config SET last_poll_sent = ? WHERE canal_id = ?
        """, (datetime.now(), canal_id))
        
        conn.commit()
        conn.close()
    
    def get_poll_stats(self, canal_id):
        """Retorna estatísticas de enquetes do canal."""
        conn = connect()
        c = conn.cursor()
        c.execute("""
            SELECT COUNT(*) as total_polls, MAX(data_envio) as last_poll
            FROM polls_sent WHERE canal_id = ?
        """, (canal_id,))
        result = c.fetchone()
        conn.close()
        
        return {
            'total_polls': result[0] if result else 0,
            'last_poll': result[1] if result and result[1] else 'Nunca'
        }

# Instância global do poll manager
poll_manager = PollManager()
