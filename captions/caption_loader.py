# Sistema para carregar legendas por idioma

import random
import os
import importlib.util
from db.db import connect

class CaptionLoader:
    def __init__(self):
        self.create_language_table()
        self.caption_cache = {}
        self.available_languages = ['pt_br', 'en_us', 'es_es']
    
    def create_language_table(self):
        """Cria tabela para configuração de idioma por canal."""
        conn = connect()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS canal_language (
                canal_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'pt_br',
                ativo BOOLEAN DEFAULT 1
            )
        """)
        conn.commit()
        conn.close()
    
    def set_canal_language(self, canal_id, language='pt_br'):
        """Define idioma para um canal específico."""
        if language not in self.available_languages:
            language = 'pt_br'
        
        conn = connect()
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO canal_language (canal_id, language, ativo)
            VALUES (?, ?, 1)
        """, (canal_id, language))
        conn.commit()
        conn.close()
    
    def get_canal_language(self, canal_id):
        """Retorna idioma configurado para o canal."""
        conn = connect()
        c = conn.cursor()
        c.execute("""
            SELECT language FROM canal_language 
            WHERE canal_id = ? AND ativo = 1
        """, (canal_id,))
        result = c.fetchone()
        conn.close()
        
        return result[0] if result else 'pt_br'
    
    def load_captions(self, language):
        """Carrega legendas do arquivo de idioma específico."""
        if language in self.caption_cache:
            return self.caption_cache[language]
        
        try:
            # Caminho para o arquivo de idioma
            file_path = os.path.join(os.path.dirname(__file__), f"{language}.py")
            
            # Carrega o módulo dinamicamente
            spec = importlib.util.spec_from_file_location(f"captions_{language}", file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Não foi possível carregar o módulo {language}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Cache das legendas
            self.caption_cache[language] = module.CAPTIONS
            return module.CAPTIONS
            
        except Exception as e:
            print(f"Erro ao carregar idioma {language}: {e}")
            # Fallback para português - evita recursão infinita
            if language != 'pt_br':
                return self.load_captions('pt_br')
            else:
                # Se até o português falhar, retorna lista padrão
                return ["Conteúdo exclusivo disponível!"]
    
    def get_random_caption(self, canal_id=None, language=None):
        """Retorna uma legenda aleatória de TODOS os idiomas misturados."""
        # Carrega legendas de todos os idiomas disponíveis
        all_captions = []
        for lang in self.available_languages:
            captions = self.load_captions(lang)
            all_captions.extend(captions)
        
        # Retorna uma legenda aleatória de qualquer idioma
        return random.choice(all_captions)

    def get_available_languages(self):
        """Retorna lista de idiomas disponíveis."""
        return self.available_languages

# Instância global do caption loader
caption_loader = CaptionLoader()
