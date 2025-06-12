from PIL import Image, ImageDraw, ImageFont
import io
from db.db import connect

class WatermarkManager:
    def __init__(self):
        self.create_watermark_table()
    
    def create_watermark_table(self):
        """Cria tabela para configurações de watermark por canal."""
        conn = connect()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS canal_watermarks (
                canal_id INTEGER PRIMARY KEY,
                watermark_text TEXT,
                position TEXT DEFAULT 'bottom-right',
                opacity INTEGER DEFAULT 70,
                font_size INTEGER DEFAULT 20,
                color TEXT DEFAULT 'white',
                ativo BOOLEAN DEFAULT 1
            )
        """)
        conn.commit()
        conn.close()
    
    def set_watermark(self, canal_id, text, position='bottom-right', opacity=70, font_size=20, color='white'):
        """Define watermark para um canal específico."""
        conn = connect()
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO canal_watermarks 
            (canal_id, watermark_text, position, opacity, font_size, color, ativo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (canal_id, text, position, opacity, font_size, color))
        conn.commit()
        conn.close()
    
    def get_watermark_config(self, canal_id):
        """Retorna configuração de watermark para um canal."""
        conn = connect()
        c = conn.cursor()
        c.execute("""
            SELECT watermark_text, position, opacity, font_size, color
            FROM canal_watermarks 
            WHERE canal_id = ? AND ativo = 1
        """, (canal_id,))
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                'text': result[0],
                'position': result[1],
                'opacity': result[2],
                'font_size': result[3],
                'color': result[4]
            }
        return None
    
    def add_watermark_to_image(self, image_file_id, canal_id, bot):
        """Adiciona watermark a uma imagem."""
        config = self.get_watermark_config(canal_id)
        if not config:
            return None
        
        try:
            # Implementação básica - retorna None por enquanto
            # Você pode implementar com PIL se necessário
            return None
            
        except Exception as e:
            print(f"Erro ao adicionar watermark: {e}")
            return None

# Instância global do watermark manager
watermark_manager = WatermarkManager()
