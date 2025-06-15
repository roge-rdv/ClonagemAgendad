#!/bin/bash
# Deploy seguro com backup automático

echo "🚀 DEPLOY SEGURO - Bot Multi-Nicho"

# 1. Parar bot
echo "⏹️ Parando bot..."
pkill -f "python3 main.py" || echo "Bot não estava rodando"

# 2. BACKUP OBRIGATÓRIO do banco
echo "💾 Fazendo backup do banco..."
if [ -f "clonagem.db" ]; then
    cp clonagem.db "backup-$(date +%Y%m%d-%H%M%S).db"
    echo "✅ Backup criado: backup-$(date +%Y%m%d-%H%M%S).db"
else
    echo "ℹ️ Nenhum banco encontrado (primeira instalação)"
fi

# 3. Backup do config atual
echo "📋 Backup do config..."
if [ -f "config.py" ]; then
    cp config.py config-backup.py
    echo "✅ Config salvo em config-backup.py"
fi

# 4. Atualizar código
echo "📥 Baixando atualizações..."
git pull origin main

# 5. Instalar dependências
echo "📦 Instalando dependências..."
pip3 install -r requirements.txt

# 6. Verificar se config existe
echo "⚙️ Verificando configurações..."
if [ ! -f "config.py" ]; then
    if [ -f "config-backup.py" ]; then
        cp config-backup.py config.py
        echo "✅ Config restaurado do backup"
    else
        echo "❌ ERRO: config.py não encontrado!"
        echo "💡 Copie config-exemplo.py para config.py e configure"
        exit 1
    fi
fi

# 7. Testar migração do banco
echo "🔄 Testando migração do banco..."
python3 -c "
from db.db import create_tables
try:
    create_tables()
    print('✅ Migração do banco OK!')
except Exception as e:
    print(f'❌ Erro na migração: {e}')
    exit(1)
"

# 8. Iniciar bot
echo "🔄 Iniciando bot..."
screen -S telegram-bot -d -m python3 main.py

# 9. Aguardar inicialização
sleep 3

# 10. Verificar se está rodando
if pgrep -f "python3 main.py" > /dev/null; then
    echo "✅ Bot iniciado com sucesso!"
    echo "📱 Teste com /debug no Telegram"
    echo "📊 Use /statusnichos para verificar"
    echo "👀 Use 'screen -r telegram-bot' para ver logs"
    echo ""
    echo "📋 BACKUPS CRIADOS:"
    ls -la backup-*.db 2>/dev/null || echo "Nenhum backup anterior"
else
    echo "❌ ERRO: Bot não iniciou!"
    echo "📋 Verificando logs..."
    screen -S telegram-bot -X stuff "^C"
    python3 main.py
fi
