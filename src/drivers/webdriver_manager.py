"""
WebDriver管理器模块

负责WebDriver的初始化、配置和反检测机制
"""

import os
import random
import logging
import tempfile # Added
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import SessionNotCreatedException # Added
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
        self.temp_user_data_dir = None # For storing path to temp user data dir
        
    def create_driver(self, headless: bool = False, user_data_dir: Optional[str] = None) -> webdriver.Chrome:
        """
        创建Chrome WebDriver实例
        :param headless: 是否使用无头模式
        :param user_data_dir: Chrome用户数据目录路径，用于保持登录状态
        :return: WebDriver实例
        """
        options = self._create_chrome_options(headless, user_data_dir)
        
        try:
            driver_path = ChromeDriverManager().install()
            service = Service(executable_path=driver_path)
            logging.info(f"Using ChromeDriver at: {driver_path}")
            logging.info(f"Chrome options being used: {options.arguments}")
            driver = webdriver.Chrome(service=service, options=options)
            
            self._apply_anti_detection(driver)
            self._set_request_headers(driver)
            return driver
        except SessionNotCreatedException as e:
            logging.error(f"SessionNotCreatedException during WebDriver initialization.")
            logging.error(f"User-data-dir used: {self.temp_user_data_dir or user_data_dir}")
            logging.error(f"Chrome options: {options.arguments}")
            logging.error(f"Exception details: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected exception during WebDriver initialization: {e}")
            logging.error(f"Chrome options: {options.arguments}")
            raise
    
    def _create_chrome_options(self, headless: bool, user_data_dir: Optional[str]) -> webdriver.ChromeOptions:
        """
        创建Chrome选项
        :param headless: 是否使用无头模式
        :param user_data_dir: Chrome用户数据目录路径
        :return: Chrome选项对象
        """
        options = webdriver.ChromeOptions()

        if user_data_dir:
            options.add_argument(f'--user-data-dir={user_data_dir}')
        else:
            self.temp_user_data_dir = tempfile.mkdtemp()
            options.add_argument(f'--user-data-dir={self.temp_user_data_dir}')
            logging.info(f"Using temporary user data directory: {self.temp_user_data_dir}")
        
        if headless:
            options.add_argument('--headless=new')

        # Explicitly add required options
        options.add_argument('--no-sandbox') # Already added by default config usually but ensure
        options.add_argument('--disable-dev-shm-usage') # Already added by default config usually but ensure
        options.add_argument('--disable-gpu') # From config.CHROME_OPTIONS
        options.add_argument('--disable-extensions') # From config.CHROME_OPTIONS
        options.add_argument('--remote-debugging-port=0')
        options.add_argument('--start-maximized')
        options.add_argument('--single-process')

        # Add other options from config, avoiding duplicates if possible (though Chrome handles them)
        # Standard options from config:
        # CHROME_OPTIONS = [
        #     '--disable-gpu', # Already added
        #     '--window-size=1920,1080',
        #     '--disable-extensions', # Already added
        #     '--disable-popup-blocking',
        #     '--ignore-certificate-errors',
        #     '--disable-blink-features=AutomationControlled'
        # ]
        # Additional options added previously:
        # '--disable-setuid-sandbox'
        # '--disable-features=VizDisplayCompositor'

        # Let's be very explicit and add them all, Chrome should handle duplicates.
        current_options_set = set(options.arguments)
        
        # Options from task description
        explicit_options = [
            '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage', 
            '--remote-debugging-port=0', '--disable-extensions', 
            '--start-maximized', '--single-process'
        ]
        for opt in explicit_options:
            if opt not in current_options_set:
                options.add_argument(opt)
                current_options_set.add(opt)

        # Options from config file
        for option in self.config.get_all_chrome_options():
            if option not in current_options_set:
                options.add_argument(option)
                current_options_set.add(option)
        
        # Other potentially useful options (some might have been added in previous attempts)
        other_useful_options = [
            '--disable-setuid-sandbox',
            '--disable-features=VizDisplayCompositor', # From previous attempts
        ]
        for opt in other_useful_options:
            if opt not in current_options_set:
                options.add_argument(opt)
                current_options_set.add(opt)

        # Anti-detection (already part of config.CHROME_OPTIONS via disable-blink-features)
            options.add_argument(option)
        
        # 禁用自动化检测
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 设置浏览器首选项
        options.add_experimental_option("prefs", self.config.BROWSER_PREFS)
        
        # 添加随机用户代理
        user_agent = random.choice(self.config.USER_AGENTS)
        if f'--user-agent={user_agent}' not in current_options_set:
             options.add_argument(f'--user-agent={user_agent}')
        
        return options

    # Method to clean up temp user data dir if created
    def cleanup_temp_user_data_dir(self):
        if self.temp_user_data_dir and os.path.exists(self.temp_user_data_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_user_data_dir)
                logging.info(f"Successfully cleaned up temporary user data directory: {self.temp_user_data_dir}")
                self.temp_user_data_dir = None
            except Exception as e:
                logging.error(f"Error cleaning up temporary user data directory {self.temp_user_data_dir}: {e}")

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
                # print("浏览器已关闭") # Reduced verbosity, covered by crawler.close()
        except Exception as e:
            logging.error(f"关闭浏览器时出错: {e}")

    # Consider calling cleanup_temp_user_data_dir() in the main crawler's close method
    # if an instance of WebDriverManager is retained by the crawler.
    # For now, OS will handle temp dir cleanup.

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
