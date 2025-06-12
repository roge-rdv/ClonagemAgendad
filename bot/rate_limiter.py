import time
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self):
        # Armazena timestamps dos últimos envios por canal
        self.send_history = defaultdict(deque)
        # Configurações de limite
        self.max_messages_per_minute = 20  # Máximo 20 mensagens por minuto por canal
        self.max_messages_per_hour = 200   # Máximo 200 mensagens por hora por canal
        self.min_interval_between_sends = 3  # Mínimo 3 segundos entre envios
        
    def can_send(self, canal_id):
        """
        Verifica se é seguro enviar mensagem para o canal.
        Returns: (bool, float) - (pode_enviar, tempo_para_esperar)
        """
        now = time.time()
        history = self.send_history[canal_id]
        
        # Remove timestamps antigos (mais de 1 hora)
        while history and now - history[0] > 3600:
            history.popleft()
        
        # Verifica limite por hora
        if len(history) >= self.max_messages_per_hour:
            oldest = history[0]
            wait_time = 3600 - (now - oldest)
            return False, wait_time
        
        # Verifica limite por minuto
        recent_messages = sum(1 for t in history if now - t < 60)
        if recent_messages >= self.max_messages_per_minute:
            # Encontra o timestamp mais antigo dos últimos 60 segundos
            recent_timestamps = [t for t in history if now - t < 60]
            oldest_recent = min(recent_timestamps)
            wait_time = 60 - (now - oldest_recent)
            return False, wait_time
        
        # Verifica intervalo mínimo entre envios
        if history and now - history[-1] < self.min_interval_between_sends:
            wait_time = self.min_interval_between_sends - (now - history[-1])
            return False, wait_time
        
        return True, 0
    
    def record_send(self, canal_id):
        """Registra que uma mensagem foi enviada para o canal."""
        now = time.time()
        self.send_history[canal_id].append(now)
    
    def get_stats(self, canal_id):
        """Retorna estatísticas de uso do canal."""
        now = time.time()
        history = self.send_history[canal_id]
        
        # Remove timestamps antigos
        while history and now - history[0] > 3600:
            history.popleft()
        
        last_hour = len(history)
        last_minute = sum(1 for t in history if now - t < 60)
        last_send = history[-1] if history else 0
        
        return {
            'messages_last_hour': last_hour,
            'messages_last_minute': last_minute,
            'last_send_ago': now - last_send if last_send else 0,
            'can_send_now': self.can_send(canal_id)[0]
        }

# Instância global do rate limiter
rate_limiter = RateLimiter()
