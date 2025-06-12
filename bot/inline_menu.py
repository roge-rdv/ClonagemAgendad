from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes

class InlineMenu:
    def __init__(self):
        self.menu_structure = {
            'main': {
                'title': '🤖 *Bot de Clonagem Agendada - Menu Principal*\n\nEscolha uma opção:\n\n💡 *Dica:* Use `/setup` para configuração inicial automática',
                'buttons': [
                    [('⚡ Postar Agora', 'post_now'), ('📊 Status', 'status_menu')],
                    [('⚙️ Configurações', 'config_menu'), ('📋 Relatórios', 'reports_menu')],
                    [('❓ Ajuda', 'help_menu')]
                ]
            },
            'status_menu': {
                'title': '📊 *Status do Sistema*\n\nEscolha o que deseja verificar:',
                'buttons': [
                    [('⏱️ Rate Limiting', 'rate_limit_status'), ('⏰ Horários', 'schedule_status')],
                    [('📊 Enquetes', 'poll_status'), ('📈 Estatísticas', 'stats_general')],
                    [('◀️ Voltar', 'main')]
                ]
            },
            'config_menu': {
                'title': '⚙️ *Configurações*\n\nO que deseja configurar?',
                'buttons': [
                    [('⏰ Horários', 'config_schedule'), ('🎨 Estilos', 'config_style')],
                    [('🖼️ Watermarks', 'config_watermark'), ('📊 Enquetes', 'config_polls')],
                    [('📋 Listar Configs', 'list_configs'), ('◀️ Voltar', 'main')]
                ]
            },
            'help_menu': {
                'title': '❓ *Central de Ajuda*\n\nEscolha o tópico:',
                'buttons': [
                    [('⚡ Comandos Básicos', 'help_basic'), ('⚙️ Configuração', 'help_config')],
                    [('📊 Relatórios', 'help_reports'), ('🐛 Problemas', 'help_troubleshoot')],
                    [('◀️ Voltar', 'main')]
                ]
            },
            'reports_menu': {
                'title': '📋 *Relatórios*\n\nQue tipo de relatório?',
                'buttons': [
                    [('📊 Geral', 'report_general'), ('📈 Por Canal', 'report_by_canal')],
                    [('⏰ Horários', 'report_schedule'), ('📋 Configurações', 'report_configs')],
                    [('◀️ Voltar', 'main')]
                ]
            }
        }
    
    def get_menu_keyboard(self, menu_name):
        """Retorna o teclado inline para um menu específico."""
        menu = self.menu_structure.get(menu_name, self.menu_structure['main'])
        keyboard = []
        
        for row in menu['buttons']:
            button_row = []
            for text, callback_data in row:
                button_row.append(InlineKeyboardButton(text, callback_data=callback_data))
            keyboard.append(button_row)
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_menu_text(self, menu_name):
        """Retorna o texto do menu."""
        menu = self.menu_structure.get(menu_name, self.menu_structure['main'])
        return menu['title']

# Instância global do menu inline
inline_menu = InlineMenu()
