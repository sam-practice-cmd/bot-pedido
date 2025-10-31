import os
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIGURAÇÃO INICIAL E VARIÁVEIS DE AMBIENTE ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# ATENÇÃO: Coloque a URL pública da sua API (ex: https://meu-servidor.onrender.com)
# NÃO PODE SER http://localhost:3000
API_BASE_URL = os.getenv("API_BASE_URL") 
GARCOM_GROUP_ID = os.getenv("GARCOM_GROUP_ID")
COZINHA_GROUP_ID = os.getenv("COZINHA_GROUP_ID")

if not all([TOKEN, API_BASE_URL, GARCOM_GROUP_ID, COZINHA_GROUP_ID]):
    raise ValueError("Erro: Verifique se todas as variáveis estão no .env (TOKEN, API_BASE_URL, GARCOM_GROUP_ID, COZINHA_GROUP_ID)")

# URL base da API (conforme seu README)
API_URL = f"{API_BASE_URL}/api"

# --- FUNÇÕES DE AJUDA ---

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envia uma mensagem com o ID do chat/grupo atual."""
    chat_id = update.message.chat.id
    await update.message.reply_text(f"O ID deste Chat/Grupo é: {chat_id}")

# Função helper para formatar erros da API
def formatar_erro_api(e: httpx.HTTPStatusError) -> str:
    try:
        # Tenta pegar a mensagem de erro específica do JSON da API
        erro_data = e.response.json()
        if 'message' in erro_data:
            return f"Erro na API: {erro_data['message']}"
        if 'error' in erro_data:
             return f"Erro na API: {erro_data['error']}"
    except Exception:
        pass # Se não for JSON, retorna o erro genérico
    return f"Erro na API ({e.response.status_code}): {e.response.text}"

# --- NOVO COMANDO /START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra o menu de ajuda principal."""
    chat_id_str = str(update.message.chat.id)
    
    if chat_id_str == GARCOM_GROUP_ID:
        menu_text = (
            "--- Menu Garçom 👨‍🍳 ---\n\n"
            "/abrir [ID_Mesa] [Nome_Cliente]\n"
            "   (Abre uma comanda)\n\n"
            "/pedir [ID_Comanda] [ID_Mesa] [ID_Produto] [Qtd]\n"
            "   (Adiciona um pedido)\n\n"
            "/fechar [ID_Comanda]\n"
            "   (Fecha e calcula a comanda)\n\n"
            "/comanda [ID_Comanda]\n"
            "   (Vê detalhes da comanda)\n\n"
            "/produtos\n"
            "   (Lista o cardápio)\n\n"
            "/mesas\n"
            "   (Lista o status das mesas)\n\n"
            "/ver_prontos\n"
            "   (Vê pedidos prontos para entrega)"
        )
    elif chat_id_str == COZINHA_GROUP_ID:
        menu_text = (
            "--- Menu Cozinha 🍳 ---\n\n"
            "/pedidos_aguardando\n"
            "   (Lista pedidos na fila)\n\n"
            "/pedidos_em_preparo\n"
            "   (Lista pedidos em preparo)\n\n"
            "/pedidos_prontos\n"
            "   (Lista pedidos prontos)\n\n"
            "/em_preparo [ID_Pedido]\n"
            "   (Muda status para 'em preparo')\n\n"
            "/pronto [ID_Pedido]\n"
            "   (Muda status para 'pronto')"
        )
    else:
        # Resposta para chats privados ou não autorizados
        menu_text = (
            "Bot não autorizado para este chat.\n"
            f"ID deste chat: {update.message.chat.id}\n"
            "Adicione este ID ao seu arquivo .env (GARCOM_GROUP_ID ou COZINHA_GROUP_ID)."
        )
        
    await update.message.reply_text(menu_text)

# --- COMANDOS DO GARÇOM (GRUPO GARÇOM) ---

