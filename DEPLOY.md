# Como garantir que o bot reinicie automaticamente após reboot

Se quiser que o bot inicie automaticamente após reiniciar o servidor, adicione ao `crontab`:

```bash
crontab -e
```
E adicione a linha:
```bash
@reboot cd /root/ClonagemAgendad && source venv/bin/activate && pip install -r requirements.txt && nohup python3 main.py &
```

**Explicação do comando:**
- `@reboot` - Executa quando o servidor reinicia
- `cd /root/ClonagemAgendad` - Vai para a pasta do projeto
- `source venv/bin/activate` - Ativa o ambiente virtual
- `pip install -r requirements.txt` - Instala/atualiza dependências automaticamente
- `nohup python3 main.py &` - Roda o bot em background

**Vantagem:** Sempre que o servidor reiniciar, as dependências serão atualizadas automaticamente antes de iniciar o bot.