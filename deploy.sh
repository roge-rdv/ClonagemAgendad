#!/bin/bash
# 🚀 DEPLOY UNIFICADO - Bot Multi-Nicho
# Script principal de deploy seguro com backup automático

echo "🚀 DEPLOY BOT MULTI-NICHO - Versão Unificada"
echo "=============================================="

# Verificar se está no diretório correto
if [ ! -f "main.py" ]; then
    echo "❌ ERRO: Execute este script na pasta do projeto!"
    echo "💡 Use: cd /caminho/para/telegram-bot && ./deploy.sh"
    exit 1
fi

# 1. Parar bot atual
echo "⏹️ Parando bot atual..."
pkill -f "python3 main.py" || echo "ℹ️ Bot não estava rodando"
sleep 2

# 2. BACKUP AUTOMÁTICO
echo "💾 Fazendo backups de segurança..."
timestamp=$(date +%Y%m%d-%H%M%S)

# Backup do banco
if [ -f "clonagem.db" ]; then
    cp clonagem.db "backup-db-$timestamp.db"
    echo "✅ Banco salvo: backup-db-$timestamp.db"
else
    echo "ℹ️ Nenhum banco encontrado (primeira instalação)"
fi

# Backup do config atual (IMPORTANTE!)
if [ -f "config.py" ]; then
    cp config.py "config-backup-$timestamp.py"
    echo "✅ Config atual salvo: config-backup-$timestamp.py"
fi

# 3. Atualizar código do GitHub
echo "📥 Baixando atualizações do GitHub..."
if [ -d ".git" ]; then
    git stash  # Salva mudanças locais temporariamente
    git pull origin main
    
    # Se houve conflito no config.py, restaura o backup
    if [ -f "config-backup-$timestamp.py" ] && [ ! -f "config.py" ]; then
        cp "config-backup-$timestamp.py" config.py
        echo "🔄 Config restaurado do backup"
    fi
else
    echo "⚠️ Não é um repositório Git - pulando atualização"
fi

# 4. Instalar/atualizar dependências
echo "📦 Instalando dependências..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
else
    echo "📦 Instalando dependências manualmente..."
    pip3 install python-telegram-bot==20.8
    pip3 install APScheduler==3.10.4
    pip3 install requests
    pip3 install Pillow
fi

# 5. Verificar configurações
echo "⚙️ Verificando configurações..."

# Se não tem config.py, tenta criar do exemplo
if [ ! -f "config.py" ]; then
    if [ -f "config-exemplo.py" ]; then
        echo "📋 Copiando config do exemplo..."
        cp config-exemplo.py config.py
        echo "⚠️ ATENÇÃO: Configure seu token em config.py!"
        echo "💡 Edite: nano config.py"
    elif [ -f "config-backup-$timestamp.py" ]; then
        cp "config-backup-$timestamp.py" config.py
        echo "🔄 Config restaurado do backup"
    else
        echo "❌ ERRO: Nenhum config.py encontrado!"
        echo "💡 Copie config-exemplo.py para config.py e configure"
        exit 1
    fi
fi

# Verificar se token está configurado
if grep -q "SEU_TOKEN_AQUI" config.py; then
    echo "⚠️ ATENÇÃO: Token ainda não foi configurado!"
    echo "💡 Edite config.py e adicione seu token do @BotFather"
    echo "🔧 Use: nano config.py"
    echo ""
    echo "Deseja continuar mesmo assim? (y/N)"
    read -r resposta
    if [ "$resposta" != "y" ] && [ "$resposta" != "Y" ]; then
        echo "❌ Deploy cancelado"
        exit 1
    fi
fi

# 6. Testar migração do banco
echo "🔄 Testando migração do banco de dados..."
python3 -c "
from db.db import create_tables
try:
    create_tables()
    print('✅ Migração do banco concluída!')
except Exception as e:
    print(f'❌ Erro na migração: {e}')
    exit(1)
" || exit 1

# 7. Verificar se screen está disponível
if ! command -v screen &> /dev/null; then
    echo "📦 Instalando screen..."
    apt update && apt install screen -y
fi

# 8. Iniciar bot
echo "🔄 Iniciando bot em background..."
screen -S telegram-bot -d -m python3 main.py

# 9. Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 5

# 10. Verificar se está funcionando
if pgrep -f "python3 main.py" > /dev/null; then
    echo ""
    echo "🎉 ==============================================="
    echo "✅ BOT INICIADO COM SUCESSO!"
    echo "==============================================="
    echo ""
    echo "📱 PRÓXIMOS PASSOS:"
    echo "1. Teste no Telegram: /start"
    echo "2. Verifique status: /debug"
    echo "3. Ver estatísticas: /statusnichos"
    echo ""
    echo "👀 COMANDOS ÚTEIS:"
    echo "• Ver logs: screen -r telegram-bot"
    echo "• Parar bot: pkill -f 'python3 main.py'"
    echo "• Status: ps aux | grep python3"
    echo ""
    echo "📋 BACKUPS CRIADOS:"
    ls -la backup-*$timestamp* 2>/dev/null || echo "Nenhum backup anterior"
    echo ""
else
    echo ""
    echo "❌ ==============================================="
    echo "ERRO: BOT NÃO INICIOU!"
    echo "==============================================="
    echo ""
    echo "🔍 VERIFICANDO PROBLEMA..."
    
    # Tentar rodar em foreground para ver erro
    echo "📋 Tentando executar em foreground para diagnóstico:"
    timeout 10 python3 main.py || echo "Bot parou com erro"
    
    echo ""
    echo "🆘 POSSÍVEIS SOLUÇÕES:"
    echo "1. Verificar token em config.py"
    echo "2. Verificar dependências: pip3 list"
    echo "3. Ver logs: screen -r telegram-bot"
    echo "4. Restaurar backup se necessário"
fi

echo ""
echo "📊 RESUMO DO DEPLOY:"
echo "• Data: $(date)"
echo "• Backup banco: backup-db-$timestamp.db"
echo "• Backup config: config-backup-$timestamp.py"
echo "• Status: $(pgrep -f 'python3 main.py' > /dev/null && echo 'ATIVO' || echo 'INATIVO')"