async def abrir_comanda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/abrir [mesa_id] [nome_cliente] - Cria a Comanda."""
    if str(update.message.chat.id) != GARCOM_GROUP_ID:
        return await update.message.reply_text("Comando restrito ao grupo de Garçons.")

    try:
        if len(context.args) < 2:
            raise ValueError("Formato incorreto. Use: /abrir [ID da Mesa] [Nome do Cliente]")
        
        mesa_id = int(context.args[0])
        nome_cliente = " ".join(context.args[1:])
        
        payload = {"mesa_id": mesa_id, "nome_cliente": nome_cliente}
        
        async with httpx.AsyncClient() as client:
            # POST /api/comandas
            response = await client.post(f"{API_URL}/comandas", json=payload)
            response.raise_for_status() # Causa erro se a API falhar (4xx, 5xx)
            data = response.json()

        await update.message.reply_text(
            f"✅ Comanda aberta com sucesso!\n\n"
            f"ID da Comanda: {data['id']} (Guarde este ID!)\n"
            f"Cliente: {data['nome_cliente']}\n"
            f"Mesa ID: {data['mesa_id']}"
        )

    except (ValueError, TypeError):
        await update.message.reply_text("Formato incorreto. Use: /abrir [ID da Mesa] [Nome do Cliente]")
    except httpx.HTTPStatusError as e:
        await update.message.reply_text(formatar_erro_api(e))
    except Exception as e:
        await update.message.reply_text(f"Ocorreu um erro: {str(e)}")


async def pedir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/pedir [comanda_id] [mesa_id] [produto_id] [quantidade] - Adiciona um item."""
    if str(update.message.chat.id) != GARCOM_GROUP_ID:
        return await update.message.reply_text("Comando restrito ao grupo de Garçons.")

    try:
        if len(context.args) != 4:
            raise ValueError("Formato incorreto. Use: /pedir [ID_Comanda] [ID_Mesa] [ID_Produto] [Qtd]")
        
        comanda_id = int(context.args[0])
        mesa_id = int(context.args[1])
        produto_id = int(context.args[2])
        quantidade = int(context.args[3])
        
        # Pega o nome do garçom que está fazendo o pedido
        garcom_nome = update.message.from_user.first_name

        # --- ALTERAÇÃO AQUI ---
        # Adicionado o campo 'cliente' ao payload, conforme novo schema
        payload = {
            "comanda_id": comanda_id,
            "mesa_id": mesa_id,
            "produto_id": produto_id,
            "quantidade": quantidade,
            "cliente": garcom_nome 
        }
        # --- FIM DA ALTERAÇÃO ---
        
        async with httpx.AsyncClient() as client:
            # POST /api/pedidos
            response = await client.post(f"{API_URL}/pedidos", json=payload)
            response.raise_for_status()
            data = response.json()

        await update.message.reply_text(
            f"Pedido (ID: {data['id']}) adicionado à comanda {data['comanda_id']}.\n"
            f"Status: {data['status']}"
        )
            
    except (ValueError, TypeError):
        await update.message.reply_text("Formato incorreto. Use: /pedir [ID_Comanda] [ID_Mesa] [ID_Produto] [Qtd]")
    except httpx.HTTPStatusError as e:
        await update.message.reply_text(formatar_erro_api(e))
    except Exception as e:
        await update.message.reply_text(f"Ocorreu um erro: {str(e)}")


async def fechar_comanda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/fechar [id_comanda] - Encerra a Comanda e calcula o total."""
    if str(update.message.chat.id) != GARCOM_GROUP_ID:
        return await update.message.reply_text("Comando restrito ao grupo de Garçons.")

    try:
        id_comanda = int(context.args[0])
        
        async with httpx.AsyncClient() as client:
            # PATCH /api/comandas/:id/encerrar
            response = await client.patch(f"{API_URL}/comandas/{id_comanda}/encerrar")
            response.raise_for_status()
            data = response.json()
        
        # README diz que essa rota retorna o total e libera a mesa
        await update.message.reply_text(
            f"Comanda {id_comanda} encerrada.\n"
            f"Valor Total: R$ {data['total']:.2f}\n"
            f"Mesa (ID: {data['mesa_id']}) agora está disponível."
        )
            
    except (IndexError, ValueError):
        await update.message.reply_text("Formato incorreto. Use: /fechar [ID_Comanda]")
    except httpx.HTTPStatusError as e:
        await update.message.reply_text(formatar_erro_api(e))
    except Exception as e:
        await update.message.reply_text(f"Ocorreu um erro: {str(e)}")


async def listar_produtos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/produtos - Lista os produtos do restaurante."""
    if str(update.message.chat.id) != GARCOM_GROUP_ID:
        return await update.message.reply_text("Comando restrito ao grupo de Garçons.")

    try:
        async with httpx.AsyncClient() as client:
            # GET /api/produtos
            response = await client.get(f"{API_URL}/produtos")
            response.raise_for_status()
            produtos = response.json()
            
        if not produtos:
            return await update.message.reply_text("Nenhum produto disponível cadastrado.")

        resposta = "--- Cardápio (ID - Nome - Preço) ---\n\n"
        for p in produtos:
            # Mostra apenas produtos disponíveis
            if p.get('disponibilidade', True): 
                resposta += f"{p['id']} - {p['nome']} - R$ {p['preco']}\n"
        
        await update.message.reply_text(resposta)
            
    except httpx.HTTPStatusError as e:
        await update.message.reply_text(formatar_erro_api(e))
    except Exception as e:
        await update.message.reply_text(f"Ocorreu um erro: {str(e)}")

