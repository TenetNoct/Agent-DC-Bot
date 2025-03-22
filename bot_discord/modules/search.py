# search.py
# Busca na web e em arquivos

import requests
import json
import os
import logging
import re
import time
import hashlib
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Importações para navegador headless
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException, StaleElementReferenceException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Selenium não está instalado. A busca headless não estará disponível.")
    logger.info("Para instalar, execute: pip install selenium webdriver-manager")

# Tenta importar o Playwright como alternativa
try:
    import playwright
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

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
        
        # Inicializa o driver do navegador headless se disponível
        self.headless_driver = None
        self.headless_available = SELENIUM_AVAILABLE
        self.playwright_available = PLAYWRIGHT_AVAILABLE
        
        # Sistema de cache para resultados de busca
        self.cache_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'search_cache'
        )
        # Cria o diretório de cache se não existir
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Configuração do cache
        self.cache_enabled = True
        self.cache_expiry = 24  # Horas até a expiração do cache
        
    def _get_cache_key(self, query, engine, num_results):
        """Gera uma chave única para o cache baseada na consulta e parâmetros"""
        # Cria uma string com todos os parâmetros relevantes
        cache_string = f"{query}|{engine}|{num_results}"
        # Gera um hash MD5 para usar como nome de arquivo
        return hashlib.md5(cache_string.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, cache_key):
        """Retorna o caminho completo para o arquivo de cache"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _get_from_cache(self, query, engine, num_results):
        """Tenta obter resultados do cache"""
        if not self.cache_enabled:
            return None
            
        cache_key = self._get_cache_key(query, engine, num_results)
        cache_path = self._get_cache_path(cache_key)
        
        # Verifica se o arquivo de cache existe
        if not os.path.exists(cache_path):
            return None
            
        try:
            # Carrega os dados do cache
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # Verifica se o cache expirou
            cache_time = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01T00:00:00'))
            expiry_time = datetime.now() - timedelta(hours=self.cache_expiry)
            
            if cache_time < expiry_time:
                logger.info(f"Cache expirado para consulta: {query}")
                return None
                
            logger.info(f"Resultados obtidos do cache para: {query}")
            return cache_data.get('results', [])
                
        except Exception as e:
            logger.warning(f"Erro ao ler cache: {e}")
            return None
    
    def _save_to_cache(self, query, engine, num_results, results):
        """Salva os resultados no cache"""
        if not self.cache_enabled or not results:
            return False
            
        cache_key = self._get_cache_key(query, engine, num_results)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            # Prepara os dados para o cache
            cache_data = {
                'query': query,
                'engine': engine,
                'num_results': num_results,
                'timestamp': datetime.now().isoformat(),
                'results': results
            }
            
            # Salva os dados no cache
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=4, ensure_ascii=False)
                
            logger.info(f"Resultados salvos no cache para: {query}")
            return True
                
        except Exception as e:
            logger.warning(f"Erro ao salvar cache: {e}")
            return False
    
    def web_search(self, query, engine='google', num_results=5):
        """Realiza uma busca na web usando Google, Bing ou navegador headless"""
        if not self.search_enabled:
            logger.warning("Busca na web desativada nas configurações")
            return ["Busca na web desativada. Ative nas configurações do bot."]
        
        # Tenta obter resultados do cache primeiro
        cached_results = self._get_from_cache(query, engine, num_results)
        if cached_results:
            return cached_results
        
        # Se não encontrou no cache, realiza a busca
        results = None
        
        # Tenta usar o navegador headless primeiro se disponível
        if engine.lower() == 'headless':
            if self.headless_available:
                results = self._headless_search(query, num_results)
            elif self.playwright_available:
                results = self._playwright_search(query, num_results)
            else:
                logger.warning("Nenhum navegador headless disponível")
                results = ["Busca headless não disponível. Instale o Selenium ou Playwright."]
        elif engine.lower() == 'google':
            results = self._google_search(query, num_results)
        elif engine.lower() == 'bing':
            results = self._bing_search(query, num_results)
        else:
            logger.error(f"Motor de busca não suportado: {engine}")
            results = ["Motor de busca não suportado. Use 'google', 'bing' ou 'headless'."]
        
        # Salva os resultados no cache se forem válidos
        if results and isinstance(results, list) and isinstance(results[0], dict):
            self._save_to_cache(query, engine, num_results, results)
            
        return results
    
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
    
    def _headless_search(self, query, num_results=5):
        """Realiza uma busca usando o Selenium com navegador headless"""
        if not self.headless_available:
            logger.error("Selenium não está disponível para busca headless")
            return ["Busca headless não disponível. Instale o Selenium com 'pip install selenium webdriver-manager'"]
        
        try:
            # Inicializa o driver se ainda não foi inicializado
            if self.headless_driver is None:
                # Configura as opções do Chrome
                chrome_options = Options()
                chrome_options.add_argument("--headless=new")  # Novo modo headless
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-notifications")
                chrome_options.add_argument("--disable-infobars")
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                # Inicializa o driver
                try:
                    service = Service(ChromeDriverManager().install())
                    self.headless_driver = webdriver.Chrome(service=service, options=chrome_options)
                    logger.info("Driver do Chrome inicializado com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao inicializar o driver do Chrome: {e}")
                    return [f"Erro ao inicializar o navegador: {e}"]
            
            # Formata a consulta para URL
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            
            # Acessa a página de resultados
            self.headless_driver.get(search_url)
            
            # Aguarda o carregamento dos resultados com retry
            max_retries = 3
            retries = 0
            result_elements = []
            
            while retries < max_retries and not result_elements:
                try:
                    # Aguarda o carregamento dos resultados
                    WebDriverWait(self.headless_driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.g, div[data-sokoban-container]"))
                    )
                    
                    # Tenta diferentes seletores para maior compatibilidade
                    selectors = ["div.g", "div[data-sokoban-container]", "div.MjjYud"]
                    
                    for selector in selectors:
                        result_elements = self.headless_driver.find_elements(By.CSS_SELECTOR, selector)
                        if result_elements:
                            break
                    
                    if not result_elements:
                        logger.warning(f"Nenhum resultado encontrado com os seletores. Tentativa {retries+1}/{max_retries}")
                        retries += 1
                        time.sleep(2)  # Espera antes de tentar novamente
                        
                except TimeoutException:
                    logger.warning(f"Timeout ao aguardar resultados da busca. Tentativa {retries+1}/{max_retries}")
                    retries += 1
                    time.sleep(2)  # Espera antes de tentar novamente
            
            # Extrai os resultados
            search_results = []
            
            for i, element in enumerate(result_elements):
                if i >= num_results:
                    break
                    
                try:
                    # Tenta diferentes seletores para o título
                    title = ""
                    for title_selector in ["h3", ".LC20lb"]:
                        try:
                            title_element = element.find_element(By.CSS_SELECTOR, title_selector)
                            title = title_element.text
                            if title:
                                break
                        except (NoSuchElementException, StaleElementReferenceException):
                            continue
                    
                    # Tenta diferentes seletores para o link
                    link = ""
                    for link_selector in ["a", "a[href]"]:
                        try:
                            link_element = element.find_element(By.CSS_SELECTOR, link_selector)
                            link = link_element.get_attribute("href")
                            if link and link.startswith("http"):
                                break
                        except (NoSuchElementException, StaleElementReferenceException):
                            continue
                    
                    # Tenta diferentes seletores para o snippet
                    snippet = ""
                    for snippet_selector in ["div.VwiC3b", ".lyLwlc", ".lEBKkf", ".s3v9rd"]:
                        try:
                            snippet_element = element.find_element(By.CSS_SELECTOR, snippet_selector)
                            snippet = snippet_element.text
                            if snippet:
                                break
                        except (NoSuchElementException, StaleElementReferenceException):
                            continue
                    
                    # Verifica se encontrou pelo menos título e link
                    if title and link:
                        search_results.append({
                            'title': title,
                            'link': link,
                            'snippet': snippet or "Sem descrição disponível"
                        })
                except Exception as e:
                    logger.warning(f"Erro ao extrair resultado {i}: {e}")
            
            # Se não encontrou resultados, tenta uma abordagem alternativa
            if not search_results and retries >= max_retries:
                logger.warning("Tentando método alternativo de extração de resultados")
                try:
                    # Captura todos os links e textos visíveis
                    links = self.headless_driver.find_elements(By.TAG_NAME, "a")
                    for i, link_element in enumerate(links):
                        if i >= num_results * 2:  # Procura mais links para filtrar depois
                            break
                            
                        try:
                            href = link_element.get_attribute("href")
                            text = link_element.text
                            
                            # Filtra apenas links relevantes (ignora menus, etc)
                            if (href and href.startswith("http") and 
                                "google" not in href.lower() and 
                                text and len(text) > 15):
                                
                                search_results.append({
                                    'title': text,
                                    'link': href,
                                    'snippet': "Sem descrição disponível"
                                })
                                
                                if len(search_results) >= num_results:
                                    break
                        except Exception:
                            continue
                except Exception as e:
                    logger.warning(f"Erro no método alternativo: {e}")
            
            # Se ainda não encontrou resultados, retorna mensagem de erro
            if not search_results:
                return ["Não foi possível extrair resultados da busca. Tente novamente mais tarde."]
                
            return search_results
            
        except Exception as e:
            logger.error(f"Erro ao realizar busca headless: {e}")
            # Tenta reinicializar o driver em caso de erro crítico
            try:
                if self.headless_driver:
                    self.headless_driver.quit()
            except:
                pass
            self.headless_driver = None
            return [f"Erro ao realizar busca: {e}"]
        
    def _playwright_search(self, query, num_results=5):
        """Realiza uma busca usando o Playwright com navegador headless"""
        if not self.playwright_available:
            logger.error("Playwright não está disponível para busca headless")
            return ["Busca headless com Playwright não disponível. Instale com 'pip install playwright' e execute 'playwright install'"]
        
        try:
            with sync_playwright() as p:
                # Inicializa o navegador
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                # Formata a consulta para URL
                search_url = f"https://www.google.com/search?q={quote_plus(query)}"
                
                # Acessa a página de resultados
                page.goto(search_url, wait_until="domcontentloaded")
                
                # Aguarda o carregamento dos resultados
                page.wait_for_selector("div.g, div[data-sokoban-container], div.MjjYud", timeout=10000)
                
                # Extrai os resultados
                search_results = []
                
                # Tenta diferentes seletores para encontrar os resultados
                selectors = ["div.g", "div[data-sokoban-container]", "div.MjjYud"]
                result_elements = None
                
                for selector in selectors:
                    result_elements = page.query_selector_all(selector)
                    if result_elements and len(result_elements) > 0:
                        break
                
                if not result_elements or len(result_elements) == 0:
                    logger.warning("Nenhum resultado encontrado com os seletores no Playwright")
                    browser.close()
                    return ["Não foi possível encontrar resultados. Tente novamente mais tarde."]
                
                # Processa os resultados encontrados
                for i, element in enumerate(result_elements):
                    if i >= num_results:
                        break
                        
                    try:
                        # Tenta extrair o título
                        title = ""
                        title_element = element.query_selector("h3") or element.query_selector(".LC20lb")
                        if title_element:
                            title = title_element.inner_text()
                        
                        # Tenta extrair o link
                        link = ""
                        link_element = element.query_selector("a[href]") 
                        if link_element:
                            link = link_element.get_attribute("href")
                        
                        # Tenta extrair o snippet
                        snippet = ""
                        snippet_selectors = ["div.VwiC3b", ".lyLwlc", ".lEBKkf", ".s3v9rd"]
                        for snippet_selector in snippet_selectors:
                            snippet_element = element.query_selector(snippet_selector)
                            if snippet_element:
                                snippet = snippet_element.inner_text()
                                if snippet:
                                    break
                        
                        # Adiciona o resultado se tiver pelo menos título e link
                        if title and link:
                            search_results.append({
                                'title': title,
                                'link': link,
                                'snippet': snippet or "Sem descrição disponível"
                            })
                    except Exception as e:
                        logger.warning(f"Erro ao extrair resultado {i} com Playwright: {e}")
                
                # Fecha o navegador
                browser.close()
                
                # Se não encontrou resultados, retorna mensagem de erro
                if not search_results:
                    return ["Não foi possível extrair resultados da busca. Tente novamente mais tarde."]
                    
                return search_results
                
        except Exception as e:
            logger.error(f"Erro ao realizar busca com Playwright: {e}")
            return [f"Erro ao realizar busca: {e}"]
    
    def close_driver(self):
        """Fecha o driver do navegador headless para liberar recursos"""
        if self.headless_driver:
            try:
                self.headless_driver.quit()
                self.headless_driver = None
                logger.info("Driver do navegador headless fechado com sucesso")
                return True
            except Exception as e:
                logger.error(f"Erro ao fechar driver do navegador: {e}")
                return False
        return True
    
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