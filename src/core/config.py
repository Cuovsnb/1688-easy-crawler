"""
爬虫配置管理模块

包含所有的配置常量、设置和默认值
"""

import os
from typing import List, Dict, Any


class CrawlerConfig:
    """爬虫配置类"""

    # 基础URL配置
    DEFAULT_BASE_URL = "https://www.1688.com"
    GLOBAL_BASE_URL = "https://global.1688.com"

    # 搜索相关配置
    SEARCH_PATH = "/s/offer_search.htm"

    # 用户代理列表
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]

    # Chrome选项配置
    CHROME_OPTIONS = {
        'basic': [
            '--disable-gpu',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--window-size=1920,1080'
        ],
        'anti_detection': [
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-images',
            '--disable-default-apps',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-background-networking'
        ],
        'language': [
            '--lang=zh-CN',
            '--accept-lang=zh-CN,zh,en-US,en'
        ]
    }

    # 浏览器首选项
    BROWSER_PREFS = {
        "profile.default_content_setting_values": {
            "notifications": 2,
            "popups": 2,
            "media_stream": 2,
            "geolocation": 2,
        },
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 2,
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1
    }

    # 超时配置
    TIMEOUTS = {
        'page_load': 30,
        'element_wait': 10,
        'login_timeout': 60,
        'popup_wait': 5,
        'search_wait': 15
    }

    # 延迟配置
    DELAYS = {
        'min_delay': 2,
        'max_delay': 5,
        'page_load_min': 3,
        'page_load_max': 6,
        'scroll_delay': 1
    }

    # 文件路径配置
    PATHS = {
        'cookies': 'outputs/cookies/1688_cookies.json',
        'url_cache': 'outputs/cache/successful_urls.txt',
        'logs': 'outputs/logs/1688_crawler.log',
        'excel': 'outputs/excel',
        'json': 'outputs/json',
        'html_debug': 'outputs/html_debug'
    }

    # 登录页面检测关键词
    LOGIN_INDICATORS = {
        'url_keywords': [
            'login.1688.com',
            'login.taobao.com',
            'login.alibaba.com',
            'auth.alibaba.com',
            'passport.1688.com',
            'passport.alibaba.com',
            '/member/signin',
            '/login',
            '/signin'
        ],
        'title_keywords': [
            '登录', '登陆', 'login', 'signin',
            '会员', 'member', '身份验证'
        ]
    }

    # 弹窗选择器配置
    POPUP_SELECTORS = [
        "div.ui-dialog",
        "div.dialog-wrap",
        "div.modal",
        "div.popup",
        "div.overlay",
        "div[class*='dialog']",
        "div[class*='modal']",
        "div[class*='popup']",
        "div[id*='dialog']",
        "div[id*='modal']",
        "div[id*='popup']"
    ]

    # 商品选择器配置
    PRODUCT_SELECTORS = {
        'standard': [
            "div[data-h5-type='offerCard']",
            "div.offer-list-row-offer",
            "div.offer-card",
            "div.J_offerCard",
            "div.list-item",
            "div.sm-offer-item",
            "div.sm-offer-card",
            "div.card-container",
            "div.grid-offer-item",
            "div.grid-mode-offer",
            "div[class*='offer-item']",
            "div.item-info-container",
            "div.item-mod__item",
            "div[data-spm*='offer']"
        ],
        'xpath': [
            "//div[contains(@class, 'offer-card')]",
            "//div[contains(@class, 'product-card')]",
            "//div[contains(@class, 'item')]//a[contains(@href, 'offer')]",
            "//div[contains(@class, 'gallery')]//div[contains(@class, 'item')]"
        ]
    }

    # 数据导出配置
    EXPORT_CONFIG = {
        'excel_engine': 'openpyxl',
        'column_mapping': {
            'title': '商品标题',
            'price': '价格',
            'shop': '店铺名称',
            'sales': '销量',
            'link': '商品链接',
            'image': '图片链接'
        }
    }

    @classmethod
    def get_search_url(cls, base_url: str) -> str:
        """获取搜索URL"""
        return f"{base_url}{cls.SEARCH_PATH}"

    @classmethod
    def get_all_chrome_options(cls) -> List[str]:
        """获取所有Chrome选项"""
        options = []
        for category in cls.CHROME_OPTIONS.values():
            options.extend(category)
        return options

    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        for path_key, path_value in cls.PATHS.items():
            if path_key.endswith('_dir'):
                os.makedirs(path_value, exist_ok=True)
            else:
                # 确保文件的目录存在
                dir_path = os.path.dirname(path_value)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
