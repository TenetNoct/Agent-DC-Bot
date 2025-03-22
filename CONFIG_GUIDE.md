# 📚 Guia de Configuração do Bot Conversacional para Discord com LM Studio

Este guia fornece instruções detalhadas sobre como configurar, personalizar e utilizar o Bot Conversacional para Discord com LM Studio.

## 📋 Índice

1. [Configuração Inicial](#configuração-inicial)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Configurações Personalizadas](#configurações-personalizadas)
4. [Sistema de Memória](#sistema-de-memória)
5. [Sistema de Busca](#sistema-de-busca)
6. [Personalização da IA](#personalização-da-ia)
7. [Comandos Disponíveis](#comandos-disponíveis)
8. [Solução de Problemas](#solução-de-problemas)

## 🚀 Configuração Inicial

### Pré-requisitos

- Python 3.8 ou superior instalado
- Token de bot do Discord
- LM Studio configurado e em execução

### Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Configure o arquivo `.env` conforme descrito abaixo
4. Execute o bot usando `run_bot.bat` ou `python -m bot_discord.core.bot`

### Configuração Interativa via Discord

A maneira mais fácil de configurar o bot é usando o comando `!setup` diretamente no Discord:

1. Inicie o bot com as configurações mínimas (token do Discord)
2. Em um canal do Discord onde o bot tenha permissões, digite `!setup`
3. Siga as instruções interativas para configurar todas as funcionalidades

> **Nota**: Apenas usuários com permissões de administrador podem usar o comando `!setup`

### Configuração do Arquivo .env

Crie um arquivo `.env` na pasta `bot_discord` baseado no arquivo `.env.example`:

```
# Configurações do Discord
DISCORD_TOKEN=seu_token_aqui

# Configurações do LM Studio
LM_STUDIO_API_URL=http://localhost:1234/v1

# Chaves de API para busca na web
GOOGLE_API_KEY=sua_chave_google_aqui
GOOGLE_CX=seu_cx_google_aqui
BING_API_KEY=sua_chave_bing_aqui

# Configurações de log
LOG_LEVEL=INFO
```

#### Obtenção das Chaves e Tokens

1. **Token do Discord**:
   - Acesse o [Portal de Desenvolvedores do Discord](https://discord.com/developers/applications)
   - Selecione seu aplicativo ou crie um novo
   - Na seção "Bot", clique em "Reset Token" para obter um novo token
   - Copie o token e adicione ao arquivo `.env`

2. **URL da API do LM Studio**:
   - Inicie o LM Studio e configure-o para expor a API
   - Por padrão, a URL é `http://localhost:1234/v1`

3. **Chaves de API para Busca na Web** (opcional):
   - **Google**:
     - Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/)
     - Ative a API Custom Search
     - Crie credenciais para obter a chave de API
     - Configure um mecanismo de pesquisa personalizado para obter o CX
   - **Bing**:
     - Inscreva-se no [Portal do Azure](https://portal.azure.com/)
     - Crie um recurso de Pesquisa Bing
     - Obtenha a chave de API nas configurações do recurso

## 📂 Estrutura do Projeto

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
├── 📂 logs             # Registros de atividade do bot
├── .env.example       # Modelo para configuração de variáveis de ambiente
├── requirements.txt   # Bibliotecas necessárias
```

## 🔧 Configurações Personalizadas

O bot utiliza um arquivo `config.json` para armazenar configurações personalizadas. Este arquivo é criado automaticamente na primeira execução com valores padrão, mas pode ser editado manualmente ou através dos comandos do bot.

### Configurações Disponíveis

| Configuração | Descrição | Valor Padrão |
|--------------|-----------|-------------|
| `prefix` | Prefixo para comandos | `!` |
| `memory_limit` | Número de mensagens para lembrar | `25` |
| `memory_persistence` | Persistência de memória | `true` |
| `ai_model` | Modelo de IA | `default` |
| `search_enabled` | Busca na web | `false` |
| `log_level` | Nível de log | `INFO` |
| `bot_keyword` | Palavra-chave para acionar o bot | `""` (vazio) |
| `bot_personality` | Personalidade do bot | `assistente amigável` |

### Palavra-Chave do Bot

O bot pode ser configurado para responder quando uma palavra-chave específica é mencionada em uma mensagem, além de responder a menções diretas. Esta funcionalidade permite uma interação mais natural com o bot.

#### Como Configurar a Palavra-Chave

1. **Usando o Comando**: Use o comando `-palavra_chave` seguido da palavra ou frase desejada:
   ```
   -palavra_chave Jarvis
   ```

2. **Manualmente**: Edite o arquivo `config.json` e altere o valor da propriedade `bot_keyword`:
   ```json
   "bot_keyword": "Jarvis"
   ```

#### Como o Bot Detecta a Palavra-Chave

O bot verifica cada mensagem recebida para determinar se deve responder:

1. **Menção Direta**: O bot sempre responde quando é mencionado diretamente (@NomeDoBot).
2. **Palavra-Chave**: Se uma palavra-chave estiver configurada, o bot responderá quando essa palavra for detectada em qualquer parte da mensagem (não diferencia maiúsculas de minúsculas).

#### Exemplos

Se a palavra-chave configurada for "Jarvis":

- "Ei Jarvis, qual é o clima hoje?" - O bot responderá
- "JARVIS, me ajude com isso" - O bot responderá (não diferencia maiúsculas/minúsculas)
- "Você conhece o Jarvis?" - O bot responderá (a palavra-chave está presente)
- "Como posso te ajudar?" - O bot NÃO responderá (palavra-chave ausente e sem menção)

### Personalidade do Bot

Você pode definir a personalidade do bot para influenciar como ele responde às mensagens. Esta configuração é passada para o modelo de IA como parte do contexto.

### Configurações Disponíveis

| Parâmetro | Descrição | Valor Padrão |
|-----------|-----------|---------------|
| `prefix` | Prefixo para comandos | `!` |
| `memory_limit` | Número de mensagens para lembrar | `25` |
| `memory_persistence` | Persistência de memória | `true` |
| `ai_model` | Modelo de IA padrão | `default` |
| `search_enabled` | Busca na web ativada | `false` |
| `log_level` | Nível de log | `INFO` |

### Como Editar Configurações

Você pode editar as configurações de duas formas:

1. **Através do comando no Discord**:
   ```
   !config prefix -
   !config memory_limit 50
   !config search_enabled true
   ```

2. **Editando o arquivo `config.json` diretamente**:
   ```json
   {
       "prefix": "-",
       "memory_limit": 50,
       "memory_persistence": true,
       "ai_model": "default",
       "search_enabled": true,
       "log_level": "INFO"
   }
   ```

## 💾 Sistema de Memória

O bot utiliza um sistema de memória de duas camadas para armazenar informações:

### Memória de Curto Prazo

A memória de curto prazo armazena as mensagens recentes trocadas entre usuários e o bot. Esta memória é limitada pelo parâmetro `memory_limit` nas configurações.

- **Configuração**: Você pode ajustar o tamanho da memória de curto prazo usando o comando `!config memory_limit 50` (substitua `!` pelo seu prefixo atual e `50` pelo número desejado de mensagens).
- **Limpeza**: Use o comando `!limpar` para apagar toda a memória de curto prazo.

### Memória de Longo Prazo

A memória de longo prazo armazena informações permanentes, como a personalidade configurada do bot e preferências de usuários.

- **Persistência**: Por padrão, a memória é salva em um arquivo JSON para persistir entre reinicializações do bot. Você pode desativar esta funcionalidade com `!config memory_persistence false`.

### Arquivo de Memória

Quando a persistência está ativada, o bot salva as informações no arquivo `bot_discord/data/memory.json`. Este arquivo contém:

```json
{
    "short_term": [
        {"user_id": "123456789", "username": "Usuário", "content": "Olá bot!", "timestamp": "2023-01-01T12:00:00", "is_bot": false},
        {"user_id": "bot", "username": "Bot", "content": "Olá! Como posso ajudar?", "timestamp": "2023-01-01T12:00:01", "is_bot": true}
    ],
    "long_term": {
        "personality": {
            "value": "assistente amigável",
            "timestamp": "2023-01-01T10:00:00"
        }
    }
}
```

## 🔍 Sistema de Busca

O bot oferece capacidade de busca na web para encontrar informações atualizadas. Existem três métodos de busca disponíveis:

### 1. Busca via API do Google

Utiliza a API Custom Search do Google para realizar buscas.

- **Configuração**: Requer uma chave de API do Google e um ID de mecanismo de pesquisa personalizado (CX).
- **Vantagens**: Resultados precisos e estruturados.
- **Desvantagens**: Limitado a um número de consultas gratuitas por dia.

### 2. Busca via API do Bing

Utiliza a API de Pesquisa do Bing para realizar buscas.

- **Configuração**: Requer uma chave de API do Bing.
- **Vantagens**: Boa qualidade de resultados.
- **Desvantagens**: Serviço pago após um período de avaliação.

### 3. Busca Headless (Recomendado)

Utiliza um navegador headless (Chrome) para realizar buscas de forma automatizada, sem necessidade de APIs pagas.

- **Configuração**: Requer a instalação do Selenium e WebDriver (`pip install selenium webdriver-manager`).
- **Vantagens**: Gratuito e sem limites de consultas.
- **Desvantagens**: Pode ser mais lento que as APIs e está sujeito a bloqueios por captchas em caso de uso intensivo.

### Como Ativar a Busca

1. Ative a busca nas configurações:
   ```
   !config search_enabled true
   ```

2. Use o comando de busca:
   ```
   !buscar como funciona a inteligência artificial
   ```

3. Por padrão, o bot tentará usar o método headless se as APIs não estiverem configuradas.

## 🤖 Personalização da IA

O bot permite personalizar a forma como a IA responde através da configuração de personalidade.

### Definindo a Personalidade

Use o comando `!personalidade` seguido da descrição desejada:

```
!personalidade assistente técnico especializado em programação Python
```

Exemplos de personalidades:
- Assistente técnico especializado em uma linguagem ou tecnologia
- Professor de uma disciplina específica
- Conselheiro amigável e informal
- Especialista em um determinado assunto

A personalidade definida é armazenada na memória de longo prazo e será usada em todas as interações futuras até ser alterada.

### Modelo de IA

O bot utiliza o LM Studio como backend para processamento de linguagem natural. Você pode configurar qual modelo usar através da configuração `ai_model`:

```
!config ai_model nome_do_modelo
```

O modelo padrão é definido como "default" e utiliza o modelo configurado no LM Studio.

## 🤖 Comandos Disponíveis

O bot oferece diversos comandos para interação e configuração. Todos os comandos começam com o prefixo configurado (padrão: `-`).

### Comandos Básicos

- `-ajuda` - Mostra a lista completa de comandos disponíveis e instruções de uso
- `-config [param] [valor]` - Configura parâmetros do bot
- `-limpar` - Limpa a memória de curto prazo do bot
- `-buscar [consulta]` - Busca informações na web
- `-personalidade [descrição]` - Define a personalidade do bot
- `-palavra_chave [palavra]` - Define a palavra-chave que ativa o bot

### Detalhes dos Comandos

#### `-ajuda`
Exibe um guia completo de uso do bot, incluindo todos os comandos disponíveis e suas descrições.

#### `-config [param] [valor]`
Configura parâmetros específicos do bot.

Exemplos:
- `-config prefix !` - Altera o prefixo para !
- `-config memory_limit 50` - Define o limite de memória para 50 mensagens
- `-config search_enabled true` - Ativa a busca na web
- `-config memory_persistence false` - Desativa a persistência de memória

Se usado sem parâmetros, mostra a configuração atual.

#### `-limpar`
Limpa a memória de curto prazo do bot, removendo o histórico de conversas recentes.

#### `-buscar [consulta]`
Busca informações na web sobre o tópico especificado.

Exemplo: `-buscar clima em São Paulo`

#### `-personalidade [descrição]`
Define a personalidade do bot para as conversas.

Exemplos:
- `-personalidade assistente técnico`

> **Nota**: Substitua `-` pelo prefixo configurado no seu bot.

## ❓ Solução de Problemas

Aqui estão algumas soluções para problemas comuns que você pode encontrar ao configurar e usar o bot:

### Problemas de Conexão com o Discord

- **Erro de Token Inválido**: Verifique se o token no arquivo `.env` está correto e não expirou.
- **Bot Não Responde**: Certifique-se de que o bot tem as permissões necessárias no servidor do Discord.
- **Intents não Autorizadas**: Ative os "Privileged Gateway Intents" no Portal de Desenvolvedores do Discord para seu bot.

### Problemas com LM Studio

- **Erro de Conexão**: Verifique se o LM Studio está em execução e expondo a API na porta correta.
- **Respostas Vazias**: Verifique se o modelo está carregado corretamente no LM Studio.
- **Erros de Timeout**: Aumente o timeout nas configurações ou use um modelo mais leve se o atual for muito pesado.

### Problemas com a Busca na Web

- **Selenium não Instalado**: Execute `pip install selenium webdriver-manager` para instalar as dependências necessárias.
- **Driver não Encontrado**: O WebDriver Manager deve baixar automaticamente o driver correto. Se falhar, baixe manualmente o ChromeDriver compatível com sua versão do Chrome.
- **Captchas**: Se o Google começar a mostrar captchas, reduza a frequência de buscas ou alterne para as APIs.

### Problemas de Memória

- **Erro ao Salvar/Carregar Memória**: Verifique as permissões de escrita na pasta `data`.
- **Memória não Persiste**: Confirme que `memory_persistence` está definido como `true` nas configurações.

### Logs e Depuração

O bot mantém logs detalhados na pasta `logs`. Verifique os arquivos de log para informações sobre erros específicos.

Você pode ajustar o nível de log nas configurações:

```
!config log_level DEBUG
```

Níveis disponíveis: DEBUG, INFO, WARNING, ERROR, CRITICAL