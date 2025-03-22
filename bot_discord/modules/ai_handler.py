# ai_handler.py
# Conexão com LM Studio

import requests
import json
import logging
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do logger
logger = logging.getLogger(__name__)

class AIHandler:
    def __init__(self, config):
        self.config = config
        self.api_url = os.getenv('LM_STUDIO_API_URL', 'http://localhost:1234/v1')
        self.model = config.get_config_value('ai_model')
        self.max_tokens = 2048  # Valor padrão
        self.temperature = 0.7  # Valor padrão
        
    def set_model_params(self, max_tokens=None, temperature=None):
        """Define parâmetros do modelo de IA"""
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if temperature is not None:
            self.temperature = temperature
    
    def generate_response(self, prompt, context=None):
        """Gera uma resposta usando o LM Studio"""
        try:
            # Prepara o contexto para o modelo
            messages = []
            
            # Adiciona contexto se fornecido
            if context:
                for msg in context:
                    role = "assistant" if msg.get("is_bot", False) else "user"
                    messages.append({
                        "role": role,
                        "content": msg.get("content", "")
                    })
            
            # Adiciona a mensagem atual
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Prepara os dados para a API
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # Faz a requisição para a API
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            
            # Verifica se a requisição foi bem-sucedida
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"Erro na API do LM Studio: {response.status_code} - {response.text}")
                return "Desculpe, ocorreu um erro ao processar sua mensagem."
                
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem."
    
    def format_prompt(self, user_message, bot_personality=None):
        """Formata o prompt com a personalidade do bot"""
        if bot_personality:
            return f"[Personalidade: {bot_personality}]\n\nUsuário: {user_message}"
        return user_message
    
    def process_response(self, response):
        """Processa a resposta do modelo para melhorar a inteligibilidade"""
        # Aqui podem ser adicionadas regras para melhorar a resposta
        # Por exemplo, remover repetições, corrigir formatação, etc.
        return response