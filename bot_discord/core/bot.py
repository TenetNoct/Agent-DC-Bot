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
            # Será implementada posteriormente
    
    def load_commands(self):
        # Carregamento de comandos personalizados
        # Será implementado posteriormente
        pass
        
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