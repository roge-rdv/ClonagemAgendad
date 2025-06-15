# 🆘 Solução de Problemas

## 🔍 Diagnóstico Rápido

### Comando de Debug
```bash
/debug
```
**Use SEMPRE que tiver problemas!** Mostra:
- Status de acesso aos canais
- Quantidade de posts salvos
- Handlers ativos
- Dicas de solução

## ❌ Problemas Comuns

### 1. "Bot SEM acesso" no /debug

**Sintomas:**
- `/debug` mostra "Bot SEM acesso" para algum canal
- Posts não estão sendo capturados

**Soluções:**
```bash
1. Adicionar bot como ADMIN no canal fonte
2. Dar permissão de "LER MENSAGENS"
3. Postar algo NOVO no canal (bot só vê mensagens após ser adicionado)
4. Verificar se o ID do canal está correto
```

**Como adicionar bot como admin:**
1. Abrir canal → Configurações → Administradores
2. Adicionar Bot → Dar permissões necessárias

### 2. "Nenhum post pendente com nicho definido"

**Sintomas:**
- Logs mostram sempre essa mensagem
- Bot não está enviando posts

**Soluções:**
```bash
# 1. Verificar se tem posts salvos
/statusnichos

# 2. Se não tem posts, postar conteúdo NOVO nos canais fonte

# 3. Se tem posts mas sem nicho, limpar banco
/limparbanco CONFIRMAR

# 4. Forçar envio
/postartodos
```

### 3. Posts salvos mas não enviados

**Sintomas:**
- `/statusnichos` mostra posts salvos
- Mas não mostra posts enviados

**Soluções:**
```bash
# 1. Verificar horários
/horarios CANAL_ID list

# 2. Liberar horários
/horariosrapidos livre

# 3. Forçar envio
/postartodos

# 4. Verificar rate limit
/debug (olhar seção de rate limiting)
```

### 4. ModuleNotFoundError

**Erro:**
```
ModuleNotFoundError: No module named 'telegram'
```

**Solução:**
```bash
# Instalar dependências
pip3 install -r requirements.txt

# Ou instalar manualmente
pip3 install python-telegram-bot==20.8
pip3 install APScheduler==3.10.4
```

### 5. "Permission denied" ou "Access denied"

**Erro:**
```
PermissionError: [Errno 13] Permission denied
```

**Soluções:**
```bash
# Dar permissão de execução
chmod +x main.py
chmod +x deploy.sh

# Verificar proprietário
chown -R $USER:$USER .

# Rodar como root se necessário
sudo python3 main.py
```

### 6. Bot não responde comandos

**Sintomas:**
- Comandos /start, /debug não funcionam
- Bot parece offline

**Soluções:**
```bash
# 1. Verificar se bot está rodando
ps aux | grep python3

# 2. Verificar logs
tail -f bot.log
# ou
journalctl -u telegram-bot.service -f

# 3. Reiniciar bot
pkill -f "python3 main.py"
python3 main.py

# 4. Verificar token
# Editar config.py e confirmar token
```

### 7. Rate limit atingido

**Sintomas:**
- Logs mostram "Rate limit atingido"
- Posts param de ser enviados

**Soluções:**
```bash
# 1. Aguardar (é normal)
# 2. Verificar configuração de rate limit
# 3. Ajustar configurações em bot/rate_limiter.py
# 4. Usar /postartodos para ignorar rate limit temporariamente
```

### 8. "No such column: canal_fonte"

**Erro:**
```
sqlite3.OperationalError: no such column: canal_fonte
```

**Solução:**
```bash
# Apagar banco antigo e recriar
rm clonagem.db
python3 main.py

# Ou atualizar banco
# O bot faz isso automaticamente na inicialização
```

## 🔧 Ferramentas de Debug

### Ver Logs em Tempo Real
```bash
# Se usando screen
screen -r telegram-bot

# Se usando systemd
journalctl -u telegram-bot.service -f

# Se usando nohup
tail -f bot.log
```

### Verificar Processos
```bash
# Ver se bot está rodando
ps aux | grep python3

# Ver uso de CPU/RAM
htop

# Matar processo
pkill -f "python3 main.py"
```

