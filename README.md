# 🤖 Bot de Pedidos para Restaurante (Telegram)

> Projeto desenvolvido para o **Trabalho Interdisciplinar de Sistemas Integrados de Gestão Empresarial** da **PUC Minas**.

Este bot atua como a **interface de front-end** (o "garçom" e a "cozinha") para a **API central do restaurante**, permitindo a **gestão completa de comandas, mesas e pedidos diretamente pelo Telegram**.

---

## ✨ Funcionalidades Principais

### 👮 Segurança por Grupos
O bot só responde a comandos em **dois grupos privados e autorizados**:

- **👨‍🍷 Grupo Garçons:** abrir comandas, fazer pedidos, listar produtos e fechar contas.  
- **👨‍🍳 Grupo Cozinha:** visualizar pedidos pendentes e atualizar status (ex: “em preparo”, “pronto”).

### 📡 Integração Direta com a API
O bot **não possui lógica de negócios** — ele é apenas um **cliente assíncrono** que consome os **endpoints da API REST** do restaurante.

### 🔔 Notificações em Tempo Real
A **Cozinha** notifica automaticamente o **grupo dos Garçons** sempre que o status de um pedido muda (ex: “Pedido 5 está PRONTO!”).

---

## 🛠️ Tecnologias Utilizadas

- 🐍 **Python 3**
- 💬 **python-telegram-bot** — integração com o Telegram  
- 🌐 **httpx** — chamadas de API assíncronas  
- 🔑 **python-dotenv** — gestão de variáveis de ambiente  

---

## 💡 Extensões Recomendadas (VSCode)

Para melhor experiência de desenvolvimento:

- **Python** (Microsoft) → linting, debugging e IntelliSense  
- **Pylance** (Microsoft) → aprimora IntelliSense e checagem de tipos  
- **DotENV** → syntax highlighting para arquivos `.env`  

---

## 🚀 Como Executar Localmente

### 1️⃣ Pré-requisitos

- Python **3.10+**
- A **API do Restaurante** deve estar rodando (local ou online)
- Um **bot criado via [@BotFather](https://t.me/BotFather)** para obter o TOKEN

---

### 2️⃣ Instalação

Clone o repositório e acesse a pasta:

```bash
git clone https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
cd SEU-REPOSITORIO
```

#### Método A — Usando `requirements.txt` (recomendado)
```bash
# Windows
py -m pip install -r requirements.txt

# macOS / Linux
python3 -m pip install -r requirements.txt
```

#### Método B — Instalando manualmente
```bash
# Windows
py -m pip install python-telegram-bot httpx python-dotenv

# macOS / Linux
python3 -m pip install python-telegram-bot httpx python-dotenv
```

---

### 3️⃣ Configuração do Ambiente `.env`

Crie um arquivo `.env` na raiz do projeto (ou copie de `.env.example`):

```bash
# Token do Bot (obtido via @BotFather)
TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."

# URL base da API (use URL pública se o bot estiver online)
API_BASE_URL="http://localhost:3000"

# --- IDs dos Grupos (use /getid para descobrir) ---
GARCOM_GROUP_ID="-100123456789"
COZINHA_GROUP_ID="-100987654321"
```

---

### 4️⃣ Rodando o Bot

Execute o bot com:

```bash
py bot.py
```

O terminal deve exibir:
```
Bot (Modo API) iniciado e rodando...
```

---

## 📋 Comandos Disponíveis

O bot **só aceitará comandos vindos dos grupos configurados no `.env`**.

---

### 🍽️ Grupo “Garçons”

| Comando | Descrição | Exemplo |
|----------|------------|---------|
| `/start` | Mostra o menu de ajuda | — |
| `/abrir [ID_Mesa] [Nome_Cliente]` | Abre nova comanda | `/abrir 1 Joao Silva` |
| `/pedir [ID_Comanda] [ID_Produto] [Qtd]` | Adiciona produtos a uma comanda | `/pedir 101 5 2` |
| `/fechar [ID_Comanda]` | Encerra uma comanda e libera mesa | `/fechar 101` |
| `/comanda [ID_Comanda]` | Mostra detalhes e total atual | `/comanda 101` |
| `/produtos` | Lista produtos com IDs e preços | — |
| `/mesas` | Mostra status atual das mesas | — |

---

### 🔪 Grupo “Cozinha”

| Comando | Descrição | Exemplo |
|----------|------------|---------|
| `/start` | Mostra o menu de ajuda | — |
| `/pedidos_aguardando` | Lista pedidos recém-feitos | — |
| `/pedidos_em_preparo` | Lista pedidos em preparo | — |
| `/pedidos_prontos` | Lista pedidos finalizados | — |
| `/em_preparo [ID_Pedido]` | Marca pedido como “em preparo” | `/em_preparo 52` |
| `/pronto [ID_Pedido]` | Marca pedido como “pronto” e notifica garçons | `/pronto 52` |

---

## 🧩 Estrutura Simplificada

```
📂 bot-restaurante/
 ┣ 📜 bot.py
 ┣ 📜 .env.example
 ┣ 📜 requirements.txt
 ┣ 📂 src/
 ┃ ┣ 📜 handlers.py
 ┃ ┣ 📜 services.py
 ┃ ┗ 📜 utils.py
 ┗ 📂 logs/
```

---

## 💬 Créditos

Desenvolvido por **[Seu Nome]**  
PUC Minas — Sistemas de Informação  
Trabalho Interdisciplinar de **Sistemas Integrados de Gestão Empresarial**
