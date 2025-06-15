import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, CallbackQueryHandler
from bot.rate_limiter import rate_limiter
from config import CANAIS_DESTINO, CANAL_MAPPINGS
from bot.smart_scheduler import smart_scheduler
from bot.watermark_manager import watermark_manager
from bot.caption_formatter import caption_formatter
from bot.poll_manager import poll_manager
from captions.caption_loader import caption_loader
from bot.inline_menu import inline_menu
from bot.setup_wizard import setup_wizard, WIZARD_STEP_1, WIZARD_STEP_2, WIZARD_STEP_3, WIZARD_STEP_4, WIZARD_CONFIRM
from bot.help_system import help_system
from bot.nicho_caption_generator import nicho_caption_generator

# Defina o ID do admin do bot (pode ser seu user_id)
BOT_ADMIN_ID = 8169883791  # Substitua pelo seu ID

def is_admin(user_id):
    return user_id == BOT_ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Menu básico."""
    if not update.message or not update.effective_user:
        return

    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Acesso negado. Este bot é restrito ao administrador.\n\n"
            "🇧🇷 Para adquirir este bot, entre em contato com @rogee_rdvv\n"
            "🇺🇸 To acquire this bot, contact @rogee_rdvv\n"
            "🇪🇦 Para comprar este bot, comuníquese con @rogee_rdvv"
        )
        return

    text = (
        "🤖 **Bot Multi-Nicho Ativo!**\n\n"
        "📊 **Comandos disponíveis:**\n"
        "/statusnichos - Ver status de todos os nichos\n"
        "/postaragora - Forçar envio imediato\n"
        "/deletartudo CONFIRMAR - Apagar todas as mensagens\n\n"
        "🔥 **Bot monitorando 6 nichos ativos!**"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /menu - Alias para /start."""
    await start(update, context)

async def setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /setup - Inicia o wizard de configuração."""
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Comando restrito ao administrador.\n\n"
            "🇧🇷 Para adquirir este bot, entre em contato com @rogee_rdvv\n"
            "🇺🇸 To acquire this bot, contact @rogee_rdvv",
            parse_mode='Markdown'
        )
        return
    
    return await setup_wizard.start_wizard(update, context)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manipula todas as callback queries do menu inline."""
    query = update.callback_query
    if not query:
        return
    
    await query.answer()
    
    callback_data = query.data
    if not callback_data:
        return
    
    # Se é callback do wizard, NÃO PROCESSA AQUI - deixa o ConversationHandler processar
    if callback_data.startswith('wiz_'):
        return  # Retorna sem processar
    
    # Menus de navegação
    if callback_data in ['main', 'status_menu', 'config_menu', 'help_menu', 'reports_menu']:
        text = inline_menu.get_menu_text(callback_data)
        keyboard = inline_menu.get_menu_keyboard(callback_data)
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
    
    # Ações do menu principal
    elif callback_data == 'post_now':
        from bot.telegram_bot import send_scheduled_posts
        await send_scheduled_posts(context)
        await query.edit_message_text("✅ Postagem executada!")
    
    elif callback_data == 'refresh_main':
        text = inline_menu.get_menu_text('main')
        keyboard = inline_menu.get_menu_keyboard('main')
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)
    
    # Status
    elif callback_data == 'rate_limit_status':
        await show_rate_limit_status(query, context)
    elif callback_data == 'schedule_status':
        await show_schedule_status(query, context)
    elif callback_data == 'poll_status':
        await show_poll_status(query, context)
    
    # Configurações
    elif callback_data.startswith('config_'):
        await show_config_help(query, callback_data)
    
    # Sistema de ajuda
    elif callback_data.startswith('help_'):
        await help_system.show_help(update, context, callback_data)
    
    # Relatórios
    elif callback_data.startswith('report_'):
        await show_report(query, callback_data)

