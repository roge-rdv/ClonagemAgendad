from config import SCHEDULE_HOURS
from bot.telegram_bot import send_scheduled_posts
from bot.smart_scheduler import smart_scheduler

def start_scheduler(app=None):
    """Inicia o agendador com base no SCHEDULE_HOURS configurado."""
    if app is not None:
        # Converte horas para segundos
        interval_seconds = SCHEDULE_HOURS * 3600
        # Executa baseado no intervalo configurado em config.py
        app.job_queue.run_repeating(send_scheduled_posts, interval=interval_seconds)
        print(f"Scheduler iniciado: envios a cada {SCHEDULE_HOURS} horas ({interval_seconds} segundos)")
