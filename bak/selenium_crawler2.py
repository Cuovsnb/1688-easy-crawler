import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional, Any, Union, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from login_helper import LoginHelper

class Alibaba1688SeleniumCrawler:
    """
    使用Selenium实现的1688网站爬虫类
    """

    def __init__(self, base_url=None, headless=False, user_data_dir=None):
        """
        初始化爬虫
        :param base_url: 基础URL (global.1688.com 或 www.1688.com)
        :param headless: 是否使用无头模式
        :param user_data_dir: Chrome用户数据目录路径，用于保持登录状态
        """
        self.base_url = base_url or "https://www.1688.com"
        self.search_url = f"{self.base_url}/s/offer_search.htm"
        self.driver = self._init_driver(headless, user_data_dir)
        self.login_helper = LoginHelper(self.driver)
        self.data = []

    def _init_driver(self, headless: bool = False, user_data_dir: str = None):
        """
        初始化Chrome驱动 - 增强反检测机制
        :param headless: 是否使用无头模式
        :param user_data_dir: Chrome用户数据目录路径
        :return: WebDriver实例
        """
        options = webdriver.ChromeOptions()

        # 添加用户数据目录以保持登录状态
        if user_data_dir and os.path.exists(user_data_dir):
            options.add_argument(f'--user-data-dir={user_data_dir}')
            options.add_argument('--profile-directory=Default')
            print(f"已加载Chrome用户数据目录: {user_data_dir}")

        if headless:
            options.add_argument('--headless=new')  # 使用新的headless模式

        # 基本参数
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

        # 增强的反检测参数
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # 禁用图片加载，提高速度
        # 注意：不禁用JavaScript，因为1688需要JS来正常工作
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-background-networking')

        # 设置语言和地区
        options.add_argument('--lang=zh-CN')
        options.add_argument('--accept-lang=zh-CN,zh,en-US,en')

        # 禁用自动化检测
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # 设置更真实的浏览器首选项
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,  # 禁用通知
                "popups": 2,  # 禁用弹窗
                "media_stream": 2,  # 禁用媒体流
                "geolocation": 2,  # 禁用地理位置
            },
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 2,  # 禁用图片
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1
        }
        options.add_experimental_option("prefs", prefs)

        # 添加更真实的用户代理
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')

        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            # 增强的反检测JavaScript注入
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
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
            })

            # 设置额外的请求头
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
                ]),
                "acceptLanguage": "zh-CN,zh;q=0.9,en;q=0.8",
                "platform": "Win32"
            })

            return driver
        except Exception as e:
            logging.error(f"初始化WebDriver失败: {e}")
            raise
        return driver

    def get_random_delay(self, min_seconds: float = 2, max_seconds: float = 5) -> float:
        """获取随机延迟时间"""
        delay = random.uniform(min_seconds, max_seconds)
        print(f"等待 {delay:.2f} 秒...")
        time.sleep(delay)
        return delay

    def _load_cookies(self, cookie_file: str = "1688_cookies.json"):
        """
        加载保存的Cookie
        :param cookie_file: Cookie文件路径
        """
        try:
            import json
            if os.path.exists(cookie_file):
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                    for cookie in cookies:
                        try:
                            self.driver.add_cookie(cookie)
                        except Exception as e:
                            print(f"添加Cookie失败: {e}")
                print(f"已加载{len(cookies)}个Cookie")
                return True
            else:
                print("Cookie文件不存在")
                return False
        except Exception as e:
            print(f"加载Cookie失败: {e}")
            return False

    def _save_cookies(self, cookie_file: str = "1688_cookies.json"):
        """
        保存当前Cookie
        :param cookie_file: Cookie文件路径
        """
        try:
            import json
            cookies = self.driver.get_cookies()
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f"已保存{len(cookies)}个Cookie到{cookie_file}")
            return True
        except Exception as e:
            print(f"保存Cookie失败: {e}")
            return False

    def _try_direct_search_url(self, keyword: str) -> bool:
        """
        尝试直接构造搜索URL访问，绕过首页搜索
        :param keyword: 搜索关键词
        :return: 是否成功
        """
        try:
            import urllib.parse

            # URL编码关键词
            encoded_keyword = urllib.parse.quote(keyword, safe='')

            # 构造多种可能的搜索URL
            search_urls = [
                # 标准搜索URL
                f"{self.base_url}/s/offer_search.htm?keywords={encoded_keyword}",
                # 带更多参数的搜索URL
                f"{self.base_url}/s/offer_search.htm?keywords={encoded_keyword}&n=y&tab=offer",
                # 全球站搜索URL（如果是global.1688.com）
                f"{self.base_url}/product.htm?keywords={encoded_keyword}",
                # 备用搜索格式
                f"{self.base_url}/offer_search.htm?keywords={encoded_keyword}",
            ]

            for i, url in enumerate(search_urls, 1):
                try:
                    print(f"尝试直接访问搜索URL {i}/{len(search_urls)}: {url}")

                    # 先访问主页以设置基本的域名Cookie
                    if i == 1:  # 只在第一次尝试时访问主页
                        print("先访问主页设置基本Cookie...")
                        self.driver.get(self.base_url)
                        time.sleep(2)

                        # 尝试加载保存的Cookie
                        self._load_cookies()
                        time.sleep(1)

                    # 访问搜索URL
                    self.driver.get(url)
                    time.sleep(self.get_random_delay(3, 6))

                    # 检查是否成功到达搜索结果页面
                    current_url = self.driver.current_url.lower()
                    page_title = self.driver.title

                    print(f"当前URL: {current_url}")
                    print(f"页面标题: {page_title}")

                    # 检查是否被重定向到登录页面
                    if self._is_redirected_to_login():
                        print(f"❌ URL {i} 被重定向到登录页面")
                        continue

                    # 检查是否是有效的搜索结果页面
                    if self._is_search_results_page_enhanced(keyword):
                        print(f"✅ URL {i} 成功访问搜索结果页面")
                        # 保存成功的Cookie以备后用
                        self._save_cookies()
                        return True
                    else:
                        print(f"❌ URL {i} 不是有效的搜索结果页面")

                except Exception as e:
                    print(f"❌ URL {i} 访问失败: {e}")
                    continue

            print("所有直接搜索URL都失败")
            return False

        except Exception as e:
            print(f"直接搜索URL方法出错: {e}")
            return False

    def _is_redirected_to_login(self) -> bool:
        """
        检查是否被重定向到登录页面
        :return: True表示被重定向到登录页面
        """
        try:
            current_url = self.driver.current_url.lower()
            login_indicators = [
                'login.1688.com',
                'login.taobao.com',
                'login.alibaba.com',
                'auth.alibaba.com',
                'passport.1688.com',
                'passport.alibaba.com',
                '/member/signin',
                '/login',
                '/signin'
            ]

            for indicator in login_indicators:
                if indicator in current_url:
                    return True

            # 检查页面标题
            page_title = self.driver.title.lower()
            if any(word in page_title for word in ['登录', 'login', 'signin', '登陆']):
                return True

            return False

        except Exception:
            return False

    def _extract_products_from_search_page(self, keyword: str) -> list:
        """
        从搜索结果页面提取商品信息
        :param keyword: 搜索关键词
        :return: 商品列表
        """
        try:
            print("开始从搜索结果页面提取商品信息...")

            # 等待页面加载
            time.sleep(self.get_random_delay(2, 4))

            # 处理可能的弹窗
            self._handle_popups_on_search_page()

            # 滚动页面加载更多商品
            print("滚动页面加载更多商品...")
            self._scroll_page_enhanced()

            # 提取商品信息
            print("开始提取商品信息...")
            all_found_products = []

            print("\n===== 方式1: 使用标准选择器查找商品 =====")
            products_method1 = self._extract_products_method1()

            print("\n===== 方式2: 使用XPath查找商品 =====")
            products_method2 = self._extract_products_method2()

            print("\n===== 方式3: 使用JavaScript查找商品 =====")
            products_method3 = self._extract_products_method3()

            print("\n===== 方式4: 使用更宽泛的选择器查找商品 =====")
            products_method4 = self._extract_products_method4()

            print("\n===== 方式5: 使用数据属性查找商品 =====")
            products_method5 = self._extract_products_method5()

            # 合并所有找到的产品信息
            for method_num, method_products in enumerate([products_method1, products_method2, products_method3, products_method4, products_method5], 1):
                if method_products:
                    print(f"方式{method_num}找到了{len(method_products)}个商品")
                    all_found_products.extend(method_products)
                else:
                    print(f"方式{method_num}没有找到商品")

            # 去重和验证
            unique_products = []
            seen_titles = set()
            for product in all_found_products:
                title = product.get('title', '')
                # 验证商品信息的有效性
                if (title and
                    title not in seen_titles and
                    len(title.strip()) > 0 and
                    title != '未知商品' and
                    not any(keyword in title.lower() for keyword in ['登录', '注册', '首页', '导航'])):
                    seen_titles.add(title)
                    unique_products.append(product)

            print(f"\n总共找到{len(unique_products)}个有效唯一商品")

            # 显示前几个商品信息用于验证
            if unique_products:
                print("\n前3个商品预览：")
                for i, product in enumerate(unique_products[:3], 1):
                    print(f"  {i}. {product.get('title', '无标题')[:50]}...")
                    print(f"     价格: {product.get('price', '无价格')}")
                    print(f"     店铺: {product.get('shop', '无店铺')}")

            return unique_products

        except Exception as e:
            print(f"从搜索页面提取商品时出错: {e}")
            self._save_page_source("extract_error_page.html")
            return []

    def _handle_popups_on_search_page(self):
        """处理搜索结果页面的弹窗"""
        try:
            print("检查搜索结果页面是否有弹窗...")

            # 检测弹窗
            has_popup = self._detect_popups_silent()
            if has_popup:
                print("检测到弹窗，尝试关闭...")
                self._close_popups_enhanced_silent()
                time.sleep(1)
            else:
                print("未检测到弹窗")

        except Exception as e:
            print(f"处理搜索页面弹窗时出错: {e}")

    def search_products(self, keyword, pages=1):
        """
        搜索商品 - 改进的流程，优先使用直接URL访问
        :param keyword: 搜索关键词
        :param pages: 爬取页数
        :return: 商品列表，如果出错则返回空列表
        """
        print(f"\n开始爬取'{keyword}'商品信息...")
        all_products = []

        # 设置更真实的请求头
        self.driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)

        # 添加更真实的请求头
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        try:
            # 策略1: 直接构造搜索URL，绕过首页搜索
            if self._try_direct_search_url(keyword):
                print("✅ 直接URL搜索成功")
                # 跳过首页访问，直接进入商品提取流程
                return self._extract_products_from_search_page(keyword)

            # 策略2: 如果直接URL失败，尝试访问主页再搜索
            print("直接URL搜索失败，尝试传统搜索方式...")

            # 1. 访问主页（国内或国外）
            print(f"访问主页: {self.base_url}")
            self.driver.get(self.base_url)
            time.sleep(self.get_random_delay(3, 5))

            # 2. 等待主页加载完毕，判断是否有广告和弹窗
            print("等待主页加载完毕...")
            time.sleep(self.get_random_delay(2, 4))

            # 3. 检查是否需要登录
            if self.login_helper.is_login_page():
                print("检测到需要登录...")
                if not self.login_helper.handle_login():
                    logging.error("登录失败，请手动处理")
                    return all_products

            # 4. 自动检测弹窗和广告
            print("自动检测页面是否有广告和弹窗...")
            has_popup = self._detect_popups()

            if has_popup:
                print("检测到弹窗或广告，开始自动关闭...")
                self._close_popups_enhanced()
            else:
                # 询问用户是否有弹窗
                user_sees_popup = input("自动检测未发现弹窗。您是否看到页面上有弹窗或广告？(1=是, 0=否): ").strip()
                if user_sees_popup == '1':
                    print("用户确认有弹窗，开始关闭...")
                    self._close_popups_enhanced()
                else:
                    print("用户确认无弹窗，继续下一步...")

            # 5. 连续5次尝试关闭弹窗，简化用户交互
            popup_attempts = 0
            max_popup_attempts = 5

            while popup_attempts < max_popup_attempts:
                popup_attempts += 1
                print(f"第{popup_attempts}次清理弹窗...")

                # 检测是否有弹窗
                has_popup = self._detect_popups_silent()
                if not has_popup:
                    break

                # 尝试关闭弹窗
                self._close_popups_enhanced_silent()
                time.sleep(1)  # 等待页面响应

            # 5次尝试后询问用户
            print(f"已完成{popup_attempts}次弹窗清理尝试")
            user_response = input("弹窗是否清理成功？(0=否, 1=成功): ").strip()

            if user_response == '1':
                print("用户确认弹窗清理成功，继续下一步...")
            else:
                print("用户确认弹窗未清理成功")
                print("请手动关闭页面上的弹窗...")

                # 倒计时5秒
                for i in range(5, 0, -1):
                    print(f"倒计时 {i} 秒...")
                    time.sleep(1)

                # 询问是否进入主页面成功
                main_page_response = input("是否已成功进入主页面？(0=否, 1=成功): ").strip()

                if main_page_response == '1':
                    print("用户确认已成功进入主页面，继续下一步...")
                else:
                    print("用户确认未成功进入主页面，但继续执行...")

            # 6. 等待浏览器进入主页，确保主页加载完毕
            print("等待浏览器进入主页，确保主页加载完毕...")
            time.sleep(self.get_random_delay(2, 4))

            # 7. 在搜索框输入关键词并搜索
            print(f"在首页搜索框输入关键词: '{keyword}'")
            search_attempts = 0
            max_search_attempts = 5
            search_success = False

            while search_attempts < max_search_attempts and not search_success:
                search_attempts += 1
                print(f"搜索尝试 {search_attempts}/{max_search_attempts}")

                # 尝试执行搜索
                if self._perform_search_from_homepage(keyword):
                    # 询问用户搜索是否成功
                    user_response = input("搜索是否成功？(0=成功, 1=失败): ").strip()
                    if user_response == '0':
                        print("用户确认搜索成功")
                        search_success = True
                        break
                    else:
                        print("用户确认搜索失败，尝试其他方式...")
                else:
                    print("自动搜索失败，尝试其他方式...")

                if search_attempts >= max_search_attempts:
                    print("5次搜索尝试均失败，提醒用户手动搜索")
                    input(f"请手动在浏览器中搜索关键词 '{keyword}'，然后按 Enter 键继续...")
                    search_success = True  # 假设用户手动搜索成功
                    break

                time.sleep(1)

            # 8. 等待载入新的页面（搜索结果页面）
            print("等待搜索结果页面加载完毕...")
            time.sleep(self.get_random_delay(3, 5))

            # 9. 智能检测和用户确认搜索结果页面
            current_url = self.driver.current_url.lower()
            page_title = self.driver.title

            print(f"当前页面URL: {current_url}")
            print(f"当前页面标题: {page_title}")

            # 自动检测是否是搜索结果页面
            is_search_results = self._is_search_results_page_enhanced(keyword)

            if is_search_results:
                print("✅ 自动检测：当前已在搜索结果页面")
                is_search_page = '0'  # 自动确认
            else:
                print("❌ 自动检测：当前不在搜索结果页面")
                print("页面特征分析：")
                if "1688.com" in current_url and ("offer_search" not in current_url and "search" not in current_url):
                    print("  - 这似乎是1688主页或其他页面")
                if keyword.lower() not in current_url.lower() and keyword.lower() not in page_title.lower():
                    print(f"  - 页面URL和标题都不包含关键词 '{keyword}'")

                is_search_page = input("请确认当前是否是搜索结果页面？(0=是, 1=否): ").strip()

            if is_search_page == '0':
                print("✅ 确认已在搜索结果页面")
                # 保存当前页面的HTML用来判断页面元素
                self._save_page_source(f"search_results_page_{keyword}.html")
                print(f"已保存页面HTML: search_results_page_{keyword}.html")
            else:
                print("❌ 确认不在搜索结果页面，需要手动搜索")
                input(f"请手动搜索关键词 '{keyword}' 并进入搜索结果页面，然后按 Enter 键继续...")
                # 再次保存页面
                self._save_page_source(f"manual_search_results_page_{keyword}.html")

                # 再次检测
                if self._is_search_results_page_enhanced(keyword):
                    print("✅ 手动搜索后检测到搜索结果页面")
                else:
                    print("⚠️  警告：手动搜索后仍未检测到搜索结果页面特征")

            # 10. 滚动页面加载更多商品（仅在搜索结果页面）
            if is_search_page == '0':
                print("滚动页面加载更多商品...")
                self._scroll_page_enhanced()
            else:
                print("⚠️  跳过滚动：当前不在搜索结果页面")

            # 11. 提取商品信息（仅在搜索结果页面）
            if is_search_page == '0':
                print("开始提取商品信息...")
                all_found_products = []

                print("\n===== 方式1: 使用标准选择器查找商品 =====")
                products_method1 = self._extract_products_method1()

                print("\n===== 方式2: 使用XPath查找商品 =====")
                products_method2 = self._extract_products_method2()

                print("\n===== 方式3: 使用JavaScript查找商品 =====")
                products_method3 = self._extract_products_method3()

                print("\n===== 方式4: 使用更宽泛的选择器查找商品 =====")
                products_method4 = self._extract_products_method4()

                print("\n===== 方式5: 使用数据属性查找商品 =====")
                products_method5 = self._extract_products_method5()

                # 合并所有找到的产品信息
                for method_num, method_products in enumerate([products_method1, products_method2, products_method3, products_method4, products_method5], 1):
                    if method_products:
                        print(f"方式{method_num}找到了{len(method_products)}个商品")
                        all_found_products.extend(method_products)
                    else:
                        print(f"方式{method_num}没有找到商品")

                # 去重和验证
                unique_products = []
                seen_titles = set()
                for product in all_found_products:
                    title = product.get('title', '')
                    # 验证商品信息的有效性
                    if (title and
                        title not in seen_titles and
                        len(title.strip()) > 0 and
                        title != '未知商品' and
                        not any(keyword in title.lower() for keyword in ['登录', '注册', '首页', '导航'])):
                        seen_titles.add(title)
                        unique_products.append(product)

                print(f"\n总共找到{len(unique_products)}个有效唯一商品")

                # 显示前几个商品信息用于验证
                if unique_products:
                    print("\n前3个商品预览：")
                    for i, product in enumerate(unique_products[:3], 1):
                        print(f"  {i}. {product.get('title', '无标题')[:50]}...")
                        print(f"     价格: {product.get('price', '无价格')}")
                        print(f"     店铺: {product.get('shop', '无店铺')}")

                all_products.extend(unique_products)

                # 12. 点击商品列表的第一个商品
                if unique_products:
                    print("\n尝试点击第一个商品...")
                    self._click_first_product_improved()
                else:
                    print("❌ 未找到有效商品，无法点击")
                    print("可能原因：")
                    print("  1. 当前页面不是真正的搜索结果页面")
                    print("  2. 页面结构发生了变化")
                    print("  3. 需要登录或处理验证码")
            else:
                print("⚠️  跳过商品提取：当前不在搜索结果页面")
                print("请确保已正确进入商品搜索结果页面")

            return all_products

        except Exception as e:
            logging.error(f"搜索商品时出错: {e}")
            self._save_page_source("error_page.html")
            return all_products

    def _detect_popups(self) -> bool:
        """
        增强的弹窗检测，包括iframe检测和更详细的调试信息
        :return: True表示检测到弹窗，False表示未检测到
        """
        try:
            print("开始增强弹窗检测...")

            # 保存页面源码用于调试
            self._save_page_source("popup_detection_debug.html")
            print("已保存页面源码用于调试: popup_detection_debug.html")

            # 1. 检测iframe中的弹窗
            print("检测iframe中的弹窗...")
            iframe_popup_found = self._detect_iframe_popups()
            if iframe_popup_found:
                print("在iframe中检测到弹窗")
                return True

            # 2. 增强的弹窗选择器列表
            popup_selectors = [
                # AiBUY弹窗专门检测 - 更全面的选择器
                "div:contains('1688AiBUY')",
                "div:contains('1688 AiBUY')",
                "div:contains('AiBUY')",
                "div:contains('官方跨境采购助手')",
                "div:contains('官方跨境采购助手来了')",
                "div:contains('立即下载')",
                "div:contains('汇聚转化')",
                "div:contains('跨境同款')",
                "div[class*='aibuy']",
                "div[id*='aibuy']",
                "div[class*='download']",
                "div[id*='download']",
                # 通过样式特征检测弹窗
                "div[style*='position: fixed'][style*='z-index']",
                "div[style*='position: absolute'][style*='z-index']",
                "div[style*='position: fixed'][style*='top']",
                # 通用弹窗检测
                "div.login-dialog-wrap",
                "div.next-dialog-wrapper",
                ".next-dialog-close",
                ".overlay", ".modal", ".popup", ".dialog",
                "div[class*='dialog']",
                "div[class*='modal']",
                "div[class*='popup']",
                "div[class*='ad']",
                "div[class*='advertisement']",
                ".nc_iconfont.btn_slide",  # 验证码
                ".nc-lang-cnt",
                # 更多可能的弹窗容器
                "div[role='dialog']",
                "div[role='alertdialog']",
                "div[aria-modal='true']"
            ]

            popup_found = False
            for selector in popup_selectors:
                try:
                    # 处理包含文本的选择器
                    if ":contains(" in selector:
                        # 转换为XPath
                        text = selector.split(":contains('")[1].split("')")[0]
                        tag = selector.split(":contains(")[0]
                        xpath_selector = f"//{tag}[contains(text(), '{text}')]"
                        elements = self.driver.find_elements(By.XPATH, xpath_selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    visible_elements = [el for el in elements if el.is_displayed()]
                    if visible_elements:
                        print(f"检测到弹窗元素: {selector} (共{len(visible_elements)}个)")
                        popup_found = True

                        # 输出详细的元素信息用于调试
                        for i, el in enumerate(visible_elements[:3]):  # 最多显示3个元素的信息
                            try:
                                element_text = el.text.strip()[:100]  # 限制文本长度
                                element_class = el.get_attribute('class') or ''
                                element_id = el.get_attribute('id') or ''
                                element_style = el.get_attribute('style') or ''

                                print(f"  元素{i+1}:")
                                print(f"    文本: {element_text}")
                                print(f"    类名: {element_class}")
                                print(f"    ID: {element_id}")
                                print(f"    样式: {element_style[:100]}")

                                # 查找关闭按钮
                                close_buttons = el.find_elements(By.XPATH, ".//*[contains(@class, 'close') or contains(text(), '×') or contains(text(), 'X') or contains(@aria-label, 'close')]")
                                if close_buttons:
                                    print(f"    找到{len(close_buttons)}个可能的关闭按钮")
                                    for j, btn in enumerate(close_buttons[:2]):
                                        btn_text = btn.text.strip()
                                        btn_class = btn.get_attribute('class') or ''
                                        print(f"      关闭按钮{j+1}: 文本='{btn_text}', 类名='{btn_class}'")

                            except Exception as detail_error:
                                print(f"    获取元素详细信息时出错: {detail_error}")

                except Exception as e:
                    print(f"检测选择器 '{selector}' 时出错: {e}")
                    continue

            if not popup_found:
                print("未检测到明显的弹窗元素")

            return popup_found

        except Exception as e:
            print(f"检测弹窗时出错: {e}")
            return False

    def _detect_iframe_popups(self) -> bool:
        """
        检测iframe中的弹窗
        :return: True表示检测到iframe中的弹窗，False表示未检测到
        """
        try:
            print("开始检测iframe中的弹窗...")
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"找到{len(iframes)}个iframe")

            for i, iframe in enumerate(iframes):
                try:
                    print(f"检测iframe {i+1}/{len(iframes)}")

                    # 获取iframe信息
                    iframe_src = iframe.get_attribute('src') or ''
                    iframe_id = iframe.get_attribute('id') or ''
                    iframe_class = iframe.get_attribute('class') or ''

                    print(f"  iframe信息: src='{iframe_src[:50]}...', id='{iframe_id}', class='{iframe_class}'")

                    # 切换到iframe
                    self.driver.switch_to.frame(iframe)

                    # 在iframe中查找弹窗元素
                    iframe_popup_selectors = [
                        "div:contains('AiBUY')",
                        "div:contains('下载')",
                        "div:contains('采购助手')",
                        "div[class*='popup']",
                        "div[class*='modal']",
                        "div[class*='dialog']",
                        "div[style*='position: fixed']"
                    ]

                    for selector in iframe_popup_selectors:
                        try:
                            if ":contains(" in selector:
                                text = selector.split(":contains('")[1].split("')")[0]
                                tag = selector.split(":contains(")[0]
                                xpath_selector = f"//{tag}[contains(text(), '{text}')]"
                                elements = self.driver.find_elements(By.XPATH, xpath_selector)
                            else:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                            visible_elements = [el for el in elements if el.is_displayed()]
                            if visible_elements:
                                print(f"  在iframe中检测到弹窗: {selector} (共{len(visible_elements)}个)")
                                return True

                        except Exception as selector_error:
                            continue

                except Exception as iframe_error:
                    print(f"  检测iframe {i+1}时出错: {iframe_error}")
                finally:
                    # 切回主文档
                    self.driver.switch_to.default_content()

            print("未在iframe中检测到弹窗")
            return False

        except Exception as e:
            print(f"检测iframe弹窗时出错: {e}")
            # 确保切回主文档
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def _detect_popups_silent(self) -> bool:
        """
        静默的弹窗检测，不输出详细信息
        :return: True表示检测到弹窗，False表示未检测到
        """
        try:
            # 1. 检测iframe中的弹窗
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframes:
                try:
                    self.driver.switch_to.frame(iframe)
                    iframe_popup_selectors = [
                        "div:contains('AiBUY')",
                        "div:contains('下载')",
                        "div:contains('采购助手')",
                        "div[class*='popup']",
                        "div[class*='modal']",
                        "div[class*='dialog']",
                        "div[style*='position: fixed']"
                    ]

                    for selector in iframe_popup_selectors:
                        try:
                            if ":contains(" in selector:
                                text = selector.split(":contains('")[1].split("')")[0]
                                tag = selector.split(":contains(")[0]
                                xpath_selector = f"//{tag}[contains(text(), '{text}')]"
                                elements = self.driver.find_elements(By.XPATH, xpath_selector)
                            else:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                            visible_elements = [el for el in elements if el.is_displayed()]
                            if visible_elements:
                                return True
                        except Exception:
                            continue
                except Exception:
                    pass
                finally:
                    self.driver.switch_to.default_content()

            # 2. 主页面弹窗检测
            popup_selectors = [
                # AiBUY弹窗专门检测
                "div:contains('1688AiBUY')",
                "div:contains('1688 AiBUY')",
                "div:contains('AiBUY')",
                "div:contains('官方跨境采购助手')",
                "div:contains('官方跨境采购助手来了')",
                "div:contains('立即下载')",
                "div:contains('汇聚转化')",
                "div:contains('跨境同款')",
                "div[class*='aibuy']",
                "div[id*='aibuy']",
                "div[class*='download']",
                "div[id*='download']",
                # 通过样式特征检测弹窗
                "div[style*='position: fixed'][style*='z-index']",
                "div[style*='position: absolute'][style*='z-index']",
                "div[style*='position: fixed'][style*='top']",
                # 通用弹窗检测
                "div.login-dialog-wrap",
                "div.next-dialog-wrapper",
                ".next-dialog-close",
                ".overlay", ".modal", ".popup", ".dialog",
                "div[class*='dialog']",
                "div[class*='modal']",
                "div[class*='popup']",
                "div[role='dialog']",
                "div[role='alertdialog']",
                "div[aria-modal='true']"
            ]

            for selector in popup_selectors:
                try:
                    if ":contains(" in selector:
                        text = selector.split(":contains('")[1].split("')")[0]
                        tag = selector.split(":contains(")[0]
                        xpath_selector = f"//{tag}[contains(text(), '{text}')]"
                        elements = self.driver.find_elements(By.XPATH, xpath_selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    visible_elements = [el for el in elements if el.is_displayed()]
                    if visible_elements:
                        return True
                except Exception:
                    continue

            return False

        except Exception:
            return False

    def _close_popups_enhanced_silent(self) -> bool:
        """
        静默的弹窗关闭方法，不输出详细信息
        :return: True表示成功关闭，False表示失败
        """
        try:
            success = False

            # 方法1: 处理iframe中的弹窗
            if self._close_iframe_popups_silent():
                success = True

            # 方法2: 专门处理AiBUY弹窗
            if self._close_aibuy_popup_silent():
                success = True

            # 方法3: 点击关闭按钮
            if self._click_close_buttons_silent():
                success = True

            # 方法4: 尝试多种键盘操作
            if self._try_keyboard_close_silent():
                success = True

            # 方法5: 点击遮罩层关闭
            if self._click_overlay_to_close_silent():
                success = True

            # 方法6: JavaScript强制关闭
            if self._javascript_force_close_silent():
                success = True

            return success

        except Exception:
            return False

    def _close_iframe_popups_silent(self) -> bool:
        """静默关闭iframe中的弹窗"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframes:
                try:
                    self.driver.switch_to.frame(iframe)
                    close_selectors = [
                        "button:contains('×')",
                        "span:contains('×')",
                        "div:contains('×')",
                        ".close",
                        ".close-btn",
                        "[class*='close']",
                        "[aria-label*='close']"
                    ]

                    for selector in close_selectors:
                        try:
                            if ":contains(" in selector:
                                text = selector.split(":contains('")[1].split("')")[0]
                                tag = selector.split(":contains(")[0]
                                xpath_selector = f"//{tag}[contains(text(), '{text}')]"
                                elements = self.driver.find_elements(By.XPATH, xpath_selector)
                            else:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                            visible_elements = [el for el in elements if el.is_displayed() and el.is_enabled()]
                            if visible_elements:
                                self.driver.execute_script("arguments[0].click();", visible_elements[0])
                                time.sleep(1)
                                return True
                        except Exception:
                            continue
                except Exception:
                    pass
                finally:
                    self.driver.switch_to.default_content()
            return False
        except Exception:
            return False

    def _close_aibuy_popup_silent(self) -> bool:
        """静默处理AiBUY弹窗"""
        try:
            aibuy_texts = [
                '1688AiBUY', '1688 AiBUY', 'AiBUY',
                '官方跨境采购助手', '官方跨境采购助手来了',
                '立即下载', '汇聚转化', '跨境同款'
            ]

            for text in aibuy_texts:
                try:
                    xpath_selector = f"//*[contains(text(), '{text}')]"
                    elements = self.driver.find_elements(By.XPATH, xpath_selector)
                    for element in elements:
                        if element.is_displayed():
                            if self._find_and_click_close_in_container_silent(element):
                                return True
                except Exception:
                    continue

            # 通过样式特征查找
            style_selectors = [
                "div[style*='position: fixed'][style*='z-index']",
                "div[style*='position: absolute'][style*='z-index']",
                "div[style*='position: fixed'][style*='top']"
            ]

            for selector in style_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element_text = element.text.lower()
                            if any(keyword in element_text for keyword in ['aibuy', '下载', '采购助手', '跨境']):
                                if self._find_and_click_close_in_container_silent(element):
                                    return True
                except Exception:
                    continue

            return False
        except Exception:
            return False

    def _find_and_click_close_in_container_silent(self, container_element) -> bool:
        """静默在容器元素中查找并点击关闭按钮"""
        try:
            close_selectors = [
                ".//*[contains(@class, 'close')]",
                ".//*[contains(text(), '×')]",
                ".//*[contains(text(), 'X')]",
                ".//*[contains(@aria-label, 'close')]",
                ".//*[contains(@title, 'close')]",
                ".//*[contains(@title, '关闭')]",
                ".//button[contains(@class, 'close')]",
                ".//span[contains(@class, 'close')]",
                ".//i[contains(@class, 'close')]"
            ]

            for selector in close_selectors:
                try:
                    close_buttons = container_element.find_elements(By.XPATH, selector)
                    visible_buttons = [btn for btn in close_buttons if btn.is_displayed() and btn.is_enabled()]
                    if visible_buttons:
                        if self._try_multiple_click_methods_silent(visible_buttons[0]):
                            return True
                except Exception:
                    continue

            # 向上查找父级容器
            current_element = container_element
            for level in range(5):
                try:
                    parent = current_element.find_element(By.XPATH, "..")
                    if parent and parent.tag_name != 'html':
                        current_element = parent
                        for selector in close_selectors:
                            try:
                                close_buttons = current_element.find_elements(By.XPATH, selector)
                                visible_buttons = [btn for btn in close_buttons if btn.is_displayed() and btn.is_enabled()]
                                if visible_buttons:
                                    if self._try_multiple_click_methods_silent(visible_buttons[0]):
                                        return True
                            except Exception:
                                continue
                    else:
                        break
                except Exception:
                    break

            # 尝试点击容器外部关闭
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                self.driver.execute_script("arguments[0].click();", body)
                time.sleep(1)
                return True
            except Exception:
                pass

            return False
        except Exception:
            return False

    def _try_multiple_click_methods_silent(self, element) -> bool:
        """静默尝试多种点击方法"""
        try:
            # JavaScript点击
            try:
                self.driver.execute_script("arguments[0].click();", element)
                time.sleep(1)
                return True
            except Exception:
                pass

            # 普通点击
            try:
                element.click()
                time.sleep(1)
                return True
            except Exception:
                pass

            # ActionChains点击
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).click(element).perform()
                time.sleep(1)
                return True
            except Exception:
                pass

            return False
        except Exception:
            return False

    def _click_close_buttons_silent(self) -> bool:
        """静默点击关闭按钮"""
        try:
            close_selectors = [
                "div[class*='aibuy'] .close",
                "div[class*='aibuy'] .close-btn",
                "div[class*='aibuy'] [class*='close']",
                "div[class*='download'] .close",
                "div[class*='download'] .close-btn",
                "div[class*='download'] [class*='close']",
                "div.login-dialog-wrap i.next-icon-close",
                ".next-dialog-close",
                "button[aria-label*='close' i]",
                "button[title*='close' i]",
                "button[title*='关闭']",
                "i[class*='icon-close']",
                "i[class*='close']",
                "span[class*='icon-close']",
                "span[class*='close']",
                ".close-btn",
                ".close",
                "div[class*='close']",
                "a[class*='close']",
                "[data-dismiss='modal']",
                "[data-dismiss='dialog']",
                "button:contains('×')",
                "span:contains('×')",
                "div:contains('×')",
                "i:contains('×')",
                "a:contains('×')",
                "img[src*='close']",
                "img[alt*='close']",
                "img[alt*='关闭']",
                "[role='button'][aria-label*='close']",
                "button[class*='modal-close']",
                "button[class*='popup-close']"
            ]

            for selector in close_selectors:
                try:
                    if ":contains(" in selector:
                        text = selector.split(":contains('")[1].split("')")[0]
                        tag = selector.split(":contains(")[0]
                        xpath_selector = f"//{tag}[contains(text(), '{text}')]"
                        elements = self.driver.find_elements(By.XPATH, xpath_selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    visible_elements = [el for el in elements if el.is_displayed() and el.is_enabled()]
                    if visible_elements:
                        if self._try_multiple_click_methods_silent(visible_elements[0]):
                            return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def _try_keyboard_close_silent(self) -> bool:
        """静默尝试键盘操作关闭弹窗"""
        try:
            from selenium.webdriver.common.keys import Keys
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ESCAPE)
            time.sleep(1)
            body.send_keys(Keys.ENTER)
            time.sleep(1)
            body.send_keys(Keys.SPACE)
            time.sleep(1)
            return True
        except Exception:
            return False

    def _click_overlay_to_close_silent(self) -> bool:
        """静默点击遮罩层关闭弹窗"""
        try:
            overlay_selectors = [
                ".overlay",
                ".modal-backdrop",
                ".popup-overlay",
                ".dialog-overlay",
                "div[style*='position: fixed'][style*='background']",
                "div[style*='position: absolute'][style*='background']"
            ]

            for selector in overlay_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [el for el in elements if el.is_displayed()]
                    if visible_elements:
                        self.driver.execute_script("arguments[0].click();", visible_elements[0])
                        time.sleep(1)
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def _javascript_force_close_silent(self) -> bool:
        """静默使用JavaScript强制关闭弹窗"""
        try:
            js_code = """
            var fixedElements = document.querySelectorAll('div[style*="position: fixed"], div[style*="position: absolute"]');
            var removed = 0;
            fixedElements.forEach(function(el) {
                var style = window.getComputedStyle(el);
                var zIndex = parseInt(style.zIndex);
                if (zIndex > 100) {
                    el.style.display = 'none';
                    removed++;
                }
            });

            var textElements = document.querySelectorAll('*');
            textElements.forEach(function(el) {
                var text = el.textContent || '';
                if (text.includes('AiBUY') || text.includes('下载') || text.includes('采购助手')) {
                    var parent = el.parentElement;
                    while (parent && parent !== document.body) {
                        var style = window.getComputedStyle(parent);
                        if (style.position === 'fixed' || style.position === 'absolute') {
                            parent.style.display = 'none';
                            removed++;
                            break;
                        }
                        parent = parent.parentElement;
                    }
                }
            });

            var overlays = document.querySelectorAll('.overlay, .modal-backdrop, .popup-overlay');
            overlays.forEach(function(el) {
                el.style.display = 'none';
                removed++;
            });

            return removed;
            """

            removed_count = self.driver.execute_script(js_code)
            if removed_count > 0:
                time.sleep(1)
                return True
            return False
        except Exception:
            return False

    def _close_popups_enhanced(self) -> bool:
        """
        增强的弹窗关闭方法，包括多种关闭策略和iframe处理
        :return: True表示成功关闭，False表示失败
        """
        try:
            print("开始增强弹窗关闭流程...")
            success = False

            # 保存关闭前的页面状态
            self._save_page_source("before_close_popup.html")
            print("已保存关闭前页面状态")

            # 方法1: 处理iframe中的弹窗
            print("方法1: 尝试处理iframe中的弹窗...")
            if self._close_iframe_popups():
                print("iframe弹窗关闭成功")
                success = True

            # 方法2: 专门处理AiBUY弹窗
            print("方法2: 尝试专门处理AiBUY弹窗...")
            if self._close_aibuy_popup_enhanced():
                print("AiBUY弹窗关闭成功")
                success = True

            # 方法3: 点击关闭按钮
            print("方法3: 尝试点击关闭按钮...")
            if self._click_close_buttons_enhanced():
                print("点击关闭按钮成功")
                success = True

            # 方法4: 尝试多种键盘操作
            print("方法4: 尝试键盘操作...")
            if self._try_keyboard_close():
                print("键盘操作关闭成功")
                success = True

            # 方法5: 点击遮罩层关闭
            print("方法5: 尝试点击遮罩层关闭...")
            if self._click_overlay_to_close():
                print("点击遮罩层关闭成功")
                success = True

            # 方法6: JavaScript强制关闭
            print("方法6: 尝试JavaScript强制关闭...")
            if self._javascript_force_close():
                print("JavaScript强制关闭成功")
                success = True

            # 保存关闭后的页面状态
            self._save_page_source("after_close_popup.html")
            print("已保存关闭后页面状态")

            return success

        except Exception as e:
            print(f"增强弹窗关闭失败: {e}")
            return False

    def _close_iframe_popups(self) -> bool:
        """
        关闭iframe中的弹窗
        :return: True表示成功关闭，False表示失败
        """
        try:
            print("开始关闭iframe中的弹窗...")
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')

            for i, iframe in enumerate(iframes):
                try:
                    print(f"处理iframe {i+1}/{len(iframes)}")
                    self.driver.switch_to.frame(iframe)

                    # 在iframe中查找并点击关闭按钮
                    close_selectors = [
                        "button:contains('×')",
                        "span:contains('×')",
                        "div:contains('×')",
                        ".close",
                        ".close-btn",
                        "[class*='close']",
                        "[aria-label*='close']"
                    ]

                    for selector in close_selectors:
                        try:
                            if ":contains(" in selector:
                                text = selector.split(":contains('")[1].split("')")[0]
                                tag = selector.split(":contains(")[0]
                                xpath_selector = f"//{tag}[contains(text(), '{text}')]"
                                elements = self.driver.find_elements(By.XPATH, xpath_selector)
                            else:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                            visible_elements = [el for el in elements if el.is_displayed() and el.is_enabled()]
                            if visible_elements:
                                print(f"  在iframe中找到关闭按钮: {selector}")
                                self.driver.execute_script("arguments[0].click();", visible_elements[0])
                                time.sleep(1)
                                return True

                        except Exception:
                            continue

                except Exception as iframe_error:
                    print(f"  处理iframe {i+1}时出错: {iframe_error}")
                finally:
                    self.driver.switch_to.default_content()

            return False

        except Exception as e:
            print(f"关闭iframe弹窗时出错: {e}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def _try_keyboard_close(self) -> bool:
        """
        尝试多种键盘操作关闭弹窗
        :return: True表示成功，False表示失败
        """
        try:
            from selenium.webdriver.common.keys import Keys
            body = self.driver.find_element(By.TAG_NAME, "body")

            # 尝试ESC键
            print("  尝试ESC键...")
            body.send_keys(Keys.ESCAPE)
            time.sleep(1)

            # 尝试Enter键
            print("  尝试Enter键...")
            body.send_keys(Keys.ENTER)
            time.sleep(1)

            # 尝试空格键
            print("  尝试空格键...")
            body.send_keys(Keys.SPACE)
            time.sleep(1)

            return True

        except Exception as e:
            print(f"  键盘操作失败: {e}")
            return False

    def _click_overlay_to_close(self) -> bool:
        """
        点击遮罩层关闭弹窗
        :return: True表示成功，False表示失败
        """
        try:
            overlay_selectors = [
                ".overlay",
                ".modal-backdrop",
                ".popup-overlay",
                ".dialog-overlay",
                "div[style*='position: fixed'][style*='background']",
                "div[style*='position: absolute'][style*='background']"
            ]

            for selector in overlay_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [el for el in elements if el.is_displayed()]

                    if visible_elements:
                        print(f"  找到遮罩层: {selector}")
                        # 点击遮罩层的边缘区域
                        self.driver.execute_script("arguments[0].click();", visible_elements[0])
                        time.sleep(1)
                        return True

                except Exception:
                    continue

            return False

        except Exception as e:
            print(f"  点击遮罩层失败: {e}")
            return False

    def _javascript_force_close(self) -> bool:
        """
        使用JavaScript强制关闭弹窗
        :return: True表示成功，False表示失败
        """
        try:
            # JavaScript代码来强制关闭各种弹窗
            js_code = """
            // 移除所有固定定位的元素（可能是弹窗）
            var fixedElements = document.querySelectorAll('div[style*="position: fixed"], div[style*="position: absolute"]');
            var removed = 0;
            fixedElements.forEach(function(el) {
                var style = window.getComputedStyle(el);
                var zIndex = parseInt(style.zIndex);
                if (zIndex > 100) {  // 高z-index通常是弹窗
                    el.style.display = 'none';
                    removed++;
                }
            });

            // 移除包含特定文本的元素
            var textElements = document.querySelectorAll('*');
            textElements.forEach(function(el) {
                var text = el.textContent || '';
                if (text.includes('AiBUY') || text.includes('下载') || text.includes('采购助手')) {
                    var parent = el.parentElement;
                    while (parent && parent !== document.body) {
                        var style = window.getComputedStyle(parent);
                        if (style.position === 'fixed' || style.position === 'absolute') {
                            parent.style.display = 'none';
                            removed++;
                            break;
                        }
                        parent = parent.parentElement;
                    }
                }
            });

            // 移除遮罩层
            var overlays = document.querySelectorAll('.overlay, .modal-backdrop, .popup-overlay');
            overlays.forEach(function(el) {
                el.style.display = 'none';
                removed++;
            });

            return removed;
            """

            removed_count = self.driver.execute_script(js_code)
            if removed_count > 0:
                print(f"  JavaScript强制移除了{removed_count}个可能的弹窗元素")
                time.sleep(1)
                return True
            else:
                print("  JavaScript未找到需要移除的弹窗元素")
                return False

        except Exception as e:
            print(f"  JavaScript强制关闭失败: {e}")
            return False

    def _close_aibuy_popup_enhanced(self) -> bool:
        """
        增强的AiBUY弹窗处理方法
        :return: True表示成功关闭，False表示失败
        """
        try:
            print("开始增强AiBUY弹窗处理...")

            # 1. 通过文本特征查找AiBUY弹窗
            aibuy_texts = [
                '1688AiBUY', '1688 AiBUY', 'AiBUY',
                '官方跨境采购助手', '官方跨境采购助手来了',
                '立即下载', '汇聚转化', '跨境同款'
            ]

            for text in aibuy_texts:
                try:
                    print(f"  查找包含文本 '{text}' 的元素...")
                    xpath_selector = f"//*[contains(text(), '{text}')]"
                    elements = self.driver.find_elements(By.XPATH, xpath_selector)

                    for element in elements:
                        if element.is_displayed():
                            print(f"  找到AiBUY弹窗元素，包含文本: {text}")

                            # 输出元素详细信息
                            try:
                                element_tag = element.tag_name
                                element_class = element.get_attribute('class') or ''
                                element_id = element.get_attribute('id') or ''
                                print(f"    元素标签: {element_tag}")
                                print(f"    元素类名: {element_class}")
                                print(f"    元素ID: {element_id}")
                            except:
                                pass

                            # 尝试多种方式找到关闭按钮
                            if self._find_and_click_close_in_container(element):
                                return True

                except Exception as e:
                    print(f"  处理AiBUY文本 '{text}' 时出错: {e}")
                    continue

            # 2. 通过样式特征查找AiBUY弹窗
            print("  通过样式特征查找AiBUY弹窗...")
            style_selectors = [
                "div[style*='position: fixed'][style*='z-index']",
                "div[style*='position: absolute'][style*='z-index']",
                "div[style*='position: fixed'][style*='top']"
            ]

            for selector in style_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element_text = element.text.lower()
                            if any(keyword in element_text for keyword in ['aibuy', '下载', '采购助手', '跨境']):
                                print(f"  通过样式找到疑似AiBUY弹窗: {selector}")
                                print(f"    弹窗文本预览: {element_text[:100]}")

                                if self._find_and_click_close_in_container(element):
                                    return True

                except Exception as e:
                    print(f"  通过样式查找AiBUY弹窗时出错: {e}")
                    continue

            # 3. 通过类名和ID查找AiBUY弹窗
            print("  通过类名和ID查找AiBUY弹窗...")
            class_id_selectors = [
                "div[class*='aibuy']", "div[id*='aibuy']",
                "div[class*='download']", "div[id*='download']",
                "div[class*='popup']", "div[class*='modal']"
            ]

            for selector in class_id_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element_text = element.text.lower()
                            if any(keyword in element_text for keyword in ['aibuy', '下载', '采购助手']):
                                print(f"  通过类名/ID找到疑似AiBUY弹窗: {selector}")

                                if self._find_and_click_close_in_container(element):
                                    return True

                except Exception as e:
                    print(f"  通过类名/ID查找时出错: {e}")
                    continue

            print("  未找到AiBUY弹窗或无法关闭")
            return False

        except Exception as e:
            print(f"增强AiBUY弹窗处理时出错: {e}")
            return False

    def _find_and_click_close_in_container(self, container_element) -> bool:
        """
        在容器元素中查找并点击关闭按钮
        :param container_element: 容器元素
        :return: True表示成功点击关闭按钮，False表示失败
        """
        try:
            # 1. 在当前元素中查找关闭按钮
            close_selectors = [
                ".//*[contains(@class, 'close')]",
                ".//*[contains(text(), '×')]",
                ".//*[contains(text(), 'X')]",
                ".//*[contains(@aria-label, 'close')]",
                ".//*[contains(@title, 'close')]",
                ".//*[contains(@title, '关闭')]",
                ".//button[contains(@class, 'close')]",
                ".//span[contains(@class, 'close')]",
                ".//i[contains(@class, 'close')]"
            ]

            for selector in close_selectors:
                try:
                    close_buttons = container_element.find_elements(By.XPATH, selector)
                    visible_buttons = [btn for btn in close_buttons if btn.is_displayed() and btn.is_enabled()]

                    if visible_buttons:
                        print(f"    找到关闭按钮: {selector}")
                        for btn in visible_buttons:
                            try:
                                btn_text = btn.text.strip()
                                btn_class = btn.get_attribute('class') or ''
                                print(f"      按钮文本: '{btn_text}', 类名: '{btn_class}'")

                                # 尝试多种点击方式
                                if self._try_multiple_click_methods(btn):
                                    print(f"    成功点击关闭按钮")
                                    return True

                            except Exception as btn_error:
                                print(f"      点击按钮时出错: {btn_error}")
                                continue

                except Exception as selector_error:
                    continue

            # 2. 向上查找父级容器中的关闭按钮
            print("    在父级容器中查找关闭按钮...")
            current_element = container_element
            for level in range(5):  # 最多向上查找5级
                try:
                    parent = current_element.find_element(By.XPATH, "..")
                    if parent and parent.tag_name != 'html':
                        current_element = parent

                        # 在父级中查找关闭按钮
                        for selector in close_selectors:
                            try:
                                close_buttons = current_element.find_elements(By.XPATH, selector)
                                visible_buttons = [btn for btn in close_buttons if btn.is_displayed() and btn.is_enabled()]

                                if visible_buttons:
                                    print(f"    在父级{level+1}中找到关闭按钮: {selector}")
                                    if self._try_multiple_click_methods(visible_buttons[0]):
                                        return True

                            except Exception:
                                continue
                    else:
                        break

                except Exception:
                    break

            # 3. 尝试点击容器外部关闭
            print("    尝试点击容器外部关闭弹窗...")
            try:
                # 点击body元素
                body = self.driver.find_element(By.TAG_NAME, "body")
                self.driver.execute_script("arguments[0].click();", body)
                time.sleep(1)
                return True
            except Exception as e:
                print(f"    点击外部关闭失败: {e}")

            return False

        except Exception as e:
            print(f"    在容器中查找关闭按钮时出错: {e}")
            return False

    def _try_multiple_click_methods(self, element) -> bool:
        """
        尝试多种点击方法
        :param element: 要点击的元素
        :return: True表示成功点击，False表示失败
        """
        try:
            # 方法1: JavaScript点击
            try:
                self.driver.execute_script("arguments[0].click();", element)
                time.sleep(1)
                return True
            except Exception as e:
                print(f"      JavaScript点击失败: {e}")

            # 方法2: 普通点击
            try:
                element.click()
                time.sleep(1)
                return True
            except Exception as e:
                print(f"      普通点击失败: {e}")

            # 方法3: ActionChains点击
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).click(element).perform()
                time.sleep(1)
                return True
            except Exception as e:
                print(f"      ActionChains点击失败: {e}")

            return False

        except Exception as e:
            print(f"      多种点击方法都失败: {e}")
            return False

    def _click_close_buttons_enhanced(self) -> bool:
        """
        增强的关闭按钮点击方法
        :return: True表示成功点击，False表示失败
        """
        try:
            print("开始增强关闭按钮点击...")

            close_selectors = [
                # AiBUY弹窗专门选择器
                "div[class*='aibuy'] .close",
                "div[class*='aibuy'] .close-btn",
                "div[class*='aibuy'] [class*='close']",
                "div[class*='download'] .close",
                "div[class*='download'] .close-btn",
                "div[class*='download'] [class*='close']",
                # 高优先级通用关闭按钮
                "div.login-dialog-wrap i.next-icon-close",
                ".next-dialog-close",
                "button[aria-label*='close' i]",
                "button[title*='close' i]",
                "button[title*='关闭']",
                # 图标类关闭按钮
                "i[class*='icon-close']",
                "i[class*='close']",
                "span[class*='icon-close']",
                "span[class*='close']",
                # 通用关闭按钮
                ".close-btn",
                ".close",
                "div[class*='close']",
                "a[class*='close']",
                "[data-dismiss='modal']",
                "[data-dismiss='dialog']",
                # X符号按钮
                "button:contains('×')",
                "span:contains('×')",
                "div:contains('×')",
                "i:contains('×')",
                "a:contains('×')",
                # 图片形式的关闭按钮
                "img[src*='close']",
                "img[alt*='close']",
                "img[alt*='关闭']",
                # 更多可能的关闭按钮
                "[role='button'][aria-label*='close']",
                "button[class*='modal-close']",
                "button[class*='popup-close']"
            ]

            success_count = 0
            for selector in close_selectors:
                try:
                    print(f"  尝试选择器: {selector}")

                    # 处理包含文本的选择器
                    if ":contains(" in selector:
                        text = selector.split(":contains('")[1].split("')")[0]
                        tag = selector.split(":contains(")[0]
                        xpath_selector = f"//{tag}[contains(text(), '{text}')]"
                        elements = self.driver.find_elements(By.XPATH, xpath_selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    visible_elements = [el for el in elements if el.is_displayed() and el.is_enabled()]

                    if visible_elements:
                        print(f"    找到{len(visible_elements)}个可见的关闭按钮")

                        for i, element in enumerate(visible_elements):
                            try:
                                # 获取元素信息
                                element_text = element.text.strip()
                                element_class = element.get_attribute('class') or ''
                                element_tag = element.tag_name

                                print(f"    按钮{i+1}: 标签={element_tag}, 文本='{element_text}', 类名='{element_class[:50]}'")

                                # 尝试多种点击方法
                                if self._try_multiple_click_methods(element):
                                    print(f"    成功点击关闭按钮: {selector}")
                                    success_count += 1

                                    # 等待一下看是否关闭成功
                                    time.sleep(1)

                                    # 验证是否成功关闭
                                    try:
                                        if not element.is_displayed():
                                            print(f"    验证：弹窗已关闭")
                                            return True
                                    except:
                                        # 元素可能已被移除，认为关闭成功
                                        print(f"    验证：弹窗元素已移除")
                                        return True

                            except Exception as element_error:
                                print(f"    处理按钮{i+1}时出错: {element_error}")
                                continue

                except Exception as selector_error:
                    print(f"  选择器 '{selector}' 处理出错: {selector_error}")
                    continue

            if success_count > 0:
                print(f"  总共成功点击了{success_count}个关闭按钮")
                return True
            else:
                print("  未找到可点击的关闭按钮")
                return False

        except Exception as e:
            print(f"增强关闭按钮点击失败: {e}")
            return False

    def _click_first_product_improved(self) -> bool:
        """
        改进的点击第一个商品方法，避免点击到收藏按钮
        :return: True表示成功点击，False表示失败
        """
        try:
            print("开始寻找第一个商品进行点击...")

            # 商品选择器列表（按优先级排序）
            product_selectors = [
                "div[data-h5-type='offerCard'] a[href*='offer']",  # 商品链接
                "div[data-h5-type='offerCard'] .title a",  # 标题链接
                "div[data-h5-type='offerCard'] .offer-title a",  # 商品标题
                "div.offer-list-row-offer a[href*='offer']",  # 列表模式商品链接
                "div.offer-card a[href*='offer']",  # 卡片模式商品链接
                "div.J_offerCard a[href*='offer']",  # 旧版商品链接
                "div[class*='offer-item'] a[href*='offer']",  # 通用商品链接
                "div[class*='product'] a[href*='offer']",  # 产品链接
                "a[href*='detail.1688.com']",  # 详情页链接
                "a[href*='offer.1688.com']"   # 商品页链接
            ]

            for selector in product_selectors:
                try:
                    print(f"尝试选择器: {selector}")
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    # 过滤可见且可点击的元素
                    clickable_elements = []
                    for element in elements:
                        try:
                            if (element.is_displayed() and
                                element.is_enabled() and
                                element.get_attribute('href') and
                                'offer' in element.get_attribute('href')):

                                # 检查是否是收藏按钮或其他非商品链接
                                element_text = element.text.strip().lower()
                                element_class = element.get_attribute('class') or ''

                                # 排除收藏、购物车等按钮
                                if any(keyword in element_text for keyword in ['收藏', 'favorite', '购物车', 'cart', '立即购买', 'buy']):
                                    continue
                                if any(keyword in element_class for keyword in ['favorite', 'cart', 'buy', 'collect']):
                                    continue

                                clickable_elements.append(element)
                        except Exception:
                            continue

                    if clickable_elements:
                        # 点击第一个符合条件的商品
                        first_product = clickable_elements[0]
                        product_href = first_product.get_attribute('href')
                        product_text = first_product.text.strip()

                        print(f"找到第一个商品链接: {product_text[:50]}...")
                        print(f"商品URL: {product_href}")

                        # 使用JavaScript点击，避免被其他元素遮挡
                        self.driver.execute_script("arguments[0].click();", first_product)
                        print("成功点击第一个商品")

                        # 等待页面跳转
                        time.sleep(3)

                        # 验证是否成功跳转到商品详情页
                        current_url = self.driver.current_url
                        if 'detail.1688.com' in current_url or 'offer.1688.com' in current_url:
                            print(f"成功跳转到商品详情页: {current_url}")
                            return True
                        else:
                            print(f"点击后未跳转到预期页面，当前URL: {current_url}")
                            return False

                except Exception as e:
                    print(f"使用选择器 '{selector}' 时出错: {e}")
                    continue

            print("未找到可点击的商品链接")
            return False

        except Exception as e:
            print(f"点击第一个商品时出错: {e}")
            return False

    def _is_search_results_page_enhanced(self, keyword: str) -> bool:
        """
        增强的搜索结果页面检测
        :param keyword: 搜索关键词
        :return: True表示是搜索结果页面，False表示不是
        """
        try:
            current_url = self.driver.current_url.lower()
            page_title = self.driver.title.lower()

            print(f"页面检测 - URL: {current_url}")
            print(f"页面检测 - 标题: {page_title}")

            # 检查1：URL必须包含搜索相关路径
            search_url_patterns = [
                'offer_search.htm',
                'search/product.htm',
                '/s/offer_search',
                'search-result',
                'search.htm'
            ]

            has_search_url = any(pattern in current_url for pattern in search_url_patterns)
            print(f"URL搜索特征检测: {has_search_url}")

            # 检查2：URL或标题包含关键词
            has_keyword = keyword.lower() in current_url or keyword.lower() in page_title
            print(f"关键词匹配检测: {has_keyword}")

            # 检查3：页面包含商品列表特征元素
            product_indicators = [
                "div[data-h5-type='offerCard']",
                "div.offer-list-wrapper",
                "div.list-offer-items-wrapper",
                "ul.offerlist",
                "div.gallery-grid-container",
                "div.sm-offer-list",
                "div.offer-card-wrapper"
            ]

            has_product_elements = False
            for selector in product_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 0:
                        print(f"找到商品列表元素: {selector} ({len(elements)}个)")
                        has_product_elements = True
                        break
                except Exception:
                    continue

            print(f"商品列表元素检测: {has_product_elements}")

            # 检查4：页面不是主页
            is_not_homepage = not (
                current_url.endswith('1688.com/') or
                current_url.endswith('1688.com') or
                '阿里1688' in page_title or
                'alibaba.com' in page_title
            )
            print(f"非主页检测: {is_not_homepage}")

            # 综合判断
            is_search_page = has_search_url and has_keyword and has_product_elements and is_not_homepage

            print(f"最终判断结果: {is_search_page}")
            print(f"  - 搜索URL: {has_search_url}")
            print(f"  - 关键词匹配: {has_keyword}")
            print(f"  - 商品元素: {has_product_elements}")
            print(f"  - 非主页: {is_not_homepage}")

            return is_search_page

        except Exception as e:
            print(f"页面检测时出错: {e}")
            return False

    def _scroll_page_enhanced(self):
        """增强的页面滚动功能"""
        try:
            print("开始增强滚动页面以加载更多商品...")

            # 获取初始页面高度
            initial_height = self.driver.execute_script("return document.body.scrollHeight")
            print(f"初始页面高度: {initial_height}px")

            scroll_attempts = 0
            max_scroll_attempts = 5
            successful_scrolls = 0

            while scroll_attempts < max_scroll_attempts:
                scroll_attempts += 1
                print(f"滚动尝试 {scroll_attempts}/{max_scroll_attempts}")

                # 记录滚动前的高度
                before_scroll_height = self.driver.execute_script("return document.body.scrollHeight")

                # 滚动到页面底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                print(f"已滚动到页面底部")

                # 等待内容加载
                time.sleep(3)

                # 检查页面高度是否发生变化
                after_scroll_height = self.driver.execute_script("return document.body.scrollHeight")
                print(f"滚动前高度: {before_scroll_height}px, 滚动后高度: {after_scroll_height}px")

                if after_scroll_height > before_scroll_height:
                    successful_scrolls += 1
                    print(f"✅ 滚动成功，页面高度增加了 {after_scroll_height - before_scroll_height}px")
                else:
                    print("❌ 页面高度未变化，可能已加载完所有内容")
                    break

                # 尝试点击"加载更多"按钮
                try:
                    load_more_selectors = [
                        "button:contains('加载更多')",
                        "a:contains('加载更多')",
                        "div:contains('加载更多')",
                        ".load-more",
                        ".more-btn",
                        "[data-action='load-more']"
                    ]

                    for selector in load_more_selectors:
                        try:
                            if "contains" in selector:
                                # 使用XPath处理contains
                                xpath_selector = f"//*[contains(text(), '加载更多') or contains(text(), '更多') or contains(text(), 'more')]"
                                elements = self.driver.find_elements(By.XPATH, xpath_selector)
                            else:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                            visible_elements = [el for el in elements if el.is_displayed() and el.is_enabled()]
                            if visible_elements:
                                print(f"找到加载更多按钮: {selector}")
                                self.driver.execute_script("arguments[0].click();", visible_elements[0])
                                print("已点击加载更多按钮")
                                time.sleep(2)
                                break
                        except Exception:
                            continue
                except Exception as e:
                    print(f"尝试点击加载更多按钮时出错: {e}")

                # 短暂等待
                time.sleep(1)

            # 滚动回页面顶部
            self.driver.execute_script("window.scrollTo(0, 0);")
            print("已滚动回页面顶部")

            final_height = self.driver.execute_script("return document.body.scrollHeight")
            print(f"最终页面高度: {final_height}px")
            print(f"页面滚动完成，成功滚动 {successful_scrolls} 次")

            return successful_scrolls > 0

        except Exception as e:
            print(f"增强滚动时出错: {e}")
            return False

    def _go_to_next_page(self, page):
        """跳转到下一页"""
        try:
            next_page_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".fui-next"))
            )
            next_page_btn.click()
            return True
        except TimeoutException:
            return False

    def _check_captcha(self) -> bool:
        """
        检查是否有验证码、登录弹窗或广告弹窗，并尝试关闭它们
        :return: 如果检测到需要手动处理的情况（如验证码）返回True，否则返回False
        """
        try:
            print("开始检查页面是否有弹窗、广告或验证码...")
            # 1. 检查并关闭各种可能的弹窗 (多次尝试机制)
            popup_selectors_data = [
                ("1688登录弹窗主体", "div.login-dialog-wrap"), # 更具体的1688登录弹窗
                ("1688登录弹窗关闭按钮", "div.login-dialog-wrap i.next-icon-close"),
                ("1688登录弹窗旧版关闭", "div.login-dialog a.sufei-dialog-close"), # 旧版登录弹窗关闭
                ("通用Next弹窗", "div.next-dialog-wrapper div.next-dialog"),
                ("通用Next弹窗关闭按钮", "div.next-dialog-wrapper div.next-dialog .next-dialog-close"), # 匹配 <i> 或 <span>
                ("登录弹窗关闭", ".next-dialog-close"), # 保留泛用型
                ("通用弹窗关闭X", "div[class*='dialog'] span[class*='close']"),
                ("通用弹窗关闭X", "div[class*='modal'] span[class*='close']"),
                ("通用弹窗关闭X", "div[class*='popup'] span[class*='close']"),
                ("通用关闭按钮", "button[aria-label*='close' i]"),
                ("通用关闭图标", "i[class*='icon-close']"),
                ("惠买卖推广关闭", "div.bottom-image-ad span.close-btn"),
                ("首页新人弹窗关闭", "div.home-newcomer-popup-close"),
                ("活动弹窗关闭", "div[class*='promotion-dialog'] div[class*='close']"),
                ("调查问卷关闭", "div[class*='survey-dialog'] a[class*='close']"),
                # 保留原有的选择器，可在此处继续添加
                ("登录弹窗关闭", "div.login-blocks button.close"),
                ("登录弹窗关闭", "i.next-icon-close"),
                ("广告弹窗关闭", "div.dialog-close"),
                ("广告弹窗关闭", "div[class*='advert'] .close-btn"),
                ("广告弹窗关闭", "div[class*='ads-dialog'] .close"),
                ("广告弹窗关闭", "a[data-spm-click*='close']"), # 通用关闭链接
                ("新人福利弹窗", "div.rax-view-v2[style*='position: fixed'] div[style*='background-image']"), # 尝试更具体的选择器
                ("新人福利关闭按钮", "img[src*='close.png']"), # 如果有关闭图片
                ("可能的遮罩层关闭按钮", "div[class*='mask'] div[class*='close']")
            ]

            max_outer_loops = 3 # 最多进行3轮完整的pop-up清理尝试
            for loop_num in range(max_outer_loops):
                closed_in_this_loop = False
                print(f"进行第 {loop_num + 1}/{max_outer_loops} 轮通用弹窗检查...")
                for selector_type, selector in popup_selectors_data:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        visible_elements = [el for el in elements if el.is_displayed() and el.is_enabled()]

                        if not visible_elements:
                            continue

                        for element in visible_elements: # 通常只会有一个，但以防万一
                            print(f"检测到可见的 '{selector_type}' (选择器: {selector})，尝试关闭...")
                            self.driver.execute_script("arguments[0].click();", element)
                            time.sleep(1.5)  # 等待关闭动画和DOM变化
                            # 尝试验证是否关闭 (元素可能从DOM移除或不可见)
                            try:
                                if not element.is_displayed(): # 检查原引用是否不可见
                                    print(f"'{selector_type}' (选择器: {selector}) 点击后不再可见，可能已关闭。")
                                    closed_in_this_loop = True
                                else: # 如果元素还在且可见，尝试通过重新查找确认
                                    if not self.driver.find_elements(By.CSS_SELECTOR, selector): # 如果重新查找也找不到
                                        print(f"'{selector_type}' (选择器: {selector}) 点击后重新查找不到，确认已关闭。")
                                        closed_in_this_loop = True
                                    else:
                                        print(f"'{selector_type}' (选择器: {selector}) 点击后仍然存在。")
                            except StaleElementReferenceException:
                                print(f"'{selector_type}' (选择器: {selector}) 点击后元素已失效，确认已关闭。")
                                closed_in_this_loop = True

                            if closed_in_this_loop: # 如果关闭了一个，立即重新开始扫描所有popup_selectors
                                print(f"成功关闭一个 '{selector_type}'，将重新扫描所有通用弹窗。")
                                break # 跳出当前elements的循环
                    except Exception as e_inner:
                        print(f"在处理选择器 '{selector}' 时发生错误: {e_inner}")
                        continue

                    if closed_in_this_loop: # 如果内层break了 (因为关闭了弹窗)
                        break # 跳出popup_selectors的循环，开始新一轮的max_outer_loops

                if not closed_in_this_loop:
                    print("本轮未关闭任何新的通用弹窗。结束通用弹窗检查。")
                    break # 如果一整轮popup_selectors都没有关闭任何东西，则认为通用弹窗处理完毕
                # 如果 closed_in_this_loop 为 True，则外层循环会继续，进行下一轮检查

            # 2. 检查广告遮罩层并尝试关闭
            try:
                # 查找所有可能的遮罩层
                overlays = self.driver.find_elements(By.CSS_SELECTOR,
                    ".overlay, .modal, .popup, .dialog, .popover, .modal-dialog, .popup-dialog, "
                    ".popup-overlay, .modal-overlay, .popup-container, .modal-container, "
                    ".popup-wrapper, .modal-wrapper, .popup-content, .modal-content"
                )

                for overlay in overlays:
                    try:
                        if overlay.is_displayed():
                            print("检测到遮罩层，尝试点击关闭...")
                            # 尝试点击遮罩层外部关闭
                            self.driver.execute_script("arguments[0].click();", overlay)
                            time.sleep(0.5)

                            # 如果遮罩层还在，尝试按ESC键
                            if overlay.is_displayed():
                                from selenium.webdriver.common.keys import Keys
                                overlay.send_keys(Keys.ESCAPE)
                                time.sleep(0.5)
                    except:
                        continue
            except Exception as e:
                print(f"处理遮罩层时出错: {e}")

            # 3. 检查滑动验证码 (通常需要手动处理)
            captcha_selectors = [
                ".nc_iconfont.btn_slide",  # 滑动验证码
                ".nc-lang-cnt",  # 验证码容器
                ".nc_iconfont.btn_ok",  # 验证成功按钮
                ".btn_slide",  # 滑动按钮
                "#nc_1_wrapper",  # 验证码包装器
                "#nocaptcha",  # 无验证码验证
                ".nc-container",  # 验证码容器
                "#nc_1_n1z"  # 滑块
            ]

            for selector in captcha_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                visible_captcha_elements = [el for el in elements if el.is_displayed()]
                if visible_captcha_elements:
                    print(f"检测到可见的验证码相关元素: {selector}。这通常需要手动操作。")
                    self._save_page_source("captcha_detected.html")
                    return True # 表明需要手动干预

            # 3. 检查iframe中的验证码
            try:
                iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
                for iframe in iframes:
                    try:
                        self.driver.switch_to.frame(iframe)
                        # 检查iframe中是否有验证码
                        iframe_captcha_elements = self.driver.find_elements(By.CSS_SELECTOR, ".captcha, .geetest, .nc-container, .slider, .slide-verify")
                        visible_iframe_captcha = [el for el in iframe_captcha_elements if el.is_displayed()]
                        if visible_iframe_captcha:
                            print(f"检测到 iframe 内的可见验证码元素 ({[el.get_attribute('class') for el in visible_iframe_captcha]})。需要手动处理。")
                            self._save_page_source("iframe_captcha_detected.html")
                            return True # 表明需要手动干预
                    except:
                        pass
                    finally:
                        # 切回主文档
                        self.driver.switch_to.default_content()
            except Exception as e:
                print(f"检查iframe时出错: {e}")

            # 4. 检查登录弹窗
            login_modal_selectors = [
                ".login-dialog",
                ".J_LoginBox",
                ".login-container",
                ".login-wrap",
                ".login-dialog-container",
                ".login-box",
                ".login-modal",
                ".sign-flow",
                ".sign-flow-dialog",
                ".next-dialog",
                ".next-overlay-wrapper",
                ".sufei-dialog"
            ]

            for selector in login_modal_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                visible_login_modals = [el for el in elements if el.is_displayed()]
                if visible_login_modals:
                    print(f"检测到可见的登录弹窗: {selector}。")
                    # 尝试自动关闭的逻辑已移至前面的通用弹窗关闭部分
                    # 此处仅检测，如果通用关闭逻辑失败，则判定为需要手动处理
                    print("如果登录弹窗仍然存在且无法自动关闭，可能需要手动处理。")
                    self._save_page_source("login_modal_detected.html")
                    return True # 表明需要手动干预

            # 5. 检查页面是否重定向到登录页
            login_urls = [
                'login.1688.com',
                'login.taobao.com',
                'login.alibaba.com',
                'auth.alibaba.com',
                'passport.1688.com',
                'passport.alibaba.com',
                '/member/signin',
                '/login',
                '/signin',
                '/member/security'
            ]

            current_url = self.driver.current_url.lower()
            for url in login_urls:
                if url in current_url:
                    print(f"检测到页面已重定向到登录相关URL: {current_url}")
                    self._save_page_source("login_page_redirect_detected.html")
                    return True # 表明需要手动干预

            return False

        except Exception as e:
            error_msg = f"检查验证码时出错: {e}"
            print(error_msg)
            logging.error(error_msg, exc_info=True)
            # 保存当前页面用于调试
            self._save_page_source("captcha_error.html")
            return False

    def _perform_search_from_homepage(self, keyword: str) -> bool:
        """
        在1688首页上执行搜索操作
        :param keyword: 搜索关键词
        :return: 搜索操作是否成功
        """
        print(f"尝试在1688首页定位搜索框并搜索 '{keyword}'...")

        # 尝试多种方式定位搜索框
        search_box_selectors = [
            "input[name='keywords']",
            "input[placeholder*='搜索']",
            "input[placeholder*='Search']",
            "input.search-input",
            "input[type='search']",
            "input.next-input",
            ".search-box input",
            "#J_searchInput",
            "#q",  # 1688常用的搜索框ID
            ".search-bar input",
            ".mod-searchbar-main input", # 常见的1688搜索框
            "div.input-wrap input",
            "input.searchbar-input",
            "input.searchbar-keyword",
            "input[role='searchbox']"
        ]

        for attempt in range(5):  # 尝试5次不同的定位方式
            if attempt > 0:
                print(f"第{attempt+1}次尝试定位搜索框...")
                # 尝试不同的搜索方法，可能帮助定位更多元素
                self.driver.execute_script("window.scrollTo(0, 0);") # 滚动到页面顶部
                time.sleep(0.5)

            for selector in search_box_selectors:
                try:
                    print(f"尝试使用选择器: {selector}")
                    # 先尝试常规方式查找
                    search_boxes = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_search_boxes = [box for box in search_boxes if box.is_displayed() and box.is_enabled()]

                    if visible_search_boxes:
                        search_box = visible_search_boxes[0]
                        print(f"找到搜索框: {selector}")
                        # 清除可能的默认文本
                        search_box.clear()
                        # 输入搜索关键词
                        search_box.send_keys(keyword)
                        time.sleep(1)

                        # 尝试按Enter键提交
                        search_box.send_keys(Keys.ENTER)
                        print(f"已在搜索框中输入 '{keyword}' 并按Enter键")
                        time.sleep(3)  # 等待搜索结果加载

                        # 如果Enter键没有触发搜索，尝试点击搜索按钮
                        if "1688.com" in self.driver.current_url and "offer_search" not in self.driver.current_url:
                            search_button_selectors = [
                                "button.search-button",
                                ".search-box button",
                                "button[type='submit']",
                                ".search-bar button",
                                ".submit-btn",
                                ".search-submit",
                                ".mod-searchbar-action button", # 常见的1688搜索按钮
                                ".search-wrap .icon-btn",
                                "span.searchbar-submit",
                                "div.searchbar-action"
                            ]

                            for btn_selector in search_button_selectors:
                                try:
                                    buttons = self.driver.find_elements(By.CSS_SELECTOR, btn_selector)
                                    visible_buttons = [btn for btn in buttons if btn.is_displayed()]
                                    if visible_buttons:
                                        search_button = visible_buttons[0]
                                        search_button.click()
                                        print(f"点击了搜索按钮: {btn_selector}")
                                        time.sleep(3)  # 等待搜索结果加载
                                        break
                                except Exception as btn_err:
                                    print(f"尝试点击搜索按钮 '{btn_selector}' 时出错: {str(btn_err)}")
                                    continue

                        # 检查是否已导航到搜索结果页面
                        if "offer_search" in self.driver.current_url or "search/product" in self.driver.current_url:
                            print(f"成功导航到搜索结果页面: {self.driver.current_url}")
                            return True

                        print(f"执行搜索后当前URL: {self.driver.current_url}")
                        # 即使URL没有明确包含搜索标记，也返回成功，让后续验证逻辑判断
                        if keyword.lower() in self.driver.current_url.lower() or keyword.lower() in self.driver.title.lower():
                            print(f"URL或标题包含关键词'{keyword}'，认为搜索可能成功")
                            return True
                        return True
                except Exception as e:
                    print(f"尝试使用选择器 '{selector}' 定位搜索框时出错: {str(e)}")
                    continue

            # 如果当前尝试失败，等待一下再试
            time.sleep(1)

            # 尝试JavaScript方式定位搜索框
            if attempt == 3:
                try:
                    print("尝试使用JavaScript定位搜索框...")
                    # 通过JavaScript尝试定位常见搜索框
                    js_result = self.driver.execute_script("""
                    var inputs = document.querySelectorAll('input');
                    for(var i=0; i<inputs.length; i++) {
                        var input = inputs[i];
                        if(input.type === 'text' || input.type === 'search' || !input.type) {
                            if(input.offsetWidth > 0 && input.offsetHeight > 0) {
                                input.value = arguments[0];
                                return true;
                            }
                        }
                    }
                    return false;
                    """, keyword)

                    if js_result:
                        print("通过JavaScript成功定位并填充搜索框")
                        # 尝试触发表单提交
                        self.driver.execute_script("""
                        var forms = document.forms;
                        for(var i=0; i<forms.length; i++) {
                            var form = forms[i];
                            if(form.method && (form.method.toLowerCase() === 'get' || form.method.toLowerCase() === 'post')) {
                                form.submit();
                                return true;
                            }
                        }
                        return false;
                        """)
                        time.sleep(3)

                        # 检查是否已导航到搜索结果页面
                        if "offer_search" in self.driver.current_url or "search/product" in self.driver.current_url:
                            print(f"JavaScript方法成功导航到搜索结果页面: {self.driver.current_url}")
                            return True
                except Exception as js_err:
                    print(f"JavaScript方法定位搜索框时出错: {str(js_err)}")

        print("无法在首页找到并使用搜索框，已尝试5种不同方法")
        return False

    def _wait_for_element(self, selector: str, timeout: int = 15) -> bool:
        """等待元素出现"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except TimeoutException:
            print(f"等待元素超时: {selector}")
            return False

    def _find_products(self) -> list:
        """查找商品元素"""
        # 尝试多种选择器定位商品元素
        product_selectors = [
            "div[data-h5-type='offerCard']",  # 新版本1688
            "div[data-p4p-id]",  # 带商品ID的元素
            ".offer-list-row",
            ".J_offerCard",
            ".offer-card-wrapper",
            ".offer-card",
            "div[class*='offer']",
            "div[data-content*='product']",
            "div[class*='product']",
            "div[class*='item']",
            "div[data-spm*='offer']"
        ]

        for selector in product_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"使用选择器 '{selector}' 找到 {len(elements)} 个商品元素")
                    return elements
            except Exception as e:
                print(f"使用选择器 '{selector}' 时出错: {e}")

        print("未找到商品元素，请检查页面结构或选择器")
        return []

    def _extract_products(self) -> List[Dict]:
        """
        从当前页面提取商品信息
        在提取前会检查并处理登录弹窗
        """
        products = []

        try:
            # 等待页面加载完成
            time.sleep(3)  # 基础等待

            # 检查并处理登录弹窗和验证码，最多重试3次
            max_retries = 3
            retry_count = 0
            print("开始提取商品前的页面检查和处理流程...")
            while retry_count < max_retries:
                # _check_captcha会尝试关闭广告/弹窗，并检测验证码/登录页
                if self._check_captcha():
                    retry_count += 1
                    wait_time = 15 * retry_count  # 增加等待时间
                    print(f"页面检测到需要处理的情况（如广告、验证码、登录弹窗）。尝试次数 {retry_count}/{max_retries}。")
                    print(f"请检查浏览器，如果需要手动操作（例如：关闭无法自动处理的广告、完成滑块验证、登录），请在 {wait_time} 秒内完成。")
                    print(f"程序将在 {wait_time} 秒后自动继续尝试。")
                    time.sleep(wait_time)

                    if retry_count >= max_retries:
                        print(f"已达到最大尝试次数 ({max_retries})。")
                        user_choice = input("无法自动处理页面。请手动调整页面确保无遮挡和验证码，然后按 Enter键 尝试最后一次提取，或输入 'skip' 跳过当前页面的提取: ").strip().lower()
                        if user_choice == 'skip':
                            print("用户选择跳过当前页面的提取。")
                            self._save_page_source("page_extraction_skipped_by_user.html")
                            return []
                        else: # 用户按Enter，尝试最后一次检查和提取
                            print("尝试在用户手动操作后进行最后一次页面检查...")
                            if self._check_captcha(): # 再次检查
                                print("手动操作后仍检测到问题，无法提取当前页面。")
                                self._save_page_source("page_extraction_failed_after_manual.html")
                                return []
                            else:
                                print("手动操作后页面检查通过，尝试提取商品信息...")
                                break # 跳出重试循环，继续提取
                else:
                    print("页面检查通过，未检测到已知广告、验证码或登录弹窗阻碍。")
                    break # 没有检测到问题，退出重试循环
            else: # 循环正常结束 (未通过break，意味着retry_count >= max_retries 且最后一次检查仍有问题)
                if retry_count >= max_retries:
                     # 这种情况理论上会被内部的 if retry_count >= max_retries 捕获并返回
                     # 但为保险起见，如果流程走到这里，说明依然有问题
                    print("所有自动和手动辅助尝试后，页面仍存在问题，无法提取当前页面。")
                    self._save_page_source("page_extraction_failed_final_attempt.html")
                    return []

            # 保存页面源代码用于调试
            self._save_page_source("search_page.html")

            # 滚动页面以加载更多内容
            self._scroll_page()

            # 查找商品元素
            all_products = self._find_products()
            if not all_products:
                print("未找到商品元素，请检查页面结构或选择器")
                print("页面标题:", self.driver.title)
                print("当前URL:", self.driver.current_url)
                return []

            print(f"\n找到 {len(all_products)} 个商品")

            # 提取每个商品的信息
            max_products = min(10, len(all_products))  # 限制最多处理10个商品
            for idx, item in enumerate(all_products[:max_products], 1):
                try:
                    print(f"\n正在处理第 {idx}/{max_products} 个商品...")
                    product_info = self._extract_product_info(item)
                    if product_info:
                        products.append(product_info)
                        print(f"已提取: {product_info.get('title', '未知商品')}")
                        print(f"价格: {product_info.get('price', 'N/A')}")
                        print(f"店铺: {product_info.get('shop', 'N/A')}")
                except Exception as e:
                    print(f"提取商品信息时出错: {e}")
                    continue

            print(f"\n成功提取 {len(products)}/{max_products} 个商品信息")

        except Exception as e:
            error_msg = f"提取商品时发生错误: {str(e)}"
            print(error_msg)
            logging.error(error_msg, exc_info=True)
            self._save_page_source("error_page.html")

        print(f"提取结束，本页共提取到 {len(products)} 个商品。")
        return products

    def _is_search_results_page(self, keyword: str, is_subsequent_page: bool = False) -> bool:
        try:
            # 等待页面上出现一些表明是商品列表页的关键元素，增加等待时间
            WebDriverWait(self.driver, 10).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-h5-type='offerCard']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='offer-list']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul[class*='offerlist']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='gallery-grid-container']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.list-offer-items-wrapper"))
                )
            )
            print("检测到商品列表相关的容器元素，页面可能已加载。")
        except TimeoutException:
            current_url_for_debug = self.driver.current_url
            page_title_for_debug = self.driver.title
            print(f"超时：等待商品列表容器元素超时。URL: {current_url_for_debug}, Title: {page_title_for_debug}")
            if not is_subsequent_page: # 如果是首次加载搜索页，这通常意味着失败
                self._save_page_source(f"timeout_no_product_container_initial_{keyword}.html")
                return False
            # 对于后续页面，可能是最后一页无商品，允许继续其他检查
            print("后续页面未找到商品列表容器，可能为空页或最后一页。")

        """检查当前是否是目标关键词的搜索结果页面"""
        current_url = self.driver.current_url.lower()
        page_title = self.driver.title.lower()
        print(f"开始验证搜索结果页: URL='{current_url}', Title='{page_title}', Keyword='{keyword}'")

        # 检查URL是否包含搜索路径
        is_correct_path = ('offer_search.htm' in current_url or
                           'product.htm' in current_url or # global.1688.com
                           '/s/' in current_url) # 有时是 /s/offer_search.htm
        if not is_correct_path:
            print(f"URL路径不匹配: {current_url}")
            # 对于后续页面，如果路径改变，可能意味着离开搜索结果
            if is_subsequent_page: return False

        # 检查关键词是否在URL或标题中 (更宽松)
        keyword_present = keyword.lower() in current_url or keyword.lower() in page_title
        if not keyword_present:
            print(f"关键词 '{keyword}' 未在URL或标题中找到。")
            # 对于第一页，关键词必须存在。后续页面可能URL不直接含关键词，但标题应相关。
            if not is_subsequent_page: return False
            # 如果是后续页面，且标题也不含关键词，则很可能不是结果页
            if is_subsequent_page and keyword.lower() not in page_title:
                print("后续页面标题也不含关键词，判定为非结果页。")
                return False

        # 检查页面是否包含商品列表的典型元素
        product_list_selectors = [
            "div[data-h5-type='offerCard']", # 新版
            "div[class*='offer-list-wrapper']",
            "div[class*='list-offer-items-wrapper']",
            "ul[class*='offerlist']",
            ".offer-list-row",
            "div[class*='gallery-grid-container']", # global.1688.com
            "div[class*='app-offer']" # 另一个可能的容器
        ]
        product_list_found = False
        for selector in product_list_selectors:
            try:
                if self.driver.find_elements(By.CSS_SELECTOR, selector):
                    print(f"找到商品列表指示元素: '{selector}'")
                    product_list_found = True
                    break
            except Exception:
                pass # 忽略查找单个选择器的错误

        if not product_list_found:
            print("未找到明确的商品列表指示元素。")
            # 如果是第一页搜索，没有列表元素则基本判定失败
            # 后续页面可能因各种原因（如最后一页为空）没有列表，但URL和标题应仍指示是搜索场景
            if not is_subsequent_page: return False
            # 若是后续页，且URL和标题也弱相关，则判定失败
            if is_subsequent_page and not (is_correct_path and keyword_present):
                 return False

        final_verdict = (is_correct_path or is_subsequent_page) and keyword_present and product_list_found
        # 对于后续页面，如果路径和关键词仍在，但列表为空（可能是最后一页），也算通过
        if is_subsequent_page and (is_correct_path and keyword_present) and not product_list_found:
            print("后续页面，路径和关键词匹配但未找到商品列表元素，可能为空页或最后一页，暂时通过。")
            final_verdict = True

        print(f"搜索结果页验证结果: {final_verdict}")
        return final_verdict

    def _scroll_page(self):
        """滚动页面以加载所有内容"""
        print("开始滚动页面以加载更多商品...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 5  # 限制滚动次数，避免无限滚动

        while scroll_attempts < max_scroll_attempts:
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"滚动尝试 {scroll_attempts+1}/{max_scroll_attempts}")

            # 等待页面加载
            time.sleep(2)  # 增加等待时间，给页面更多加载时间

            # 计算新的滚动高度并与上一个滚动高度比较
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("页面高度未变化，可能已加载完所有内容")
                break
            last_height = new_height
            scroll_attempts += 1

            # 中间暂停一下，尝试点击“加载更多”按钮（如果有的话）
            try:
                load_more_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), '加载更多') or contains(text(), '显示更多') or contains(text(), '更多')]")
                visible_buttons = [btn for btn in load_more_buttons if btn.is_displayed() and btn.is_enabled()]

                if visible_buttons:
                    print("点击加载更多按钮...")
                    self.driver.execute_script("arguments[0].click();", visible_buttons[0])
                    time.sleep(2)  # 等待加载
            except Exception as e:
                print(f"尝试点击加载更多时出错: {e}")

        # 尝试在页面中间位置模拟鼠标移动，这可能会触发一些情况下的内容加载
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element_with_offset(self.driver.find_element(By.TAG_NAME, "body"), 50, 50)
            actions.perform()
            time.sleep(1)
        except Exception as e:
            print(f"模拟鼠标移动时出错: {e}")

        # 最后滚动回页面顶部
        self.driver.execute_script("window.scrollTo(0, 0);")
        print("页面滚动完成")

        # 等待所有内容完全加载
        time.sleep(2)

    def _extract_products_method1(self):
        """方式1: 使用标准CSS选择器查找商品"""
        products = []
        try:
            # 更新的标准选择器，增加更多可能的选择器
            selectors = [
                "div[data-h5-type='offerCard']",
                "div.offer-list-row-offer",
                "div.offer-card",
                "div.J_offerCard",
                "div.list-item",  # 新1688可能使用的选择器
                "div.sm-offer-item",
                "div.sm-offer-card",
                "div.card-container",
                "div.grid-offer-item",
                "div.grid-mode-offer",
                "div[class*='offer-item']",
                "div.item-info-container",
                "div.item-mod__item",
                "div[data-spm*='offer']"
            ]

            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"使用选择器 '{selector}' 找到 {len(elements)} 个商品")
                    for element in elements[:20]:  # 处理前20个，增加提取数量
                        product_info = self._extract_product_details_from_element(element)
                        if product_info:
                            products.append(product_info)
                    if products:  # 只有当成功提取到商品时才跳出
                        break

            # 如果上面的选择器都没找到商品，尝试一个更通用的方法
            if not products:
                print("尝试更通用的方法查找商品...")
                # 尝试找到所有包含商品相关文本的元素
                elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '元') or contains(text(), '￥')]")
                print(f"通过价格文本定位到 {len(elements)} 个可能的商品元素")

                for element in elements[:30]:  # 尝试更多元素
                    try:
                        # 尝试向上找到可能的商品容器
                        parent = element
                        for _ in range(3):  # 向上查找3层父元素
                            if parent:
                                parent = parent.find_element(By.XPATH, "..")
                                product_info = self._extract_product_details_from_element(parent)
                                if product_info:
                                    products.append(product_info)
                                    break
                    except:
                        continue
        except Exception as e:
            print(f"方式1提取商品时出错: {e}")

        return products

    def _extract_products_method2(self):
        """方式2: 使用XPath查找商品"""
        products = []
        try:
            # XPath选择器
            xpaths = [
                "//div[contains(@class, 'offer-card')]",
                "//div[contains(@class, 'product-card')]",
                "//div[contains(@class, 'item')]//a[contains(@href, 'offer')]",
                "//div[contains(@class, 'gallery')]//div[contains(@class, 'item')]"
            ]

            for xpath in xpaths:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements:
                    print(f"使用XPath '{xpath}' 找到 {len(elements)} 个商品")
                    for element in elements[:10]:  # 只处理前10个
                        product_info = self._extract_product_details_from_element(element)
                        if product_info:
                            products.append(product_info)
                    break
        except Exception as e:
            print(f"方式2提取商品时出错: {e}")

        return products

    def _extract_products_method3(self):
        """方式3: 使用JavaScript查找商品"""
        products = []
        try:
            # 使用JavaScript查找商品元素
            js_result = self.driver.execute_script("""
            var products = [];
            var elements = document.querySelectorAll('a[href*="offer"]');

            for(var i=0; i<Math.min(elements.length, 10); i++) {
                var el = elements[i];
                var priceEl = el.querySelector('*[class*="price"]') || el.querySelector('*[class*="Price"]');
                var titleEl = el.querySelector('*[class*="title"]') || el.querySelector('*[class*="Title"]');

                var product = {
                    title: titleEl ? titleEl.innerText.trim() : '',
                    price: priceEl ? priceEl.innerText.trim() : '',
                    link: el.href
                };

                if(product.title) {
                    products.push(product);
                }
            }

            return products;
            """)

            print(f"使用JavaScript找到 {len(js_result) if js_result else 0} 个商品")
            for item in js_result or []:
                product_info = {
                    'title': item.get('title', ''),
                    'price': item.get('price', ''),
                    'url': item.get('link', ''),
                    'source': '方式3: JavaScript'
                }
                if product_info['title']:
                    products.append(product_info)
        except Exception as e:
            print(f"方式3提取商品时出错: {e}")

        return products

    def _extract_products_method4(self):
        """方式4: 使用更宽泛的选择器查找商品"""
        products = []
        try:
            # 更宽泛的选择器
            selectors = [
                "div[class*='offer']",
                "div[class*='product']",
                "div[class*='item']",
                "a[href*='offer']"
            ]

            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"使用宽泛选择器 '{selector}' 找到 {len(elements)} 个潜在商品")
                    for element in elements[:20]:  # 尝试更多元素
                        # 进一步过滤，确保是商品卡片
                        if element.get_attribute('class') and ('card' in element.get_attribute('class') or 'item' in element.get_attribute('class')):
                            product_info = self._extract_product_details_from_element(element)
                            if product_info:
                                products.append(product_info)
                    if products:
                        break
        except Exception as e:
            print(f"方式4提取商品时出错: {e}")

        return products

    def _extract_products_method5(self):
        """方式5: 使用数据属性查找商品"""
        products = []
        try:
            # 使用数据属性查找
            selectors = [
                "div[data-p4p-id]",
                "div[data-offer-id]",
                "div[data-item-id]",
                "div[data-spm*='offer']",
                "div[data-tracking]"
            ]

            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"使用数据属性选择器 '{selector}' 找到 {len(elements)} 个商品")
                    for element in elements[:10]:
                        product_info = self._extract_product_details_from_element(element)
                        if product_info:
                            products.append(product_info)
                    if products:
                        break
        except Exception as e:
            print(f"方式5提取商品时出错: {e}")

        return products

    def _extract_product_details_from_element(self, element):
        """从元素中提取商品详细信息"""
        product_info = {
            'title': '',
            'price': '',
            'shop': '',
            'url': '',
            'source': '元素提取'
        }

        try:
            # 尝试查找标题
            title_selectors = [
                "*[class*='title']",
                "*[class*='name']",
                "span",
                "a",
                "div"
            ]

            for selector in title_selectors:
                try:
                    title_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for title_el in title_elements:
                        text = title_el.text.strip()
                        if text and len(text) > 5 and len(text) < 100:  # 合理的标题长度
                            product_info['title'] = text
                            break
                    if product_info['title']:
                        break
                except:
                    continue

            # 尝试查找价格
            price_selectors = [
                "*[class*='price']",
                "*[class*='Price']",
                "*[class*='money']",
                "*[class*='amount']"
            ]

            for selector in price_selectors:
                try:
                    price_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for price_el in price_elements:
                        text = price_el.text.strip()
                        if text and ('￥' in text or '$' in text or '¥' in text or '元' in text):
                            product_info['price'] = text
                            break
                    if product_info['price']:
                        break
                except:
                    continue

            # 尝试查找店铺名称
            shop_selectors = [
                "*[class*='shop']",
                "*[class*='store']",
                "*[class*='seller']",
                "*[class*='company']"
            ]

            for selector in shop_selectors:
                try:
                    shop_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for shop_el in shop_elements:
                        text = shop_el.text.strip()
                        if text and len(text) > 2 and len(text) < 50:  # 合理的店铺名长度
                            product_info['shop'] = text
                            break
                    if product_info['shop']:
                        break
                except:
                    continue

            # 尝试查找URL
            try:
                link_element = element.find_element(By.CSS_SELECTOR, "a[href*='detail']") or element.find_element(By.CSS_SELECTOR, "a")
                product_info['url'] = link_element.get_attribute('href')
            except:
                # 如果元素本身是链接
                if element.tag_name == 'a':
                    product_info['url'] = element.get_attribute('href')

                # 或者尝试从父元素中查找链接
                if not product_info['url']:
                    try:
                        parent = element.find_element(By.XPATH, "./..")
                        link_element = parent.find_element(By.CSS_SELECTOR, "a")
                        product_info['url'] = link_element.get_attribute('href')
                    except:
                        pass

            # 如果没有找到足够的信息，返回None
            if not product_info['title'] or not product_info['url']:
                return None

            return product_info
        except Exception as e:
            print(f"从元素中提取商品详细信息时出错: {e}")
            return None

    def _click_first_product(self):
        """尝试点击第一个可点击的商品"""
        try:
            # 重点找商品详情链接，而不是收藏或其他功能链接
            clickable_selectors = [
                "a[href*='detail.1688.com']",  # 确保是商品详情链接
                "a[href*='offer/']",
                "a.title-link",  # 通常标题链接会指向商品详情
                "div[class*='title'] a",
                "div[data-h5-type='offerCard'] a.title",
                # 下面是更多具体的选择器，排除功能性链接
                "a:not([href*='favorite']):not([href*='cart']):not([href*='login'])[href*='detail']",
                "div.offer-title a",
                "div.title a",
                "div.product-title a",
                "div.item-title a",
                "h4.title a",
                "div.offer-card a.title",
                # 最后才尝试更通用的选择器
                "div[data-h5-type='offerCard'] a",
                "div.offer-list-row-offer a",
                "div.offer-card a",
                "div.J_offerCard a"
            ]

            # 尝试使用JavaScript直接找到首个商品标题链接
            try:
                js_links = self.driver.execute_script("""
                // 找到所有可能的商品标题链接
                var links = [];

                // 尝试各种可能包含标题的元素
                var titleElements = document.querySelectorAll('a[href*="detail"], div[class*="title"] a, h4 a, div[class*="product"] a');

                for (var i = 0; i < titleElements.length; i++) {
                    var link = titleElements[i];
                    var href = link.getAttribute('href');

                    // 包含 detail 或 offer 但不包含收藏和购物车的链接
                    if (href && (href.includes('detail') || href.includes('offer')) &&
                        !href.includes('favorite') && !href.includes('cart') && !href.includes('login')) {

                        // 检查链接是否可见
                        var rect = link.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            links.push({
                                element: link,
                                href: href,
                                text: link.innerText.trim() || 'No Text'
                            });
                        }
                    }
                }
                return links;
                """)

                if js_links and len(js_links) > 0:
                    print(f"JavaScript找到 {len(js_links)} 个可能的商品链接")

                    # 显示找到的所有链接信息
                    for i, link_info in enumerate(js_links[:5]):
                        print(f"  候选链接 {i+1}: {link_info['text']} -> {link_info['href']}")

                    # 点击第一个链接
                    self.driver.execute_script("arguments[0].click();", js_links[0]['element'])
                    print(f"通过JavaScript点击商品链接: {js_links[0]['text']} -> {js_links[0]['href']}")

                    # 等待新页面加载
                    time.sleep(3)

                    # 保存商品详情页
                    self._save_page_source("product_detail_page.html")
                    print(f"当前URL: {self.driver.current_url}")
                    print(f"页面标题: {self.driver.title}")

                    # 检查是否进入了登录页面
                    if "login" in self.driver.current_url.lower() or "登录" in self.driver.title:
                        print("警告：点击后进入了登录页面，尝试回退并尝试下一个方法")
                        self.driver.back()
                        time.sleep(2)
                    else:
                        return True
            except Exception as js_error:
                print(f"JavaScript点击方法出错: {js_error}")

            # 如果JavaScript方法失败，尝试原始的Selenium方法
            for selector in clickable_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_links = [el for el in elements if el.is_displayed() and el.is_enabled()]

                    if visible_links:
                        # 列出候选链接
                        for i, link in enumerate(visible_links[:5]):
                            href = link.get_attribute('href')
                            text = link.text.strip() or "[无文本]"

                            # 跳过收藏、购物车、登录等功能性链接
                            if href and ("favorite" in href or "cart" in href or "login" in href):
                                print(f"  跳过功能性链接: {text} -> {href}")
                                continue

                            print(f"  候选链接 {i+1}: {text} -> {href}")

                        # 选择第一个非功能性链接
                        valid_links = [link for link in visible_links
                                     if link.get_attribute('href') and
                                     not any(skip in link.get_attribute('href') for skip in ['favorite', 'cart', 'login'])]

                        if valid_links:
                            first_link = valid_links[0]
                            href = first_link.get_attribute('href')
                            text = first_link.text.strip() or "[无文本]"

                            print(f"选择点击链接: {text} -> {href}")

                            # 使用JavaScript点击，避免可能的遮挡问题
                            self.driver.execute_script("arguments[0].click();", first_link)
                            print("已点击商品链接")

                            # 等待新页面加载
                            time.sleep(3)

                            # 保存商品详情页
                            self._save_page_source("product_detail_page.html")
                            print(f"当前URL: {self.driver.current_url}")
                            print(f"页面标题: {self.driver.title}")

                            # 检查是否进入了登录页面
                            if "login" in self.driver.current_url.lower() or "登录" in self.driver.title:
                                print("警告：点击后进入了登录页面，尝试返回并点击下一个链接")
                                self.driver.back()
                                time.sleep(2)
                                continue

                            return True
                except Exception as sel_error:
                    print(f"尝试选择器 '{selector}' 时出错: {sel_error}")
                    continue

            # 如果前面的方法都失败，尝试直接用XPath查找商品标题元素
            try:
                title_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '商品') or contains(text(), '产品')]")
                if title_elements:
                    print(f"找到 {len(title_elements)} 个可能的商品标题元素")

                    for title_el in title_elements[:5]:
                        try:
                            # 尝试找到包含标题的父元素并从那里查找链接
                            parent = title_el
                            for _ in range(3):  # 向上找3层父元素
                                if parent:
                                    parent = parent.find_element(By.XPATH, "..")
                                    links = parent.find_elements(By.TAG_NAME, "a")
                                    valid_links = [link for link in links
                                                if link.get_attribute('href') and
                                                not any(skip in link.get_attribute('href') for skip in ['favorite', 'cart', 'login'])]

                                    if valid_links:
                                        link = valid_links[0]
                                        print(f"从商品标题元素找到链接: {link.get_attribute('href')}")
                                        self.driver.execute_script("arguments[0].click();", link)

                                        # 等待新页面加载
                                        time.sleep(3)

                                        # 保存商品详情页
                                        self._save_page_source("product_detail_page.html")
                                        print(f"当前URL: {self.driver.current_url}")
                                        print(f"页面标题: {self.driver.title}")

                                        # 检查是否进入了登录页面
                                        if "login" in self.driver.current_url.lower() or "登录" in self.driver.title:
                                            print("警告：点击后进入了登录页面，继续尝试")
                                            self.driver.back()
                                            time.sleep(2)
                                            continue

                                        return True
                        except Exception as inner_e:
                            print(f"处理商品标题元素时出错: {inner_e}")
                            continue
            except Exception as xpath_error:
                print(f"XPath方法寻找商品标题时出错: {xpath_error}")

            print("所有方法均未能找到可点击的商品链接")
            return False
        except Exception as e:
            print(f"点击第一个商品时出错: {e}")
            return False

    def _extract_product_info(self, item) -> Optional[Dict[str, Any]]:
        """
        从商品元素中提取信息
        :param item: 商品元素
        :return: 商品信息字典，如果提取失败则返回None
        """
        try:
            # 尝试多种选择器获取标题
            title = None
            title_selectors = [
                ("title", "title"),
                ("title", "offer-title"),
                ("title", "title-text"),
                ("alt", "img"),
                ("data-logs-value", "a")
            ]

            for attr, selector in title_selectors:
                try:
                    elem = item.find_element(By.CSS_SELECTOR, selector) if selector else item
                    if attr == "title":
                        title = elem.get_attribute("title") or elem.text.strip()
                    else:
                        title = elem.get_attribute(attr) or elem.text.strip()
                    if title and len(title) > 2:  # 确保标题有效
                        break
                except:
                    continue

            title = title or "未知商品"

            # 获取商品链接
            link = "#"
            try:
                link_elem = item.find_element(By.CSS_SELECTOR, "a")
                link = link_elem.get_attribute("href") or "#"
            except:
                pass

            # 获取价格
            price_elem = self._find_element(item, ".price, .offer-price, .price-text, .price strong")
            price = price_elem.text.strip() if price_elem else "价格面议"

            # 获取店铺名称
            shop_elem = self._find_element(item, ".shop-name, .seller, .company-name a, .company-name")
            shop = shop_elem.text.strip() if shop_elem else "未知店铺"

            # 获取销量
            sales_elem = self._find_element(item, ".sale, .sale-count, .sold-count, .deal-cnt")
            sales = sales_elem.text.strip() if sales_elem else "0人付款"

            # 获取商品图片
            img_elem = self._find_element(item, "img")
            image = img_elem.get_attribute('src') if img_elem else ""

            return {
                'title': title,
                'price': price,
                'shop': shop,
                'sales': sales,
                'link': link,
                'image': image
            }

        except Exception as e:
            logging.error(f"提取商品信息时出错: {e}")
            return None

    def _find_element(self, parent, selector):
        """安全地查找元素"""
        try:
            return parent.find_element(By.CSS_SELECTOR, selector)
        except:
            return None

    def _save_page_source(self, filename: str):
        """保存页面源代码用于调试"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"已保存页面源代码到 {filename}")
        except Exception as e:
            print(f"保存页面源代码时出错: {e}")

    def _extract_product_info(self, item) -> Dict[str, str]:
        """
        从商品元素中提取信息
        :param item: 商品元素
        :return: 商品信息字典
        """
        result = {
            'title': '未知商品',
            'price': '价格面议',
            'shop': '未知店铺',
            'sales': '0人付款',
            'link': '#',
            'image': ''
        }

        try:
            # 1. 提取标题
            title_selectors = [
                ("[title]", "title"),
                (".title, .offer-title, .title-text, .organic-gallery-title", "text"),
                (".title a", "title"),
                (".offer-list-row-title", "text"),
                (".offer-param a[title]", "title"),
                (".offer-param a", "text")
            ]

            for selector, attr in title_selectors:
                try:
                    elem = item.find_element(By.CSS_SELECTOR, selector)
                    if elem and elem.is_displayed():
                        if attr == "text":
                            title = elem.text.strip()
                        else:
                            title = elem.get_attribute(attr).strip()
                        if title and len(title) > 2:  # 确保标题有效
                            result['title'] = title
                            break
                except:
                    continue

            # 2. 提取链接
            link_selectors = [
                "a[href*='detail']",
                "a[href*='offer']",
                ".title a[href]",
                "a[href^='//detail']",
                "a[href^='http']"
            ]

            for selector in link_selectors:
                try:
                    link_elem = item.find_element(By.CSS_SELECTOR, selector)
                    href = link_elem.get_attribute("href")
                    if href and (href.startswith("http") or href.startswith("//")):
                        if href.startswith("//"):
                            href = "https:" + href
                        result['link'] = href
                        break
                except:
                    continue

            # 3. 提取价格
            price_selectors = [
                ".price .value, .price-value, .price-text, .price strong",
                ".price, .price-range, .price-wrapper",
                "[data-price], [data-spm*='price']",
                ".offer-price, .price-now",
                ".price-module__price"
            ]

            for selector in price_selectors:
                try:
                    price_elem = item.find_element(By.CSS_SELECTOR, selector)
                    if price_elem and price_elem.is_displayed():
                        price = price_elem.text.strip()
                        if price and any(c.isdigit() for c in price):
                            result['price'] = price.replace("\n", " ").strip()
                            break
                except:
                    continue

            # 4. 提取店铺名称
            shop_selectors = [
                ".shop-name, .seller, .company-name, .company-text",
                "[data-company-name], [data-spm*='shop']",
                "[data-nick], .shop-enter-name",
                ".shop-name a, .company-name a"
            ]

            for selector in shop_selectors:
                try:
                    shop_elem = item.find_element(By.CSS_SELECTOR, selector)
                    if shop_elem and shop_elem.is_displayed():
                        shop = shop_elem.text.strip()
                        if shop and len(shop) > 1:
                            result['shop'] = shop
                            break
                except:
                    continue

            # 5. 提取销量
            sales_selectors = [
                ".sale, .sale-count, .sold-count, .deal-cnt",
                "[data-sale-count], [data-sales], [data-spm*='deal']",
                "[title*='成交'], [title*='交易']",
                ".sold-module__sold-count, .trade"
            ]

            for selector in sales_selectors:
                try:
                    sales_elem = item.find_element(By.CSS_SELECTOR, selector)
                    if sales_elem and sales_elem.is_displayed():
                        sales = sales_elem.text.strip()
                        if sales and any(c.isdigit() for c in sales):
                            result['sales'] = sales
                            break
                except:
                    continue

            # 6. 提取图片
            img_selectors = [
                "img[src*='.jpg'], img[src*='.jpeg'], img[src*='.png'], img[src*='.webp']",
                "img[data-src*='.jpg'], img[data-src*='.jpeg'], img[data-src*='.png']",
                "img[data-image-src], [data-image] img",
                ".pic-box img, .pic img, .img img"
            ]

            for selector in img_selectors:
                try:
                    img_elem = item.find_element(By.CSS_SELECTOR, selector)
                    if img_elem and img_elem.is_displayed():
                        img_src = (img_elem.get_attribute("src") or
                                  img_elem.get_attribute("data-src") or
                                  img_elem.get_attribute("data-image-src") or
                                  img_elem.get_attribute("data-lazy-src"))

                        if img_src:
                            if img_src.startswith("//"):
                                img_src = "https:" + img_src
                            elif img_src.startswith("http"):
                                pass  # 已经是完整URL
                            elif not (img_src.startswith("data:") or img_src.startswith("javascript")):
                                img_src = self.base_url.rstrip("/") + "/" + img_src.lstrip("/")

                            if any(ext in img_src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                                result['image'] = img_src
                                break
                except Exception as e:
                    continue

        except Exception as e:
            print(f"提取商品信息时出错: {e}")

        return result

    def _find_element(self, parent, selector):
        """安全地查找元素"""
        try:
            return parent.find_element(By.CSS_SELECTOR, selector)
        except:
            return None

    def save_to_excel(self, products: List[Dict], keyword: str = 'products') -> str:
        """
        保存商品信息到Excel文件
        :param products: 商品列表
        :param keyword: 搜索关键词，用于生成文件名
        :return: 保存的文件路径，如果保存失败则返回空字符串
        """
        try:
            if not products or not isinstance(products, list):
                print("没有有效的商品数据可保存")
                return ""

            # 确保products中的每个元素都是字典
            valid_products = []
            for p in products:
                if isinstance(p, dict) and p.get('title') != '未知商品':
                    valid_products.append(p)

            if not valid_products:
                print("没有有效的商品数据可保存")
                return ""

            print(f"\n准备保存 {len(valid_products)} 条商品数据...")

            # 创建DataFrame并清理数据
            df = pd.DataFrame(valid_products)

            # 重命名列名为中文
            column_mapping = {
                'title': '商品标题',
                'price': '价格',
                'shop': '店铺名称',
                'sales': '销量',
                'link': '商品链接',
                'image': '图片链接'
            }
            df = df.rename(columns=column_mapping)

            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_keyword = "".join([c for c in str(keyword) if c.isalnum() or c in ' _-']).rstrip()
            filename = f"1688_{safe_keyword or 'products'}_{timestamp}.xlsx"

            # 保存到Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            filepath = os.path.abspath(filename)
            print(f"\n商品信息已保存到: {filepath}")

            # 在文件管理器中打开文件所在目录
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(os.path.dirname(filepath))
                elif os.name == 'posix':  # macOS, Linux
                    import subprocess
                    subprocess.Popen(['open', os.path.dirname(filepath)])
            except Exception as e:
                print(f"打开文件所在目录时出错: {e}")

            return filepath

        except Exception as e:
            error_msg = f"保存文件时出错: {str(e)}"
            logging.error(error_msg, exc_info=True)
            print(error_msg)
            return ""

    def close(self):
        """关闭浏览器"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("浏览器已关闭")

