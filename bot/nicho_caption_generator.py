import random
from config import get_caption_file_by_fonte

class NichoCaptionGenerator:
    def __init__(self):
        self.caption_cache = {}
        self.load_all_captions()
    
    def load_all_captions(self):
        """Carrega TODOS os arsenais de legendas! 🔥"""
        try:
            from captions.novin import ARSENAL_NOVINHAS
            self.caption_cache['novin'] = ARSENAL_NOVINHAS
        except ImportError:
            self.caption_cache['novin'] = []
        
        try:
            from captions.leaks import ARSENAL_LEAKS
            self.caption_cache['leaks'] = ARSENAL_LEAKS
        except ImportError:
            self.caption_cache['leaks'] = []
        
        try:
            from captions.latinas import ARSENAL_LATINAS
            self.caption_cache['latinas'] = ARSENAL_LATINAS
        except ImportError:
            self.caption_cache['latinas'] = []
        
        try:
            from captions.coroas import ARSENAL_COROAS
            self.caption_cache['coroas'] = ARSENAL_COROAS
        except ImportError:
            self.caption_cache['coroas'] = []
        
        try:
            from captions.gold import ARSENAL_GOLD
            self.caption_cache['gold'] = ARSENAL_GOLD
        except ImportError:
            self.caption_cache['gold'] = []
        
        try:
            from captions.backdoor import ARSENAL_BACKDOOR
            self.caption_cache['backdoor'] = ARSENAL_BACKDOOR
        except ImportError:
            self.caption_cache['backdoor'] = []
    
    def generate_caption_by_fonte(self, canal_fonte_id, post_data=None):
        """Gera caption ESPECÍFICA baseada no canal fonte! 🎯"""
        caption_file = get_caption_file_by_fonte(canal_fonte_id)
        
        # Pega as legendas do nicho específico
        captions = self.caption_cache.get(caption_file, [])
        
        if not captions:
            # Fallback caso não tenha legendas do nicho
            return "🔥 Conteúdo exclusivo disponível no VIP! 👉 @vipcentralaccess_bot"
        
        # Retorna uma legenda ALEATÓRIA do arsenal específico
        base_caption = random.choice(captions)
        
        # 20% chance de adicionar URGÊNCIA EXTRA
        if random.random() < 0.2:
            urgencia_extra = [
                "\n\n⚠️ ÚLTIMAS 12 HORAS NO AR!",
                "\n\n🚨 MATERIAL SENDO DELETADO!",
                "\n\n💀 SÓ ATÉ MEIA-NOITE!",
                "\n\n🔥 PROMOÇÃO ACABA HOJE!"
            ]
            base_caption += random.choice(urgencia_extra)
        
        return base_caption
    
    def get_nicho_stats(self):
        """Retorna estatísticas dos arsenais carregados."""
        stats = {}
        for nicho, captions in self.caption_cache.items():
            stats[nicho] = len(captions)
        return stats

# Instância global do gerador de legendas por nicho
nicho_caption_generator = NichoCaptionGenerator()
