import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)

# --- CONFIGURAÇÃO INICIAL ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_ID = os.getenv("ALLOWED_CHAT_ID")

if TOKEN is None:
    raise ValueError("Erro: O token do Telegram não foi encontrado.")

# --- NOSSOS NOVOS "ESTADOS" DE CONVERSA ---
SELECT_MESA, SELECT_ITEM = range(2)

# --- COMANDOS NORMAIS ---

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envia uma mensagem com o ID do chat/grupo atual."""
    chat_id = update.message.chat.id
    await update.message.reply_text(f"O ID deste chat é: {chat_id}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start com o menu principal."""
    if ALLOWED_CHAT_ID and str(update.message.chat.id) != ALLOWED_CHAT_ID:
        await update.message.reply_text("Desculpe, este bot só pode ser usado no grupo autorizado.")
        return

    menu_text = (
        "Olá! Eu sou o bot de pedidos do restaurante 🍔\n\n"
        "Use os comandos:\n\n"
        "/pedir - Inicia um novo pedido com menu de botões\n"
        "/listar - Lista todas as mesas abertas\n"
        "/encerrar <mesa> - Fecha o pedido de uma mesa\n"
        "/cancelar - Cancela a operação atual\n"
    )
    # CORREÇÃO: Removido parse_mode
    await update.message.reply_text(menu_text)

# --- INÍCIO DO PROTÓTIPO: CONVERSATION HANDLER ---

async def start_pedido(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia o fluxo de pedido (/pedir) e pergunta a MESA."""
    if ALLOWED_CHAT_ID and str(update.message.chat.id) != ALLOWED_CHAT_ID:
        return ConversationHandler.END 

    keyboard = [
        [
            InlineKeyboardButton("Mesa 1", callback_data="mesa_1"),
            InlineKeyboardButton("Mesa 2", callback_data="mesa_2"),
        ],
        [
            InlineKeyboardButton("Mesa 3", callback_data="mesa_3"),
            InlineKeyboardButton("Mesa 4", callback_data="mesa_4"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Qual mesa deseja atender?", reply_markup=reply_markup)
    
    return SELECT_MESA


async def select_mesa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa o clique no botão da MESA e pergunta o ITEM."""
    query = update.callback_query
    await query.answer() 

    mesa_id = query.data
    context.user_data["current_mesa"] = mesa_id

    keyboard = [
        [
            InlineKeyboardButton("🍕 Pizza", callback_data="item_Pizza"),
            InlineKeyboardButton("🍟 Batata Frita", callback_data="item_Batata Frita"),
        ],
        [
            InlineKeyboardButton("🍢 Espeto", callback_data="item_Espeto"),
            InlineKeyboardButton("💧 Água", callback_data="item_Água"),
        ],
        [
            InlineKeyboardButton("🥤 Refri", callback_data="item_Refri"),
            InlineKeyboardButton("🍊 Suco", callback_data="item_Suco"),
        ],
        [
            InlineKeyboardButton("✅ CONCLUIR PEDIDO", callback_data="concluir"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # CORREÇÃO: Removido parse_mode
    await query.edit_message_text(
        text=f"Mesa: {mesa_id}\n\nO que deseja adicionar?",
        reply_markup=reply_markup
    )
    
    return SELECT_ITEM


async def select_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa o clique no botão de ITEM."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data 
    mesa_id = context.user_data.get("current_mesa")

    if callback_data == "concluir":
        # CORREÇÃO: Removido parse_mode
        await query.edit_message_text(f"Pedido da {mesa_id} concluído e salvo.")
        context.user_data.pop("current_mesa", None)
        return ConversationHandler.END

    else:
        item_name = callback_data.split("_")[1] 
        user_name = query.from_user.first_name
        
        mesas_dict = context.bot_data.get("mesas", {})

        if mesa_id in mesas_dict:
            mesas_dict[mesa_id]["items"].append(item_name)
        else:
            mesas_dict[mesa_id] = {
                "user": user_name,
                "items": [item_name],
                "status": "aberto"
            }
        
        # CORREÇÃO: Removido parse_mode
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"✅ {item_name} adicionado(a) à {mesa_id}."
        )
        
        return SELECT_ITEM


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela a operação atual."""
    if ALLOWED_CHAT_ID and str(update.message.chat.id) != ALLOWED_CHAT_ID:
        return ConversationHandler.END

    await update.message.reply_text("Operação cancelada.")
    context.user_data.pop("current_mesa", None) 
    return ConversationHandler.END

# --- FIM DO PROTÓTIPO ---


# --- COMANDOS QUE JÁ TINHAMOS (AGORA CORRIGIDOS) ---

async def listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista todas as mesas e seus pedidos."""
    if ALLOWED_CHAT_ID and str(update.message.chat.id) != ALLOWED_CHAT_ID:
        return

    mesas_dict = context.bot_data.get("mesas", {})
    if not mesas_dict:
        await update.message.reply_text("Nenhuma mesa com pedido aberto no momento.")
        return
        
    resposta = "📋 --- Mesas Abertas --- 📋\n\n"
    for mesa_id, pedido in mesas_dict.items():
        resposta += f"-----------------------------------\n"
        resposta += f"📌 Mesa: {mesa_id.upper()}\n"
        resposta += f"     Status: {pedido['status']} (por {pedido['user']})\n"
        resposta += f"     Itens:\n"
        for item in pedido["items"]:
            resposta += f"        - {item}\n"
        resposta += "\n"
    
    # CORREÇÃO: Removido parse_mode
    await update.message.reply_text(resposta)

async def prontos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ALLOWED_CHAT_ID and str(update.message.chat.id) != ALLOWED_CHAT_ID:
        return
    await update.message.reply_text("Função /prontos ainda não implementada.")

async def encerrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fecha (remove) uma mesa da lista de pedidos."""
    if ALLOWED_CHAT_ID and str(update.message.chat.id) != ALLOWED_CHAT_ID:
        return

    try:
        mesa_id = context.args[0].lower()
        mesas_dict = context.bot_data.get("mesas", {})
        
        if mesa_id in mesas_dict:
            mesas_dict.pop(mesa_id)
            # CORREÇÃO: Removido parse_mode
            await update.message.reply_text(f"Mesa {mesa_id} foi encerrada com sucesso.")
        else:
            # CORREÇÃO: Removido parse_mode
            await update.message.reply_text(f"Erro: Mesa {mesa_id} não foi encontrada ou já está fechada.")
    except (IndexError, ValueError):
        await update.message.reply_text("Formato incorreto. Use: /encerrar <mesa>\nExemplo: /encerrar mesa_1")


# --- CONFIGURAÇÃO E EXECUÇÃO DO BOT ---

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.bot_data["mesas"] = {}

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("pedir", start_pedido)],
        states={
            SELECT_MESA: [CallbackQueryHandler(select_mesa)],
            SELECT_ITEM: [CallbackQueryHandler(select_item)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )
    
    app.add_handler(conv_handler)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("listar", listar))
    app.add_handler(CommandHandler("encerrar", encerrar))
    app.add_handler(CommandHandler("prontos", prontos))
    app.add_handler(CommandHandler("getid", getid))
    app.add_handler(CommandHandler("cancelar", cancelar))

    print("Bot iniciado e rodando (modo de menu de botões)...")
    app.run_polling()

if __name__ == "__main__":
    main()