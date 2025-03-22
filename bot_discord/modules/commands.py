# commands.py
# Comandos customizados do bot

import discord
from discord.ext import commands
import logging

# Configuração do logger
logger = logging.getLogger(__name__)

class CommandHandler:
    def __init__(self, bot, config, memory, ai_handler, search_engine):
        self.bot = bot
        self.config = config
        self.memory = memory
        self.ai_handler = ai_handler
        self.search_engine = search_engine
        
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
        
        @self.bot.command(name='limpar', help='Limpa a memória de curto prazo do bot')
        async def clear_memory_command(ctx):
            await self._clear_memory_command(ctx)
        
        @self.bot.command(name='buscar', help='Busca informações na web')
        async def search_command(ctx, *, query):
            await self._search_command(ctx, query)
        
        @self.bot.command(name='personalidade', help='Define a personalidade do bot')
        async def personality_command(ctx, *, personality):
            await self._personality_command(ctx, personality)
    
    async def _help_command(self, ctx):
        """Mostra a lista de comandos disponíveis"""
        prefix = self.config.get_prefix()
        embed = discord.Embed(
            title="Comandos Disponíveis",
            description=f"Prefixo atual: `{prefix}`",
            color=discord.Color.blue()
        )
        
        # Adiciona os comandos ao embed
        embed.add_field(
            name=f"{prefix}ajuda",
            value="Mostra esta mensagem de ajuda",
            inline=False
        )
        embed.add_field(
            name=f"{prefix}config [param] [valor]",
            value="Configura parâmetros do bot. Exemplo: `{prefix}config prefix !`",
            inline=False
        )
        embed.add_field(
            name=f"{prefix}limpar",
            value="Limpa a memória de curto prazo do bot",
            inline=False
        )
        embed.add_field(
            name=f"{prefix}buscar [consulta]",
            value="Busca informações na web",
            inline=False
        )
        embed.add_field(
            name=f"{prefix}personalidade [descrição]",
            value="Define a personalidade do bot",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
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
    
    async def _search_command(self, ctx, query):
        """Busca informações na web"""
        if not self.config.get_config_value('search_enabled'):
            await ctx.send("❌ Busca na web desativada. Ative nas configurações do bot.")
            return
        
        await ctx.send(f"🔍 Buscando informações sobre: `{query}`...")
        
        # Realiza a busca
        results = self.search_engine.web_search(query)
        
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