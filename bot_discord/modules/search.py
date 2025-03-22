# search.py
# Busca na web e em arquivos

import requests
import json
import os
import logging
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do logger
logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self, config):
        self.config = config
        self.search_enabled = config.get_config_value('search_enabled')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cx = os.getenv('GOOGLE_CX')
        self.bing_api_key = os.getenv('BING_API_KEY')
        
    def web_search(self, query, engine='google', num_results=5):
        """Realiza uma busca na web usando Google ou Bing"""
        if not self.search_enabled:
            logger.warning("Busca na web desativada nas configurações")
            return ["Busca na web desativada. Ative nas configurações do bot."]
            
        if engine.lower() == 'google':
            return self._google_search(query, num_results)
        elif engine.lower() == 'bing':
            return self._bing_search(query, num_results)
        else:
            logger.error(f"Motor de busca não suportado: {engine}")
            return ["Motor de busca não suportado. Use 'google' ou 'bing'."]
    
    def _google_search(self, query, num_results=5):
        """Realiza uma busca usando a API do Google"""
        if not self.google_api_key or not self.google_cx:
            logger.error("Chaves de API do Google não configuradas")
            return ["Chaves de API do Google não configuradas."]
            
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cx,
                'q': query,
                'num': num_results
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                results = response.json()
                search_results = []
                
                if 'items' in results:
                    for item in results['items']:
                        search_results.append({
                            'title': item.get('title', ''),
                            'link': item.get('link', ''),
                            'snippet': item.get('snippet', '')
                        })
                    
                return search_results
            else:
                logger.error(f"Erro na API do Google: {response.status_code} - {response.text}")
                return [f"Erro na busca: {response.status_code}"]
                
        except Exception as e:
            logger.error(f"Erro ao realizar busca no Google: {e}")
            return [f"Erro ao realizar busca: {e}"]
    
    def _bing_search(self, query, num_results=5):
        """Realiza uma busca usando a API do Bing"""
        if not self.bing_api_key:
            logger.error("Chave de API do Bing não configurada")
            return ["Chave de API do Bing não configurada."]
            
        try:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}
            params = {"q": query, "count": num_results}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                results = response.json()
                search_results = []
                
                if 'webPages' in results and 'value' in results['webPages']:
                    for item in results['webPages']['value']:
                        search_results.append({
                            'title': item.get('name', ''),
                            'link': item.get('url', ''),
                            'snippet': item.get('snippet', '')
                        })
                    
                return search_results
            else:
                logger.error(f"Erro na API do Bing: {response.status_code} - {response.text}")
                return [f"Erro na busca: {response.status_code}"]
                
        except Exception as e:
            logger.error(f"Erro ao realizar busca no Bing: {e}")
            return [f"Erro ao realizar busca: {e}"]
    
    def file_search(self, query, directory=None):
        """Busca por conteúdo em arquivos locais"""
        # Implementação básica de busca em arquivos
        # Pode ser expandida para usar indexação ou algoritmos mais eficientes
        results = []
        
        if directory is None:
            directory = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data'
            )
        
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith('.txt') or file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if query.lower() in content.lower():
                                    results.append({
                                        'file': file,
                                        'path': file_path,
                                        'match': "Conteúdo encontrado"
                                    })
                        except Exception as e:
                            logger.error(f"Erro ao ler arquivo {file_path}: {e}")
            
            return results
        except Exception as e:
            logger.error(f"Erro ao buscar em arquivos: {e}")
            return [f"Erro ao buscar em arquivos: {e}"]