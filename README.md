# Como usar pyenv + venv no Windows

1. **Instale o pyenv-win**  
   Siga as instruções: https://github.com/pyenv-win/pyenv-win#installation

2. **Instale a versão desejada do Python**  
   ```
   pyenv install 3.10.13
   ```

3. **Defina a versão global/local do Python**  
   - Para todo o sistema:
     ```
     pyenv global 3.10.13
     ```
   - Ou apenas para o projeto (dentro da pasta do projeto):
     ```
     pyenv local 3.10.13
     ```

4. **Reabra o terminal**  
   Isso garante que o pyenv está no PATH e a versão correta está ativa.

5. **Verifique a versão ativa**  
   ```
   python --version
   ```

6. **Crie o ambiente virtual normalmente**  
   ```
   python -m venv venv
   ```

7. **Ative o venv**  
   ```
   venv\Scripts\activate
   ```

8. **Selecione o interpretador do venv no VSCode**  
   Siga os passos já descritos anteriormente.

> **Dica:**  
> O pyenv-win só gerencia as versões do Python. O venv funciona normalmente após você ativar a versão desejada com o pyenv.

# Pronto!  
Agora seu ambiente virtual usará a versão do Python gerenciada pelo pyenv.

# Como testar o projeto principal

1. **Ative o ambiente virtual**
   ```
   venv\Scripts\activate
   ```

2. **Instale as dependências**
   ```
   pip install -r requirements.txt
   ```

3. **Configure o arquivo `config.py`**
   - Insira o token do seu bot, IDs corretos dos canais/grupos e a chave da API Gemini.

4. **Garanta que o bot está como admin no canal fonte e nos canais destino**

5. **Execute o projeto**
   ```
   python main.py
   ```

6. **Fluxo esperado**
   - O bot ficará ouvindo o canal fonte.
   - Quando um novo post for feito no canal fonte, ele será salvo no banco.
   - A cada intervalo definido (`SCHEDULE_HOURS`), o bot irá clonar o post para os canais destino.

7. **Dicas de teste**
   - Faça um post no canal fonte e veja se ele aparece nos canais destino após o intervalo.
   - Verifique o banco `clonagem.db` para ver se os dados estão sendo salvos.
   - Veja o terminal para logs e possíveis erros.

> **Obs:** Se precisar rodar o bot em modo debug, use o VSCode e coloque breakpoints no código.

Pronto! O projeto estará rodando e pronto para testes.

> **Importante:**  
> O projeto, do jeito atual, só clona posts novos que chegarem após o bot estar rodando.  
> **Posts antigos do canal fonte não são clonados automaticamente.**

## Como clonar posts antigos do canal fonte?

1. **Limitação da API:**  
   Bots do Telegram não conseguem acessar mensagens antigas de canais diretamente pela API, apenas recebem novas mensagens.

2. **Alternativas para clonar posts antigos:**
   - Use um script separado com uma conta userbot (ex: [Telethon](https://docs.telethon.dev/)) para baixar as mensagens antigas e inserir no banco.
   - Ou encaminhe manualmente as mensagens antigas para o bot (em grupos funciona, em canais não).

3. **Fluxo padrão do projeto:**  
   - O bot só irá postar/clonar mensagens que chegarem após ele estar rodando.
   - Para clonar mensagens antigas, será necessário um processo manual ou um script extra usando uma conta de usuário.

> **Sobre o formato das mídias:**  
> O bot, no formato atual, só clona mensagens individuais (foto, vídeo, documento) conforme chegam do canal fonte.  
> **Se o canal fonte postar álbuns (mídia em grupo):**
> - Para clonar como álbum (enviando várias mídias juntas), é necessário implementar o tratamento de "media groups" (álbuns) no código do bot.
> - O esqueleto atual **não trata álbuns**. Cada mídia do álbum seria tratada como mensagem separada.
> - Para clonar álbuns corretamente, adapte o handler para identificar `media_group_id` e armazenar/enviar todas as mídias do grupo juntas usando `send_media_group`.
