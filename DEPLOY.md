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
   cd ClonagemAgendad
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Configure o arquivo `config.py`** com seu token, canais, etc.

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

---

## Observações

- Não é necessário criar um novo droplet, a não ser que queira separar projetos.
- Certifique-se de remover arquivos antigos para evitar conflitos.
- Sempre use ambiente virtual para evitar problemas de dependências.
- Faça backup do banco de dados (`clonagem.db`) se necessário.

---

**Dúvidas ou suporte? Fale com [@rogee_rdvv](https://t.me/rogee_rdvv)**
