from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TELEGRAM_BOT_TOKEN = ""  # Substitua pelo seu token

async def list_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text("Envie uma mensagem em cada grupo/canal que deseja capturar o ID.\n"
                                    "Este bot irá responder com o ID do chat.")
    # O ID do chat pode ser obtido em qualquer mensagem recebida
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title or "Sem título"
    await update.message.reply_text(f"ID: {chat_id}\nTítulo: {chat_title}")

# Observação:
# O bot SÓ recebe mensagens diretamente em grupos ou canais SE:
# - Em grupos: o bot precisa ser adicionado e receber mensagens (não pode ser "somente admin silencioso").
# - Em canais: bots NÃO recebem mensagens de outros membros/canal, apenas mensagens que eles mesmos enviam.
#   Para obter o ID de um canal, faça o seguinte:
#   1. Adicione o bot como admin no canal.
#   2. Envie uma mensagem QUALQUER no canal.
#   3. No seu código, use o método getUpdates ou envie uma mensagem para o bot em privado e use o chat_id retornado.
#   4. Alternativamente, encaminhe uma mensagem do canal para o bot em privado. O bot pode ler o "forward_from_chat.id".

# Para facilitar, adicione um handler para qualquer mensagem privada para capturar encaminhamentos:
async def any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.forward_from_chat:
        chat_id = update.message.forward_from_chat.id
        chat_title = update.message.forward_from_chat.title or "Sem título"
        await update.message.reply_text(f"ID do canal/grupo encaminhado: {chat_id}\nTítulo: {chat_title}")
    else:
        chat_id = update.effective_chat.id
        chat_title = update.effective_chat.title or "Sem título"
        await update.message.reply_text(f"ID deste chat: {chat_id}\nTítulo: {chat_title}")

def main():
    import sys
    if sys.version_info < (3, 7):
        print("Este script requer Python 3.7 ou superior.")
        return
    # Solução para o erro de weakref: use python-telegram-bot >= 20.x e Python >= 3.7
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", list_chats))
    app.add_handler(CommandHandler("id", list_chats))
    app.add_handler(MessageHandler(filters.ALL, any_message))  # Captura qualquer mensagem privada ou encaminhada
    app.run_polling()

if __name__ == "__main__":
    main()
