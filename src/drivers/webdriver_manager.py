"""
WebDriver管理器模块

负责WebDriver的初始化、配置和反检测机制
"""

import os
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional

from ..core.config import CrawlerConfig


class WebDriverManager:
    """WebDriver管理器"""
    
    def __init__(self, config: CrawlerConfig = None):
        """
        初始化WebDriver管理器
        :param config: 爬虫配置对象
        """
        self.config = config or CrawlerConfig()
        
    def create_driver(self, headless: bool = False, user_data_dir: Optional[str] = None) -> webdriver.Chrome:
        """
        创建Chrome WebDriver实例
        :param headless: 是否使用无头模式
        :param user_data_dir: Chrome用户数据目录路径，用于保持登录状态
        :return: WebDriver实例
        """
        options = self._create_chrome_options(headless, user_data_dir)
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # 应用反检测JavaScript
            self._apply_anti_detection(driver)
            
            # 设置额外的请求头
            self._set_request_headers(driver)
            
            return driver
            
        except Exception as e:
            logging.error(f"初始化WebDriver失败: {e}")
            raise
    
    def _create_chrome_options(self, headless: bool, user_data_dir: Optional[str]) -> webdriver.ChromeOptions:
        """
        创建Chrome选项
        :param headless: 是否使用无头模式
        :param user_data_dir: Chrome用户数据目录路径
        :return: Chrome选项对象
        """
        options = webdriver.ChromeOptions()
        
        # 添加用户数据目录以保持登录状态
        if user_data_dir and os.path.exists(user_data_dir):
            options.add_argument(f'--user-data-dir={user_data_dir}')
            options.add_argument('--profile-directory=Default')
            print(f"已加载Chrome用户数据目录: {user_data_dir}")
        
        # 无头模式
        if headless:
            options.add_argument('--headless=new')
        
        # 添加所有配置的Chrome选项
        for option in self.config.get_all_chrome_options():
            options.add_argument(option)
        
        # 禁用自动化检测
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 设置浏览器首选项
        options.add_experimental_option("prefs", self.config.BROWSER_PREFS)
        
        # 添加随机用户代理
        user_agent = random.choice(self.config.USER_AGENTS)
        options.add_argument(f'--user-agent={user_agent}')
        
        return options
    
    def _apply_anti_detection(self, driver: webdriver.Chrome):
        """
        应用反检测JavaScript
        :param driver: WebDriver实例
        """
        anti_detection_script = """
            // 隐藏webdriver属性
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 模拟真实的Chrome环境
            window.navigator.chrome = {
                runtime: {},
                app: {
                    isInstalled: false,
                },
                webstore: {
                    onInstallStageChanged: {},
                    onDownloadProgress: {},
                },
            };

            // 模拟真实的插件列表
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {type: "application/pdf", suffixes: "pdf", description: "", enabledPlugin: Plugin},
                        description: "",
                        filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    }
                ],
            });

            // 设置语言
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en-US', 'en'],
            });

            // 隐藏自动化相关属性
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;

            // 模拟真实的权限API
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            // 添加真实的屏幕属性
            Object.defineProperty(screen, 'availTop', {
                get: () => 0
            });
            Object.defineProperty(screen, 'availLeft', {
                get: () => 0
            });
        """
        
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": anti_detection_script
        })
    
    def _set_request_headers(self, driver: webdriver.Chrome):
        """
        设置额外的请求头
        :param driver: WebDriver实例
        """
        user_agent = random.choice(self.config.USER_AGENTS)
        
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": user_agent,
            "acceptLanguage": "zh-CN,zh;q=0.9,en;q=0.8",
            "platform": "Win32"
        })
    
    @staticmethod
    def close_driver(driver: webdriver.Chrome):
        """
        安全关闭WebDriver
        :param driver: WebDriver实例
        """
        try:
            if driver:
                driver.quit()
                print("浏览器已关闭")
        except Exception as e:
            logging.error(f"关闭浏览器时出错: {e}")
    
    def apply_stealth_mode(self, driver: webdriver.Chrome):
        """
        应用隐身模式设置
        :param driver: WebDriver实例
        """
        # 设置更真实的请求头
        driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)
        
        # 重新设置用户代理
        self._set_request_headers(driver)
