import logging
import os
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Importa a biblioteca duckduckgo_search e suas exceções
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import (
    DuckDuckGoSearchException,
    RatelimitException,
    TimeoutException,
    ConversationLimitException
)

logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self, config):
        self.config = config
        self.timeout = 30
        
        # Configuração do cache
        self.cache_enabled = self.config.get_config_value('CACHE_ENABLED', True)
        self.cache_expiry = int(self.config.get_config_value('CACHE_EXPIRY', 24))
        
        # Diretório de cache
        self.cache_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'data' / 'search_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações de região e segurança
        self.region = self.config.get_config_value('SEARCH_REGION', 'br-pt')
        self.safesearch = self.config.get_config_value('SEARCH_SAFESEARCH', 'moderate')
        
        # Inicializa o cache se necessário
        self._clean_expired_cache()
    
    def web_search(self, query, search_type='text', num_results=5, engine=None):
        """Realiza uma busca na web usando DuckDuckGo
        
        Args:
            query (str): Consulta de busca
            search_type (str): Tipo de busca ('text', 'news', 'images')
            num_results (int): Número máximo de resultados
            engine (str, optional): Parâmetro ignorado, mantido para compatibilidade
            
        Returns:
            list: Lista de resultados processados para a IA
        """
        try:
            # Verifica se há resultados em cache
            if self.cache_enabled:
                cached_results = self._get_from_cache(query, search_type)
                if cached_results:
                    logger.info(f"Resultados obtidos do cache para: {query}")
                    return cached_results
            
            # Informa ao usuário que está realizando a busca
            logger.info(f"Realizando busca por: {query}")
            
            # Realiza a busca de acordo com o tipo
            if search_type == 'news':
                results = self._news_search(query, num_results)
            elif search_type == 'images':
                results = self._image_search(query, num_results)
            else:  # text search (padrão)
                results = self._text_search(query, num_results)
            
            # Processa os resultados para a IA
            processed_results = self._preprocess_for_ai(results)
            
            # Salva no cache se habilitado
            if self.cache_enabled and processed_results:
                self._save_to_cache(query, search_type, processed_results)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return [{"title": "Erro na busca", "link": "", "snippet": f"Ocorreu um erro ao buscar por '{query}'. Tente novamente mais tarde."}]
    
    def _text_search(self, query, num_results):
        """Realiza busca de texto usando DuckDuckGo"""
        try:
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, region=self.region, safesearch=self.safesearch, max_results=num_results):
                    results.append({
                        'title': r.get('title', ''),
                        'link': r.get('href', ''),
                        'snippet': r.get('body', '')
                    })
                return results
        except RatelimitException as e:
            logger.error(f"Limite de requisições excedido: {e}")
            return [{'title': 'Limite de requisições excedido', 'link': '', 'snippet': 'Tente novamente mais tarde.'}]
        except TimeoutException as e:
            logger.error(f"Timeout na busca: {e}")
            return [{'title': 'Timeout na busca', 'link': '', 'snippet': 'A busca demorou muito para responder. Tente novamente.'}]
        except DuckDuckGoSearchException as e:
            logger.error(f"Erro na API do DuckDuckGo: {e}")
            return [{'title': 'Erro na busca', 'link': '', 'snippet': 'Ocorreu um erro na API de busca. Tente novamente mais tarde.'}]
        except Exception as e:
            logger.error(f"Erro na busca de texto: {e}")
            return []
    
    def _news_search(self, query, num_results):
        """Realiza busca de notícias usando DuckDuckGo"""
        try:
            with DDGS() as ddgs:
                results = []
                for r in ddgs.news(query, region=self.region, max_results=num_results):
                    results.append({
                        'title': r.get('title', ''),
                        'link': r.get('url', ''),
                        'snippet': r.get('body', ''),
                        'date': r.get('date', '')
                    })
                return results
        except RatelimitException as e:
            logger.error(f"Limite de requisições excedido: {e}")
            return [{'title': 'Limite de requisições excedido', 'link': '', 'snippet': 'Tente novamente mais tarde.'}]
        except TimeoutException as e:
            logger.error(f"Timeout na busca: {e}")
            return [{'title': 'Timeout na busca', 'link': '', 'snippet': 'A busca demorou muito para responder. Tente novamente.'}]
        except DuckDuckGoSearchException as e:
            logger.error(f"Erro na API do DuckDuckGo: {e}")
            return [{'title': 'Erro na busca', 'link': '', 'snippet': 'Ocorreu um erro na API de busca. Tente novamente mais tarde.'}]
        except Exception as e:
            logger.error(f"Erro na busca de notícias: {e}")
            return []
    
    def _clean_expired_cache(self):
        """Remove arquivos de cache expirados"""
        if not self.cache_enabled:
            return
            
        try:
            # Define o tempo de expiração
            expiry_time = datetime.now() - timedelta(hours=self.cache_expiry)
            
            # Verifica todos os arquivos no diretório de cache
            for cache_file in self.cache_dir.glob('*.json'):
                try:
                    # Carrega os dados do arquivo
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # Verifica se o cache expirou
                    timestamp = cache_data.get('timestamp', 0)
                    if timestamp < expiry_time.timestamp():
                        # Remove o arquivo expirado
                        os.remove(cache_file)
                        logger.debug(f"Cache expirado removido: {cache_file.name}")
                except Exception as e:
                    # Se houver erro ao processar um arquivo, tenta removê-lo
                    logger.error(f"Erro ao processar arquivo de cache {cache_file.name}: {e}")
                    try:
                        os.remove(cache_file)
                    except:
                        pass
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
    
    def _get_from_cache(self, query, search_type):
        """Obtém resultados do cache"""
        try:
            # Cria um nome de arquivo baseado na consulta e tipo de busca
            # Remove caracteres especiais e sanitiza o nome do arquivo
            import re
            cache_key = re.sub(r'[^a-zA-Z0-9_-]', '_', f"{query}_{search_type}".lower())
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            # Verifica se o arquivo existe
            if not cache_file.exists():
                return None
                
            # Carrega os dados do cache
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # Verifica se o cache expirou
            timestamp = cache_data.get('timestamp', 0)
            expiry_time = datetime.now() - timedelta(hours=self.cache_expiry)
            
            if timestamp < expiry_time.timestamp():
                # Remove o cache expirado
                os.remove(cache_file)
                return None
                
            # Retorna os resultados do cache
            return cache_data.get('results', [])
            
        except Exception as e:
            logger.error(f"Erro ao ler cache: {e}")
            return None
    
    def _save_to_cache(self, query, search_type, results):
        """Salva resultados no cache"""
        try:
            # Cria um nome de arquivo baseado na consulta e tipo de busca
            # Remove caracteres especiais e sanitiza o nome do arquivo
            import re
            cache_key = re.sub(r'[^a-zA-Z0-9_-]', '_', f"{query}_{search_type}".lower())
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            # Prepara os dados para salvar
            cache_data = {
                'query': query,
                'search_type': search_type,
                'timestamp': datetime.now().timestamp(),
                'results': results
            }
            
            # Salva os dados no arquivo
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            logger.debug(f"Resultados salvos em cache: {cache_file.name}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
    
    def _image_search(self, query, num_results):
        """Realiza busca de imagens usando DuckDuckGo"""
        try:
            with DDGS() as ddgs:
                results = []
                for r in ddgs.images(query, region=self.region, safesearch=self.safesearch, max_results=num_results):
                    results.append({
                        'title': r.get('title', ''),
                        'link': r.get('image', ''),
                        'snippet': r.get('title', ''),
                        'thumbnail': r.get('thumbnail', '')
                    })
                return results
        except RatelimitException as e:
            logger.error(f"Limite de requisições excedido: {e}")
            return [{'title': 'Limite de requisições excedido', 'link': '', 'snippet': 'Tente novamente mais tarde.'}]
        except TimeoutException as e:
            logger.error(f"Timeout na busca: {e}")
            return [{'title': 'Timeout na busca', 'link': '', 'snippet': 'A busca demorou muito para responder. Tente novamente.'}]
        except DuckDuckGoSearchException as e:
            logger.error(f"Erro na API do DuckDuckGo: {e}")
            return [{'title': 'Erro na busca', 'link': '', 'snippet': 'Ocorreu um erro na API de busca. Tente novamente mais tarde.'}]
        except Exception as e:
            logger.error(f"Erro na busca de imagens: {e}")
            return []
    
    def _preprocess_for_ai(self, results):
        """Processa os resultados para um formato adequado para a IA
        
        Args:
            results (list): Lista de resultados da busca
            
        Returns:
            list: Lista de resultados processados
        """
        if not results:
            return []
            
        # Limita o tamanho dos resultados para não sobrecarregar a IA
        processed_results = []
        for result in results[:10]:  # Limita a 10 resultados
            # Cria uma cópia do resultado para não modificar o original
            processed = {}
            
            # Processa o título (limita a 100 caracteres)
            if 'title' in result:
                processed['title'] = result['title'][:100] if len(result['title']) > 100 else result['title']
            
            # Processa o link
            if 'link' in result:
                processed['link'] = result['link']
            
            # Processa o snippet (limita a 300 caracteres)
            if 'snippet' in result:
                processed['snippet'] = result['snippet'][:300] if len(result['snippet']) > 300 else result['snippet']
            
            # Adiciona data para notícias
            if 'date' in result:
                processed['date'] = result['date']
                
            processed_results.append(processed)
            
        return processed_results