async def listar_mesas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/mesas - Lista o status de todas as mesas."""
    if str(update.message.chat.id) != GARCOM_GROUP_ID:
        return await update.message.reply_text("Comando restrito ao grupo de Garçons.")

    try:
        async with httpx.AsyncClient() as client:
            # GET /api/mesas
            response = await client.get(f"{API_URL}/mesas")
            response.raise_for_status()
            mesas = response.json()
            
        if not mesas:
            return await update.message.reply_text("Nenhuma mesa cadastrada.")

        resposta = "--- Status das Mesas ---\n\n"
        for m in mesas:
            resposta += f"ID: {m['id']} (Nº: {m['numero']}) - Status: {m['status'].upper()}\n"
        
        await update.message.reply_text(resposta)
            
    except httpx.HTTPStatusError as e:
        await update.message.reply_text(formatar_erro_api(e))
    except Exception as e:
        await update.message.reply_text(f"Ocorreu um erro: {str(e)}")


async def buscar_comanda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/comanda [id_comanda] - Lista pedidos e total da comanda."""
    if str(update.message.chat.id) != GARCOM_GROUP_ID:
        return await update.message.reply_text("Comando restrito ao grupo de Garçons.")

    try:
        id_comanda = int(context.args[0])
        
        async with httpx.AsyncClient() as client:
            # GET /api/comandas/:id
            response = await client.get(f"{API_URL}/comandas/{id_comanda}")
            response.raise_for_status()
            comanda = response.json()

        # Formatando a resposta (baseado no Exemplo 7 do README)
        resposta = f"--- Comanda {comanda['id']} ---\n"
        resposta += f"Cliente: {comanda['nome_cliente']}\n"
        resposta += f"Mesa: {comanda['mesas']['numero']} (Status: {comanda['mesas']['status']})\n"
        resposta += f"Status Comanda: {comanda['status']}\n\n"
        resposta += "Pedidos:\n"
        
        if not comanda['pedidos']:
            resposta += "- Nenhum pedido registrado.\n"
        else:
            for p in comanda['pedidos']:
                resposta += f"- {p['quantidade']}x {p['produtos']['nome']} (Status: {p['status']})\n"
        
        resposta += f"\nTotal Atual: R$ {comanda['total']:.2f}"
        
        await update.message.reply_text(resposta)
            
    except (IndexError, ValueError):
        await update.message.reply_text("Formato incorreto. Use: /comanda [ID_Comanda]")
    except httpx.HTTPStatusError as e:
        await update.message.reply_text(formatar_erro_api(e))
    except Exception as e:
        await update.message.reply_text(f"Ocorreu um erro: {str(e)}")

# --- NOVO COMANDO PARA GARÇOM ---
async def ver_pedidos_prontos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ver_prontos - (Garçom) Lista os pedidos prontos para entrega."""
    if str(update.message.chat.id) != GARCOM_GROUP_ID:
        return await update.message.reply_text("Comando restrito ao grupo de Garçons.")

    try:
        async with httpx.AsyncClient() as client:
            # Chama o mesmo endpoint da cozinha: GET /api/pedidos/prontos
            response = await client.get(f"{API_URL}/pedidos/prontos")
            response.raise_for_status()
            pedidos = response.json()
            
        if not pedidos:
            return await update.message.reply_text("Nenhum pedido pronto para entrega no momento.")

        resposta = "--- Pedidos Prontos para Entrega ---\n\n"
        for p in pedidos:
            # O README não especifica o retorno, então mostramos o que temos
            resposta += f"ID Pedido: {p['id']} (Comanda: {p['comanda_id']})\n"
            resposta += f"Qtd: {p['quantidade']}x Produto ID: {p['produto_id']}\n\n"
        
        await update.message.reply_text(resposta)
            
    except httpx.HTTPStatusError as e:
        await update.message.reply_text(formatar_erro_api(e))
    except Exception as e:
        await update.message.reply_text(f"Ocorreu um erro: {str(e)}")

# --- COMANDOS DA COZINHA (GRUPO COZINHA) ---

async def listar_pedidos_status(update: Update, context: ContextTypes.DEFAULT_TYPE, endpoint: str, titulo: str):
    """Função interna para listar pedidos por status."""
    if str(update.message.chat.id) != COZINHA_GROUP_ID:
        return await update.message.reply_text("Comando restrito ao grupo da Cozinha.")

    try:
        async with httpx.AsyncClient() as client:
            # GET /api/pedidos/prontos ou /em-preparo
            response = await client.get(f"{API_URL}/pedidos/{endpoint}")
            response.raise_for_status()
            pedidos = response.json()
            
        if not pedidos:
            return await update.message.reply_text(f"Nenhum pedido com status '{titulo}'.")

        resposta = f"--- Pedidos: {titulo.upper()} ---\n\n"
        for p in pedidos:
            # O README não especifica o retorno, então mostramos o que temos
            resposta += f"ID Pedido: {p['id']} (Comanda: {p['comanda_id']})\n"
            resposta += f"Qtd: {p['quantidade']}x Produto ID: {p['produto_id']}\n\n"
        
        await update.message.reply_text(resposta)
            
    except httpx.HTTPStatusError as e:
        await update.message.reply_text(formatar_erro_api(e))
    except Exception as e:
        await update.message.reply_text(f"Ocorreu um erro: {str(e)}")


async def pedidos_aguardando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/pedidos_aguardando - Lista o que está aguardando preparo."""
    if str(update.message.chat.id) != COZINHA_GROUP_ID:
        return await update.message.reply_text("Comando restrito ao grupo da Cozinha.")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/pedidos?status=aguardando%20preparo")
            response.raise_for_status(); pedidos = response.json()
        
        if not pedidos: return await update.message.reply_text("Nenhum pedido aguardando preparo.")
        
        resposta = "--- Pedidos Aguardando Preparo ---\n\n"
        for p in pedidos:
            resposta += f"ID Pedido: {p['id']} (Comanda: {p['comanda_id']})\n"
        await update.message.reply_text(resposta)
    except Exception as e: await update.message.reply_text(f"Erro: {e}")


