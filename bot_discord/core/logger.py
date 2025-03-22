# logger.py
# Sistema de logs

import logging
import os
from datetime import datetime

def setup_logger(name, log_level=None):
    """Configura e retorna um logger com o nome especificado"""
    # Obtém o nível de log das variáveis de ambiente ou usa INFO como padrão
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    # Converte string de nível de log para constante do logging
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Cria o logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Evita duplicação de handlers
    if not logger.handlers:
        # Cria o diretório de logs se não existir
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'logs'
        )
        os.makedirs(log_dir, exist_ok=True)
        
        # Define o nome do arquivo de log com data atual
        log_file = os.path.join(
            log_dir,
            f"{datetime.now().strftime('%Y-%m-%d')}.log"
        )
        
        # Configura o handler de arquivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        
        # Configura o handler de console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        
        # Define o formato do log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Adiciona os handlers ao logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# Função para registrar erros críticos
def log_critical_error(logger, error, context=None):
    """Registra um erro crítico com contexto adicional"""
    error_message = f"ERRO CRÍTICO: {error}"
    
    if context:
        error_message += f"\nContexto: {context}"
    
    logger.critical(error_message)
    
# Função para registrar eventos importantes
def log_event(logger, event_type, message):
    """Registra um evento importante"""
    logger.info(f"EVENTO [{event_type}]: {message}")