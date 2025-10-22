import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 1. Carrega as variáveis do arquivo .env
load_dotenv()

# 2. Pega o token do ambiente
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if TOKEN is None:
    raise ValueError("Erro: O token do Telegram não foi encontrado.")

# --- FUNÇÕES DE COMANDO ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start com o menu principal."""
    menu_text = (
        "Olá! Eu sou o bot de pedidos do restaurante 🍔\n\n"
        "Aqui estão os comandos que você pode usar:\n\n"
        "*/cadastrar* - Inicia um novo pedido\n"
        "*/listar* - Lista todos os pedidos em andamento\n"
        "*/prontos* - Mostra os pedidos prontos para entrega\n"
        "*/encerrar* - Fecha um pedido\n"
    )
    
    # CORREÇÃO APLICADA AQUI:
    # Trocamos para "Markdown" (v1) que é menos rigoroso 
    # e não precisamos mais do .replace()
    await update.message.reply_text(menu_text, parse_mode="Markdown")

async def cadastrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder para o comando /cadastrar."""
    await update.message.reply_text("Função /cadastrar ainda não implementada.")
    # Aqui entrará a lógica para cadastrar um pedido

async def listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder para o comando /listar."""
    await update.message.reply_text("Função /listar ainda não implementada.")
    # Aqui entrará a lógica para buscar na API e listar os pedidos

async def prontos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder para o comando /prontos."""
    await update.message.reply_text("Função /prontos ainda não implementada.")

async def encerrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder para o comando /encerrar."""
    await update.message.reply_text("Função /encerrar ainda não implementada.")


# --- CONFIGURAÇÃO E EXECUÇÃO DO BOT ---

# 3. Cria o ApplicationBuilder
app = ApplicationBuilder().token(TOKEN).build()

# 4. Registra todos os handlers (manipuladores de comando)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cadastrar", cadastrar))
app.add_handler(CommandHandler("listar", listar))
app.add_handler(CommandHandler("prontos", prontos))
app.add_handler(CommandHandler("encerrar", encerrar))

# 5. Inicia o bot
print("Bot iniciado e rodando...")
app.run_polling()