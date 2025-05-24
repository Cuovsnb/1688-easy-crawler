"""
URL构造器模块

负责构造各种搜索URL，支持不同的参数组合和编码方式
"""

import urllib.parse
from typing import List, Dict, Any, Optional

from ..core.config import CrawlerConfig


class URLBuilder:
    """URL构造器"""
    
    def __init__(self, config: CrawlerConfig = None):
        """
        初始化URL构造器
        :param config: 爬虫配置对象
        """
        self.config = config or CrawlerConfig()
    
    def build_search_urls(self, keyword: str, base_url: Optional[str] = None) -> List[str]:
        """
        构造搜索URL列表
        :param keyword: 搜索关键词
        :param base_url: 基础URL，如果为None则使用配置中的默认值
        :return: 搜索URL列表
        """
        base_url = base_url or self.config.DEFAULT_BASE_URL
        search_urls = []
        
        try:
            # 编码关键词
            encoded_keyword = urllib.parse.quote(keyword, safe='')
            encoded_keyword_plus = urllib.parse.quote_plus(keyword)
            
            # 方式1: 标准搜索URL
            standard_urls = self._build_standard_search_urls(keyword, encoded_keyword, base_url)
            search_urls.extend(standard_urls)
            
            # 方式2: 带更多参数的搜索URL
            enhanced_urls = self._build_enhanced_search_urls(keyword, encoded_keyword, base_url)
            search_urls.extend(enhanced_urls)
            
            # 方式3: 不同编码方式的URL
            encoding_urls = self._build_encoding_variant_urls(keyword, encoded_keyword_plus, base_url)
            search_urls.extend(encoding_urls)
            
            # 方式4: 国际站URL（如果适用）
            if 'global' not in base_url:
                global_urls = self._build_global_search_urls(keyword, encoded_keyword)
                search_urls.extend(global_urls)
            
            print(f"构造了 {len(search_urls)} 个搜索URL")
            return search_urls
            
        except Exception as e:
            print(f"构造搜索URL时出错: {e}")
            return []
    
    def _build_standard_search_urls(self, keyword: str, encoded_keyword: str, base_url: str) -> List[str]:
        """构造标准搜索URL"""
        urls = []
        
        # 基础参数组合
        param_combinations = [
            # 最简单的参数
            {'keywords': encoded_keyword},
            
            # 常用参数组合
            {
                'keywords': encoded_keyword,
                'n': 'y',
                'search': 'y'
            },
            
            # 完整参数组合
            {
                'keywords': encoded_keyword,
                'n': 'y',
                'netin': '2',
                'spm': 'a26352.13672862.searchbar.1',
                'search': 'y',
                'pageSize': '60',
                'beginPage': '1'
            },
            
            # 移动端参数
            {
                'keywords': encoded_keyword,
                'from': 'mobile',
                'search': 'y'
            }
        ]
        
        search_path = self.config.get_search_url(base_url)
        
        for params in param_combinations:
            try:
                query_string = urllib.parse.urlencode(params)
                url = f"{search_path}?{query_string}"
                urls.append(url)
            except Exception as e:
                print(f"构造标准URL时出错: {e}")
                continue
        
        return urls
    
    def _build_enhanced_search_urls(self, keyword: str, encoded_keyword: str, base_url: str) -> List[str]:
        """构造增强搜索URL"""
        urls = []
        
        # 增强参数组合
        enhanced_params = [
            # 带排序参数
            {
                'keywords': encoded_keyword,
                'n': 'y',
                'search': 'y',
                'sortType': 'default',
                'orderType': 'desc'
            },
            
            # 带价格范围
            {
                'keywords': encoded_keyword,
                'n': 'y',
                'search': 'y',
                'priceStart': '0',
                'priceEnd': '999999'
            },
            
            # 带地区参数
            {
                'keywords': encoded_keyword,
                'n': 'y',
                'search': 'y',
                'province': '',
                'city': ''
            },
            
            # 带时间戳
            {
                'keywords': encoded_keyword,
                'n': 'y',
                'search': 'y',
                't': str(int(__import__('time').time()))
            }
        ]
        
        search_path = self.config.get_search_url(base_url)
        
        for params in enhanced_params:
            try:
                query_string = urllib.parse.urlencode(params)
                url = f"{search_path}?{query_string}"
                urls.append(url)
            except Exception as e:
                print(f"构造增强URL时出错: {e}")
                continue
        
        return urls
    
    def _build_encoding_variant_urls(self, keyword: str, encoded_keyword_plus: str, base_url: str) -> List[str]:
        """构造不同编码方式的URL"""
        urls = []
        
        try:
            # 不同编码方式
            encoding_variants = [
                # URL编码（+号方式）
                {
                    'keywords': encoded_keyword_plus,
                    'n': 'y',
                    'search': 'y'
                },
                
                # UTF-8编码
                {
                    'keywords': keyword.encode('utf-8').decode('utf-8'),
                    'n': 'y',
                    'search': 'y'
                },
                
                # 原始关键词（不编码）
                {
                    'keywords': keyword,
                    'n': 'y',
                    'search': 'y'
                }
            ]
            
            search_path = self.config.get_search_url(base_url)
            
            for params in encoding_variants:
                try:
                    query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
                    url = f"{search_path}?{query_string}"
                    urls.append(url)
                except Exception as e:
                    print(f"构造编码变体URL时出错: {e}")
                    continue
            
        except Exception as e:
            print(f"构造编码变体URL时出错: {e}")
        
        return urls
    
    def _build_global_search_urls(self, keyword: str, encoded_keyword: str) -> List[str]:
        """构造国际站搜索URL"""
        urls = []
        
        try:
            global_base_url = self.config.GLOBAL_BASE_URL
            
            # 国际站参数
            global_params = [
                {
                    'keywords': encoded_keyword,
                    'SearchText': encoded_keyword,
                    'IndexArea': 'product_en',
                    'CatId': '',
                    'viewtype': 'G'
                },
                
                {
                    'keywords': encoded_keyword,
                    'tab': 'all',
                    'searchType': 'product'
                }
            ]
            
            # 国际站搜索路径
            global_search_paths = [
                '/search/product.htm',
                '/products',
                '/search'
            ]
            
            for search_path in global_search_paths:
                for params in global_params:
                    try:
                        query_string = urllib.parse.urlencode(params)
                        url = f"{global_base_url}{search_path}?{query_string}"
                        urls.append(url)
                    except Exception as e:
                        print(f"构造国际站URL时出错: {e}")
                        continue
            
        except Exception as e:
            print(f"构造国际站URL时出错: {e}")
        
        return urls
    
    def build_product_detail_url(self, product_id: str, base_url: Optional[str] = None) -> str:
        """
        构造商品详情页URL
        :param product_id: 商品ID
        :param base_url: 基础URL
        :return: 商品详情页URL
        """
        base_url = base_url or self.config.DEFAULT_BASE_URL
        
        try:
            # 1688商品详情页URL格式
            detail_url = f"{base_url}/offer/{product_id}.html"
            return detail_url
            
        except Exception as e:
            print(f"构造商品详情URL时出错: {e}")
            return ""
    
    def build_shop_url(self, shop_id: str, base_url: Optional[str] = None) -> str:
        """
        构造店铺URL
        :param shop_id: 店铺ID
        :param base_url: 基础URL
        :return: 店铺URL
        """
        base_url = base_url or self.config.DEFAULT_BASE_URL
        
        try:
            # 1688店铺URL格式
            shop_url = f"{base_url}/shop/{shop_id}.html"
            return shop_url
            
        except Exception as e:
            print(f"构造店铺URL时出错: {e}")
            return ""
    
    def parse_search_url(self, url: str) -> Dict[str, Any]:
        """
        解析搜索URL，提取参数
        :param url: 搜索URL
        :return: 解析结果字典
        """
        try:
            parsed_url = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # 提取关键信息
            result = {
                'base_url': f"{parsed_url.scheme}://{parsed_url.netloc}",
                'path': parsed_url.path,
                'keyword': '',
                'page_size': '',
                'page_number': '',
                'sort_type': '',
                'all_params': query_params
            }
            
            # 提取关键词
            keyword_params = ['keywords', 'keyword', 'q', 'SearchText']
            for param in keyword_params:
                if param in query_params:
                    result['keyword'] = query_params[param][0]
                    break
            
            # 提取页面大小
            if 'pageSize' in query_params:
                result['page_size'] = query_params['pageSize'][0]
            
            # 提取页码
            page_params = ['beginPage', 'page', 'pageNum']
            for param in page_params:
                if param in query_params:
                    result['page_number'] = query_params[param][0]
                    break
            
            # 提取排序类型
            if 'sortType' in query_params:
                result['sort_type'] = query_params['sortType'][0]
            
            return result
            
        except Exception as e:
            print(f"解析搜索URL时出错: {e}")
            return {
                'error': str(e),
                'original_url': url
            }
    
    def modify_search_url(self, url: str, modifications: Dict[str, str]) -> str:
        """
        修改搜索URL的参数
        :param url: 原始URL
        :param modifications: 要修改的参数字典
        :return: 修改后的URL
        """
        try:
            parsed_url = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # 应用修改
            for key, value in modifications.items():
                query_params[key] = [value]
            
            # 重新构造URL
            new_query = urllib.parse.urlencode(query_params, doseq=True)
            new_url = urllib.parse.urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                new_query,
                parsed_url.fragment
            ))
            
            return new_url
            
        except Exception as e:
            print(f"修改搜索URL时出错: {e}")
            return url
    
    def get_next_page_url(self, current_url: str) -> str:
        """
        获取下一页的URL
        :param current_url: 当前页面URL
        :return: 下一页URL
        """
        try:
            parsed_result = self.parse_search_url(current_url)
            current_page = int(parsed_result.get('page_number', '1'))
            next_page = current_page + 1
            
            modifications = {'beginPage': str(next_page)}
            next_url = self.modify_search_url(current_url, modifications)
            
            return next_url
            
        except Exception as e:
            print(f"获取下一页URL时出错: {e}")
            return ""
    
    def validate_search_url(self, url: str) -> bool:
        """
        验证搜索URL是否有效
        :param url: 要验证的URL
        :return: 是否有效
        """
        try:
            parsed_url = urllib.parse.urlparse(url)
            
            # 检查基本格式
            if not parsed_url.scheme or not parsed_url.netloc:
                return False
            
            # 检查是否包含1688域名
            if '1688.com' not in parsed_url.netloc:
                return False
            
            # 检查是否是搜索路径
            search_paths = ['/s/offer_search.htm', '/search', '/products']
            if not any(path in parsed_url.path for path in search_paths):
                return False
            
            # 检查是否有关键词参数
            query_params = urllib.parse.parse_qs(parsed_url.query)
            keyword_params = ['keywords', 'keyword', 'q', 'SearchText']
            has_keyword = any(param in query_params for param in keyword_params)
            
            return has_keyword
            
        except Exception as e:
            print(f"验证搜索URL时出错: {e}")
            return False