async def pedidos_em_preparo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/pedidos_em_preparo - Lista pedidos em preparo."""
    await listar_pedidos_status(update, context, "em-preparo", "Em Preparo")


async def pedidos_prontos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/pedidos_prontos - Lista pedidos prontos."""
    await listar_pedidos_status(update, context, "prontos", "Prontos")


async def set_status_pedido(update: Update, context: ContextTypes.DEFAULT_TYPE, novo_status: str):
    """Função interna para mudar o status de um pedido."""
    if str(update.message.chat.id) != COZINHA_GROUP_ID:
        return await update.message.reply_text("Comando restrito ao grupo da Cozinha.")
        
    try:
        id_pedido = int(context.args[0])
        payload = {"status": novo_status}
        
        async with httpx.AsyncClient() as client:
            # PATCH /api/pedidos/:id
            response = await client.patch(f"{API_URL}/pedidos/{id_pedido}", json=payload)
            response.raise_for_status()
            data = response.json()

        await update.message.reply_text(f"Pedido {data['id']} atualizado para: {data['status']}")
            
        # Notificar o grupo dos Garçons
        await context.bot.send_message(
            chat_id=GARCOM_GROUP_ID, 
            text=f"🔔 AVISO: Pedido {data['id']} (Comanda: {data['comanda_id']}) está *{novo_status.upper()}*!",
            parse_mode="Markdown"
        )

    except (IndexError, ValueError):
        await update.message.reply_text(f"Formato incorreto. Use: /{novo_status.replace(' ', '_')} [ID_Pedido]")
    except httpx.HTTPStatusError as e:
        await update.message.reply_text(formatar_erro_api(e))
    except Exception as e:
        await update.message.reply_text(f"Ocorreu um erro: {str(e)}")


async def em_preparo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/em_preparo [id_pedido] - Atualiza pedido para 'em preparo'."""
    await set_status_pedido(update, context, "em preparo")


async def pronto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/pronto [id_pedido] - Atualiza pedido para 'pronto'."""
    await set_status_pedido(update, context, "pronto")

# --- CONFIGURAÇÃO E EXECUÇÃO DO BOT ---

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Comandos do Garçom
    app.add_handler(CommandHandler("abrir", abrir_comanda))
    app.add_handler(CommandHandler("pedir", pedir))
    app.add_handler(CommandHandler("fechar", fechar_comanda))
    app.add_handler(CommandHandler("produtos", listar_produtos))
    app.add_handler(CommandHandler("mesas", listar_mesas))
    app.add_handler(CommandHandler("comanda", buscar_comanda)) 
    app.add_handler(CommandHandler("ver_prontos", ver_pedidos_prontos)) # <-- NOVO HANDLER
    
    # Comandos da Cozinha
    app.add_handler(CommandHandler("em_preparo", em_preparo))
    app.add_handler(CommandHandler("pronto", pronto))
    app.add_handler(CommandHandler("pedidos_aguardando", pedidos_aguardando))
    app.add_handler(CommandHandler("pedidos_em_preparo", pedidos_em_preparo))
    app.add_handler(CommandHandler("pedidos_prontos", pedidos_prontos))
    
    # Comando de Ajuda
    app.add_handler(CommandHandler("getid", getid))
    
    # Comando /start genérico
    app.add_handler(CommandHandler("start", start)) # Adicionei o /start

    print("Bot (Modo API) iniciado e rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()

