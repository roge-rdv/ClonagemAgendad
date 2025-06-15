import sqlite3
from datetime import datetime, time
from db.db import connect

class SmartScheduler:
    def __init__(self):
        self.create_schedule_table()
    
    def create_schedule_table(self):
        """Cria tabela para armazenar horários personalizados por canal."""
        try:
            conn = connect()
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS canal_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    canal_id INTEGER NOT NULL,
                    horario TEXT NOT NULL,
                    ativo BOOLEAN DEFAULT 1,
                    UNIQUE(canal_id, horario)
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erro ao criar tabela de horários: {e}")
    
    def add_schedule(self, canal_id, horario):
        """Adiciona um horário para um canal específico."""
        try:
            conn = connect()
            c = conn.cursor()
            c.execute(
                "INSERT OR IGNORE INTO canal_schedules (canal_id, horario, ativo) VALUES (?, ?, 1)",
                (canal_id, horario)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao adicionar horário: {e}")
            return False
    
    def remove_schedule(self, canal_id, horario):
        """Remove um horário de um canal específico."""
        try:
            conn = connect()
            c = conn.cursor()
            c.execute(
                "DELETE FROM canal_schedules WHERE canal_id = ? AND horario = ?",
                (canal_id, horario)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erro ao remover horário: {e}")
    
    def get_schedules(self, canal_id):
        """Retorna todos os horários ativos de um canal."""
        try:
            conn = connect()
            c = conn.cursor()
            c.execute(
                "SELECT horario FROM canal_schedules WHERE canal_id = ? AND ativo = 1 ORDER BY horario",
                (canal_id,)
            )
            schedules = [row[0] for row in c.fetchall()]
            conn.close()
            return schedules
        except Exception as e:
            print(f"Erro ao buscar horários: {e}")
            return []
    
    def should_post_now(self, canal_id, current_time=None):
        """Verifica se deve postar agora para um canal específico."""
        schedules = self.get_schedules(canal_id)
        
        # Se há horários personalizados configurados, usa eles
        if schedules:
            if current_time is None:
                current_time = datetime.now().strftime("%H:%M")
            return current_time in schedules
        
        # MUDANÇA: Se não há horários personalizados, SEMPRE PODE POSTAR! 🔥
        # Antes estava muito restritivo, agora é mais agressivo
        return True
    
    def get_next_post_time(self, canal_id, current_time=None):
        """Retorna o próximo horário de postagem para um canal."""
        if current_time is None:
            current_time = datetime.now().time()
        
        schedules = self.get_schedules(canal_id)
        if not schedules:
            return None
        
        # Converte horários para objetos time
        schedule_times = []
        for schedule in schedules:
            try:
                hour, minute = map(int, schedule.split(':'))
                schedule_times.append(time(hour, minute))
            except:
                continue
        
        # Encontra o próximo horário
        for schedule_time in schedule_times:
            if schedule_time > current_time:
                return schedule_time.strftime("%H:%M")
        
        # Se não há horário hoje, retorna o primeiro de amanhã
        if schedule_times:
            return schedule_times[0].strftime("%H:%M")
        
        return None
    
    def get_all_canal_schedules(self):
        """Retorna todos os agendamentos de todos os canais."""
        try:
            conn = connect()
            c = conn.cursor()
            c.execute("""
                SELECT canal_id, GROUP_CONCAT(horario, ', ') as horarios
                FROM canal_schedules 
                WHERE ativo = 1 
                GROUP BY canal_id
            """)
            result = {}
            for row in c.fetchall():
                result[row[0]] = row[1].split(', ') if row[1] else []
            conn.close()
            return result
        except Exception as e:
            print(f"Erro ao buscar todos os horários: {e}")
            return {}

# Instância global do smart scheduler
smart_scheduler = SmartScheduler()
