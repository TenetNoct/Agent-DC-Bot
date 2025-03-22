# Bot Conversacional para Discord com LM Studio

Um bot para Discord que utiliza modelos de linguagem locais através do LM Studio para criar interações naturais e inteligentes.

## Características

- 🤖 Integração com LM Studio para processamento de linguagem natural
- 💬 Responde a menções e palavras-chave configuráveis
- 🧠 Sistema de memória para manter contexto das conversas
- 🔍 Capacidade de busca na web para informações atualizadas
- ⚙️ Configuração flexível via comandos, assistente interativo ou arquivo de configuração
- 📝 Suporte a comandos personalizados
- 🛡️ Sistema de moderação automática para filtrar conteúdo indesejado
- 🔔 Sistema de notificações via Telegram ou Webhook

## Requisitos

- Python 3.8 ou superior
- Discord.py 2.0 ou superior
- LM Studio configurado com API habilitada
- Token de bot do Discord

## Instalação

1. Clone este repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure o arquivo `.env` na pasta `bot_discord` com seu token do Discord
4. Execute o bot: `python run_bot.py` ou use o arquivo `run_bot.bat` (Windows)

## Configuração

Consulte o arquivo `CONFIG_GUIDE.md` para instruções detalhadas sobre como configurar o bot.

Alternativamente, use o comando `!setup` no Discord para iniciar o assistente de configuração interativo.

## Comandos Principais

- `!ajuda` - Mostra a lista de comandos disponíveis
- `!setup` - Inicia o assistente de configuração interativo
- `!config [param] [valor]` - Configura parâmetros do bot
- `!limpar` - Limpa a memória de curto prazo do bot
- `!buscar [consulta]` - Busca informações na web
- `!personalidade [descrição]` - Define a personalidade do bot

## Assistente de Configuração Interativo

O comando `!setup` inicia um assistente interativo que guia o administrador através das seguintes configurações:

1. **Nome do Bot e Palavra-Chave**: Define a palavra-chave que ativa o bot nas conversas
2. **Prefixo de Comandos**: Permite alterar o prefixo usado para comandos
3. **Memória Permanente**: Configura o armazenamento de mensagens importantes
4. **Sistema de Busca**: Configura o sistema de busca headless (Selenium/Playwright)
5. **Moderação Automática**: Configura filtros para spam, flood e palavras proibidas
6. **Personalidade do Bot**: Escolha entre formal, casual e humorístico
7. **Notificações**: Configura notificações via Telegram ou Webhook

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

---

## 🏗 **Arquitetura do Sistema**

O sistema será estruturado de forma modular para garantir eficiência e flexibilidade. A arquitetura seguirá os seguintes princípios:
- **Modularização**: O código será dividido em módulos especializados para facilitar a manutenção.
- **Eficiência**: O bot armazenará e recuperará memórias de forma otimizada.
- **Personalização**: O usuário poderá configurar prompts, comandos e comportamento do bot.
- **Persistência de Memória**: O bot lembrará de informações relevantes entre conversas.
- **Segurança**: Controle de acesso e proteção contra abusos.

---

## 📝 **Funcionalidades Principais**

### 🔹 1. Interação via Discord
- Monitoramento de mensagens e resposta a menções ou palavras-chave.
- Uso de **comandos personalizados** para configurar o bot.
- Suporte a **mensagens diretas** e **respostas dentro de canais**.
- Registro de logs para monitoramento.

### 🔹 2. Integração com LM Studio
- Envio de mensagens do Discord para o LM Studio e recepção de respostas.
- Customização do **prompt de comportamento** do bot.
- Processamento de mensagens para melhorar a inteligibilidade.

### 🔹 3. Memória e Persistência
- O bot lembrará das últimas **25 mensagens** trocadas.
- Memória configurável para armazenar informações permanentes.
- Armazenação de preferências do usuário.

### 🔹 4. Busca e Recuperação de Informação
- O bot poderá buscar informações **na internet** mediante comandos.
- Pesquisa interna dentro de arquivos e memórias persistentes.

### 🔹 5. Configuração e Personalização
- O usuário pode definir como o bot **age** e **responde**.
- Configuração de prefixos para comandos e palavras-chave.
- Personalização do tempo de armazenamento da memória.

---

## 🏗 **Estrutura do Projeto**

```
📂 bot_discord
├── 📂 core             # Núcleo principal do bot
│   ├── bot.py         # Inicialização do bot e conexão com Discord
│   ├── config.py      # Configuração de variáveis globais
│   ├── logger.py      # Sistema de logs
├── 📂 modules          # Módulos independentes
│   ├── memory.py      # Sistema de memória e persistência
│   ├── ai_handler.py  # Conexão com LM Studio
│   ├── search.py      # Busca na web e em arquivos
│   ├── commands.py    # Comandos customizados do bot
├── 📂 data             # Armazena dados persistentes
│   ├── memory.json    # Banco de memória do bot
│   ├── config.json    # Configurações personalizadas
├── requirements.txt   # Bibliotecas necessárias
├── README.md          # Documentação do projeto
```

---

## ⚙ **Tecnologias Utilizadas**

- **Python** - Linguagem principal
- **discord.py** - Biblioteca para interação com o Discord
- **LM Studio API** - Para IA local
- **SQLite / JSON** - Para armazenamento de memória
- **Google/Bing API** - Para buscas na web

---

## 📌 **Fluxo de Funcionamento**

1. O bot é iniciado e conectado ao Discord.
2. Ele escuta mensagens nos canais definidos.
3. Quando acionado (menção/palavra-chave/comando), processa a mensagem.
4. Se for uma consulta para a IA, a mensagem é enviada ao LM Studio.
5. O LM Studio gera uma resposta, que é processada e enviada ao Discord.
6. Caso seja um comando de configuração, o bot ajusta suas definições.
7. O bot armazena informações importantes na memória para consultas futuras.

---

## 🔐 **Segurança e Controle**

- **Tokens protegidos** via arquivos `.env`.
- **Controle de permissões** para evitar abuso.
- **Mecanismos anti-spam** para evitar sobrecarga.
- **Registro de logs** para monitoramento de erros e eventos.

---

## 🎯 **Próximos Passos**

1. **Pesquisar** as APIs do Discord e LM Studio para implementação.
2. **Criar o bot base** com conexão ao Discord.
3. **Implementar comandos básicos** e testar a interação com o Discord.
4. **Desenvolver o sistema de memória** e busca persistente.
5. **Integrar o LM Studio** e validar as respostas da IA.
6. **Otimizar eficiência e segurança**.

---

## 🔗 **Referências**
- [Documentação do Discord API](https://discord.dev)
- [discord.py GitHub](https://github.com/Rapptz/discord.py)
- [LM Studio Site Oficial](https://lmstudio.ai)
- [SQLite Documentação](https://www.sqlite.org/docs.html)

---

Este documento será atualizado conforme o desenvolvimento avançar. 🚀