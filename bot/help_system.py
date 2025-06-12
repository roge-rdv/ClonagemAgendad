from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

class HelpSystem:
    def __init__(self):
        self.help_content = {
            'help_basic': {
                'title': '⚡ *Comandos Básicos*',
                'content': (
                    "**Comandos principais do bot:**\n\n"
                    "🎛️ `/start` - Menu principal (comando padrão)\n"
                    "🧙‍♂️ `/setup` - Assistente de configuração\n"
                    "⚡ `/postaragora` - Força envio imediato\n"
                    "📊 `/ratelimit` - Status do rate limiting\n\n"
                    "💡 **Dica:** Use sempre `/start` para acessar o menu!"
                )
            },
            'help_config': {
                'title': '⚙️ *Configuração*',
                'content': (
                    "**Como configurar o bot:**\n\n"
                    "⏰ **Horários:**\n"
                    "`/configurarhorarios CANAL_ID add 14:30`\n"
                    "`/listarhorarios` - Ver horários\n\n"
                    "🎨 **Estilos de legenda:**\n"
                    "`/configurarestilo CANAL_ID provocativo`\n"
                    "Estilos: provocativo, exclusivo, urgencia, curiosidade\n\n"
                    "🏷️ **Watermarks:**\n"
                    "`/configurarwatermark CANAL_ID 'Texto' posicao`\n\n"
                    "📊 **Enquetes:**\n"
                    "`/configurarenquetes CANAL_ID 168`"
                )
            },
            'help_reports': {
                'title': '📋 *Relatórios*',
                'content': (
                    "**Como usar os relatórios:**\n\n"
                    "📊 **Status geral:**\n"
                    "Use o menu principal → Status\n\n"
                    "⏱️ **Rate limiting:**\n"
                    "Mostra quantas mensagens foram enviadas\n\n"
                    "⏰ **Horários:**\n"
                    "Lista horários configurados por canal\n\n"
                    "📊 **Enquetes:**\n"
                    "Status das enquetes automáticas\n\n"
                    "💡 **Dica:** Verifique regularmente o status!"
                )
            },
            'help_troubleshoot': {
                'title': '🐛 *Solução de Problemas*',
                'content': (
                    "**Problemas comuns e soluções:**\n\n"
                    "❌ **Posts não estão sendo enviados:**\n"
                    "• Verifique se há posts no canal fonte\n"
                    "• Confirme se os horários estão configurados\n"
                    "• Use `/postaragora` para forçar envio\n\n"
                    "⚠️ **Rate limit atingido:**\n"
                    "• É normal, o bot aguarda automaticamente\n"
                    "• Verifique com `/ratelimit`\n\n"
                    "🔧 **Bot não responde:**\n"
                    "• Verifique se o bot está online\n"
                    "• Tente reiniciar com o comando do admin\n\n"
                    "📞 **Precisa de mais ajuda?**\n"
                    "Entre em contato com o administrador."
                )
            }
        }
    
    def get_help_content(self, help_type):
        """Retorna o conteúdo de ajuda específico."""
        return self.help_content.get(help_type, {
            'title': '❓ Ajuda não encontrada',
            'content': 'Conteúdo de ajuda não disponível.'
        })
    
    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE, help_type):
        """Mostra ajuda específica."""
        help_data = self.get_help_content(help_type)
        
        text = f"{help_data['title']}\n\n{help_data['content']}"
        
        keyboard = [
            [InlineKeyboardButton("◀️ Voltar ao Menu Ajuda", callback_data="help_menu")],
            [InlineKeyboardButton("🏠 Menu Principal", callback_data="main")]
        ]
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif update.message:
            await update.message.reply_text(
                text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard)
            )

# Instância global do sistema de ajuda
help_system = HelpSystem()
