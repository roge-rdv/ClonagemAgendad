# 🚀 Comandos do Bot Multi-Nicho

## 📋 Comandos Básicos

### `/start`
Inicia o bot e mostra o menu principal.
```
/start
```

### `/statusnichos`
Mostra estatísticas completas de todos os nichos.
```
/statusnichos
```
**Retorna:**
- Posts salvos por nicho
- Posts enviados por nicho
- Quantidade de legendas disponíveis
- Status geral do banco

### `/debug`
Informações detalhadas dos canais e permissões.
```
/debug
```
**Útil para:**
- Verificar se o bot tem acesso aos canais
- Ver quantos posts foram salvos
- Diagnosticar problemas

## ⚡ Comandos de Postagem

### `/postaragora`
Força envio imediato respeitando scheduler e rate limit.
```
/postaragora
```

### `/postartodos`
**FORÇA** envio de todos os nichos ignorando horários.
```
/postartodos
```
**⚠️ Cuidado:** Ignora rate limiting, use com moderação!

### `/forcarpost`
Envia um post de teste de um nicho específico.
```
/forcarpost novin
/forcarpost leaks
/forcarpost latinas
/forcarpost coroas
/forcarpost ourovip
/forcarpost backdoor
```

## ⏰ Comandos de Horários

### `/horarios`
Configura horários específicos para cada canal.

**Sintaxe:**
```
/horarios CANAL_ID ACAO HORARIO
```

**Exemplos:**
```bash
# Adicionar horário
/horarios -1002574788580 add 14:30
/horarios -1002574788580 add 18:00

# Listar horários
/horarios -1002574788580 list

# Remover horário
/horarios -1002574788580 remove 14:30
```

**IDs dos Canais:**
- Novin: `-1002574788580`
- Leaks: `-1002651133010`
- Latinas: `-1002707898874`
- Coroas: `-1002765829939`
- OuroVIP: `-1002870159887`
- Backdoor: `-1002759274414`

### `/horariosrapidos`
Configurações rápidas para todos os canais.

```bash
# A cada 2 horas (8 posts/dia)
/horariosrapidos agressivo

# A cada 4 horas (4 posts/dia)
/horariosrapidos normal

# A cada 8 horas (2 posts/dia)
/horariosrapidos conservador

# Remove horários (posta sempre que receber)
/horariosrapidos livre
```

## 🗑️ Comandos de Limpeza

### `/deletartudo`
**DELETA** todas as mensagens enviadas pelo bot.
```
/deletartudo CONFIRMAR
```
**⚠️ ATENÇÃO:** Não tem volta! Use apenas se necessário.

### `/limparbanco`
Remove posts antigos sem nicho definido.
```
/limparbanco CONFIRMAR
```

## 📊 Exemplos Práticos

### Configuração Básica (Primeiro Uso)
```bash
1. /start
2. /debug (verificar se tudo está OK)
3. /horariosrapidos normal (configurar horários)
4. /statusnichos (ver status)
```

### Rotina Diária
```bash
1. /statusnichos (ver estatísticas)
2. /postaragora (forçar posts se necessário)
3. /debug (se tiver problemas)
```

### Configuração Avançada
```bash
# Configurar horários específicos para cada nicho
/horarios -1002574788580 add 08:00  # Novin manhã
/horarios -1002574788580 add 20:00  # Novin noite

/horarios -1002651133010 add 14:00  # Leaks tarde
/horarios -1002651133010 add 22:00  # Leaks noite
```

### Teste de Nichos
```bash
/forcarpost novin
/forcarpost leaks
/forcarpost latinas
/forcarpost coroas
/forcarpost ourovip
/forcarpost backdoor
```

## 🔧 Troubleshooting

### Bot não está postando?
```bash
1. /debug (verificar acesso aos canais)
2. /statusnichos (ver se tem posts pendentes)
3. /horariosrapidos livre (remover restrições)
4. /postartodos (forçar envio)
```

### Muitas mensagens de erro?
```bash
1. /limparbanco CONFIRMAR (limpar dados antigos)
2. Reiniciar o bot
3. /debug (verificar novamente)
```

### Quer começar do zero?
```bash
1. /deletartudo CONFIRMAR (apagar mensagens)
2. /limparbanco CONFIRMAR (limpar banco)
3. /horariosrapidos livre (resetar horários)
4. Postar novo conteúdo nos canais fonte
```

## 📱 Dicas Importantes

- **Sempre use `/debug`** para verificar problemas
- **Configure horários** com `/horariosrapidos` ou `/horarios`
- **O bot só captura mensagens NOVAS** após ser adicionado aos canais
- **Seja admin** nos canais fonte para o bot funcionar
- **Use `/statusnichos`** para monitorar performance

---

**💡 Lembre-se:** O bot precisa ser **ADMINISTRADOR** nos canais fonte para conseguir ler as mensagens!
