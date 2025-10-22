import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 1. Carrega as variáveis do arquivo .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Carrega o ID do chat permitido (do seu .env)
# O str() é para garantir que estamos comparando tipos iguais
ALLOWED_CHAT_ID = os.getenv("ALLOWED_CHAT_ID")

if TOKEN is None:
    raise ValueError("Erro: O token do Telegram não foi encontrado.")
if ALLOWED_CHAT_ID is None:
    print("AVISO: ALLOWED_CHAT_ID não está configurado no .env. O bot responderá a qualquer um.")

# --- FUNÇÃO DE AJUDA PARA PEGAR O ID ---

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envia uma mensagem com o ID do chat/grupo atual."""
    chat_id = update.message.chat.id
    await update.message.reply_text(f"O ID deste chat é: {chat_id}")

# --- FUNÇÕES DE COMANDO COM VERIFICAÇÃO ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start com o menu principal."""
    
    # --- BLOQUEIO DE SEGURANÇA ---
    if str(update.message.chat.id) != ALLOWED_CHAT_ID:
        await update.message.reply_text("Desculpe, este bot só pode ser usado no grupo autorizado.")
        return
    # --- FIM DO BLOQUEIO ---

    menu_text = (
        "Olá! Eu sou o bot de pedidos do restaurante 🍔\n\n"
        "Aqui estão os comandos que você pode usar:\n\n"
        "*/cadastrar* <mesa> <item>\n"
        "*/listar*\n"
        "*/encerrar* <mesa>\n"
    )
    await update.message.reply_text(menu_text, parse_mode="Markdown")


async def cadastrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cadastra um novo pedido ou adiciona item a uma mesa existente."""
    
    # --- BLOQUEIO DE SEGURANÇA ---
    if str(update.message.chat.id) != ALLOWED_CHAT_ID:
        return # Ignora silenciosamente no privado
    # --- FIM DO BLOQUEIO ---

    if len(context.args) < 2:
        await update.message.reply_text("Formato incorreto. Use: /cadastrar <mesa> <item>\nExemplo: /cadastrar mesa1 1 Pizza e 1 Refri")
        return
        
    mesa_id = context.args[0].lower()
    descricao_item = " ".join(context.args[1:])
    user_name = update.message.from_user.first_name
    
    mesas_dict = context.bot_data.get("mesas", {})
    
    if mesa_id in mesas_dict:
        mesas_dict[mesa_id]["items"].append(descricao_item)
        await update.message.reply_text(f"Item adicionado com sucesso à *{mesa_id}*.", parse_mode="Markdown")
    else:
        mesas_dict[mesa_id] = {
            "user": user_name,
            "items": [descricao_item],
            "status": "aberto"
        }
        await update.message.reply_text(f"Mesa *{mesa_id}* aberta com sucesso e item cadastrado.", parse_mode="Markdown")


async def listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista todas as mesas e seus pedidos."""
    
    # --- BLOQUEIO DE SEGURANÇA ---
    if str(update.message.chat.id) != ALLOWED_CHAT_ID:
        return # Ignora silenciosamente no privado
    # --- FIM DO BLOQUEIO ---

    mesas_dict = context.bot_data.get("mesas", {})
    
    if not mesas_dict:
        await update.message.reply_text("Nenhuma mesa com pedido aberto no momento.")
        return
        
    resposta = "📋 *--- Mesas Abertas ---* 📋\n\n"
    
    for mesa_id, pedido in mesas_dict.items():
        user = pedido['user']
        status = pedido['status']
        
        resposta += f"-----------------------------------\n"
        resposta += f"📌 *Mesa:* {mesa_id.upper()}\n"
        resposta += f"     *Status:* {status} (por {user})\n"
        resposta += f"     *Itens:*\n"
        
        for item in pedido["items"]:
            resposta += f"        - {item}\n"
        resposta += "\n"
        
    await update.message.reply_text(resposta, parse_mode="Markdown")


async def prontos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder para o comando /prontos."""
    # --- BLOQUEIO DE SEGURANÇA ---
    if str(update.message.chat.id) != ALLOWED_CHAT_ID:
        return
    # --- FIM DO BLOQUEIO ---
    await update.message.reply_text("Função /prontos ainda não implementada.")


async def encerrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fecha (remove) uma mesa da lista de pedidos."""
    
    # --- BLOQUEIO DE SEGURANÇA ---
    if str(update.message.chat.id) != ALLOWED_CHAT_ID:
        return
    # --- FIM DO BLOQUEIO ---

    try:
        mesa_id = context.args[0].lower()
        mesas_dict = context.bot_data.get("mesas", {})
        
        if mesa_id in mesas_dict:
            pedido_encerrado = mesas_dict.pop(mesa_id)
            await update.message.reply_text(f"Mesa *{mesa_id}* foi encerrada com sucesso.", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"Erro: Mesa *{mesa_id}* não foi encontrada ou já está fechada.", parse_mode="Markdown")

    except (IndexError, ValueError):
        await update.message.reply_text("Formato incorreto. Use: /encerrar <mesa>\nExemplo: /encerrar mesa1")


# --- CONFIGURAÇÃO E EXECUÇÃO DO BOT ---

app = ApplicationBuilder().token(TOKEN).build()
app.bot_data["mesas"] = {}

# Registra os handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cadastrar", cadastrar))
app.add_handler(CommandHandler("listar", listar))
app.add_handler(CommandHandler("prontos", prontos))
app.add_handler(CommandHandler("encerrar", encerrar))
# Adiciona o novo comando /getid
app.add_handler(CommandHandler("getid", getid))

print("Bot iniciado e rodando (modo de teste com mesas)...")
app.run_polling()