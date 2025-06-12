from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import CANAIS_DESTINO
from bot.smart_scheduler import smart_scheduler
from bot.caption_formatter import caption_formatter
from bot.watermark_manager import watermark_manager

# Estados do wizard
WIZARD_STEP_1, WIZARD_STEP_2, WIZARD_STEP_3, WIZARD_STEP_4, WIZARD_CONFIRM = range(5)

class SetupWizard:
    def __init__(self):
        self.wizard_data = {}
    
    async def start_wizard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia o wizard de configuração."""
        if not update.effective_user:
            return ConversationHandler.END
        
        user_id = update.effective_user.id
        self.wizard_data[user_id] = {}
        
        text = (
            "🧙‍♂️ *Assistente de Configuração*\n\n"
            "Vou te ajudar a configurar o bot passo a passo!\n\n"
            "**Passo 1/4: Escolha o Canal**\n"
            "Para qual canal você quer configurar?"
        )
        
        keyboard = []
        for canal in CANAIS_DESTINO:
            keyboard.append([InlineKeyboardButton(f"Canal {canal}", callback_data=f"wiz_canal_{canal}")])
        keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="wiz_cancel")])
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif update.message:
            await update.message.reply_text(
                text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        return WIZARD_STEP_1
    
    async def wizard_step_1(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Passo 1: Selecionar canal."""
        query = update.callback_query
        if not query:
            return ConversationHandler.END
        
        await query.answer()
        
        if query.data == "wiz_cancel":
            await query.edit_message_text("❌ Configuração cancelada.")
            return ConversationHandler.END
        
        if not query.data or not query.from_user:
            return ConversationHandler.END
        
        canal_id = int(query.data.replace("wiz_canal_", ""))
        user_id = query.from_user.id
        self.wizard_data[user_id]['canal_id'] = canal_id
        
        text = (
            f"✅ Canal selecionado: `{canal_id}`\n\n"
            "**Passo 2/4: Configurar Horários**\n"
            "Escolha os horários de postagem:"
        )
        
        keyboard = [
            [InlineKeyboardButton("🌅 Manhã (08:00, 10:00)", callback_data="wiz_schedule_morning")],
            [InlineKeyboardButton("☀️ Tarde (14:00, 16:00)", callback_data="wiz_schedule_afternoon")],
            [InlineKeyboardButton("🌙 Noite (20:00, 22:00)", callback_data="wiz_schedule_evening")],
            [InlineKeyboardButton("🔄 Todos os períodos", callback_data="wiz_schedule_all")],
            [InlineKeyboardButton("⏭️ Pular este passo", callback_data="wiz_skip_schedule")],
            [InlineKeyboardButton("◀️ Voltar", callback_data="wiz_back_start")]
        ]
        
        await query.edit_message_text(
            text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return WIZARD_STEP_2
    
    async def wizard_step_2(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Passo 2: Configurar horários."""
        query = update.callback_query
        if not query or not query.from_user or not query.data:
            return ConversationHandler.END
        
        await query.answer()
        
        user_id = query.from_user.id
        canal_id = self.wizard_data[user_id]['canal_id']
        
        if query.data == "wiz_back_start":
            return await self.start_wizard(update, context)
        
        # Configura horários baseado na escolha
        schedule_map = {
            "wiz_schedule_morning": ["08:00", "10:00"],
            "wiz_schedule_afternoon": ["14:00", "16:00"],
            "wiz_schedule_evening": ["20:00", "22:00"],
            "wiz_schedule_all": ["08:00", "14:00", "20:00"],
            "wiz_skip_schedule": []
        }
        
        schedules = schedule_map.get(query.data, [])
        self.wizard_data[user_id]['schedules'] = schedules
        
        for schedule in schedules:
            smart_scheduler.add_schedule(canal_id, schedule)
        
        text = (
            f"✅ Horários configurados: {', '.join(schedules) if schedules else 'Nenhum'}\n\n"
            "**Passo 3/4: Estilo das Legendas**\n"
            "Escolha o estilo para as legendas:"
        )
        
        keyboard = [
            [InlineKeyboardButton("😈 Provocativo", callback_data="wiz_style_provocativo")],
            [InlineKeyboardButton("💎 Exclusivo", callback_data="wiz_style_exclusivo")],
            [InlineKeyboardButton("⚡ Urgência", callback_data="wiz_style_urgencia")],
            [InlineKeyboardButton("👀 Curiosidade", callback_data="wiz_style_curiosidade")],
            [InlineKeyboardButton("⏭️ Pular este passo", callback_data="wiz_skip_style")],
            [InlineKeyboardButton("◀️ Voltar", callback_data="wiz_back_step1")]
        ]
        
        await query.edit_message_text(
            text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return WIZARD_STEP_3
    
    async def wizard_step_3(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Passo 3: Configurar estilo."""
        query = update.callback_query
        if not query or not query.from_user or not query.data:
            return ConversationHandler.END
        
        await query.answer()
        
        user_id = query.from_user.id
        canal_id = self.wizard_data[user_id]['canal_id']
        
        if query.data == "wiz_back_step1":
            return await self.wizard_step_1(update, context)
        
        # Configura estilo
        style_map = {
            "wiz_style_provocativo": "provocativo",
            "wiz_style_exclusivo": "exclusivo", 
            "wiz_style_urgencia": "urgencia",
            "wiz_style_curiosidade": "curiosidade",
            "wiz_skip_style": None
        }
        
        style = style_map.get(query.data, None)
        self.wizard_data[user_id]['style'] = style
        
        if style:
            caption_formatter.set_canal_style(canal_id, style)
        
        text = (
            f"✅ Estilo configurado: {style or 'Padrão'}\n\n"
            "**Passo 4/4: Watermark (Opcional)**\n"
            "Quer adicionar uma marca d'água nas imagens?"
        )
        
        keyboard = [
            [InlineKeyboardButton("🏷️ Sim, configurar", callback_data="wiz_watermark_yes")],
            [InlineKeyboardButton("❌ Não, pular", callback_data="wiz_watermark_no")],
            [InlineKeyboardButton("◀️ Voltar", callback_data="wiz_back_step2")]
        ]
        
        await query.edit_message_text(
            text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return WIZARD_STEP_4
    
    async def wizard_step_4(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Passo 4: Configurar watermark."""
        query = update.callback_query
        if not query or not query.from_user or not query.data:
            return ConversationHandler.END
        
        await query.answer()
        
        user_id = query.from_user.id
        canal_id = self.wizard_data[user_id]['canal_id']
        
        if query.data == "wiz_back_step2":
            return await self.wizard_step_2(update, context)
        
        if query.data == "wiz_watermark_yes":
            watermark_manager.set_watermark(canal_id, "VIP CENTRAL", "bottom-right", 70, 20, "white")
            self.wizard_data[user_id]['watermark'] = "Configurado"
        else:
            self.wizard_data[user_id]['watermark'] = "Não configurado"
        
        # Exibe resumo final
        data = self.wizard_data[user_id]
        text = (
            "🎉 *Configuração Concluída!*\n\n"
            "**Resumo das configurações:**\n\n"
            f"📺 **Canal:** `{data['canal_id']}`\n"
            f"⏰ **Horários:** {', '.join(data['schedules']) if data['schedules'] else 'Nenhum'}\n"
            f"🎨 **Estilo:** {data['style'] or 'Padrão'}\n"
            f"🏷️ **Watermark:** {data['watermark']}\n\n"
            "✅ O bot está pronto para funcionar!\n"
            "Use /menu para acessar os controles."
        )
        
        keyboard = [
            [InlineKeyboardButton("🎉 Concluir", callback_data="wiz_finish")],
            [InlineKeyboardButton("◀️ Voltar", callback_data="wiz_back_step3")]
        ]
        
        await query.edit_message_text(
            text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return WIZARD_CONFIRM
    
    async def wizard_finish(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Finaliza o wizard."""
        query = update.callback_query
        if not query:
            return ConversationHandler.END
        
        await query.answer()
        
        await query.edit_message_text(
            "🎉 *Configuração finalizada com sucesso!*\n\n"
            "Use /menu para acessar o painel de controle.",
            parse_mode='Markdown'
        )
        
        return ConversationHandler.END
    
    async def wizard_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancela o wizard."""
        if update.message:
            await update.message.reply_text("❌ Configuração cancelada.")
        return ConversationHandler.END

# Instância global do wizard
setup_wizard = SetupWizard()
