# bot.py
# Inicialização do bot e conexão com Discord

import discord
from discord.ext import commands
import os
import sys
import logging

# Adiciona o diretório raiz ao path para importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config
from core.logger import setup_logger

# Configuração do logger
logger = setup_logger(__name__)

class DiscordBot:
    def __init__(self):
        self.config = Config()
        self.token = self.config.get_token()
        
        # Configuração de intents para o bot
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        # Inicialização do bot com prefixo de comando
        self.bot = commands.Bot(command_prefix=self.config.get_prefix(), intents=intents)
        
        # Módulos do bot (serão inicializados posteriormente)
        self.memory = None
        self.ai_handler = None
        self.search_engine = None
        self.command_handler = None
        
        # Registrar eventos
        self.register_events()
        
    def register_events(self):
        @self.bot.event
        async def on_ready():
            logger.info(f'Bot conectado como {self.bot.user.name}')
            logger.info(f'ID do Bot: {self.bot.user.id}')
            logger.info('------')
            
        @self.bot.event
        async def on_message(message):
            # Ignora mensagens do próprio bot
            if message.author == self.bot.user:
                return
                
            # Processa comandos
            await self.bot.process_commands(message)
            
            # Lógica para responder a menções ou palavras-chave
            await self._handle_message_response(message)
    
    async def _handle_message_response(self, message):
        """Processa mensagens para responder a menções ou palavras-chave"""
        # Verifica se o bot foi mencionado
        was_mentioned = self.bot.user in message.mentions
        
        # Verifica se a mensagem contém a palavra-chave configurada
        keyword = self.config.get_config_value('bot_keyword', '')
        contains_keyword = keyword and keyword.lower() in message.content.lower()
        
        # Se o bot foi mencionado ou a palavra-chave foi detectada
        if was_mentioned or contains_keyword:
            # Inicializa os módulos se ainda não foram inicializados
            if not self.ai_handler:
                # Importa os módulos aqui para evitar importação circular
                from modules.memory import Memory
                from modules.ai_handler import AIHandler
                from modules.search import SearchEngine
                from modules.commands import CommandHandler
                
                # Inicializa os módulos
                self.memory = Memory(self.config)
                self.ai_handler = AIHandler(self.config)
                self.search_engine = SearchEngine(self.config)
                self.command_handler = CommandHandler(self.bot, self.config, self.memory, self.ai_handler, self.search_engine)
            
            # Adiciona a mensagem à memória
            self.memory.add_message(message.author.id, message.author.name, message.content)
            
            # Remove a menção do bot da mensagem, se presente
            user_message = message.content
            if was_mentioned:
                user_message = user_message.replace(f'<@{self.bot.user.id}>', '').strip()
            
            # Obtém o contexto da conversa da memória
            context = self.memory.get_short_term_memory()
            
            # Obtém a personalidade configurada do bot
            bot_personality = self.config.get_config_value('bot_personality', '')
            
            # Formata o prompt com a personalidade do bot
            formatted_prompt = self.ai_handler.format_prompt(user_message, bot_personality)
            
            # Gera a resposta usando o LM Studio
            response = self.ai_handler.generate_response(formatted_prompt, context)
            
            # Processa a resposta para melhorar a inteligibilidade
            processed_response = self.ai_handler.process_response(response)
            
            # Adiciona a resposta do bot à memória
            self.memory.add_message(self.bot.user.id, self.bot.user.name, processed_response, is_bot=True)
            
            # Envia a resposta
            await message.channel.send(processed_response)
            logger.info(f"Respondeu a uma mensagem de {message.author.name}")
    
    def load_commands(self):
        """Carrega os módulos e comandos do bot"""
        # Importa os módulos aqui para evitar importação circular
        from modules.memory import Memory
        from modules.ai_handler import AIHandler
        from modules.search import SearchEngine
        from modules.commands import CommandHandler
        
        # Inicializa os módulos
        self.memory = Memory(self.config)
        self.ai_handler = AIHandler(self.config)
        self.search_engine = SearchEngine(self.config)
        self.command_handler = CommandHandler(self.bot, self.config, self.memory, self.ai_handler, self.search_engine)
        
    def run(self):
        try:
            logger.info("Iniciando o bot...")
            self.bot.run(self.token)
        except Exception as e:
            logger.error(f"Erro ao iniciar o bot: {e}")
            
# Função para iniciar o bot
def start_bot():
    bot = DiscordBot()
    bot.load_commands()
    bot.run()
    
if __name__ == "__main__":
    start_bot()