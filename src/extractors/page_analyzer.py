"""
页面分析模块

负责分析页面内容、验证页面状态和提供页面相关的分析功能
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from typing import Dict, List, Optional, Tuple

from ..core.config import CrawlerConfig
from ..utils.helpers import save_page_source


class PageAnalyzer:
    """页面分析器"""
    
    def __init__(self, driver: webdriver.Chrome, config: CrawlerConfig = None):
        """
        初始化页面分析器
        :param driver: WebDriver实例
        :param config: 爬虫配置对象
        """
        self.driver = driver
        self.config = config or CrawlerConfig()
    
    def analyze_current_page(self) -> Dict[str, any]:
        """
        分析当前页面的基本信息
        :return: 页面分析结果字典
        """
        try:
            analysis = {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'page_type': self._detect_page_type(),
                'has_products': self._has_product_elements(),
                'product_count': self._count_product_elements(),
                'has_popups': self._has_popup_elements(),
                'needs_login': self._needs_login(),
                'page_loaded': self._is_page_loaded(),
                'search_keyword': self._extract_search_keyword(),
                'page_language': self._detect_page_language(),
                'timestamp': time.time()
            }
            
            print(f"页面分析完成: {analysis['page_type']}")
            return analysis
            
        except Exception as e:
            print(f"页面分析时出错: {e}")
            logging.error(f"页面分析时出错: {e}")
            return {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'page_type': 'unknown',
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _detect_page_type(self) -> str:
        """检测页面类型"""
        try:
            url = self.driver.current_url.lower()
            title = self.driver.title.lower()
            
            # 检查是否为搜索结果页
            if any(indicator in url for indicator in ['/s/offer_search', '/offer_search', '/search']):
                return 'search_results'
            
            # 检查是否为商品详情页
            if any(indicator in url for indicator in ['/offer/', '/detail/', '/product/']):
                return 'product_detail'
            
            # 检查是否为登录页
            if any(indicator in url for indicator in self.config.LOGIN_INDICATORS['url_keywords']):
                return 'login'
            
            # 检查是否为首页
            if url in ['https://www.1688.com/', 'https://www.1688.com', 'https://global.1688.com/', 'https://global.1688.com']:
                return 'homepage'
            
            # 检查标题关键词
            if any(keyword in title for keyword in ['搜索', 'search', '结果']):
                return 'search_results'
            
            if any(keyword in title for keyword in ['登录', 'login', '登陆']):
                return 'login'
            
            return 'other'
            
        except Exception as e:
            print(f"检测页面类型时出错: {e}")
            return 'unknown'
    
    def _has_product_elements(self) -> bool:
        """检查页面是否有商品元素"""
        try:
            for selector in self.config.PRODUCT_SELECTORS['standard']:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return True
            return False
        except Exception:
            return False
    
    def _count_product_elements(self) -> int:
        """统计页面中的商品元素数量"""
        try:
            total_count = 0
            for selector in self.config.PRODUCT_SELECTORS['standard']:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    total_count = max(total_count, len(elements))
            return total_count
        except Exception:
            return 0
    
    def _has_popup_elements(self) -> bool:
        """检查页面是否有弹窗元素"""
        try:
            for selector in self.config.POPUP_SELECTORS:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                visible_elements = [el for el in elements if el.is_displayed()]
                if visible_elements:
                    return True
            return False
        except Exception:
            return False
    
    def _needs_login(self) -> bool:
        """检查页面是否需要登录"""
        try:
            url = self.driver.current_url.lower()
            title = self.driver.title.lower()
            
            # 检查URL
            for keyword in self.config.LOGIN_INDICATORS['url_keywords']:
                if keyword in url:
                    return True
            
            # 检查标题
            for keyword in self.config.LOGIN_INDICATORS['title_keywords']:
                if keyword in title:
                    return True
            
            # 检查页面元素
            login_selectors = [
                "input[type='password']",
                "div.login-dialog-wrap",
                "form[action*='login']",
                "div[class*='login']",
                "button[class*='login']"
            ]
            
            login_elements_found = 0
            for selector in login_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [el for el in elements if el.is_displayed()]
                    if visible_elements:
                        login_elements_found += 1
                except:
                    continue
            
            return login_elements_found >= 2
            
        except Exception:
            return False
    
    def _is_page_loaded(self) -> bool:
        """检查页面是否完全加载"""
        try:
            # 检查页面加载状态
            ready_state = self.driver.execute_script("return document.readyState")
            if ready_state != "complete":
                return False
            
            # 检查是否有基本的页面结构
            body_elements = self.driver.find_elements(By.TAG_NAME, "body")
            if not body_elements:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _extract_search_keyword(self) -> Optional[str]:
        """从URL或页面中提取搜索关键词"""
        try:
            url = self.driver.current_url
            
            # 从URL参数中提取
            import urllib.parse as urlparse
            parsed_url = urlparse.urlparse(url)
            query_params = urlparse.parse_qs(parsed_url.query)
            
            # 常见的搜索参数名
            search_params = ['keywords', 'keyword', 'q', 'search', 'query', 'kw']
            
            for param in search_params:
                if param in query_params:
                    keyword = query_params[param][0]
                    if keyword:
                        return keyword
            
            # 从页面元素中提取
            search_input_selectors = [
                "input[name='keywords']",
                "input[name='keyword']",
                "input[name='q']",
                "input[placeholder*='搜索']",
                ".search-input input"
            ]
            
            for selector in search_input_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    value = element.get_attribute('value')
                    if value and value.strip():
                        return value.strip()
                except:
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _detect_page_language(self) -> str:
        """检测页面语言"""
        try:
            # 检查HTML lang属性
            html_element = self.driver.find_element(By.TAG_NAME, "html")
            lang = html_element.get_attribute('lang')
            if lang:
                return lang
            
            # 检查页面内容
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # 简单的中文检测
            chinese_chars = sum(1 for char in page_text if '\u4e00' <= char <= '\u9fff')
            if chinese_chars > 100:
                return 'zh-CN'
            
            return 'en'
            
        except Exception:
            return 'unknown'
    
    def validate_search_results_page(self, keyword: str, is_subsequent_page: bool = False) -> Tuple[bool, Dict[str, any]]:
        """
        验证搜索结果页面的有效性
        :param keyword: 搜索关键词
        :param is_subsequent_page: 是否为后续页面
        :return: (是否有效, 验证详情)
        """
        try:
            print(f"验证搜索结果页面 (关键词: '{keyword}', 后续页面: {is_subsequent_page})")
            
            validation_result = {
                'is_valid': False,
                'url_check': False,
                'keyword_check': False,
                'product_list_check': False,
                'current_url': self.driver.current_url,
                'page_title': self.driver.title,
                'product_count': 0,
                'error_message': ''
            }
            
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            # 1. 检查URL路径是否正确
            search_path_indicators = [
                '/s/offer_search.htm',
                '/offer_search',
                '/search',
                '/s/',
                'offer_search'
            ]
            
            for indicator in search_path_indicators:
                if indicator in current_url:
                    validation_result['url_check'] = True
                    print(f"✅ URL路径验证通过: {indicator}")
                    break
            
            if not validation_result['url_check'] and not is_subsequent_page:
                validation_result['error_message'] = "URL路径验证失败，不是搜索结果页面"
                print("❌ URL路径验证失败，不是搜索结果页面")
            
            # 2. 检查关键词是否在URL或页面中
            if keyword.lower() in current_url.lower() or keyword.lower() in page_title.lower():
                validation_result['keyword_check'] = True
                print(f"✅ 关键词验证通过: '{keyword}' 在URL或标题中")
            else:
                validation_result['error_message'] = f"关键词验证失败: '{keyword}' 不在URL或标题中"
                print(f"❌ 关键词验证失败: '{keyword}' 不在URL或标题中")
            
            # 3. 检查是否有商品列表元素
            try:
                # 等待商品列表容器出现
                WebDriverWait(self.driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".offer-list")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".grid-offer")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".sm-offer-list")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".list-item")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-h5-type='offerCard']"))
                    )
                )
                validation_result['product_list_check'] = True
                validation_result['product_count'] = self._count_product_elements()
                print("✅ 商品列表容器验证通过")
                
            except TimeoutException:
                if not is_subsequent_page:
                    validation_result['error_message'] = "等待商品列表容器元素超时"
                    print(f"❌ 超时：等待商品列表容器元素超时")
                    save_page_source(self.driver, f"timeout_no_product_container_initial_{keyword}.html", self.config.PATHS['html_debug'])
                else:
                    print("后续页面未找到商品列表容器，可能为空页或最后一页。")
            
            # 综合判断
            if is_subsequent_page:
                # 对于后续页面，如果路径和关键词仍在，但列表为空（可能是最后一页），也算通过
                if (validation_result['url_check'] or is_subsequent_page) and validation_result['keyword_check']:
                    validation_result['is_valid'] = True
                    if not validation_result['product_list_check']:
                        validation_result['error_message'] = "后续页面，路径和关键词匹配但未找到商品列表元素，可能为空页或最后一页"
                        print("后续页面，路径和关键词匹配但未找到商品列表元素，可能为空页或最后一页，暂时通过。")
            else:
                validation_result['is_valid'] = (validation_result['url_check'] and 
                                               validation_result['keyword_check'] and 
                                               validation_result['product_list_check'])
            
            print(f"搜索结果页验证结果: {validation_result['is_valid']}")
            return validation_result['is_valid'], validation_result
            
        except Exception as e:
            error_msg = f"验证搜索结果页面时出错: {e}"
            print(error_msg)
            logging.error(error_msg)
            return False, {
                'is_valid': False,
                'error_message': error_msg,
                'current_url': self.driver.current_url,
                'page_title': self.driver.title
            }
    
    def get_page_performance_metrics(self) -> Dict[str, any]:
        """获取页面性能指标"""
        try:
            metrics = self.driver.execute_script("""
            return {
                loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
                domReady: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                firstPaint: performance.getEntriesByType('paint')[0] ? performance.getEntriesByType('paint')[0].startTime : null,
                resourceCount: performance.getEntriesByType('resource').length
            };
            """)
            
            return {
                'load_time_ms': metrics.get('loadTime', 0),
                'dom_ready_ms': metrics.get('domReady', 0),
                'first_paint_ms': metrics.get('firstPaint', 0),
                'resource_count': metrics.get('resourceCount', 0),
                'timestamp': time.time()
            }
            
        except Exception as e:
            print(f"获取页面性能指标时出错: {e}")
            return {
                'error': str(e),
                'timestamp': time.time()
            }
    
    def check_page_errors(self) -> List[Dict[str, str]]:
        """检查页面中的JavaScript错误"""
        try:
            logs = self.driver.get_log('browser')
            errors = []
            
            for log in logs:
                if log['level'] in ['SEVERE', 'WARNING']:
                    errors.append({
                        'level': log['level'],
                        'message': log['message'],
                        'timestamp': log['timestamp']
                    })
            
            return errors
            
        except Exception as e:
            print(f"检查页面错误时出错: {e}")
            return [{'level': 'ERROR', 'message': f"检查失败: {e}", 'timestamp': time.time()}]
