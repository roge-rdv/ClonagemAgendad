from config import SCHEDULE_HOURS
from bot.telegram_bot import send_scheduled_posts
from bot.smart_scheduler import smart_scheduler

def start_scheduler(app=None):
    """Inicia o agendador com verificação a cada minuto para horários personalizados."""
    if app is not None:
        # Executa a cada minuto para verificar horários personalizados
        app.job_queue.run_repeating(send_scheduled_posts, interval=60)
