# Deploy do Bot de Clonagem Agendada

## Melhor Opção para Funcionamento 24h com Banco de Dados

Para garantir que o bot funcione 24 horas por dia, 7 dias por semana, com estabilidade e persistência de dados, recomenda-se o uso de um **servidor VPS Linux** (como Ubuntu Server) com acesso root. O banco de dados utilizado é SQLite, que é leve e funciona bem para bots de médio porte, mas pode ser facilmente migrado para PostgreSQL ou MySQL se necessário.

---

## Passos Recomendados

### 1. **Escolha do Servidor**

- **VPS Linux (Ubuntu 20.04 ou superior)**
  - Exemplos: DigitalOcean (recomendado), Hetzner, Contabo, AWS Lightsail, Google Cloud, Azure, Oracle Cloud Free Tier.
  - Requisitos mínimos: 1 vCPU, 1GB RAM, 10GB SSD.

---

## Já tenho um Droplet na DigitalOcean, posso reaproveitar?

**Sim!** Se você já possui um droplet (máquina virtual) na DigitalOcean usado para outro bot (ex: `telegram-bot`), pode reaproveitar o mesmo droplet para este projeto. Basta fazer uma limpeza dos arquivos antigos e instalar o novo projeto.

### **Como fazer a limpeza e instalar este projeto:**

1. **Acesse seu droplet via SSH:**
   ```bash
   ssh root@SEU_IP_DO_DROPLET
   ```

2. **(Opcional) Pare o bot antigo se estiver rodando:**
   ```bash
   ps aux | grep python
   # mate o processo antigo se necessário
   kill <PID>
   ```

3. **Exclua todos os arquivos e pastas antigos:**
   ```bash
   # Exclua a pasta do projeto antigo
   rm -rf ~/telegram-media-bot
   # Exclua outros arquivos/pastas que não vai usar
   rm -rf ~/Droplets ~/get-docker.sh ~/snap
   # (Atenção: só remova o que tem certeza que não precisa!)
   ```

4. **Clone o novo projeto:**
   ```bash
   git clone <seu-repositorio-ou-upload>
   cd ClonagemAgend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Configure o arquivo `config.py`** com seu token, canais, etc.

   Exemplo de configuração pronta para este projeto (NÃO use no Python interativo, edite o arquivo `config.py`):

   ```python
   # config.py
   TELEGRAM_BOT_TOKEN = "7275987527:AAG2Xf5t3jVooSrjQlXo6QWwrBjfriHmK2U"
   CANAL_FONTE_ID = -1002758088813
   CANAIS_DESTINO = [
       -1002870159887,
       # Adicione mais canais se necessário
   ]
   SCHEDULE_HOURS = 0.01666667  # Intervalo em horas
   ```

   > **Importante:**  
   > Edite o arquivo `config.py` com um editor de texto (nano, vim, code, notepad, etc).  
   > **Não** cole essas linhas no terminal Python interativo, pois isso gera erro de indentação.

   > **Dica:** Nunca envie seu `config.py` para o GitHub! Ele já está no `.gitignore`.

6. **(Opcional) Remova bancos de dados antigos:**
   ```bash
   rm -f clonagem.db
   ```

7. **Crie as tabelas e rode o bot:**
   ```bash
   python main.py
   ```

8. **Para rodar 24h, use:**
   ```bash
   nohup python main.py &
   # ou use tmux/screen para manter a sessão aberta
   ```

   - **nohup:** O comando acima faz o bot continuar rodando mesmo se você fechar o terminal/SSH **(mas só funciona enquanto o servidor VPS estiver ligado)**.
   - Toda a saída do bot será gravada no arquivo `nohup.out` no diretório atual.
   - Para ver os logs em tempo real:
     ```bash
     tail -f nohup.out
     ```
   - Para parar o bot, encontre o PID com `ps aux | grep python` e use `kill <PID>`.

   - **tmux/screen:** Também mantém o bot rodando no VPS mesmo se você se desconectar do SSH.

---

**Importante:**  
O bot só ficará 24h online **se estiver rodando em um servidor VPS** (como DigitalOcean, Contabo, etc).  
**Se você desligar sua máquina local, o bot para.**  
Por isso, sempre rode o bot no VPS e não no seu computador pessoal.

---

## Como garantir que o bot reinicie automaticamente após reboot

Se quiser que o bot inicie automaticamente após reiniciar o servidor, adicione ao `crontab`:

```bash
crontab -e
```
E adicione a linha:
```bash
@reboot cd /root/ClonagemAgendad && source venv/bin/activate && nohup python main.py &
```

---

## Como manter o bot 24h online mesmo com seu computador local desligado

Se você está usando um VPS como o DigitalOcean, **o bot ficará online 24h por dia** enquanto o servidor VPS estiver ligado, independentemente do seu computador local.

**O que fazer:**
- Suba o projeto e rode o bot no seu VPS (DigitalOcean).
- Use `nohup`, `tmux` ou `screen` para garantir que o bot continue rodando mesmo se você fechar o SSH.
- Você pode desligar seu computador local à vontade: o bot continuará funcionando no VPS.

**Exemplo de comando para rodar o bot 24h:**
```bash
cd /root/ClonagemAgendad
source venv/bin/activate
nohup python main.py &
```
Ou, usando tmux:
```bash
tmux new -s bot
source venv/bin/activate
python main.py
# (Depois, Ctrl+B e D para sair do tmux)
```

**Resumo:**  
O bot só depende do VPS estar ligado. Seu computador local pode ser desligado sem afetar o funcionamento do bot.

---

## Observações

- Não é necessário criar um novo droplet, a não ser que queira separar projetos.
- Certifique-se de remover arquivos antigos para evitar conflitos.
- Sempre use ambiente virtual para evitar problemas de dependências.
- Faça backup do banco de dados (`clonagem.db`) se necessário.

---

**Dúvidas ou suporte? Fale com [@rogee_rdvv](https://t.me/rogee_rdvv)**

> **Erro:**  
> The virtual environment was not created successfully because ensurepip is not available.  
> On Debian/Ubuntu systems, you need to install the python3-venv package...

## Como resolver o erro do venv no Ubuntu/Debian

Esse erro ocorre porque o pacote `python3-venv` não está instalado no seu sistema.  
Para corrigir, rode:

```bash
sudo apt update
sudo apt install python3-venv -y
```

Depois, crie novamente o ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

Agora continue normalmente com a instalação dos requisitos:

```bash
pip install -r requirements.txt
```

---

## Como atualizar o bot no DigitalOcean usando o GitHub

1. **Faça push das alterações do seu projeto local para o GitHub:**
   ```bash
   git add .
   git commit -m "sua mensagem de atualização"
   git push origin main
   ```

2. **No seu VPS (DigitalOcean), acesse a pasta do projeto:**
   ```bash
   ssh root@SEU_IP_DO_DROPLET
   cd /root/ClonagemAgendad
   ```

3. **Puxe as atualizações do GitHub:**
   ```bash
   git pull origin main
   ```

4. **(Re)instale dependências se necessário:**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Reinicie o bot:**
   - Se estiver usando `nohup`, mate o processo antigo e rode novamente:
     ```bash
     ps aux | grep python
     kill <PID_ANTIGO>
     nohup python main.py &
     ```
   - Se estiver usando `tmux` ou `screen`, basta parar e rodar de novo na sessão.

---

**Resumo:**  
- Faça push das alterações para o GitHub.
- No VPS, use `git pull` para atualizar.
- Reinstale dependências se necessário.
- Reinicie o bot.

---
