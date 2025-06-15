#!/bin/bash
# deploy.sh - Script de deploy automático

echo "🚀 Iniciando deploy do Bot Multi-Nicho..."

# Parar bot se estiver rodando
echo "⏹️ Parando bot..."
pkill -f "python3 main.py" || echo "Bot não estava rodando"

# Fazer backup do banco
echo "💾 Fazendo backup..."
cp clonagem.db backup-$(date +%Y%m%d-%H%M%S).db 2>/dev/null || echo "Sem banco para backup"

# Atualizar código
echo "📥 Baixando atualizações..."
git pull origin main

# Instalar dependências
echo "📦 Instalando dependências..."
pip3 install -r requirements.txt

# Verificar config
echo "⚙️ Verificando configurações..."
if [ ! -f "config.py" ]; then
    echo "❌ ERRO: config.py não encontrado!"
    echo "💡 Copie config-exemplo.py para config.py e configure"
    exit 1
fi

# Iniciar bot em background
echo "🔄 Iniciando bot..."
screen -S telegram-bot -d -m python3 main.py

echo "✅ Deploy concluído!"
echo "📱 Teste com /debug no Telegram"
echo "📊 Use 'screen -r ClonagemAgendad' para ver logs"