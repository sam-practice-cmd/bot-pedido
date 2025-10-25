🤖 Bot de Pedidos para Restaurante (Telegram)

Este é o repositório do Bot do Telegram desenvolvido para o Trabalho Interdisciplinar de Sistemas Integrados de Gestão Empresarial da PUC Minas.

Este bot atua como a interface de front-end (o "garçom" e a "cozinha") para a API de Restaurante central, permitindo a gestão completa de comandas, mesas e pedidos diretamente pelo Telegram.

✨ Funcionalidades Principais

👮 Segurança por Grupos: O bot só responde a comandos em dois grupos privados e autorizados:

Grupo Garçons: Pode abrir comandas, fazer pedidos, listar produtos e fechar contas.

Grupo Cozinha: Pode visualizar pedidos pendentes e atualizar seus status (ex: "em preparo", "pronto").

📡 Integração Direta com API: O bot não possui lógica de negócios. Ele é um cliente async que consome os endpoints da API REST do restaurante.

🔔 Notificações em Tempo Real: A Cozinha notifica automaticamente o grupo dos Garçons quando o status de um pedido muda (ex: "Pedido 5 está PRONTO!").

🛠️ Tecnologias Utilizadas

Python 3

python-telegram-bot (para a API do Telegram)

httpx (para chamadas de API assíncronas)

python-dotenv (para gestão de variáveis de ambiente)

🚀 Como Executar Localmente

1. Pré-requisitos

Python 3.10 ou superior.

A API do Restaurante deve estar rodando (seja localmente ou online).

Um Bot criado no Telegram (via @BotFather) para obter o TOKEN.

2. Instalação

Clone este repositório:

git clone [https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git](https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git)
cd SEU-REPOSITORIO


Instale as dependências:

# No Windows
py -m pip install -r requirements.txt

# No macOS / Linux
python3 -m pip install -r requirements.txt


(Se o requirements.txt não existir, rode: py -m pip install python-telegram-bot httpx python-dotenv)

3. Configuração do Ambiente (.env)

Crie um arquivo .env na raiz do projeto (copiando o .env.example, se houver) e preencha as seguintes variáveis:

# Token secreto do seu bot (obtido no @BotFather)
TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."

# URL base da sua API (IMPORTANTE: deve ser a URL pública, não localhost, se o bot estiver online)
API_BASE_URL="http://localhost:3000"

# --- IDs dos Grupos (Obrigatórios) ---
# Crie os grupos, adicione o bot e use o comando /getid para descobrir os IDs

# ID do grupo onde os garçons farão os pedidos
GARCOM_GROUP_ID="-100123456789"

# ID do grupo onde a cozinha verá e atualizará os pedidos
COZINHA_GROUP_ID="-100987654321"


4. Rodando o Bot

Com o .env configurado e a API rodando, inicie o bot:

py bot.py


O terminal deve exibir: Bot (Modo API) iniciado e rodando...

📋 Comandos Disponíveis

O bot só aceitará comandos vindos dos grupos configurados no .env.

👨‍🍳 Comandos do Grupo "Garçons"

/start

Mostra este menu de ajuda.

/abrir [ID_Mesa] [Nome_Cliente]

Abre uma nova comanda para a mesa e cliente especificados. O bot retornará o ID da Comanda criada.

Ex: /abrir 1 Joao Silva

/pedir [ID_Comanda] [ID_Produto] [Qtd]

Adiciona um ou mais produtos a uma comanda existente.

Ex: /pedir 101 5 2 (Pede 2x do produto ID 5 para a comanda 101)

/fechar [ID_Comanda]

Encerra uma comanda. A API calcula o total e libera a mesa.

Ex: /fechar 101

/comanda [ID_Comanda]

Busca os detalhes de uma comanda específica, incluindo todos os pedidos e o valor total atual.

Ex: /comanda 101

/produtos

Lista todos os produtos disponíveis no cardápio, com seus IDs e preços.

/mesas

Mostra o status atual de todas as mesas (disponível, ocupada).

🍳 Comandos do Grupo "Cozinha"

/start

Mostra este menu de ajuda.

/pedidos_aguardando

Lista todos os pedidos que acabaram de ser feitos e estão na fila.

/pedidos_em_preparo

Lista os pedidos que já estão sendo preparados.

/pedidos_prontos

Lista os pedidos finalizados e prontos para entrega.

/em_preparo [ID_Pedido]

Muda o status de um pedido para "em preparo".

Ex: /em_preparo 52

/pronto [ID_Pedido]

Muda o status de um pedido para "pronto" e notifica o grupo dos Garçons.

Ex: /pronto 52