def is_interactive():
    """检查是否在交互式终端中运行"""
    import sys
    return sys.stdin.isatty()

def main():
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('1688_crawler.log', encoding='utf-8')
        ]
    )

    print("\n" + "="*50)
    print("1688商品爬虫 v1.2")
    print("="*50 + "\n")

    try:
        # 获取用户输入
        if not is_interactive():
            # 非交互式模式使用默认值
            print("非交互式模式，使用默认值...")
            keyword = "手机"
            pages = 1
            base_url = "https://www.1688.com"
        else:
            try:
                keyword = input("请输入要搜索的商品(默认: 手机): ").strip() or "手机"
                pages_input = input("请输入要爬取的页数(默认: 1): ").strip()
                pages = int(pages_input) if pages_input.isdigit() and int(pages_input) > 0 else 1

                # 选择站点版本
                site_choice = input("\n请选择站点版本 (1: 国际站 global.1688.com, 2: 中文站 1688.com, 默认: 1): ").strip()
                if site_choice == "2":
                    base_url = "https://www.1688.com"
                else:
                    base_url = "https://global.1688.com"
            except EOFError:
                # 如果输入被重定向或非交互式环境，使用默认值
                print("\n检测到非交互式环境，使用默认值...")
                keyword = "手机"
                pages = 1
                base_url = "https://www.1688.com"

        # 创建爬虫实例
        print("\n正在启动浏览器...")
        crawler = Alibaba1688SeleniumCrawler(base_url=base_url, headless=False)

        try:
            print(f"\n使用站点: {base_url}")
            print(f"开始抓取'{keyword}'商品信息...")

            # 搜索商品
            products = crawler.search_products(keyword, pages=pages)

            # 保存到Excel
            if isinstance(products, list):
                if products:  # 确保products是列表且不为空
                    filename = crawler.save_to_excel(products, keyword)
                    if filename:
                        print(f"\n抓取完成，共获取 {len(products)} 条商品数据")
                        print(f"数据已保存到: {filename}")
                    else:
                        print("\n保存文件时出错，请检查日志文件获取详细信息")
                else:
                    print("\n未获取到商品数据，可能原因：")
                    print("1. 搜索条件无结果")
                    print("2. 需要登录或验证码")
                    print("3. 网站结构已更新")
                    print("4. 网络连接问题")
            else:
                print("\n获取商品数据时出错，请检查日志文件获取详细信息")

        except KeyboardInterrupt:
            print("\n用户中断操作...")
        except Exception as e:
            logging.error(f"运行爬虫时出错: {e}", exc_info=True)
            print(f"\n发生错误: {e}")
            print("\n详细信息已记录到日志文件，请查看 1688_crawler.log")

        finally:
            # 关闭浏览器
            try:
                close_choice = input("\n是否关闭浏览器?(y/n, 默认: y): ").strip().lower()
                if not close_choice or close_choice == 'y':
                    crawler.close()
                    print("\n浏览器已关闭")
            except:
                pass

            print("\n程序结束")

    except KeyboardInterrupt:
        print("\n用户中断操作，程序退出")
    except Exception as e:
        logging.error(f"程序初始化时出错: {e}", exc_info=True)
        print(f"\n程序初始化时出错: {e}")

def create_chrome_driver(use_user_data=False):
    """
    创建并配置Chrome WebDriver
    :param use_user_data: 是否使用Chrome用户数据目录
    :return: 配置好的WebDriver实例
    """
    if use_user_data:
        source_user_data = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data')

        if os.path.exists(source_user_data):
            # 创建临时目录用于存放用户数据
            temp_dir = tempfile.mkdtemp()
            temp_user_data = os.path.join(temp_dir, 'User Data')
            try:
                shutil.copytree(source_user_data, temp_user_data)

                # 设置Chrome选项
                options = webdriver.ChromeOptions()
                options.add_argument(f"--user-data-dir={temp_dir}")
                options.add_argument(f'--profile-directory=Default')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)

                # 创建WebDriver实例
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

                # 设置窗口大小
                driver.set_window_size(1200, 800)

                # 删除临时目录
                atexit.register(shutil.rmtree, temp_dir, ignore_errors=True)

                return driver
            except Exception as e:
                print(f"使用用户数据目录时出错: {e}")
                shutil.rmtree(temp_dir, ignore_errors=True)

    # 默认创建新的浏览器会话
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_size(1200, 800)

    return driver

if __name__ == "__main__":
    main()
