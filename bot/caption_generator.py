# caption_generator.py

from captions.caption_loader import caption_loader
from bot.caption_formatter import caption_formatter

def generate_caption(media_info, canal_id=None):
    """
    Retorna uma legenda aleatória da lista, formatada para o canal específico.
    Args:
        media_info (dict): Não é usado, mas mantido para compatibilidade.
        canal_id (int): ID do canal para formatação específica.
    Returns:
        str: Legenda pronta para uso no Telegram.
    """
    # Carrega legenda aleatória no idioma do canal
    base_caption = caption_loader.get_random_caption(canal_id)
    
    if canal_id:
        # Aplica formatação específica do canal/nicho
        formatted_caption = caption_formatter.format_caption_for_canal(base_caption, canal_id)
        return formatted_caption
    
    return base_caption

# O bloco de exemplo de uso foi removido para que este arquivo funcione
# exclusivamente como um módulo importável.
