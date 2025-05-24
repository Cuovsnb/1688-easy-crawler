"""
缓存管理模块

负责Cookie和URL缓存的管理
"""

import os
import json
import logging
from datetime import datetime
from selenium import webdriver
from typing import Dict, Optional, List

from ..core.config import CrawlerConfig


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, driver: webdriver.Chrome, config: CrawlerConfig = None):
        """
        初始化缓存管理器
        :param driver: WebDriver实例
        :param config: 爬虫配置对象
        """
        self.driver = driver
        self.config = config or CrawlerConfig()
        
        # 确保缓存目录存在
        self._ensure_cache_directories()
    
    def _ensure_cache_directories(self):
        """确保缓存目录存在"""
        cookie_dir = os.path.dirname(self.config.PATHS['cookies'])
        if cookie_dir:
            os.makedirs(cookie_dir, exist_ok=True)
    
    def load_cookies(self, cookie_file: Optional[str] = None) -> bool:
        """
        加载保存的Cookie
        :param cookie_file: Cookie文件路径，如果为None则使用配置中的默认路径
        :return: 是否加载成功
        """
        cookie_file = cookie_file or self.config.PATHS['cookies']
        
        try:
            if os.path.exists(cookie_file):
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                    
                loaded_count = 0
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                        loaded_count += 1
                    except Exception as e:
                        print(f"添加Cookie失败: {e}")
                        
                print(f"已加载{loaded_count}/{len(cookies)}个Cookie")
                return True
            else:
                print("Cookie文件不存在")
                return False
                
        except Exception as e:
            print(f"加载Cookie失败: {e}")
            logging.error(f"加载Cookie失败: {e}")
            return False
    
    def save_cookies(self, cookie_file: Optional[str] = None) -> bool:
        """
        保存当前Cookie
        :param cookie_file: Cookie文件路径，如果为None则使用配置中的默认路径
        :return: 是否保存成功
        """
        cookie_file = cookie_file or self.config.PATHS['cookies']
        
        try:
            cookies = self.driver.get_cookies()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(cookie_file), exist_ok=True)
            
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
                
            print(f"已保存{len(cookies)}个Cookie到{cookie_file}")
            return True
            
        except Exception as e:
            print(f"保存Cookie失败: {e}")
            logging.error(f"保存Cookie失败: {e}")
            return False
    
    def clear_cookies(self):
        """清除所有Cookie"""
        try:
            self.driver.delete_all_cookies()
            print("已清除所有Cookie")
        except Exception as e:
            print(f"清除Cookie失败: {e}")
            logging.error(f"清除Cookie失败: {e}")
    
    def load_successful_urls(self, cache_file: Optional[str] = None) -> Dict[str, str]:
        """
        加载成功的URL缓存
        :param cache_file: 缓存文件路径，如果为None则使用配置中的默认路径
        :return: 关键词到URL的映射字典
        """
        cache_file = cache_file or self.config.PATHS['url_cache']
        
        try:
            url_cache = {}
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split('|')
                            if len(parts) >= 2:
                                keyword = parts[0].strip()
                                url = parts[1].strip()
                                url_cache[keyword] = url
                            else:
                                print(f"警告：第{line_num}行格式不正确: {line}")
                                
                print(f"已加载{len(url_cache)}个成功URL缓存")
            else:
                print("URL缓存文件不存在，将创建新文件")
                
            return url_cache
            
        except Exception as e:
            print(f"加载URL缓存失败: {e}")
            logging.error(f"加载URL缓存失败: {e}")
            return {}
    
    def save_successful_url(self, keyword: str, url: str, cache_file: Optional[str] = None) -> bool:
        """
        保存成功的URL到缓存文件
        :param keyword: 搜索关键词
        :param url: 成功的URL
        :param cache_file: 缓存文件路径，如果为None则使用配置中的默认路径
        :return: 是否保存成功
        """
        cache_file = cache_file or self.config.PATHS['url_cache']
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 读取现有内容
            existing_lines = []
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    existing_lines = f.readlines()
            
            # 检查是否已存在该关键词的记录
            keyword_exists = False
            for i, line in enumerate(existing_lines):
                if line.strip() and not line.startswith('#'):
                    parts = line.split('|')
                    if len(parts) >= 2 and parts[0].strip() == keyword:
                        # 更新现有记录
                        existing_lines[i] = f"{keyword}|{url}|{timestamp}|直接访问成功\n"
                        keyword_exists = True
                        break
            
            # 如果不存在，添加新记录
            if not keyword_exists:
                new_record = f"{keyword}|{url}|{timestamp}|直接访问成功\n"
                existing_lines.append(new_record)
            
            # 写回文件
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.writelines(existing_lines)
            
            print(f"已保存成功URL: {keyword} -> {url}")
            return True
            
        except Exception as e:
            print(f"保存成功URL失败: {e}")
            logging.error(f"保存成功URL失败: {e}")
            return False
    
    def get_cached_url(self, keyword: str, cache_file: Optional[str] = None) -> Optional[str]:
        """
        获取关键词对应的缓存URL
        :param keyword: 搜索关键词
        :param cache_file: 缓存文件路径，如果为None则使用配置中的默认路径
        :return: 缓存的URL，如果不存在返回None
        """
        try:
            url_cache = self.load_successful_urls(cache_file)
            cached_url = url_cache.get(keyword)
            
            if cached_url:
                print(f"找到缓存URL: {keyword} -> {cached_url}")
                return cached_url
            else:
                print(f"未找到关键词 '{keyword}' 的缓存URL")
                return None
                
        except Exception as e:
            print(f"获取缓存URL失败: {e}")
            logging.error(f"获取缓存URL失败: {e}")
            return None
    
    def remove_cached_url(self, keyword: str, cache_file: Optional[str] = None) -> bool:
        """
        删除指定关键词的缓存URL
        :param keyword: 搜索关键词
        :param cache_file: 缓存文件路径，如果为None则使用配置中的默认路径
        :return: 是否删除成功
        """
        cache_file = cache_file or self.config.PATHS['url_cache']
        
        try:
            if not os.path.exists(cache_file):
                print(f"缓存文件不存在: {cache_file}")
                return False
            
            # 读取现有内容
            existing_lines = []
            with open(cache_file, 'r', encoding='utf-8') as f:
                existing_lines = f.readlines()
            
            # 过滤掉指定关键词的记录
            filtered_lines = []
            removed = False
            
            for line in existing_lines:
                if line.strip() and not line.startswith('#'):
                    parts = line.split('|')
                    if len(parts) >= 2 and parts[0].strip() == keyword:
                        removed = True
                        continue
                filtered_lines.append(line)
            
            if removed:
                # 写回文件
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.writelines(filtered_lines)
                print(f"已删除关键词 '{keyword}' 的缓存URL")
                return True
            else:
                print(f"未找到关键词 '{keyword}' 的缓存记录")
                return False
                
        except Exception as e:
            print(f"删除缓存URL失败: {e}")
            logging.error(f"删除缓存URL失败: {e}")
            return False
    
    def get_all_cached_urls(self, cache_file: Optional[str] = None) -> List[Dict[str, str]]:
        """
        获取所有缓存的URL记录
        :param cache_file: 缓存文件路径，如果为None则使用配置中的默认路径
        :return: 缓存记录列表
        """
        cache_file = cache_file or self.config.PATHS['url_cache']
        
        try:
            records = []
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split('|')
                            if len(parts) >= 4:
                                record = {
                                    'keyword': parts[0].strip(),
                                    'url': parts[1].strip(),
                                    'timestamp': parts[2].strip(),
                                    'status': parts[3].strip()
                                }
                                records.append(record)
            
            return records
            
        except Exception as e:
            print(f"获取所有缓存URL失败: {e}")
            logging.error(f"获取所有缓存URL失败: {e}")
            return []
    
    def clear_url_cache(self, cache_file: Optional[str] = None) -> bool:
        """
        清空URL缓存
        :param cache_file: 缓存文件路径，如果为None则使用配置中的默认路径
        :return: 是否清空成功
        """
        cache_file = cache_file or self.config.PATHS['url_cache']
        
        try:
            if os.path.exists(cache_file):
                os.remove(cache_file)
                print(f"已清空URL缓存文件: {cache_file}")
            else:
                print("URL缓存文件不存在")
            return True
            
        except Exception as e:
            print(f"清空URL缓存失败: {e}")
            logging.error(f"清空URL缓存失败: {e}")
            return False
