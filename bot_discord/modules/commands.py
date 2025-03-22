# commands.py
# Comandos customizados do bot

import discord
from discord.ext import commands
import logging
import os
import json

# Configuração do logger
logger = logging.getLogger(__name__)

class CommandHandler:
    def __init__(self, bot, config, memory, ai_handler, search_engine):
        self.bot = bot
        self.config = config
        self.memory = memory
        self.ai_handler = ai_handler
        self.search_engine = search_engine
        
        # Dicionário para armazenar comandos personalizados
        self.custom_commands = {}
        
        # Assistente de configuração interativa
        from modules.setup import SetupWizard
        self.setup_wizard = SetupWizard(bot, config, self)
        
        # Registra os comandos no bot
        self.register_commands()
    
    def register_commands(self):
        """Registra todos os comandos no bot"""
        @self.bot.command(name='ajuda', help='Mostra a lista de comandos disponíveis')
        async def help_command(ctx):
            await self._help_command(ctx)
        
        @self.bot.command(name='config', help='Configura parâmetros do bot')
        async def config_command(ctx, param=None, value=None):
            await self._config_command(ctx, param, value)
            
        @self.bot.command(name='setup', help='Inicia o assistente de configuração interativo')
        async def setup_command(ctx):
            await self.setup_wizard.start_setup(ctx)
        
        @self.bot.command(name='limpar', help='Limpa a memória de curto prazo do bot')
        async def clear_memory_command(ctx):
            await self._clear_memory_command(ctx)
        
        @self.bot.command(name='buscar', help='Busca informações na web')
        async def search_command(ctx, *, query):
            await self._search_command(ctx, query)
            
        @self.bot.command(name='buscar_com', help='Busca informações na web com um motor específico')
        async def search_with_engine_command(ctx, engine=None, *, query=None):
            if not query:
                await ctx.send("❌ Você precisa especificar uma consulta para buscar.")
                return
            await self._search_command(ctx, query, engine)
            
        @self.bot.command(name='cache_config', help='Configura o sistema de cache para buscas')
        async def cache_config_command(ctx, param=None, value=None):
            await self._cache_config_command(ctx, param, value)
        
        @self.bot.command(name='personalidade', help='Define a personalidade do bot')
        async def personality_command(ctx, *, personality):
            await self._personality_command(ctx, personality)
            
        @self.bot.command(name='palavra_chave', help='Define a palavra-chave que ativa o bot')
        async def keyword_command(ctx, *, keyword=None):
            await self._keyword_command(ctx, keyword)
        
        # Comandos para gerenciar comandos personalizados
        @self.bot.command(name='comando_add', help='Adiciona um comando personalizado')
        async def add_custom_command(ctx, cmd_name=None, *, response=None):
            await self._add_custom_command(ctx, cmd_name, response)
            
        @self.bot.command(name='comando_remove', help='Remove um comando personalizado')
        async def remove_custom_command(ctx, cmd_name=None):
            await self._remove_custom_command(ctx, cmd_name)
            
        @self.bot.command(name='comandos', help='Lista todos os comandos personalizados')
        async def list_custom_commands(ctx):
            await self._list_custom_commands(ctx)
            
        # Carrega comandos personalizados salvos
        self._load_custom_commands()
    
    async def _help_command(self, ctx):
        """Mostra um guia completo de uso do bot"""
        prefix = self.config.get_prefix()
        
        # Cria o embed principal com informações gerais
        main_embed = discord.Embed(
            title="📚 Guia de Uso do Bot",
            description=f"Bem-vindo ao guia completo do Bot Conversacional para Discord com LM Studio. Este bot permite interações naturais usando IA e oferece diversos comandos úteis.",
            color=discord.Color.blue()
        )
        
        main_embed.add_field(
            name="🔄 Interação com o Bot",
            value=f"Você pode interagir com o bot das seguintes formas:\n\n• **Comandos com prefixo**: Use `{prefix}` seguido do comando\n• **Menção direta**: Mencione o bot com @\n• **Resposta a mensagens**: Responda às mensagens do bot",
            inline=False
        )
        
        # Envia o embed principal
        await ctx.send(embed=main_embed)
        
        # Cria embed para comandos disponíveis
        commands_embed = discord.Embed(
            title="⌨️ Comandos Disponíveis",
            description=f"Prefixo atual: `{prefix}`",
            color=discord.Color.green()
        )
        
        commands_embed.add_field(
            name=f"{prefix}ajuda",
            value="Mostra este guia completo de uso do bot",
            inline=False
        )
        
        commands_embed.add_field(
            name=f"{prefix}config [param] [valor]",
            value=f"Configura parâmetros do bot.\n\nExemplos:\n• `{prefix}config prefix !` - Altera o prefixo para !\n• `{prefix}config memory_limit 50` - Define o limite de memória\n• `{prefix}config search_enabled true` - Ativa a busca na web\n• `{prefix}config memory_persistence false` - Desativa a persistência",
            inline=False
        )
        
        commands_embed.add_field(
            name=f"{prefix}limpar",
            value="Limpa a memória de curto prazo do bot, removendo o histórico de conversas recentes",
            inline=False
        )
        
        commands_embed.add_field(
            name=f"{prefix}buscar [consulta]",
            value="Busca informações na web sobre o tópico especificado\nExemplo: `{prefix}buscar clima em São Paulo`",
            inline=False
        )
        
        commands_embed.add_field(
            name=f"{prefix}personalidade [descrição]",
            value="Define a personalidade do bot para as conversas\n\nExemplos:\n• `{prefix}personalidade assistente técnico especializado em Python`\n• `{prefix}personalidade amigável e informal`\n• `{prefix}personalidade professor de história`",
            inline=False
        )
        
        commands_embed.add_field(
            name=f"{prefix}palavra_chave [palavra]",
            value="Define a palavra-chave que ativa o bot nas conversas\n\nExemplo: `{prefix}palavra_chave bot` - O bot responderá quando alguém mencionar 'bot'",
            inline=False
        )
        
        # Adiciona informações sobre comandos personalizados
        commands_embed.add_field(
            name=f"{prefix}comando_add [nome] [resposta]",
            value=f"Adiciona um comando personalizado ao bot\n\nExemplo: `{prefix}comando_add oi Olá, como vai você?`",
            inline=False
        )
        
        commands_embed.add_field(
            name=f"{prefix}comando_remove [nome]",
            value=f"Remove um comando personalizado\n\nExemplo: `{prefix}comando_remove oi`",
            inline=False
        )
        
        commands_embed.add_field(
            name=f"{prefix}comandos",
            value=f"Lista todos os comandos personalizados disponíveis",
            inline=False
        )
        
        # Adiciona comandos personalizados ao embed, se existirem
        if self.custom_commands:
            commands_embed.add_field(
                name="🤖 Comandos Personalizados",
                value=f"Os seguintes comandos personalizados estão disponíveis:\n" + 
                      '\n'.join([f"`{prefix}{cmd_name}`" for cmd_name in self.custom_commands.keys()]),
                inline=False
            )
        
        # Envia o embed de comandos
        await ctx.send(embed=commands_embed)
        
        # Cria embed para configuração e personalização
        config_embed = discord.Embed(
            title="⚙️ Configuração e Personalização",
            description="Informações sobre como configurar e personalizar o bot",
            color=discord.Color.gold()
        )
        
        config_embed.add_field(
            name="📝 Configuração da Persona",
            value=f"Use o comando `{prefix}personalidade` para definir como o bot deve se comportar nas conversas. Seja específico para obter melhores resultados.",
            inline=False
        )
        
        config_embed.add_field(
            name="💾 Sistema de Memória",
            value=f"O bot mantém duas formas de memória:\n\n• **Memória de curto prazo**: Armazena as últimas mensagens (configurável)\n• **Memória de longo prazo**: Armazena informações permanentes como preferências\n\nUse `{prefix}config memory_limit [número]` para ajustar o tamanho da memória de curto prazo.",
            inline=False
        )
        
        config_embed.add_field(
            name="🔍 Sistema de Busca",
            value=f"Ative a busca na web com `{prefix}config search_enabled true` e use o comando `{prefix}buscar` para pesquisar informações online.",
            inline=False
        )
        
        config_embed.add_field(
            name="🤖 Comandos Personalizados",
            value=f"Crie seus próprios comandos com `{prefix}comando_add [nome] [resposta]`.\nGerencie-os com `{prefix}comandos` e `{prefix}comando_remove`.",
            inline=False
        )
        
        # Envia o embed de configuração
        await ctx.send(embed=config_embed)
    
    async def _config_command(self, ctx, param=None, value=None):
        """Configura parâmetros do bot"""
        if not param:
            # Mostra a configuração atual
            embed = discord.Embed(
                title="Configuração Atual",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="Prefixo",
                value=f"`{self.config.get_prefix()}`",
                inline=True
            )
            embed.add_field(
                name="Limite de Memória",
                value=f"`{self.config.get_memory_limit()}`",
                inline=True
            )
            embed.add_field(
                name="Persistência de Memória",
                value=f"`{self.config.get_config_value('memory_persistence')}`",
                inline=True
            )
            embed.add_field(
                name="Modelo de IA",
                value=f"`{self.config.get_config_value('ai_model')}`",
                inline=True
            )
            embed.add_field(
                name="Busca na Web",
                value=f"`{self.config.get_config_value('search_enabled')}`",
                inline=True
            )
            
            await ctx.send(embed=embed)
            return
        
        # Configura um parâmetro específico
        if not value:
            await ctx.send(f"❌ Valor não especificado para o parâmetro `{param}`")
            return
        
        # Trata cada parâmetro específico
        if param.lower() == 'prefix':
            self.config.set_prefix(value)
            await ctx.send(f"✅ Prefixo alterado para `{value}`")
        
        elif param.lower() == 'memory_limit':
            try:
                limit = int(value)
                self.config.set_memory_limit(limit)
                await ctx.send(f"✅ Limite de memória alterado para `{limit}`")
            except ValueError:
                await ctx.send("❌ O limite de memória deve ser um número inteiro")
        
        elif param.lower() == 'memory_persistence':
            if value.lower() in ['true', 'yes', '1', 'sim']:
                self.config.set_config_value('memory_persistence', True)
                await ctx.send("✅ Persistência de memória ativada")
            elif value.lower() in ['false', 'no', '0', 'não']:
                self.config.set_config_value('memory_persistence', False)
                await ctx.send("✅ Persistência de memória desativada")
            else:
                await ctx.send("❌ Valor inválido. Use 'true' ou 'false'")
        
        elif param.lower() == 'search_enabled':
            if value.lower() in ['true', 'yes', '1', 'sim']:
                self.config.set_config_value('search_enabled', True)
                await ctx.send("✅ Busca na web ativada")
            elif value.lower() in ['false', 'no', '0', 'não']:
                self.config.set_config_value('search_enabled', False)
                await ctx.send("✅ Busca na web desativada")
            else:
                await ctx.send("❌ Valor inválido. Use 'true' ou 'false'")
        
        else:
            await ctx.send(f"❌ Parâmetro `{param}` não reconhecido")
    
    async def _clear_memory_command(self, ctx):
        """Limpa a memória de curto prazo do bot"""
        self.memory.clear_short_term()
        await ctx.send("✅ Memória de curto prazo limpa com sucesso")
    
    async def _search_command(self, ctx, query, engine=None):
        """Busca informações na web"""
        if not self.config.get_config_value('search_enabled'):
            await ctx.send("❌ Busca na web desativada. Ative nas configurações do bot.")
            return
        
        # Determina o motor de busca a ser usado
        if not engine:
            # Verifica se há chaves de API configuradas
            if self.search_engine.google_api_key and self.search_engine.google_cx:
                engine = 'google'
            elif self.search_engine.bing_api_key:
                engine = 'bing'
            else:
                engine = 'headless'  # Usa headless como fallback
        
        await ctx.send(f"🔍 Buscando informações sobre: `{query}` usando {engine}...")
        
        # Realiza a busca
        results = self.search_engine.web_search(query, engine=engine)
        
        if not results or isinstance(results, list) and isinstance(results[0], str):
            # Erro na busca
            await ctx.send(f"❌ {results[0] if results else 'Nenhum resultado encontrado'}")
            return
        
        # Cria um embed com os resultados
        embed = discord.Embed(
            title=f"Resultados para: {query}",
            color=discord.Color.blue()
        )
        
        for i, result in enumerate(results[:5], 1):
            embed.add_field(
                name=f"{i}. {result['title']}",
                value=f"[Link]({result['link']})\n{result['snippet']}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    async def _personality_command(self, ctx, personality):
        """Define a personalidade do bot"""
        # Armazena a personalidade na memória de longo prazo
        self.memory.store_permanent_info('personality', personality)
        await ctx.send(f"✅ Personalidade definida como: `{personality}`")
        
    async def _keyword_command(self, ctx, keyword=None):
        """Define a palavra-chave que ativa o bot"""
        if keyword is None:
            # Mostra a palavra-chave atual
            current_keyword = self.config.get_config_value('bot_keyword', '')
            if current_keyword:
                await ctx.send(f"🔑 A palavra-chave atual do bot é: **{current_keyword}**")
            else:
                await ctx.send("ℹ️ O bot atualmente não possui palavra-chave configurada. Ele responderá apenas a menções.")
            return
            
        # Define a nova palavra-chave
        self.config.set_config_value('bot_keyword', keyword)
        await ctx.send(f"✅ Palavra-chave do bot definida como: **{keyword}**")
        await ctx.send("ℹ️ O bot agora responderá quando for mencionado ou quando esta palavra-chave for detectada em uma mensagem.")
    
    async def _add_custom_command(self, ctx, cmd_name=None, response=None):
        """Adiciona um comando personalizado"""
        if not cmd_name or not response:
            await ctx.send("❌ Você precisa especificar um nome para o comando e uma resposta.")
            await ctx.send(f"Exemplo: `{self.config.get_prefix()}comando_add oi Olá, como vai você?`")
            return
        
        # Verifica se o nome do comando já existe como comando padrão
        if cmd_name in [command.name for command in self.bot.commands]:
            await ctx.send(f"❌ O comando `{cmd_name}` já existe como um comando padrão do bot.")
            return
        
        # Adiciona o comando ao dicionário
        self.custom_commands[cmd_name] = {
            "response": response,
            "created_by": ctx.author.id,
            "created_at": ctx.message.created_at.isoformat()
        }
        
        # Salva os comandos personalizados
        self._save_custom_commands()
        
        # Registra o comando dinamicamente
        @self.bot.command(name=cmd_name)
        async def dynamic_command(ctx):
            await ctx.send(self.custom_commands[cmd_name]["response"])
        
        await ctx.send(f"✅ Comando personalizado `{cmd_name}` adicionado com sucesso!")
    
    async def _remove_custom_command(self, ctx, cmd_name=None):
        """Remove um comando personalizado"""
        if not cmd_name:
            await ctx.send("❌ Você precisa especificar o nome do comando a ser removido.")
            await ctx.send(f"Exemplo: `{self.config.get_prefix()}comando_remove oi`")
            return
        
        # Verifica se o comando existe
        if cmd_name not in self.custom_commands:
            await ctx.send(f"❌ O comando personalizado `{cmd_name}` não existe.")
            return
        
        # Remove o comando do dicionário
        del self.custom_commands[cmd_name]
        
        # Salva os comandos personalizados
        self._save_custom_commands()
        
        # Remove o comando do bot (requer reinicialização para efetivar)
        await ctx.send(f"✅ Comando personalizado `{cmd_name}` removido com sucesso!")
        await ctx.send("ℹ️ Alguns comandos removidos podem continuar disponíveis até que o bot seja reiniciado.")
    
    async def _list_custom_commands(self, ctx):
        """Lista todos os comandos personalizados"""
        if not self.custom_commands:
            await ctx.send("ℹ️ Não há comandos personalizados registrados.")
            return
        
        # Cria um embed para listar os comandos
        embed = discord.Embed(
            title="🤖 Comandos Personalizados",
            description=f"Lista de comandos personalizados disponíveis. Use `{self.config.get_prefix()}comando_add` para adicionar novos comandos.",
            color=discord.Color.blue()
        )
        
        # Adiciona cada comando ao embed
        for cmd_name, cmd_data in self.custom_commands.items():
            embed.add_field(
                name=f"{self.config.get_prefix()}{cmd_name}",
                value=f"Resposta: {cmd_data['response'][:50]}{'...' if len(cmd_data['response']) > 50 else ''}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    def _save_custom_commands(self):
        """Salva os comandos personalizados em um arquivo JSON"""
        try:
            # Caminho para o arquivo de comandos personalizados
            commands_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data',
                'custom_commands.json'
            )
            
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(commands_file), exist_ok=True)
            
            # Salva os comandos no arquivo
            with open(commands_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_commands, f, indent=4, ensure_ascii=False)
                
            logger.info(f"Comandos personalizados salvos: {len(self.custom_commands)} comandos")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar comandos personalizados: {e}")
            return False
    
    async def _cache_config_command(self, ctx, param=None, value=None):
        """Configura o sistema de cache para buscas"""
        if not param:
            # Mostra a configuração atual do cache
            embed = discord.Embed(
                title="Configuração do Cache de Busca",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Cache Ativado",
                value=f"`{self.search_engine.cache_enabled}`",
                inline=True
            )
            embed.add_field(
                name="Tempo de Expiração",
                value=f"`{self.search_engine.cache_expiry}` horas",
                inline=True
            )
            embed.add_field(
                name="Diretório de Cache",
                value=f"`{self.search_engine.cache_dir}`",
                inline=False
            )
            
            await ctx.send(embed=embed)
            return
        
        # Configura um parâmetro específico
        if not value:
            await ctx.send(f"❌ Valor não especificado para o parâmetro `{param}`")
            return
        
        # Trata cada parâmetro específico
        if param.lower() == 'enabled' or param.lower() == 'ativado':
            if value.lower() in ['true', 'yes', '1', 'sim']:
                self.search_engine.cache_enabled = True
                await ctx.send("✅ Cache de busca ativado")
            elif value.lower() in ['false', 'no', '0', 'não']:
                self.search_engine.cache_enabled = False
                await ctx.send("✅ Cache de busca desativado")
            else:
                await ctx.send("❌ Valor inválido. Use 'true' ou 'false'")
        
        elif param.lower() == 'expiry' or param.lower() == 'expiração':
            try:
                expiry = int(value)
                if expiry < 1:
                    await ctx.send("❌ O tempo de expiração deve ser pelo menos 1 hora")
                    return
                    
                self.search_engine.cache_expiry = expiry
                await ctx.send(f"✅ Tempo de expiração do cache definido para `{expiry}` horas")
            except ValueError:
                await ctx.send("❌ O tempo de expiração deve ser um número inteiro de horas")
        
        elif param.lower() == 'clear' or param.lower() == 'limpar':
            if value.lower() in ['true', 'yes', '1', 'sim', 'all', 'tudo']:
                # Limpa todo o cache
                try:
                    cache_files = os.listdir(self.search_engine.cache_dir)
                    for file in cache_files:
                        if file.endswith('.json'):
                            os.remove(os.path.join(self.search_engine.cache_dir, file))
                    
                    await ctx.send(f"✅ Cache de busca limpo com sucesso. {len(cache_files)} arquivos removidos.")
                except Exception as e:
                    await ctx.send(f"❌ Erro ao limpar cache: {e}")
            else:
                await ctx.send("❌ Valor inválido. Use 'true' para limpar o cache")
        
        else:
            await ctx.send(f"❌ Parâmetro `{param}` não reconhecido. Use 'enabled', 'expiry' ou 'clear'.")
    
    def _load_custom_commands(self):
        """Carrega os comandos personalizados de um arquivo JSON"""
        try:
            # Caminho para o arquivo de comandos personalizados
            commands_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data',
                'custom_commands.json'
            )
            
            # Verifica se o arquivo existe
            if not os.path.exists(commands_file):
                logger.info("Arquivo de comandos personalizados não encontrado. Iniciando com lista vazia.")
                return False
            
            # Carrega os comandos do arquivo
            with open(commands_file, 'r', encoding='utf-8') as f:
                self.custom_commands = json.load(f)
            
            # Registra os comandos dinamicamente
            for cmd_name, cmd_data in self.custom_commands.items():
                @self.bot.command(name=cmd_name)
                async def dynamic_command(ctx, cmd_name=cmd_name):
                    await ctx.send(self.custom_commands[cmd_name]["response"])
            
            logger.info(f"Comandos personalizados carregados: {len(self.custom_commands)} comandos")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar comandos personalizados: {e}")
            self.custom_commands = {}
            return False