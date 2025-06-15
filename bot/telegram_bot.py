from telegram import Update, InputMediaPhoto, InputMediaVideo, InputMediaDocument
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from db.db import connect
from config import TELEGRAM_BOT_TOKEN, CANAIS_FONTE, get_nicho_by_fonte, get_destino_by_fonte
from bot.nicho_caption_generator import nicho_caption_generator
from bot.rate_limiter import rate_limiter
from bot.smart_scheduler import smart_scheduler
from datetime import datetime
import asyncio

# Imports opcionais (se existirem)
try:
    from bot.commands import get_command_handlers
except ImportError:
    def get_command_handlers():
        return []

try:
    from bot.poll_manager import poll_manager
except ImportError:
    class DummyPollManager:
        def should_send_poll(self, canal): return False
        def record_poll_sent(self, canal, question, poll_id): pass
        def get_random_poll(self): return {"question": "Test", "options": ["A", "B"], "anonymous": True}
    poll_manager = DummyPollManager()

try:
    from bot.watermark_manager import watermark_manager
except ImportError:
    class DummyWatermarkManager:
        def add_watermark_to_image(self, file_id, canal, bot): return None
    watermark_manager = DummyWatermarkManager()

def register_sent_message(canal_id, message_id, tipo_conteudo="post", nicho=None):
    """Registra mensagem enviada para controle de deleção."""
    try:
        conn = connect()
        c = conn.cursor()
        c.execute("""
            INSERT INTO mensagens_enviadas (canal_id, message_id, tipo_conteudo, nicho)
            VALUES (?, ?, ?, ?)
        """, (canal_id, message_id, tipo_conteudo, nicho))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao registrar mensagem: {e}")

