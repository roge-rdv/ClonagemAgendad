from telegram import Update, InputMediaPhoto, InputMediaVideo, InputMediaDocument
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from db.db import connect
from config import TELEGRAM_BOT_TOKEN, CANAL_FONTE_ID, CANAIS_DESTINO
from bot.caption_generator import generate_caption
from bot.rate_limiter import rate_limiter
from bot.smart_scheduler import smart_scheduler
from bot.watermark_manager import watermark_manager
from bot.caption_formatter import caption_formatter
from datetime import datetime
import asyncio
from bot.commands import get_command_handlers
from bot.poll_manager import poll_manager

async def handle_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return

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
    else:
        return

    caption = message.caption or ""
    post_id = str(message.message_id)
    timestamp = message.date

    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO posts (id_post, media_type, media_file_id, caption, timestamp, media_group_id) VALUES (?, ?, ?, ?, ?, ?)",
        (post_id, media_type, media_file_id, caption, timestamp, media_group_id)
    )
    conn.commit()
    conn.close()

async def send_scheduled_posts(context):
    current_time = datetime.now().strftime("%H:%M")
    
    # Verifica se deve enviar enquetes para algum canal
    for canal in CANAIS_DESTINO:
        if poll_manager.should_send_poll(canal):
            await send_poll_to_canal(context, canal)
    
    conn = connect()
    c = conn.cursor()
    # Busca primeiro álbum não enviado, senão busca mensagem individual
    c.execute("""
        SELECT media_group_id FROM posts
        WHERE media_group_id IS NOT NULL
          AND media_group_id NOT IN (SELECT DISTINCT media_group_id FROM envios WHERE media_group_id IS NOT NULL)
        ORDER BY timestamp ASC
        LIMIT 1
    """)
    group_row = c.fetchone()
    if group_row and group_row[0]:
        # Enviar álbum
        media_group_id = group_row[0]
        c.execute("""
            SELECT id_post, media_type, media_file_id, caption FROM posts
            WHERE media_group_id = ?
            ORDER BY timestamp ASC
        """, (media_group_id,))
        rows = c.fetchall()
        
        for canal in CANAIS_DESTINO:
            # Verifica se deve postar agora para este canal específico
            if not smart_scheduler.should_post_now(canal, current_time):
                continue
            
            # Verifica rate limiting
            can_send, wait_time = rate_limiter.can_send(canal)
            if not can_send:
                print(f"Rate limit atingido para canal {canal}. Aguardando {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
            
            # Cria media list específica para este canal
            media = []
            for idx, (id_post, media_type, media_file_id, caption) in enumerate(rows):
                cap = generate_caption({"caption": caption}, canal) if idx == 0 else None
                
                # Aplica watermark se for imagem
                if media_type == "photo":
                    watermarked_image = watermark_manager.add_watermark_to_image(media_file_id, canal, context.bot)
                    if watermarked_image:
                        media.append(InputMediaPhoto(watermarked_image, caption=cap, parse_mode='HTML'))
                    else:
                        media.append(InputMediaPhoto(media_file_id, caption=cap, parse_mode='HTML'))
                elif media_type == "video":
                    media.append(InputMediaVideo(media_file_id, caption=cap, parse_mode='HTML'))
                elif media_type == "document":
                    media.append(InputMediaDocument(media_file_id, caption=cap, parse_mode='HTML'))
            
            try:
                await context.bot.send_media_group(chat_id=canal, media=media)
                rate_limiter.record_send(canal)
                print(f"Álbum enviado para canal {canal} no horário agendado {current_time}")
            except Exception as e:
                print(f"Erro ao enviar para canal {canal}: {e}")
            
            for (id_post, _, _, _) in rows:
                c.execute(
                    "INSERT INTO envios (id_post, canal_destino, data_envio, media_group_id) VALUES (?, ?, datetime('now'), ?)",
                    (id_post, canal, media_group_id)
                )
        conn.commit()
        conn.close()
        return

    # Se não há álbum pendente, envia mensagem individual
    c.execute("""
        SELECT id_post, media_type, media_file_id, caption FROM posts
        WHERE media_group_id IS NULL
          AND id_post NOT IN (SELECT id_post FROM envios)
        ORDER BY timestamp ASC
        LIMIT 1
    """)
    row = c.fetchone()
    if not row:
        conn.close()
        return

    id_post, media_type, media_file_id, caption = row

    for canal in CANAIS_DESTINO:
        # Verifica se deve postar agora para este canal específico
        if not smart_scheduler.should_post_now(canal, current_time):
            continue
        
        # Verifica rate limiting
        can_send, wait_time = rate_limiter.can_send(canal)
        if not can_send:
            print(f"Rate limit atingido para canal {canal}. Aguardando {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        
        # Gera caption específica para este canal
        formatted_caption = generate_caption({"caption": caption}, canal)
        
        try:
            if media_type == "photo":
                # Tenta adicionar watermark
                watermarked_image = watermark_manager.add_watermark_to_image(media_file_id, canal, context.bot)
                if watermarked_image:
                    await context.bot.send_photo(chat_id=canal, photo=watermarked_image, caption=formatted_caption, parse_mode='HTML')
                else:
                    await context.bot.send_photo(chat_id=canal, photo=media_file_id, caption=formatted_caption, parse_mode='HTML')
            elif media_type == "video":
                await context.bot.send_video(chat_id=canal, video=media_file_id, caption=formatted_caption, parse_mode='HTML')
            elif media_type == "document":
                await context.bot.send_document(chat_id=canal, document=media_file_id, caption=formatted_caption, parse_mode='HTML')
            
            rate_limiter.record_send(canal)
            print(f"Post {id_post} enviado para canal {canal} no horário agendado {current_time}")
        except Exception as e:
            print(f"Erro ao enviar para canal {canal}: {e}")
        
        c.execute(
            "INSERT INTO envios (id_post, canal_destino, data_envio) VALUES (?, ?, datetime('now'))",
            (id_post, canal)
        )
    conn.commit()
    conn.close()

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
        
        print(f"Enquete enviada para canal {canal_id}: {poll_data['question']}")
        
    except Exception as e:
        print(f"Erro ao enviar enquete para canal {canal_id}: {e}")

def start_bot():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    # Adiciona handlers de comandos
    for handler in get_command_handlers():
        app.add_handler(handler)
    # Handler para novas mensagens do canal fonte
    app.add_handler(MessageHandler(filters.Chat(CANAL_FONTE_ID), handle_new_post))
    from bot.scheduler import start_scheduler
    start_scheduler(app)
    app.run_polling()
