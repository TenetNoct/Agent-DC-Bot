# memory.py
# Sistema de memória e persistência

import json
import os
import logging
from datetime import datetime
from collections import deque

# Configuração do logger
logger = logging.getLogger(__name__)

class Memory:
    def __init__(self, config):
        self.config = config
        self.memory_limit = config.get_memory_limit()
        self.persistence_enabled = config.get_config_value("memory_persistence")
        
        # Caminho para o arquivo de memória
        self.memory_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'memory.json'
        )
        
        # Inicializa a memória de curto prazo (últimas mensagens)
        self.short_term = deque(maxlen=self.memory_limit)
        
        # Inicializa a memória de longo prazo (informações permanentes)
        self.long_term = {}
        
        # Carrega memória persistente se habilitado
        if self.persistence_enabled:
            self.load_memory()
    
    def add_message(self, user_id, username, message, is_bot=False):
        """Adiciona uma mensagem à memória de curto prazo"""
        message_data = {
            "user_id": user_id,
            "username": username,
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "is_bot": is_bot
        }
        
        self.short_term.append(message_data)
        
        # Salva a memória se a persistência estiver habilitada
        if self.persistence_enabled:
            self.save_memory()
        
        return True
    
    def get_recent_messages(self, limit=None):
        """Retorna as mensagens mais recentes da memória de curto prazo"""
        if limit is None or limit > len(self.short_term):
            limit = len(self.short_term)
        
        return list(self.short_term)[-limit:]
    
    def store_permanent_info(self, key, value):
        """Armazena uma informação permanente na memória de longo prazo"""
        self.long_term[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        
        # Salva a memória se a persistência estiver habilitada
        if self.persistence_enabled:
            self.save_memory()
        
        return True
    
    def get_permanent_info(self, key, default=None):
        """Recupera uma informação permanente da memória de longo prazo"""
        if key in self.long_term:
            return self.long_term[key]["value"]
        return default
    
    def clear_short_term(self):
        """Limpa a memória de curto prazo"""
        self.short_term.clear()
        
        # Salva a memória se a persistência estiver habilitada
        if self.persistence_enabled:
            self.save_memory()
        
        return True
    
    def clear_long_term(self):
        """Limpa a memória de longo prazo"""
        self.long_term.clear()
        
        # Salva a memória se a persistência estiver habilitada
        if self.persistence_enabled:
            self.save_memory()
        
        return True
    
    def save_memory(self):
        """Salva a memória em um arquivo JSON"""
        try:
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            
            memory_data = {
                "short_term": list(self.short_term),
                "long_term": self.long_term
            }
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=4)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar memória: {e}")