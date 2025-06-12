import random
from db.db import connect

class CaptionFormatter:
    def __init__(self):
        self.create_formatter_table()
        # Estilos específicos para nicho +18
        self.adult_styles = {
            'provocativo': {
                'prefixos': ['🔥', '😈', '💋', '👄', '🚨'],
                'sufixos': ['<tg-spoiler>Você aguenta?</tg-spoiler>', '<tg-spoiler>Só para os corajosos!</tg-spoiler>'],
                'formatacao': 'bold'
            },
            'exclusivo': {
                'prefixos': ['💎', '👑', '🔓', '💰'],
                'sufixos': ['VIP apenas!', 'Acesso restrito!'],
                'formatacao': 'italic_bold'
            },
            'urgencia': {
                'prefixos': ['⚡', '🚀', '💥', '⏰'],
                'sufixos': ['Não perca!', 'Por tempo limitado!'],
                'formatacao': 'underline_bold'
            },
            'curiosidade': {
                'prefixos': ['👀', '🤔', '😏', '🔍'],
                'sufixos': ['<tg-spoiler>Descubra mais...</tg-spoiler>', 'Quer saber mais?'],
                'formatacao': 'spoiler'
            }
        }
    
    def create_formatter_table(self):
        """Cria tabela para configurações de formatação por canal."""
        conn = connect()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS canal_formatacao (
                canal_id INTEGER PRIMARY KEY,
                estilo TEXT DEFAULT 'provocativo',
                use_emojis BOOLEAN DEFAULT 1,
                use_spoilers BOOLEAN DEFAULT 1,
                prefixo_personalizado TEXT,
                sufixo_personalizado TEXT,
                ativo BOOLEAN DEFAULT 1
            )
        """)
        conn.commit()
        conn.close()
    
    def set_canal_style(self, canal_id, estilo='provocativo', use_emojis=True, use_spoilers=True, 
                       prefixo_personalizado=None, sufixo_personalizado=None):
        """Define estilo de formatação para um canal."""
        conn = connect()
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO canal_formatacao 
            (canal_id, estilo, use_emojis, use_spoilers, prefixo_personalizado, sufixo_personalizado, ativo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (canal_id, estilo, use_emojis, use_spoilers, prefixo_personalizado, sufixo_personalizado))
        conn.commit()
        conn.close()
    
    def get_canal_config(self, canal_id):
        """Retorna configuração de formatação para um canal."""
        conn = connect()
        c = conn.cursor()
        c.execute("""
            SELECT estilo, use_emojis, use_spoilers, prefixo_personalizado, sufixo_personalizado
            FROM canal_formatacao 
            WHERE canal_id = ? AND ativo = 1
        """, (canal_id,))
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                'estilo': result[0],
                'use_emojis': result[1],
                'use_spoilers': result[2],
                'prefixo_personalizado': result[3],
                'sufixo_personalizado': result[4]
            }
        # Configuração padrão para nicho +18
        return {
            'estilo': 'provocativo',
            'use_emojis': True,
            'use_spoilers': True,
            'prefixo_personalizado': None,
            'sufixo_personalizado': None
        }
    
    def format_caption_for_canal(self, base_caption, canal_id):
        """Formata a legenda específica para o canal/nicho."""
        config = self.get_canal_config(canal_id)
        estilo = config['estilo']
        
        if estilo not in self.adult_styles:
            estilo = 'provocativo'
        
        style_config = self.adult_styles[estilo]
        formatted_caption = base_caption
        
        # Adiciona prefixo
        if config['use_emojis']:
            if config['prefixo_personalizado']:
                prefix = config['prefixo_personalizado']
            else:
                prefix = random.choice(style_config['prefixos'])
            formatted_caption = f"{prefix} {formatted_caption}"
        
        # Aplica formatação
        formatacao = style_config['formatacao']
        if formatacao == 'bold':
            formatted_caption = f"<b>{formatted_caption}</b>"
        elif formatacao == 'italic_bold':
            formatted_caption = f"<b><i>{formatted_caption}</i></b>"
        elif formatacao == 'underline_bold':
            formatted_caption = f"<b><u>{formatted_caption}</u></b>"
        elif formatacao == 'spoiler' and config['use_spoilers']:
            formatted_caption = f"<tg-spoiler>{formatted_caption}</tg-spoiler>"
        
        # Adiciona sufixo
        if config['sufixo_personalizado']:
            suffix = config['sufixo_personalizado']
        elif config['use_spoilers'] and random.choice([True, False]):
            suffix = random.choice(style_config['sufixos'])
        else:
            suffix = ""
        
        if suffix:
            formatted_caption = f"{formatted_caption}\n\n{suffix}"
        
        return formatted_caption
    
    def get_available_styles(self):
        """Retorna estilos disponíveis para o nicho +18."""
        return list(self.adult_styles.keys())

# Instância global do caption formatter
caption_formatter = CaptionFormatter()