async def show_rate_limit_status(query, context):
    """Mostra status do rate limiting via callback."""
    status_text = "📊 *Status do Rate Limiting:*\n\n"
    
    for canal in CANAIS_DESTINO:
        stats = rate_limiter.get_stats(canal)
        status_emoji = "✅" if stats['can_send_now'] else "⚠️"
        
        status_text += f"{status_emoji} *Canal {canal}:*\n"
        status_text += f"   • Última hora: {stats['messages_last_hour']}/200\n"
        status_text += f"   • Último minuto: {stats['messages_last_minute']}/20\n"
        status_text += f"   • Pode enviar: {'Sim' if stats['can_send_now'] else 'Não'}\n\n"
    
    keyboard = [[InlineKeyboardButton("◀️ Voltar", callback_data="status_menu")]]
    await query.edit_message_text(status_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def show_schedule_status(query, context):
    """Mostra status dos horários via callback."""
    all_schedules = smart_scheduler.get_all_canal_schedules()
    
    if not all_schedules:
        text = "📅 *Horários*\n\nNenhum horário configurado."
    else:
        text = "📅 *Horários por Canal:*\n\n"
        for canal_id, horarios in all_schedules.items():
            text += f"*Canal {canal_id}:*\n"
            for horario in horarios:
                text += f"   ⏰ {horario}\n"
            text += "\n"
    
    keyboard = [[InlineKeyboardButton("◀️ Voltar", callback_data="status_menu")]]
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def show_poll_status(query, context):
    """Mostra status das enquetes via callback."""
    text = "📊 *Status das Enquetes:*\n\n"
    
    for canal in CANAIS_DESTINO:
        stats = poll_manager.get_poll_stats(canal)
        should_send = "✅" if poll_manager.should_send_poll(canal) else "⏰"
        
        text += f"{should_send} *Canal {canal}:*\n"
        text += f"   • Total: {stats['total_polls']}\n"
        text += f"   • Última: {stats['last_poll']}\n\n"
    
    keyboard = [[InlineKeyboardButton("◀️ Voltar", callback_data="status_menu")]]
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def show_config_help(query, config_type):
    """Mostra ajuda de configuração."""
    help_map = {
        'config_schedule': '⏰ Use `/configurarhorarios CANAL_ID add HH:MM`',
        'config_style': '🎨 Use `/configurarestilo CANAL_ID estilo`',
        'config_watermark': '🏷️ Use `/configurarwatermark CANAL_ID texto`',
        'config_polls': '📊 Use `/configurarenquetes CANAL_ID horas`'
    }
    
    text = help_map.get(config_type, "Ajuda não disponível")
    keyboard = [[InlineKeyboardButton("◀️ Voltar", callback_data="config_menu")]]
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def show_report(query, report_type):
    """Mostra relatórios."""
    text = f"📋 Relatório: {report_type}\n\nEm desenvolvimento..."
    keyboard = [[InlineKeyboardButton("◀️ Voltar", callback_data="reports_menu")]]
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def postar_agora(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Força envio imediato de posts pendentes."""
    if not update.message or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Comando restrito ao administrador.")
        return
    
    await update.message.reply_text("🚀 Enviando posts pendentes...")
    
    # Chama a função de envio imediato
    from bot.telegram_bot import send_scheduled_posts
    await send_scheduled_posts(context)
    
    await update.message.reply_text("✅ Execução concluída!")

async def status_rate_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Comando restrito ao administrador.\n\n"
            "🇧🇷 Para adquirir este bot, entre em contato com @rogee_rdvv\n"
            "🇺🇸 To acquire this bot, contact @rogee_rdvv",
            parse_mode='Markdown'
        )
        return
    
    status_text = "📊 *Status do Rate Limiting:*\n\n"
    
    for canal in CANAIS_DESTINO:
        stats = rate_limiter.get_stats(canal)
        status_emoji = "✅" if stats['can_send_now'] else "⚠️"
        
        status_text += f"{status_emoji} *Canal {canal}:*\n"
        status_text += f"   • Mensagens última hora: {stats['messages_last_hour']}/200\n"
        status_text += f"   • Mensagens último minuto: {stats['messages_last_minute']}/20\n"
        
        if stats['last_send_ago'] > 0:
            status_text += f"   • Último envio: {stats['last_send_ago']:.1f}s atrás\n"
        else:
            status_text += f"   • Último envio: Nunca\n"
        
        status_text += f"   • Pode enviar agora: {'Sim' if stats['can_send_now'] else 'Não'}\n\n"
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

# Este comando realmente configura horários
async def configurar_horarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Comando restrito ao administrador.\n\n"
            "🇧🇷 Para adquirir este bot, entre em contato com @rogee_rdvv\n"
            "🇺🇸 To acquire this bot, contact @rogee_rdvv",
            parse_mode='Markdown'
        )
        return
    
    args = context.args
    if not args or len(args) < 3:
        await update.message.reply_text(
            "Uso: /configurarhorarios <canal_id> <acao> <horario>\n"
            "Ações: add, remove\n"
            "Exemplo: /configurarhorarios -1001234567890 add 14:30"
        )
        return
    
    try:
        canal_id = int(args[0])
        acao = args[1].lower()
        horario = args[2]
        
        # Validar formato do horário
        hour, minute = map(int, horario.split(':'))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Horário inválido")
        
        if acao == "add":
            if smart_scheduler.add_schedule(canal_id, horario):
                await update.message.reply_text(f"✅ Horário {horario} adicionado para o canal {canal_id}")
            else:
                await update.message.reply_text("❌ Erro ao adicionar horário")
        elif acao == "remove":
            smart_scheduler.remove_schedule(canal_id, horario)
            await update.message.reply_text(f"✅ Horário {horario} removido do canal {canal_id}")
        else:
            await update.message.reply_text("Ação inválida. Use 'add' ou 'remove'")
    
    except (ValueError, IndexError):
        await update.message.reply_text("Formato inválido. Use HH:MM para horário")

async def listar_horarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Comando restrito ao administrador.\n\n"
            "🇧🇷 Para adquirir este bot, entre em contato com @rogee_rdvv\n"
            "🇺🇸 To acquire this bot, contact @rogee_rdvv",
            parse_mode='Markdown'
        )
        return
    
    all_schedules = smart_scheduler.get_all_canal_schedules()
    
    if not all_schedules:
        await update.message.reply_text("Nenhum horário personalizado configurado.")
        return
    
    message = "📅 *Horários personalizados por canal:*\n\n"
    for canal_id, horarios in all_schedules.items():
        message += f"*Canal {canal_id}:*\n"
        for horario in horarios:
            next_time = smart_scheduler.get_next_post_time(canal_id)
            status = "🟢" if next_time == horario else "⏰"
            message += f"   {status} {horario}\n"
        message += "\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def configurar_watermark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Comando restrito ao administrador.\n\n"
            "🇧🇷 Para adquirir este bot, entre em contato com @rogee_rdvv\n"
            "🇺🇸 To acquire this bot, contact @rogee_rdvv",
            parse_mode='Markdown'
        )
        return
    
    args = context.args
    if not args or len(args) < 3:
        await update.message.reply_text(
            "Uso: /configurarwatermark <canal_id> <texto> [posicao] [opacidade] [tamanho] [cor]\n"
            "Posições: top-left, top-right, bottom-left, bottom-right, center\n"
            "Exemplo: /configurarwatermark -1001234567890 'VIP CENTRAL' bottom-right 70 20 white"
        )
        return
    
    try:
        canal_id = int(args[0])
        texto = args[1]
        posicao = args[2] if len(args) > 2 else 'bottom-right'
        opacidade = int(args[3]) if len(args) > 3 else 70
        tamanho = int(args[4]) if len(args) > 4 else 20
        cor = args[5] if len(args) > 5 else 'white'
        
        watermark_manager.set_watermark(canal_id, texto, posicao, opacidade, tamanho, cor)
        await update.message.reply_text(f"✅ Watermark configurado para o canal {canal_id}")
    
    except (ValueError, IndexError) as e:
        await update.message.reply_text(f"Erro na configuração: {e}")

async def configurar_estilo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Comando restrito ao administrador.\n\n"
            "🇧🇷 Para adquirir este bot, entre em contato com @rogee_rdvv\n"
            "🇺🇸 To acquire this bot, contact @rogee_rdvv",
            parse_mode='Markdown'
        )
        return
    
    args = context.args
    if not args or len(args) < 2:
        estilos = caption_formatter.get_available_styles()
        await update.message.reply_text(
            f"Uso: /configurarestilo <canal_id> <estilo>\n"
            f"Estilos disponíveis: {', '.join(estilos)}\n"
            f"Exemplo: /configurarestilo -1001234567890 provocativo"
        )
        return
    
    try:
        canal_id = int(args[0])
        estilo = args[1]
        
        caption_formatter.set_canal_style(canal_id, estilo)
        await update.message.reply_text(f"✅ Estilo '{estilo}' configurado para o canal {canal_id}")
    
    except (ValueError, IndexError) as e:
        await update.message.reply_text(f"Erro na configuração: {e}")

async def configurar_enquetes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Comando restrito ao administrador.\n\n"
            "🇧🇷 Para adquirir este bot, entre em contato com @rogee_rdvv\n"
            "🇺🇸 To acquire this bot, contact @rogee_rdvv",
            parse_mode='Markdown'
        )
        return
    
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text(
            "Uso: /configurarenquetes <canal_id> <frequencia_horas>\n"
            "Exemplo: /configurarenquetes -1002870159887 168\n"
            "168 horas = 1 semana (padrão)"
        )
        return
    
    try:
        canal_id = int(args[0])
        frequency = int(args[1])
        
        if frequency < 1:
            raise ValueError("Frequência deve ser maior que 0")
        
        poll_manager.set_poll_frequency(canal_id, frequency)
        await update.message.reply_text(
            f"✅ Enquetes configuradas para canal {canal_id}\n"
            f"📊 Frequência: a cada {frequency} horas"
        )
    
    except (ValueError, IndexError) as e:
        await update.message.reply_text(f"Erro na configuração: {e}")

async def status_enquetes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Comando restrito ao administrador.\n\n"
            "🇧🇷 Para adquirir este bot, entre em contato com @rogee_rdvv\n"
            "🇺🇸 To acquire this bot, contact @rogee_rdvv",
            parse_mode='Markdown'
        )
        return
    
    status_text = "📊 *Status das Enquetes:*\n\n"
    
    for canal in CANAIS_DESTINO:
        stats = poll_manager.get_poll_stats(canal)
        should_send = "✅" if poll_manager.should_send_poll(canal) else "⏰"
        
        status_text += f"{should_send} *Canal {canal}:*\n"
        status_text += f"   • Total de enquetes: {stats['total_polls']}\n"
        status_text += f"   • Última enquete: {stats['last_poll']}\n"
        status_text += f"   • Próxima enquete: {'Agora' if poll_manager.should_send_poll(canal) else 'Aguardando'}\n\n"
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def enquete_agora(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Comando restrito ao administrador.\n\n"
            "🇧🇷 Para adquirir este bot, entre em contato com @rogee_rdvv\n"
            "🇺🇸 To acquire this bot, contact @rogee_rdvv",
            parse_mode='Markdown'
        )
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("Uso: /enqueteagora <canal_id>")
        return
    
    try:
        canal_id = int(args[0])
        from bot.telegram_bot import send_poll_to_canal
        await send_poll_to_canal(context, canal_id)
        await update.message.reply_text(f"✅ Enquete enviada para canal {canal_id}")
    
    except (ValueError, Exception) as e:
        await update.message.reply_text(f"Erro ao enviar enquete: {e}")

async def delete_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔥 COMANDO DESTRUIDOR - Apaga TODAS as mensagens do bot nos canais! 💀"""
    if not update.message or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Acesso negado, SEU ARROMBADO! 🖕")
        return
    
    # Confirma se o cara tem CERTEZA
    args = context.args
    if not args or args[0] != "CONFIRMAR":
        await update.message.reply_text(
            "🚨 **ATENÇÃO, SEU MALUCO!** 🚨\n\n"
            "Este comando vai **DELETAR TODAS** as mensagens que o bot enviou nos canais!\n\n"
            "⚠️ **NÃO TEM VOLTA, ARROMBADO!** ⚠️\n\n"
            "Se tu tem CERTEZA, digita:\n"
            "`/deletartudo CONFIRMAR`\n\n"
            "💀 **Use com RESPONSABILIDADE, seu animal!**",
            parse_mode='Markdown'
        )
        return
    
    await update.message.reply_text("🔥 **INICIANDO OPERAÇÃO LIMPEZA...** 💣")
    
    try:
        from db.db import connect
        
        conn = connect()
        c = conn.cursor()
        
        total_deleted = 0
        total_errors = 0
        
        # Busca TODAS as mensagens enviadas que ainda não foram deletadas
        c.execute("""
            SELECT canal_id, message_id, id FROM mensagens_enviadas 
            WHERE deletado = 0
            ORDER BY data_envio DESC
        """)
        
        messages = c.fetchall()
        
        if not messages:
            await update.message.reply_text("😅 Nenhuma mensagem pra deletar, seu trouxa! O bot tá limpo!")
            conn.close()
            return
        
        await update.message.reply_text(f"📊 Encontrei **{len(messages)}** mensagens pra DESTRUIR! 💀")
        
        # LOOP DESTRUIDOR - Apaga uma por uma!
        for canal_id, message_id, db_id in messages:
            try:
                await context.bot.delete_message(chat_id=canal_id, message_id=message_id)
                
                # Marca como deletada no banco
                c.execute("UPDATE mensagens_enviadas SET deletado = 1 WHERE id = ?", (db_id,))
                
                total_deleted += 1
                
            except Exception as e:
                total_errors += 1
                print(f"Erro ao deletar mensagem {message_id} do canal {canal_id}: {e}")
        
        conn.commit()
        conn.close()
        
        # Relatório final
        await update.message.reply_text(
            f"✅ **OPERAÇÃO CONCLUÍDA!** 🎉\n\n"
            f"💥 **Mensagens DESTRUÍDAS:** {total_deleted}\n"
            f"❌ **Erros:** {total_errors}\n\n"
            f"🔥 **Teu bot agora é um FANTASMA!** 👻",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"Erro na operação limpeza: {e}")

async def status_nichos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o status de todos os nichos."""
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Comando restrito ao administrador.\n\n"
            "🇧🇷 Para adquirir este bot, entre em contato com @rogee_rdvv\n"
            "🇺🇸 To acquire this bot, contact @rogee_rdvv",
            parse_mode='Markdown'
        )
        return

    all_schedules = smart_scheduler.get_all_canal_schedules()
    status_text = "📊 *Status de todos os nichos:*\n\n"
    for canal_id in CANAIS_DESTINO:
        horarios = all_schedules.get(canal_id, [])
        status_text += f"*Canal {canal_id}:*\n"
        if horarios:
            for horario in horarios:
                status_text += f"   ⏰ {horario}\n"
        else:
            status_text += "   Nenhum horário configurado.\n"
        status_text += "\n"
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def debug_canais(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔍 DEBUG - Mostra informações dos canais monitorados! 🎯"""
    if not update.message or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Sai fora, intruso! 🖕")
        return
    
    try:
        from config import CANAL_MAPPINGS, CANAIS_FONTE
        from db.db import connect
        
        debug_text = "🔍 **DEBUG DOS CANAIS:**\n\n"
        
        conn = connect()
        c = conn.cursor()
        
        # Verifica cada canal fonte
        for nicho, config in CANAL_MAPPINGS.items():
            fonte = config['fonte']
            destino = config['destino']
            
            debug_text += f"🎯 **{nicho.upper()}:**\n"
            debug_text += f"   📥 Fonte: `{fonte}`\n"
            debug_text += f"   📤 Destino: `{destino}`\n"
            
            # Verifica se o bot consegue acessar o canal
            try:
                chat_info = await context.bot.get_chat(fonte)
                debug_text += f"   ✅ Bot tem acesso: {chat_info.title}\n"
                debug_text += f"   👥 Tipo: {chat_info.type}\n"
            except Exception as e:
                debug_text += f"   ❌ Bot SEM acesso: {str(e)[:50]}...\n"
            
            # Verifica posts salvos
            c.execute("SELECT COUNT(*) FROM posts WHERE canal_fonte = ?", (fonte,))
            result = c.fetchone()
            posts_salvos = result[0] if result else 0
            debug_text += f"   📊 Posts salvos: {posts_salvos}\n\n"
        
        # Status geral do banco
        c.execute("SELECT COUNT(*) FROM posts")
        total_posts = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM posts WHERE canal_fonte IS NOT NULL AND nicho IS NOT NULL")
        posts_com_nicho = c.fetchone()[0]
        
        debug_text += f"📊 **RESUMO DO BANCO:**\n"
        debug_text += f"   • Total de posts: {total_posts}\n"
        debug_text += f"   • Posts com nicho: {posts_com_nicho}\n"
        debug_text += f"   • Posts sem nicho: {total_posts - posts_com_nicho}\n\n"
        
        debug_text += f"🤖 **HANDLERS ATIVOS:**\n"
        debug_text += f"   • Canais monitorados: {len(CANAIS_FONTE)}\n"
        debug_text += f"   • Lista: {', '.join(map(str, CANAIS_FONTE))}\n\n"
        
        debug_text += "💡 **DICAS:**\n"
        debug_text += "• Se 'Bot SEM acesso', adicione o bot como ADMIN no canal fonte\n"
        debug_text += "• Se 'Posts salvos: 0', poste algo nos canais fonte\n"
        debug_text += "• Use `/forcarpost` pra testar envio manual"
        
        conn.close()
        await update.message.reply_text(debug_text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Erro no debug: {e}")

async def forcar_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🚀 FORÇA um post de teste de qualquer nicho! 💣"""
    if not update.message or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Comando restrito ao administrador.")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text(
            "📋 **Uso:**\n"
            "`/forcarpost nicho`\n\n"
            "**Nichos disponíveis:**\n"
            "• novin\n• leaks\n• latinas\n• coroas\n• ourovip\n• backdoor\n\n"
            "**Exemplo:** `/forcarpost novin`",
            parse_mode='Markdown'
        )
        return
    
    nicho_escolhido = args[0].lower()
    
    try:
        from config import CANAL_MAPPINGS
        from bot.nicho_caption_generator import nicho_caption_generator
        
        if nicho_escolhido not in CANAL_MAPPINGS:
            await update.message.reply_text(f"❌ Nicho '{nicho_escolhido}' não existe!")
            return
        
        config = CANAL_MAPPINGS[nicho_escolhido]
        canal_destino = config['destino']
        canal_fonte = config['fonte']
        
        # Gera uma legenda do nicho específico
        legenda = nicho_caption_generator.generate_caption_by_fonte(canal_fonte)
        
        # Envia mensagem de teste
        test_message = f"🧪 **TESTE DO NICHO {nicho_escolhido.upper()}:**\n\n{legenda}"
        
        sent_message = await context.bot.send_message(
            chat_id=canal_destino,
            text=test_message,
            parse_mode='HTML'
        )
        
        await update.message.reply_text(
            f"✅ **Post de teste enviado!**\n\n"
            f"🎯 Nicho: {nicho_escolhido}\n"
            f"📤 Canal destino: `{canal_destino}`\n"
            f"📬 Message ID: {sent_message.message_id}",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao forçar post: {e}")

async def limpar_banco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🗑️ LIMPA o banco de dados (posts antigos sem nicho)! 💀"""
    if not update.message or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Acesso negado!")
        return
    
    args = context.args
    if not args or args[0] != "CONFIRMAR":
        await update.message.reply_text(
            "🚨 **ATENÇÃO!**\n\n"
            "Este comando vai **DELETAR** todos os posts antigos sem nicho definido!\n\n"
            "Se tem certeza, digite:\n"
            "`/limparbanco CONFIRMAR`",
            parse_mode='Markdown'
        )
        return
    
    try:
        from db.db import connect
        
        conn = connect()
        c = conn.cursor()
        
        # Conta posts sem nicho
        c.execute("SELECT COUNT(*) FROM posts WHERE canal_fonte IS NULL OR nicho IS NULL")
        posts_sem_nicho = c.fetchone()[0]
        
        if posts_sem_nicho == 0:
            await update.message.reply_text("✅ Banco já está limpo! Nenhum post sem nicho encontrado.")
            conn.close()
            return
        
        # Remove posts sem nicho
        c.execute("DELETE FROM posts WHERE canal_fonte IS NULL OR nicho IS NULL")
        c.execute("DELETE FROM envios WHERE nicho IS NULL")
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"🗑️ **Limpeza concluída!**\n\n"
            f"💀 Posts removidos: {posts_sem_nicho}\n"
            f"✅ Banco agora só tem posts com nicho definido!",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await update.message.reply_text(f"Erro na limpeza: {e}")

async def postar_todos_agora(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🚀 FORÇA envio de TODOS os nichos pendentes IGNORANDO rate limit! 💣"""
    if not update.message or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Comando restrito ao administrador.")
        return
    
    await update.message.reply_text("🚀 **ENVIANDO TODOS OS POSTS PENDENTES...**\n\n⚠️ Ignorando rate limit!")
    
    try:
        from db.db import connect
        from config import CANAL_MAPPINGS
        from bot.nicho_caption_generator import nicho_caption_generator
        
        conn = connect()
        c = conn.cursor()
        
        total_enviados = 0
        
        for nicho, config in CANAL_MAPPINGS.items():
            canal_fonte = config['fonte']
            canal_destino = config['destino']
            
            # Busca posts pendentes deste nicho
            c.execute("""
                SELECT id_post, media_type, media_file_id, caption FROM posts
                WHERE canal_fonte = ? AND nicho = ?
                  AND id_post NOT IN (SELECT id_post FROM envios WHERE nicho = ? AND id_post IS NOT NULL)
                ORDER BY timestamp ASC
                LIMIT 1
            """, (canal_fonte, nicho, nicho))
            
            row = c.fetchone()
            if not row:
                continue
            
            id_post, media_type, media_file_id, caption = row
            
            # Gera caption específica do nicho
            nicho_caption = nicho_caption_generator.generate_caption_by_fonte(canal_fonte)
            
            try:
                sent_message = None
                if media_type == "photo":
                    sent_message = await context.bot.send_photo(
                        chat_id=canal_destino, 
                        photo=media_file_id, 
                        caption=nicho_caption, 
                        parse_mode='HTML'
                    )
                elif media_type == "video":
                    sent_message = await context.bot.send_video(
                        chat_id=canal_destino, 
                        video=media_file_id, 
                        caption=nicho_caption, 
                        parse_mode='HTML'
                    )
                elif media_type == "document":
                    sent_message = await context.bot.send_document(
                        chat_id=canal_destino, 
                        document=media_file_id, 
                        caption=nicho_caption, 
                        parse_mode='HTML'
                    )
                elif media_type == "text":
                    sent_message = await context.bot.send_message(
                        chat_id=canal_destino, 
                        text=nicho_caption, 
                        parse_mode='HTML'
                    )
                
                if sent_message:
                    # Marca como enviado
                    c.execute(
                        "INSERT INTO envios (id_post, canal_destino, data_envio, nicho) VALUES (?, ?, datetime('now'), ?)",
                        (id_post, canal_destino, nicho)
                    )
                    total_enviados += 1
                    print(f"💥 FORÇADO: Post {id_post} do nicho {nicho} enviado!")
                    
                    # Delay para não quebrar o Telegram
                    await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Erro ao enviar {nicho}: {e}")
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ **MISSÃO CUMPRIDA!**\n\n"
            f"🚀 Posts enviados: {total_enviados}\n"
            f"🎯 Todos os nichos processados!",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao enviar todos: {e}")

async def configurar_horarios_canal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """⏰ CONFIGURA horários específicos para cada canal! 🎯"""
    if not update.message or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Comando restrito ao administrador.")
        return
    
    args = context.args
    if not args or len(args) < 3:
        await update.message.reply_text(
            "📋 **Uso correto:**\n\n"
            "`/horarios CANAL_ID ACAO HORARIO`\n\n"
            "**Ações:**\n"
            "• `add` - Adiciona horário\n"
            "• `remove` - Remove horário\n"
            "• `list` - Lista horários\n\n"
            "**Exemplos:**\n"
            "`/horarios -1002574788580 add 14:30`\n"
            "`/horarios -1002574788580 remove 14:30`\n"
            "`/horarios -1002574788580 list`\n\n"
            "💡 **Canais disponíveis:**\n"
            "• Novin: -1002574788580\n"
            "• Leaks: -1002651133010\n"
            "• Latinas: -1002707898874\n"
            "• Coroas: -1002765829939\n"
            "• OuroVIP: -1002870159887\n"
            "• Backdoor: -1002759274414",
            parse_mode='Markdown'
        )
        return
    
    try:
        canal_id = int(args[0])
        acao = args[1].lower()
        
        from bot.smart_scheduler import smart_scheduler
        
        if acao == "list":
            horarios = smart_scheduler.get_schedules(canal_id)
            if horarios:
                horarios_text = '\n'.join([f"   ⏰ {h}" for h in horarios])
                text = f"📅 **Horários do canal {canal_id}:**\n\n{horarios_text}"
            else:
                text = f"📅 Canal {canal_id} não tem horários específicos (posta sempre)"
            
            await update.message.reply_text(text, parse_mode='Markdown')
            return
        
        if len(args) < 3:
            await update.message.reply_text("❌ Horário obrigatório para add/remove!")
            return
        
        horario = args[2]
        
        # Validar formato do horário
        if ':' not in horario or len(horario.split(':')) != 2:
            await update.message.reply_text("❌ Formato inválido! Use HH:MM (ex: 14:30)")
            return
        
        hour, minute = map(int, horario.split(':'))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Horário inválido")
        
        if acao == "add":
            if smart_scheduler.add_schedule(canal_id, horario):
                await update.message.reply_text(f"✅ Horário {horario} adicionado para canal {canal_id}")
            else:
                await update.message.reply_text("❌ Erro ao adicionar horário")
        elif acao == "remove":
            smart_scheduler.remove_schedule(canal_id, horario)
            await update.message.reply_text(f"✅ Horário {horario} removido do canal {canal_id}")
        else:
            await update.message.reply_text("❌ Ação inválida! Use: add, remove, list")
    
    except (ValueError, IndexError) as e:
        await update.message.reply_text(f"❌ Erro: {e}")

async def horarios_rapidos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🚀 CONFIGURA horários rápidos para todos os canais! ⚡"""
    if not update.message or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Comando restrito ao administrador.")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text(
            "🚀 **Configurações Rápidas de Horários:**\n\n"
            "`/horariosrapidos agressivo` - A cada 2 horas\n"
            "`/horariosrapidos normal` - A cada 4 horas\n"
            "`/horariosrapidos conservador` - A cada 8 horas\n"
            "`/horariosrapidos livre` - Remove todos os horários\n\n"
            "💡 Aplica para TODOS os canais destino!",
            parse_mode='Markdown'
        )
        return
    
    modo = args[0].lower()
    
    try:
        from config import CANAIS_DESTINO
        from bot.smart_scheduler import smart_scheduler
        
        # Horários predefinidos
        horarios_map = {
            'agressivo': ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
            'normal': ['08:00', '12:00', '16:00', '20:00'],
            'conservador': ['10:00', '18:00'],
            'livre': []
        }
        
        if modo not in horarios_map:
            await update.message.reply_text("❌ Modo inválido! Use: agressivo, normal, conservador, livre")
            return
        
        horarios = horarios_map[modo]
        configurados = 0
        
        for canal in CANAIS_DESTINO:
            # Remove horários existentes
            existing = smart_scheduler.get_schedules(canal)
            for h in existing:
                smart_scheduler.remove_schedule(canal, h)
            
            # Adiciona novos horários
            for horario in horarios:
                if smart_scheduler.add_schedule(canal, horario):
                    configurados += 1
        
        if modo == 'livre':
            await update.message.reply_text(
                "🔓 **Modo LIVRE ativado!**\n\n"
                "✅ Todos os horários removidos\n"
                "🚀 Bot vai postar assim que receber conteúdo!"
            )
        else:
            await update.message.reply_text(
                f"✅ **Modo {modo.upper()} configurado!**\n\n"
                f"⏰ Horários: {', '.join(horarios)}\n"
                f"📊 Total configurado: {configurados} horários\n"
                f"🎯 Aplicado em {len(CANAIS_DESTINO)} canais"
            )
    
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao configurar: {e}")

def get_command_handlers():
    return [
        CommandHandler("start", start),
        CommandHandler("statusnichos", status_nichos),
        CommandHandler("postaragora", postar_agora),
        CommandHandler("postartodos", postar_todos_agora),
        CommandHandler("deletartudo", delete_all_messages),
        CommandHandler("debug", debug_canais),
        CommandHandler("forcarpost", forcar_post),
        CommandHandler("limparbanco", limpar_banco),
        CommandHandler("horarios", configurar_horarios_canal),  # NOVO!
        CommandHandler("horariosrapidos", horarios_rapidos),    # NOVO!
    ]