async def handle_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler MULTI-NICHO - Detecta de qual nicho veio! 🎯"""
    message = update.effective_message
    if not message:
        return

    # Identifica o canal fonte
    canal_fonte_id = message.chat.id
    nicho = get_nicho_by_fonte(canal_fonte_id)
    
    print(f"📥 Nova mensagem recebida do canal {canal_fonte_id}")
    
    if not nicho:
        print(f"❌ Canal fonte {canal_fonte_id} não mapeado! Canais válidos: {CANAIS_FONTE}")
        return

    print(f"✅ Nicho identificado: {nicho}")

    media_type = None
    media_file_id = None

    # Identifica se é álbum (media group)
    media_group_id = getattr(message, "media_group_id", None)

    if message.photo:
        media_type = "photo"
        media_file_id = message.photo[-1].file_id
    elif message.video:
        media_type = "video"
        media_file_id = message.video.file_id
    elif message.document:
        media_type = "document"
        media_file_id = message.document.file_id
    elif message.text:
        # Aceita também mensagens de texto
        media_type = "text"
        media_file_id = "text_message"
    else:
        print(f"❌ Tipo de mídia não suportado: {type(message)}")
        return

    caption = message.caption or message.text or ""
    post_id = str(message.message_id)
    timestamp = message.date

    # Salva no banco com informações do nicho
    try:
        conn = connect()
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO posts (id_post, media_type, media_file_id, caption, timestamp, media_group_id, canal_fonte, nicho) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (post_id, media_type, media_file_id, caption, timestamp, media_group_id, canal_fonte_id, nicho)
        )
        conn.commit()
        conn.close()
        
        print(f"🔥 Post {post_id} salvo do nicho {nicho} (fonte: {canal_fonte_id}) - Tipo: {media_type}")
    except Exception as e:
        print(f"Erro ao salvar post: {e}")

async def send_scheduled_posts(context):
    """Envia posts agendados RESPEITANDO OS NICHOS! 🔥"""
    current_time = datetime.now().strftime("%H:%M")
    
    # Verifica se deve enviar enquetes para algum canal
    from config import CANAIS_DESTINO
    try:
        from bot.poll_manager import poll_manager
        for canal in CANAIS_DESTINO:
            if poll_manager.should_send_poll(canal):
                await send_poll_to_canal(context, canal)
    except ImportError:
        pass  # Poll manager não existe
    
    try:
        conn = connect()
        c = conn.cursor()
        
        # NOVO: Verifica se as colunas existem primeiro
        c.execute("PRAGMA table_info(posts)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'canal_fonte' not in columns or 'nicho' not in columns:
            print("⚠️ Colunas do banco desatualizadas! Execute novamente o bot...")
            conn.close()
            return
        
        # Busca posts pendentes ORGANIZADOS por nicho
        c.execute("""
            SELECT canal_fonte, nicho FROM posts
            WHERE canal_fonte IS NOT NULL 
              AND nicho IS NOT NULL
              AND id_post NOT IN (SELECT id_post FROM envios WHERE id_post IS NOT NULL)
            GROUP BY canal_fonte, nicho
            ORDER BY timestamp ASC
        """)
        
        nichos_pendentes = c.fetchall()
        
        if not nichos_pendentes:
            print("📭 Nenhum post pendente com nicho definido")
            conn.close()
            return
        
        print(f"🎯 Processando {len(nichos_pendentes)} nichos pendentes...")
        
        for canal_fonte_id, nicho in nichos_pendentes:
            canal_destino = get_destino_by_fonte(canal_fonte_id)
            if not canal_destino:
                continue
            
            print(f"🔍 Verificando nicho {nicho} - Canal destino: {canal_destino}")
            
            # MUDANÇA: Verifica rate limiting ANTES do scheduler
            can_send, wait_time = rate_limiter.can_send(canal_destino)
            if not can_send:
                print(f"⏸️ Rate limit atingido para {nicho} ({canal_destino}). Aguardando {wait_time:.1f}s")
                continue  # Pula para o próximo ao invés de aguardar
            
            # Verifica se deve postar agora para este canal específico
            should_post = smart_scheduler.should_post_now(canal_destino, current_time)
            print(f"📅 Scheduler para {nicho}: {'✅ Pode postar' if should_post else '⏰ Aguardando horário'}")
            
            if not should_post:
                continue
            
            # Busca primeiro álbum não enviado deste nicho
            c.execute("""
                SELECT media_group_id FROM posts
                WHERE canal_fonte = ? AND nicho = ? AND media_group_id IS NOT NULL
                  AND media_group_id NOT IN (SELECT DISTINCT media_group_id FROM envios WHERE media_group_id IS NOT NULL AND nicho = ?)
                ORDER BY timestamp ASC
                LIMIT 1
            """, (canal_fonte_id, nicho, nicho))
            
            group_row = c.fetchone()
            
            if group_row and group_row[0]:
                # Enviar álbum do nicho específico
                await send_album_by_nicho(context, group_row[0], canal_fonte_id, canal_destino, nicho)
            else:
                # Enviar mensagem individual do nicho específico
                await send_single_post_by_nicho(context, canal_fonte_id, canal_destino, nicho)
            
            # MUDANÇA: Delay menor entre nichos
            await asyncio.sleep(2)  # Era 1, agora é 2 segundos
        
        conn.close()
    except Exception as e:
        print(f"Erro em send_scheduled_posts: {e}")
        import traceback
        traceback.print_exc()

async def send_album_by_nicho(context, media_group_id, canal_fonte_id, canal_destino, nicho):
    """Envia álbum específico do nicho."""
    try:
        conn = connect()
        c = conn.cursor()
        
        c.execute("""
            SELECT id_post, media_type, media_file_id, caption FROM posts
            WHERE media_group_id = ? AND canal_fonte = ?
            ORDER BY timestamp ASC
        """, (media_group_id, canal_fonte_id))
        
        rows = c.fetchall()
        if not rows:
            conn.close()
            return
        
        # Cria media list específica para este nicho
        media = []
        for idx, (id_post, media_type, media_file_id, caption) in enumerate(rows):
            # Gera caption específica do nicho APENAS na primeira mídia
            if idx == 0:
                nicho_caption = nicho_caption_generator.generate_caption_by_fonte(canal_fonte_id)
            else:
                nicho_caption = None
            
            # Aplica watermark se for imagem
            if media_type == "photo":
                try:
                    watermarked_image = watermark_manager.add_watermark_to_image(media_file_id, canal_destino, context.bot)
                    if watermarked_image:
                        media.append(InputMediaPhoto(watermarked_image, caption=nicho_caption, parse_mode='HTML'))
                    else:
                        media.append(InputMediaPhoto(media_file_id, caption=nicho_caption, parse_mode='HTML'))
                except:
                    media.append(InputMediaPhoto(media_file_id, caption=nicho_caption, parse_mode='HTML'))
            elif media_type == "video":
                media.append(InputMediaVideo(media_file_id, caption=nicho_caption, parse_mode='HTML'))
            elif media_type == "document":
                media.append(InputMediaDocument(media_file_id, caption=nicho_caption, parse_mode='HTML'))
        
        sent_messages = await context.bot.send_media_group(chat_id=canal_destino, media=media)
        rate_limiter.record_send(canal_destino)
        
        # Registra mensagens enviadas
        for sent_msg in sent_messages:
            register_sent_message(canal_destino, sent_msg.message_id, "album", nicho)
        
        print(f"💥 Álbum do nicho {nicho} enviado para {canal_destino}")
        
        # Marca como enviado
        for (id_post, _, _, _) in rows:
            c.execute(
                "INSERT INTO envios (id_post, canal_destino, data_envio, media_group_id, nicho) VALUES (?, ?, datetime('now'), ?, ?)",
                (id_post, canal_destino, media_group_id, nicho)
            )
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao enviar álbum do nicho {nicho}: {e}")

async def send_single_post_by_nicho(context, canal_fonte_id, canal_destino, nicho):
    """Envia post individual específico do nicho."""
    try:
        conn = connect()
        c = conn.cursor()
        
        c.execute("""
            SELECT id_post, media_type, media_file_id, caption FROM posts
            WHERE canal_fonte = ? AND nicho = ? AND media_group_id IS NULL
              AND id_post NOT IN (SELECT id_post FROM envios WHERE nicho = ? AND id_post IS NOT NULL)
            ORDER BY timestamp ASC
            LIMIT 1
        """, (canal_fonte_id, nicho, nicho))
        
        row = c.fetchone()
        if not row:
            conn.close()
            return

        id_post, media_type, media_file_id, caption = row
        
        # Gera caption específica do nicho
        nicho_caption = nicho_caption_generator.generate_caption_by_fonte(canal_fonte_id)
        
        sent_message = None
        if media_type == "photo":
            # Tenta adicionar watermark
            try:
                from bot.watermark_manager import watermark_manager
                watermarked_image = watermark_manager.add_watermark_to_image(media_file_id, canal_destino, context.bot)
                if watermarked_image:
                    sent_message = await context.bot.send_photo(chat_id=canal_destino, photo=watermarked_image, caption=nicho_caption, parse_mode='HTML')
                else:
                    sent_message = await context.bot.send_photo(chat_id=canal_destino, photo=media_file_id, caption=nicho_caption, parse_mode='HTML')
            except:
                sent_message = await context.bot.send_photo(chat_id=canal_destino, photo=media_file_id, caption=nicho_caption, parse_mode='HTML')
        elif media_type == "video":
            sent_message = await context.bot.send_video(chat_id=canal_destino, video=media_file_id, caption=nicho_caption, parse_mode='HTML')
        elif media_type == "document":
            sent_message = await context.bot.send_document(chat_id=canal_destino, document=media_file_id, caption=nicho_caption, parse_mode='HTML')
        
        if sent_message:
            # Registra mensagem enviada
            register_sent_message(canal_destino, sent_message.message_id, media_type, nicho)
            rate_limiter.record_send(canal_destino)
            print(f"🚀 Post {id_post} do nicho {nicho} enviado para {canal_destino}")
        
        # Marca como enviado
        c.execute(
            "INSERT INTO envios (id_post, canal_destino, data_envio, nicho) VALUES (?, ?, datetime('now'), ?)",
            (id_post, canal_destino, nicho)
        )
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao enviar post do nicho {nicho}: {e}")

async def send_poll_to_canal(context, canal_id):
    """Envia uma enquete para um canal específico."""
    try:
        poll_data = poll_manager.get_random_poll()
        
        # Verifica rate limiting
        can_send, wait_time = rate_limiter.can_send(canal_id)
        if not can_send:
            print(f"Rate limit atingido para enquete no canal {canal_id}. Aguardando {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        
        # Envia a enquete
        poll_message = await context.bot.send_poll(
            chat_id=canal_id,
            question=poll_data["question"],
            options=poll_data["options"],
            is_anonymous=poll_data["anonymous"],
            allows_multiple_answers=False
        )
        
        # Registra o envio
        poll_manager.record_poll_sent(canal_id, poll_data["question"], poll_message.poll.id)
        rate_limiter.record_send(canal_id)
        register_sent_message(canal_id, poll_message.message_id, "poll")
        
        print(f"📊 Enquete enviada para canal {canal_id}: {poll_data['question']}")
        
    except Exception as e:
        print(f"Erro ao enviar enquete para canal {canal_id}: {e}")

def start_bot():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Adiciona handlers de comandos
    try:
        from bot.commands import get_command_handlers
        for handler in get_command_handlers():
            app.add_handler(handler)
    except ImportError as e:
        print(f"⚠️ Comandos não carregados: {e}")
    
    # Handler para TODOS os canais fonte (multi-nicho)
    for canal_fonte in CANAIS_FONTE:
        app.add_handler(MessageHandler(filters.Chat(canal_fonte), handle_new_post))
    
    print(f"🔥 BOT MULTI-NICHO INICIADO! Monitorando {len(CANAIS_FONTE)} canais...")
    
    # Inicia scheduler
    try:
        from bot.scheduler import start_scheduler
        start_scheduler(app)
    except ImportError:
        # Scheduler simples se não existir
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        scheduler = AsyncIOScheduler()
        scheduler.add_job(send_scheduled_posts, 'interval', seconds=30, args=[app])
        scheduler.start()
        print("📅 Scheduler básico iniciado - posts a cada 30 segundos")
    
    app.run_polling()
