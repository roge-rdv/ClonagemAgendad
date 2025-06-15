# 🌐 Deploy no DigitalOcean - Bot 24h Online

## 1. 🔧 Criando Droplet

### Acessar DigitalOcean
1. Entre em [DigitalOcean](https://www.digitalocean.com/)
2. Clique em **"Create Droplet"**

### Configurações Recomendadas
- **SO:** Ubuntu 22.04 LTS
- **Plano:** Basic ($6/mês - 1GB RAM)
- **Região:** New York (ou mais próxima)
- **SSH:** Adicione sua chave SSH

## 2. 📥 Conectando no Servidor

### Via SSH
```bash
ssh root@SEU_IP_DO_DROPLET
```

### Ou via Console Web
No painel do DigitalOcean → Sua Droplet → Console

## 3. 🔨 Preparando o Ambiente

### Atualizar Sistema
```bash
apt update && apt upgrade -y
```

### Instalar Dependências
```bash
# Python e Git
apt install python3 python3-pip git screen nano -y

# Verificar versões
python3 --version
git --version
```

## 4. 📦 Baixando o Projeto

### Clonar do GitHub
```bash
# Ir para diretório home
cd /root

# Clonar projeto
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO

# OU se baixar diretamente:
mkdir bot-telegram
cd bot-telegram
# Fazer upload dos arquivos via SCP/SFTP
```

### Instalar Dependências Python
```bash
# Instalar requirements
pip3 install -r requirements.txt

# OU instalar manualmente:
pip3 install python-telegram-bot==20.8
pip3 install APScheduler==3.10.4
pip3 install requests
pip3 install Pillow
```

## 5. ⚙️ Configurando o Bot

### Editar config.py
```bash
nano config.py
```

**Configurar:**
```python
# Seu token do bot
TELEGRAM_BOT_TOKEN = "SEU_TOKEN_AQUI"

# IDs dos canais (não mude se estão corretos)
CANAL_MAPPINGS = {
    'novin': {
        'fonte': -1002557461071,
        'destino': -1002574788580,
        'caption_file': 'novin'
    },
    # ... resto dos canais
}
```

**Salvar:** `Ctrl+X` → `Y` → `Enter`

### Testar o Bot
```bash
# Teste rápido
python3 main.py
```

**Se aparecer:**
```
🔥 Iniciando Bot Multi-Nicho...
✅ Tabelas criadas/verificadas
🔥 BOT MULTI-NICHO INICIADO! Monitorando 6 canais...
```

**✅ Está funcionando!** Pressione `Ctrl+C` para parar.

## 6. 🔄 Deixando 24h Online

### Método 1: Screen (Recomendado)
```bash
# Criar sessão screen
screen -S telegram-bot

# Dentro do screen, rodar o bot
python3 main.py

# Desconectar sem parar: Ctrl+A, depois D
# Para reconectar: screen -r telegram-bot
```

### Método 2: Nohup
```bash
# Rodar em background
nohup python3 main.py > bot.log 2>&1 &

# Ver logs
tail -f bot.log

# Parar o bot
ps aux | grep python3
kill PID_DO_PROCESSO
```

### Método 3: Systemd (Mais Profissional)
```bash
# Criar service
nano /etc/systemd/system/telegram-bot.service
```

**Conteúdo:**
```ini
[Unit]
Description=Telegram Bot Multi-Nicho
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/SEU_REPOSITORIO
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Ativar:**
```bash
# Recarregar systemd
systemctl daemon-reload

# Ativar serviço
systemctl enable telegram-bot.service

# Iniciar serviço
systemctl start telegram-bot.service

# Ver status
systemctl status telegram-bot.service

# Ver logs
journalctl -u telegram-bot.service -f
```

## 7. 🔄 Atualizando o Bot

### Via Git
```bash
# Parar o bot
screen -r telegram-bot
# Ctrl+C para parar

# Ou se usando systemd:
systemctl stop telegram-bot.service

# Atualizar código
git pull origin main

# Instalar novas dependências (se houver)
pip3 install -r requirements.txt

# Reiniciar
screen -S telegram-bot
python3 main.py

# Ou se usando systemd:
systemctl start telegram-bot.service
```

### Upload Manual
```bash
# Parar bot
# Fazer upload dos arquivos novos via SCP/FileZilla
# Reiniciar bot
```

## 8. 📊 Monitoramento

### Ver se está Rodando
```bash
# Via screen
screen -list

# Via processo
ps aux | grep python3

# Via systemd
systemctl status telegram-bot.service
```

### Ver Logs
```bash
# Se usando screen
screen -r telegram-bot

# Se usando nohup
tail -f bot.log

# Se usando systemd
journalctl -u telegram-bot.service -f --lines=50
```

### Comandos do Bot
```bash
# No Telegram, mandar pro bot:
/debug
/statusnichos
/postaragora
```

## 9. 🛡️ Segurança

### Firewall Básico
```bash
# Instalar UFW
apt install ufw

# Permitir SSH
ufw allow ssh

# Ativar firewall
ufw enable

# Ver status
ufw status
```

### Backup do Banco
```bash
# Criar backup diário
crontab -e

# Adicionar linha:
0 2 * * * cp /root/SEU_REPOSITORIO/clonagem.db /root/backup-$(date +\%Y\%m\%d).db
```

## 10. 🚨 Comandos de Emergência

### Parar o Bot
```bash
# Se usando screen
screen -r telegram-bot
# Ctrl+C

# Se usando systemd
systemctl stop telegram-bot.service

# Matar processo força bruta
pkill -f "python3 main.py"
```

### Reiniciar Droplet
```bash
reboot
```

### Ver Uso de Recursos
```bash
# CPU e RAM
htop

# Espaço em disco
df -h

# Processos
ps aux | grep python
```

## 📋 Checklist de Deploy

- [ ] Droplet criado e configurado
- [ ] Python 3 e dependências instaladas
- [ ] Projeto baixado/clonado
- [ ] config.py configurado com token correto
- [ ] Bot testado manualmente
- [ ] Screen/systemd configurado
- [ ] Bot rodando 24h
- [ ] Comandos /debug e /statusnichos funcionando
- [ ] Backup configurado

## 🆘 Problemas Comuns

### "ModuleNotFoundError"
```bash
pip3 install -r requirements.txt
```

### "Permission denied"
```bash
chmod +x main.py
```

### Bot não responde
```bash
# Verificar se está rodando
ps aux | grep python3

# Ver logs de erro
journalctl -u telegram-bot.service --lines=20
```

### Sem espaço em disco
```bash
# Limpar logs antigos
find /var/log -name "*.log" -type f -delete

# Limpar cache
apt autoremove && apt autoclean
```

---

**🎉 Pronto! Seu bot está online 24h no DigitalOcean!**

**💡 Dica:** Sempre use `/debug` no Telegram para verificar se tudo está funcionando.
