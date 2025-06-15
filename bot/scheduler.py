from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from bot.telegram_bot import send_scheduled_posts

scheduler = AsyncIOScheduler()

def start_scheduler(app):
    """Inicia o agendador para envio automático de posts."""
    
    # 🔥 AQUI TU MUDA O INTERVALO PRINCIPAL!
    # Opções:
    # seconds=30 - A cada 30 segundos (MAIS AGRESSIVO)
    # minutes=5 - A cada 5 minutos (BALANCEADO)
    # hours=1 - A cada 1 hora (MAIS CONSERVADOR)
    
    scheduler.add_job(
        send_scheduled_posts,
        trigger=IntervalTrigger(hours=1),  # 🎯 MUDA AQUI!
        args=[app],
        id='send_posts',
        replace_existing=True
    )
    
    scheduler.start()
    print("📅 Scheduler iniciado: verificando posts a cada 30 segundos")
