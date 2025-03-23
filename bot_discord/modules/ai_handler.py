# ai_handler.py
# Conexão com LM Studio

import requests
import json
import logging
import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
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
    
    def __init__(self, config):
        self.config = config
        self.api_url = os.getenv('LM_STUDIO_API_URL', 'http://localhost:1234/v1')
        self.model = config.get_config_value('ai_model')
        self.max_tokens = 2048  # Valor padrão
        self.temperature = 0.7  # Valor padrão
        self.timeout = 30  # Timeout para requisições em segundos
        
        # Cache simples para respostas frequentes
        self.response_cache = {}
        self.cache_size = 50  # Tamanho máximo do cache
        self.cache_enabled = True
        
    def generate_response(self, prompt, context=None):
        """Gera uma resposta usando o LM Studio com cache e timeout"""
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
            
            # Gera uma chave de cache baseada no prompt e contexto
            cache_key = self._generate_cache_key(prompt, context)
            
            # Verifica se a resposta está no cache
            if self.cache_enabled and cache_key in self.response_cache:
                logger.info(f"Resposta obtida do cache para: {prompt[:30]}...")
                return self.response_cache[cache_key]
            
            # Prepara os dados para a API
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # Faz a requisição para a API com timeout
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=self.timeout  # Adiciona timeout para evitar bloqueios
            )
            
            # Verifica se a requisição foi bem-sucedida
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Armazena no cache se estiver habilitado
                if self.cache_enabled:
                    self._update_cache(cache_key, content)
                    
                return content
            else:
                logger.error(f"Erro na API do LM Studio: {response.status_code} - {response.text}")
                return "Desculpe, ocorreu um erro ao processar sua mensagem."
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout ao conectar com a API do LM Studio após {self.timeout} segundos")
            return "Desculpe, a resposta está demorando muito. Por favor, tente novamente."
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem."
    
    def _generate_cache_key(self, prompt, context=None):
        """Gera uma chave única para o cache baseada no prompt e contexto"""
        # Cria uma string simples para representar o contexto
        context_str = ""
        if context:
            # Usa apenas as últimas 3 mensagens do contexto para a chave
            for msg in context[-3:]:
                role = "assistant" if msg.get("is_bot", False) else "user"
                content = msg.get("content", "")[:50]  # Limita o tamanho
                context_str += f"{role}:{content[:50]}|"  # Trunca para manter a chave pequena
        
        # Combina prompt e contexto para a chave
        key_base = f"{prompt[:100]}|{context_str}"
        
        # Usa um hash para garantir tamanho fixo da chave
        import hashlib
        return hashlib.md5(key_base.encode('utf-8')).hexdigest()
    
    def _update_cache(self, key, content):
        """Atualiza o cache com uma nova resposta"""
        # Adiciona ao cache
        self.response_cache[key] = content
        
        # Se o cache excedeu o tamanho máximo, remove os itens mais antigos
        if len(self.response_cache) > self.cache_size:
            # Remove o primeiro item (o mais antigo em um dict ordenado por inserção)
            self.response_cache.pop(next(iter(self.response_cache)))
            
        logger.debug(f"Cache atualizado. Tamanho atual: {len(self.response_cache)}")
    
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

    async def _generate_response(self, prompt):
        """Gera uma resposta assíncrona usando o LM Studio"""
        try:
            # Prepara os dados para a API
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # Faz a requisição para a API com timeout
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"Erro na API do LM Studio: {response.status} - {error_text}")
                        return "Desculpe, ocorreu um erro ao processar sua mensagem."
                        
        except asyncio.TimeoutError:
            logger.error(f"Timeout ao conectar com a API do LM Studio após {self.timeout} segundos")
            return "Desculpe, a resposta está demorando muito. Por favor, tente novamente."
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem."

    async def analyze_search_results(self, results, query):
        """Analisa os resultados da busca usando a IA"""
        try:
            # Formata os resultados para o prompt incluindo o conteúdo das páginas
            formatted_results = []
            for i, res in enumerate(results[:3]):
                try:
                    # Tenta fazer o web scraping da página com headers personalizados
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(res['link'], headers=headers, timeout=10) as response:
                            if response.status == 200:
                                html = await response.text()
                                # Extrai o texto principal usando BeautifulSoup
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Remove elementos irrelevantes
                                for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'form', 'button']):
                                    tag.decompose()
                                    
                                # Encontra o conteúdo principal
                                main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=['content', 'main', 'article'])
                                if main_content:
                                    text = main_content.get_text(separator='\n', strip=True)
                                else:
                                    text = soup.get_text(separator='\n', strip=True)
                                
                                # Limpa o texto
                                text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
                                
                                # Limita o tamanho do texto mantendo parágrafos completos
                                if len(text) > 500:
                                    paragraphs = text.split('\n')
                                    text = '\n'.join(paragraphs[:5])  # Mantém os 5 primeiros parágrafos
                                    text = text[:500] + '...'
                            else:
                                text = res.get('snippet', '')
                except Exception as e:
                    logger.warning(f"Erro ao fazer scraping de {res['link']}: {e}")
                    text = res.get('snippet', '')
                
                # Formata o resultado de forma mais concisa
                formatted_results.append(
                    f"[{i+1}] {res['title']}\n"
                    f"URL: {res['link']}\n"
                    f"Resumo:\n{text}\n"
                )

            # Limita o tamanho total do texto formatado
            formatted_text = '\n---\n'.join(formatted_results)
            
            # Cria um prompt focado em responder diretamente à pergunta
            prompt = (
                f"Com base nas informações a seguir, responda diretamente à pergunta: '{query}'\n\n"
                f"{formatted_text}\n\n"
                "Diretriz: Forneça uma resposta direta e objetiva à pergunta usando apenas as informações encontradas.\n"
                "Não mencione fontes, URLs ou metadados.\n"
                "Se não encontrar uma resposta clara nos textos fornecidos, responda 'Desculpe, não encontrei uma resposta precisa para sua pergunta.'\n"
                "Mantenha a resposta concisa e focada especificamente na pergunta feita."
            )

            response = await self._generate_response(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Erro na análise de resultados: {e}")
            return "Não foi possível analisar os resultados no momento."