from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, CallbackQueryHandler
from bot.rate_limiter import rate_limiter
from config import CANAIS_DESTINO
from bot.smart_scheduler import smart_scheduler
from bot.watermark_manager import watermark_manager
from bot.caption_formatter import caption_formatter
from bot.poll_manager import poll_manager
from captions.caption_loader import caption_loader
from bot.inline_menu import inline_menu
from bot.setup_wizard import setup_wizard, WIZARD_STEP_1, WIZARD_STEP_2, WIZARD_STEP_3, WIZARD_STEP_4, WIZARD_CONFIRM
from bot.help_system import help_system

# Defina o ID do admin do bot (pode ser seu user_id)
BOT_ADMIN_ID = 8169883791  # Substitua pelo seu ID

def is_admin(user_id):
    return user_id == BOT_ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Mostra o menu principal."""
    if not update.message or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Acesso negado. Este bot é restrito ao administrador.\n\n"
            "🇧🇷 Para adquirir este bot, entre em contato com @rogee_rdvv\n"
            "🇺🇸 To acquire this bot, contact @rogee_rdvv\n"
            "🇪🇦 Para comprar este bot, comuníquese con @rogee_rdvv",
            parse_mode='Markdown'
        )
        return
    
    text = inline_menu.get_menu_text('main')
    keyboard = inline_menu.get_menu_keyboard('main')
    
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)

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
    # Chama a função de envio imediato
    from bot.telegram_bot import send_scheduled_posts
    await send_scheduled_posts(context)
    await update.message.reply_text("Postagem executada imediatamente!")

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

def get_command_handlers():
    return [
        CommandHandler("start", start),
        CommandHandler("menu", menu_command),  # Mantém /menu como alias
        CommandHandler("postaragora", postar_agora),
        CommandHandler("ratelimit", status_rate_limit),
        CommandHandler("configurarhorarios", configurar_horarios),
        CommandHandler("listarhorarios", listar_horarios),
        CommandHandler("configurarwatermark", configurar_watermark),
        CommandHandler("configurarestilo", configurar_estilo),
        CommandHandler("configurarenquetes", configurar_enquetes),
        CommandHandler("statusenquetes", status_enquetes),
        CommandHandler("enqueteagora", enquete_agora),
        # Wizard de configuração
        ConversationHandler(
            entry_points=[
                CommandHandler("setup", setup_command),
                CallbackQueryHandler(setup_command, pattern=r"^setup_wizard$")  # NOVO: permite iniciar via botão
            ],
            states={
                WIZARD_STEP_1: [CallbackQueryHandler(setup_wizard.wizard_step_1, pattern=r"^wiz_")],
                WIZARD_STEP_2: [CallbackQueryHandler(setup_wizard.wizard_step_2, pattern=r"^wiz_")],
                WIZARD_STEP_3: [CallbackQueryHandler(setup_wizard.wizard_step_3, pattern=r"^wiz_")],
                WIZARD_STEP_4: [CallbackQueryHandler(setup_wizard.wizard_step_4, pattern=r"^wiz_")],
                WIZARD_CONFIRM: [CallbackQueryHandler(setup_wizard.wizard_finish, pattern=r"^wiz_")]
            },
            fallbacks=[CommandHandler("cancel", setup_wizard.wizard_cancel)]
        ),
        # Handler para callback queries do menu (DEVE ser o último)
        CallbackQueryHandler(handle_callback_query)
    ]