### Testar Conectividade
```bash
# Testar conexão com Telegram
curl -s "https://api.telegram.org/bot<SEU_TOKEN>/getMe"

# Testar se consegue acessar canal
curl -s "https://api.telegram.org/bot<SEU_TOKEN>/getChat?chat_id=-1002574788580"
```

## 🗄️ Problemas de Banco de Dados

### Banco corrompido
```bash
# Backup atual
cp clonagem.db clonagem_backup.db

# Recriar banco
rm clonagem.db
python3 main.py
```

### Banco muito grande
```bash
# Ver tamanho
ls -lh clonagem.db

# Limpar dados antigos
/limparbanco CONFIRMAR

# Ou limpar manualmente
sqlite3 clonagem.db "DELETE FROM posts WHERE timestamp < datetime('now', '-7 days')"
```

### Verificar integridade
```bash
sqlite3 clonagem.db "PRAGMA integrity_check;"
```

## 🌐 Problemas de Rede

### Conexão lenta/instável
```bash
# Testar ping
ping 8.8.8.8

# Testar DNS
nslookup api.telegram.org

# Ajustar timeout no código
# Em bot/telegram_bot.py, adicionar:
# app = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).build()
```

### Firewall bloqueando
```bash
# Verificar regras UFW
ufw status

# Permitir saída HTTPS
ufw allow out 443
```

## 📱 Problemas de Telegram

### Bot banido/limitado
**Sintomas:**
- Erro 403: Forbidden
- Bot não consegue enviar mensagens

**Soluções:**
1. Verificar se bot não está enviando spam
2. Ajustar rate limiting
3. Entrar em contato com @BotSupport
4. Criar novo bot se necessário

### Canal deletado/inacessível
**Erro:**
```
Chat not found
```

**Soluções:**
1. Verificar se canal ainda existe
2. Verificar se bot ainda é admin
3. Atualizar IDs no config.py

## 🔄 Procedimentos de Emergência

### Reset Completo
```bash
# 1. Parar bot
pkill -f "python3 main.py"

# 2. Backup
cp clonagem.db backup-$(date +%Y%m%d).db

# 3. Limpar tudo
rm clonagem.db
/deletartudo CONFIRMAR  # No Telegram

# 4. Reiniciar
python3 main.py

# 5. Reconfigurar
/horariosrapidos livre
```

### Rollback de Código
```bash
# Ver últimos commits
git log --oneline -10

# Voltar para commit anterior
git reset --hard HEAD~1

# Ou commit específico
git reset --hard abc123

# Reiniciar bot
./deploy.sh
```

### Restaurar Backup
```bash
# Parar bot
pkill -f "python3 main.py"

# Restaurar banco
cp backup-20231201.db clonagem.db

# Reiniciar
python3 main.py
```

## 📋 Checklist de Troubleshooting

### Antes de Buscar Ajuda
- [ ] Executei `/debug` e verifiquei erros
- [ ] Verifiquei se bot está rodando (`ps aux | grep python`)
- [ ] Verifiquei logs de erro
- [ ] Testei comandos básicos (`/start`, `/statusnichos`)
- [ ] Verifiquei se sou admin nos canais
- [ ] Tentei reiniciar o bot

### Informações para Suporte
```bash
# Coletar informações do sistema
uname -a                    # Sistema operacional
python3 --version          # Versão Python
pip3 list | grep telegram  # Versão telegram-bot
df -h                      # Espaço em disco
free -h                    # Memória RAM
```

### Logs Importantes
```bash
# Últimas 50 linhas de log
journalctl -u telegram-bot.service --lines=50

# Erros específicos
journalctl -u telegram-bot.service | grep -i error

# Salvar logs para envio
journalctl -u telegram-bot.service --lines=100 > bot-debug.log
```

## 🆘 Quando Buscar Ajuda

### Fóruns e Comunidades
- GitHub Issues do projeto
- Telegram: @rogee_rdvv
- Stack Overflow (tag: python-telegram-bot)

### Informações para Incluir
1. **Erro exato** (copiar/colar)
2. **Resultado do `/debug`**
3. **Sistema operacional**
4. **Versão do Python**
5. **Últimas mudanças feitas**
6. **Logs relevantes**

---

**💡 Lembre-se:** 90% dos problemas são resolvidos com `/debug` e verificação de permissões nos canais!
