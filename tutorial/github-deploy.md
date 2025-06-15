# 🐙 GitHub Deploy e Atualizações

## 1. 📤 Subindo Projeto para GitHub

### Criar Repositório
1. Acesse [GitHub.com](https://github.com)
2. Clique em **"New Repository"**
3. Nome: `telegram-bot-multicanal` (ou outro)
4. **Private** (recomendado para bots)
5. Clique **"Create repository"**

### Preparar Projeto Local
```bash
# Entrar na pasta do projeto
cd c:\Users\shrek\Documents\CODES\Telegram-Projetos\ClonagemAgendad

# Inicializar Git
git init

# Adicionar arquivos
git add .

# Primeiro commit
git commit -m "🤖 Bot Multi-Nicho inicial"

# Conectar com GitHub
git remote add origin https://github.com/SEU_USUARIO/telegram-bot-multicanal.git

# Enviar para GitHub
git push -u origin main
```

### .gitignore Importante
```bash
# Criar arquivo .gitignore
echo "config.py
clonagem.db
*.log
__pycache__/
venv/
.env" > .gitignore

# Adicionar ao Git
git add .gitignore
git commit -m "➕ Adicionar .gitignore"
git push
```

## 2. 🔧 Config.py Seguro

### Criar config-exemplo.py
```bash
# Copiar config atual
cp config.py config-exemplo.py
```

**Editar config-exemplo.py:**
```python
# filepath: config-exemplo.py
TELEGRAM_BOT_TOKEN = "SEU_TOKEN_AQUI"

# MAPEAMENTO ORGANIZADO POR NICHO
CANAL_MAPPINGS = {
    'novin': {
        'fonte': -1002557461071,
        'destino': -1002574788580,
        'caption_file': 'novin'
    },
    # ... resto igual
}

# ... resto do arquivo igual
```

### Atualizar .gitignore
```bash
echo "config.py" >> .gitignore
git add config-exemplo.py .gitignore
git commit -m "🔒 Adicionar config exemplo e proteger config real"
git push
```

## 3. 🚀 Deploy Automático

### Script de Deploy
```bash
# Criar deploy.sh
nano deploy.sh
```

**Conteúdo:**
```bash
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
echo "📊 Use 'screen -r telegram-bot' para ver logs"
```

**Dar permissão:**
```bash
chmod +x deploy.sh
```

## 4. 📋 Estrutura de Projeto

### Organização Recomendada
```
telegram-bot-multicanal/
├── 📁 bot/
│   ├── commands.py
│   ├── telegram_bot.py
│   ├── rate_limiter.py
│   └── ...
├── 📁 captions/
│   ├── novin.py
│   ├── leaks.py
│   └── ...
├── 📁 db/
│   └── db.py
├── 📁 tutorial/
│   ├── README.md
│   ├── comandos.md
│   └── ...
├── config-exemplo.py
├── requirements.txt
├── main.py
├── deploy.sh
├── .gitignore
└── README.md
```

### README.md Principal
```bash
nano README.md
```

```markdown
# 🤖 Bot Multi-Nicho Telegram

Bot profissional para clonagem automática de canais organizados por nichos.

## 🚀 Deploy Rápido

```bash
# 1. Clonar projeto
git clone https://github.com/SEU_USUARIO/telegram-bot-multicanal.git
cd telegram-bot-multicanal

# 2. Configurar
cp config-exemplo.py config.py
nano config.py  # Adicionar seu token

# 3. Instalar e rodar
pip3 install -r requirements.txt
python3 main.py
```

## 📖 Documentação

- [📋 Comandos](tutorial/comandos.md)
- [🌐 Deploy DigitalOcean](tutorial/deploy-digitalocean.md)
- [🔧 Configurações](tutorial/configuracoes.md)

## ⚡ Deploy Automático

```bash
chmod +x deploy.sh
./deploy.sh
```

---
**Desenvolvido por @rogee_rdvv**
```

## 5. 🔄 Fluxo de Atualizações

### No Desenvolvimento (Local)
```bash
# Fazer mudanças no código
# ...

# Commit das mudanças
git add .
git commit -m "✨ Nova funcionalidade X"
git push origin main
```

### No Servidor (DigitalOcean)
```bash
# Método 1: Script automático
./deploy.sh

# Método 2: Manual
git pull origin main
pip3 install -r requirements.txt
# Reiniciar bot
```

## 6. 🏷️ Versionamento

### Tags de Versão
```bash
# Criar tag
git tag -a v1.0.0 -m "🎉 Versão 1.0.0 - Release inicial"
git push origin v1.0.0

# Ver tags
git tag -l

# Baixar versão específica
git checkout v1.0.0
```

### Branches para Features
```bash
# Criar branch para nova feature
git checkout -b feature/watermarks
# Desenvolver...
git add .
git commit -m "✨ Adicionar sistema de watermarks"
git push origin feature/watermarks

# Fazer merge via GitHub Pull Request
```

## 7. 🔒 Secrets e Segurança

### GitHub Secrets (Actions)
1. Repositório → Settings → Secrets and variables → Actions
2. Adicionar secrets:
   - `TELEGRAM_TOKEN`
   - `SERVER_HOST`
   - `SERVER_USER`
   - `SERVER_PASSWORD`

### GitHub Actions Deploy
```yaml
# .github/workflows/deploy.yml
name: Deploy Bot

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        password: ${{ secrets.SERVER_PASSWORD }}
        script: |
          cd /root/telegram-bot-multicanal
          ./deploy.sh
```

## 8. 📊 Monitoramento via GitHub

### Issues para Bugs
- Criar templates de issue
- Labels: `bug`, `enhancement`, `question`
- Milestones para versões

### Discussões
- Ativar GitHub Discussions
- Categorias: Suporte, Features, Geral

## 9. 🚨 Rollback de Emergência

### Voltar Versão Anterior
```bash
# Ver commits
git log --oneline

# Voltar para commit específico
git reset --hard COMMIT_HASH

# Ou voltar 1 commit
git reset --hard HEAD~1

# Forçar push (CUIDADO!)
git push --force-with-lease origin main
```

### Backup Automático
```bash
# Cron job para backup diário
0 2 * * * cd /root/telegram-bot-multicanal && git add . && git commit -m "🔄 Backup automático $(date)" && git push origin backup
```

## 10. 📋 Checklist de Deploy

### Desenvolvimento
- [ ] Código testado localmente
- [ ] Config.py não commitado
- [ ] .gitignore atualizado
- [ ] README.md atualizado
- [ ] Commit com mensagem clara
- [ ] Push para GitHub

### Produção
- [ ] Pull do GitHub executado
- [ ] Config.py configurado
- [ ] Dependências instaladas
- [ ] Bot reiniciado
- [ ] /debug testado
- [ ] Logs verificados

### Manutenção
- [ ] Backup do banco realizado
- [ ] Versão taggeada
- [ ] Documentação atualizada
- [ ] Monitor funcionando

---

**🎯 Com esse setup, você tem deploy profissional e atualizações automáticas!**
