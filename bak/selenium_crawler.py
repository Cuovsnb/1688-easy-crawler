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
        初始化Chrome驱动
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
        
        # 设置中文和用户代理
        options.add_argument('lang=zh_CN.UTF-8')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # 添加反检测参数
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 添加常见的用户代理
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # 修改navigator.webdriver为undefined
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // 覆盖webdriver属性
                    window.navigator.chrome = {
                        runtime: {},
                        // 其他属性
                    };
                    
                    // 覆盖plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    
                    // 覆盖languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['zh-CN', 'zh', 'en'],
                    });
                """
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
    
    def search_products(self, keyword, pages=1):
        """
        搜索商品
        :param keyword: 搜索关键词
        :param pages: 爬取页数
        :return: 商品列表，如果出错则返回空列表
        """
        print(f"\n开始爬取'{keyword}'商品信息...")
        all_products = []
        
        # 构建搜索URL
        params = {
            'keywords': keyword,
            'n': 'y',
            'netin': '2',
            'spm': 'a26352.13672862.searchbar.1',
            'search': 'y',
            'pageSize': '60',  # 每页显示60个商品
            'beginPage': '1'  # 从第一页开始
        }
        
        # 国际站和中文站的参数可能不同
        if 'global' in self.base_url:
            search_url = f"{self.base_url}/search/product.htm?{urlencode(params)}"
        else:
            search_url = f"{self.search_url}?{urlencode(params)}"
            
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
            # 1. 首先导航到搜索URL
            print(f"访问搜索页面: {search_url}")
            self.driver.get(search_url)
            time.sleep(self.get_random_delay(3, 5))
            
            # 2. 检查是否需要登录
            if self.login_helper.is_login_page():
                print("检测到需要登录...")
                if not self.login_helper.handle_login():
                    logging.error("登录失败，请手动处理")
                    return all_products
                
            # 3. 检查是否被重定向到首页
            is_homepage = "1688.com" in self.driver.current_url and "offer_search" not in self.driver.current_url and "search/product" not in self.driver.current_url
            if is_homepage:
                print(f"当前页面是1688首页（URL: {self.driver.current_url}）")
            else:
                print(f"当前页面非1688首页（URL: {self.driver.current_url}）")
            
            # 4. 进行弹窗清理
            print("开始进行弹窗清理...")
            popup_cleared = False
            for attempt in range(5):  # 尝试清理弹窗5次
                if self._check_captcha():
                    print(f"弹窗清理尝试 {attempt+1}/5: 检测到需手动处理的情况或登录页")
                    # 如果是登录页，尝试处理
                    if self.login_helper.is_login_page():
                        print("检测到登录页，尝试处理...")
                        if not self.login_helper.handle_login():
                            print("登录失败，继续尝试清理弹窗")
                else:
                    print(f"弹窗清理尝试 {attempt+1}/5: 清理成功，未检测到阻碍")
                    popup_cleared = True
                    break
                
                # 等待一下再进行下一次尝试
                time.sleep(1)
            
            if not popup_cleared:
                # 弹窗清理失败，让用户手动处理
                user_input = input("自动清理弹窗共5次尝试均失败。请手动关闭页面上的弹窗/广告，然后按 Enter 键继续，或输入 'skip' 跳过当前搜索: ").strip().lower()
                if user_input == 'skip':
                    logging.warning(f"用户选择跳过关键词 '{keyword}' 的搜索。")
                    return all_products
            
            # 5. 如果是首页，尝试定位搜索框并执行搜索
            if is_homepage:
                print(f"尝试在首页上执行搜索: '{keyword}'...")
                # 保存首页内容供分析
                self._save_page_source(f"homepage_before_search_{keyword}.html")
                
                if not self._perform_search_from_homepage(keyword):
                    # 6. 如果找不到搜索框，保存页面并提示用户
                    self._save_page_source(f"homepage_search_failed_{keyword}.html")
                    print(f"无法在首页定位搜索框。已保存页面代码供分析。")
                    
                    # 7. 提示用户手动搜索
                    user_input = input(f"无法在首页自动定位搜索框。请手动在浏览器中完成对 '{keyword}' 的搜索，然后按 Enter 键继续，或输入 'skip' 跳过此关键词: ").strip().lower()
                    if user_input == 'skip':
                        logging.warning(f"用户选择跳过关键词 '{keyword}' 的搜索。")
                        return all_products
            
            # 8. 等待搜索结果页面加载
            print("等待搜索结果页面加载...")
            time.sleep(self.get_random_delay(3, 5))
            
            # 保存页面内容用于调试
            self._save_page_source("search_results_page.html")
            
            # 添加终端确认机制，询问用户是否已在商品结果页面
            is_on_product_page = input("请确认是否已在商品结果页面(0:否, 1:是): ").strip()
            if is_on_product_page == "1":
                print("用户确认已在商品结果页面，开始提取商品信息...")
                # 保存当前页面源代码
                self._save_page_source(f"confirmed_product_page_{keyword}.html")
                
                # 使用5种不同方式查找商品信息
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
                all_found_products = []
                for method_num, method_products in enumerate([products_method1, products_method2, products_method3, products_method4, products_method5], 1):
                    if method_products:
                        print(f"方式{method_num}找到了{len(method_products)}个商品")
                        all_found_products.extend(method_products)
                    else:
                        print(f"方式{method_num}没有找到商品")
                
                # 去重
                unique_products = []
                seen_titles = set()
                for product in all_found_products:
                    title = product.get('title', '')
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        unique_products.append(product)
                
                print(f"\n总共找到{len(unique_products)}个唯一商品")
                all_products.extend(unique_products)
                
                # 尝试点击第一个商品
                if unique_products:
                    print("\n尝试点击第一个商品...")
                    self._click_first_product()
                else:
                    print("未找到任何商品，无法点击")
                
                return all_products
            else:
                print("用户确认未在商品结果页面，继续正常流程")
            
            # 交互式处理未清除的弹窗
            user_interaction_attempts = 0
            max_user_interaction_attempts = 5
            while user_interaction_attempts < max_user_interaction_attempts:
                if self.login_helper.is_login_page():
                    print("交互检查：检测到当前是登录页面，将尝试登录处理。")
                    if not self.login_helper.handle_login():
                        logging.error("交互检查中登录失败，请手动处理。")
                        return all_products # Critical failure, cannot proceed
                    # After successful login, re-run initial check_captcha for the new page state
                    print("交互检查中登录成功后，重新进行初步弹窗清理...")
                    if self._check_captcha():
                        print("交互检查中登录成功后，初步弹窗清理检测到需手动处理的情况。")
                    else:
                        print("交互检查中登录成功后，初步弹窗清理完成。")
                    
                user_sees_popup_input = input(f"自动检测完成 (尝试 {user_interaction_attempts + 1}/{max_user_interaction_attempts})。您是否仍然在页面上看到弹窗/广告？ (1=是, 0=否, skip=跳过 '{keyword}'): ").strip().lower()
                
                if user_sees_popup_input == '0':
                    print("用户确认页面已无弹窗。")
                    break
                elif user_sees_popup_input == 'skip':
                    logging.warning(f"用户选择在交互式弹窗检查中跳过关键词 '{keyword}' 的搜索。")
                    return all_products
                elif user_sees_popup_input == '1':
                    user_interaction_attempts += 1
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    # Sanitize keyword for filename
                    safe_keyword = "".join(c if c.isalnum() else "_" for c in keyword)
                    popup_html_filename = f"user_reported_popup_{safe_keyword}_{timestamp}.html"
                    self._save_page_source(popup_html_filename)
                    print(f"页面已保存到 {popup_html_filename}。尝试再次自动清理弹窗...")
                    
                    if self._check_captcha():
                        print(f"交互式清理尝试 {user_interaction_attempts}: 检测到需手动处理的情况或登录页。")
                        # If _check_captcha returns True, it implies a significant issue (like a hard captcha or login page again)
                        # We might need to break or let the next iteration handle login page check.
                    else:
                        print(f"交互式清理尝试 {user_interaction_attempts}: 自动清理完成，未检测到明显阻碍。")

                    if user_interaction_attempts >= max_user_interaction_attempts:
                        input(f"已达到最大自动清理尝试次数 ({max_user_interaction_attempts})。请手动关闭页面上任何剩余的弹窗/广告，然后按 Enter 键继续...")
                        # After manual intervention, assume popups are handled for now.
                        break
                else:
                    print("无效输入，请输入 1, 0, 或 skip。")
            
            # 验证搜索结果页面
            max_search_attempts = 2 # 允许一次手动尝试
            attempt = 0
            search_page_verified = False
            
            # 先检查当前页面URL和标题，快速验证是否已经在搜索结果页面
            current_url = self.driver.current_url.lower()
            page_title = self.driver.title.lower()
            if (keyword.lower() in current_url or keyword.lower() in page_title) and ('offer_search' in current_url or 'search/product' in current_url or 'search-result' in current_url):
                print(f"快速验证: 检测到URL和标题均包含搜索特征，直接认为已经在搜索结果页面")
                search_page_verified = True
                print("搜索识别成功，跳过后续弹窗检查...")
            
            # 如果快速验证失败，再进行详细验证
            while not search_page_verified and attempt < max_search_attempts:
                if self._is_search_results_page(keyword):
                    print("已成功进入搜索结果页面。")
                    search_page_verified = True
                    print("搜索识别成功，跳过后续弹窗检查...")
                    break
                else:
                    attempt += 1
                    current_url_display = self.driver.current_url
                    current_title_display = self.driver.title
                    print(f"自动搜索后未能确认搜索结果页面。当前URL: {current_url_display}, 标题: {current_title_display}")
                    if attempt < max_search_attempts:
                        user_input = input(f"请手动在浏览器中完成对 '{keyword}' 的搜索并导航到正确的商品列表页面，然后按 Enter键 继续，或输入 'skip' 跳过此关键词: ").strip().lower()
                        if user_input == 'skip':
                            logging.warning(f"用户选择跳过关键词 '{keyword}' 的搜索。")
                            return all_products # 返回已收集或空列表
                        
                        # 用户已经手动执行了搜索，检查当前页面URL和标题，以确认是否为搜索结果页面
                        current_url = self.driver.current_url.lower()
                        page_title = self.driver.title.lower()
                        print(f"用户手动搜索后，当前页面: URL='{current_url}', Title='{page_title}'")
                        
                        # 检查URL或标题是否包含关键词，这通常表示已经在搜索结果页面
                        if keyword.lower() in current_url or keyword.lower() in page_title or 'offer_search' in current_url or 'search/product' in current_url:
                            print(f"检测到页面URL或标题包含关键词 '{keyword}' 或搜索相关路径，认为已经是搜索结果页面")
                            search_page_verified = True # 直接标记为已验证搜索页面
                            print("搜索识别成功，跳过后续弹窗检查...")
                            break # 跳出验证循环
                        
                        # 仅当未确认是搜索结果页面时，才进行弹窗清理
                        print("用户已手动操作，但未确认进入搜索结果页面，尝试再次清理当前页面的弹窗...")
                        if self._check_captcha(): # 清理用户手动导航后的页面
                            print("手动操作后，页面清理时检测到需进一步手动处理的情况或登录页。")
                        else:
                            print("手动操作后，弹窗清理完成。")
                        # 用户按 Enter 后，循环将继续，并在顶部再次调用 _is_search_results_page
                    else:
                        logging.error(f"手动操作后仍未能确认 '{keyword}' 的搜索结果页面。将跳过此关键词。")
                        self._save_page_source(f"failed_search_verification_{keyword}.html")
                        return all_products # 返回已收集或空列表
            
            if not search_page_verified:
                logging.error(f"未能确认 '{keyword}' 的搜索结果页面，跳过提取。")
                self._save_page_source(f"search_verification_failed_final_{keyword}.html")
                return all_products

            # 处理每一页
            for page_num in range(1, pages + 1):
                print(f"\n处理第 {page_num}/{pages} 页...")
                if page_num > 1:
                    # 如果不是第一页，点击下一页
                    if not self._go_to_next_page(page_num):
                        logging.warning(f"无法跳转到第 {page_num} 页，可能已达到最后一页")
                        break
                    # 跳转后再次验证是否仍在搜索结果页（或相似页面），防止意外跳转
                    time.sleep(self.get_random_delay(2,4)) # 等待页面加载
                    if not self._is_search_results_page(keyword, is_subsequent_page=True):
                        print(f"跳转到第 {page_num} 页后，页面似乎不再是 '{keyword}' 的搜索结果页。停止翻页。")
                        self._save_page_source(f"page_{page_num}_not_results_after_nav.html")
                        break

                # 检查是否跳转到登录页 (翻页后也可能触发)
                if self.login_helper.is_login_page():
                    print("检测到需要重新登录...")
                    if not self.login_helper.handle_login():
                        logging.error("重新登录失败，终止当前关键词的爬取")
                        break
                
                # 提取当前页商品信息
                print(f"开始提取第 {page_num} 页的商品信息...")
                page_products = self._extract_products() # _extract_products 内部处理广告/验证码
                if page_products:
                    all_products.extend(page_products)
                    print(f"第 {page_num} 页成功提取 {len(page_products)} 个商品信息，总计 {len(all_products)} 个商品")
                else:
                    print(f"第 {page_num} 页未提取到商品信息或跳过提取。")
                
                if page_num < pages: # 如果不是最后一页，随机等待
                    time.sleep(self.get_random_delay(2, 5))
                
            return all_products
                
        except Exception as e:
            logging.error(f"搜索商品时出错: {e}")
            self._save_page_source("error_page.html")
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
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
            
            # 等待页面加载
            time.sleep(1)
            
            # 计算新的滚动高度并与上一个滚动高度比较
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
    
    def _extract_products_method1(self):
        """方式1: 使用标准CSS选择器查找商品"""
        products = []
        try:
            # 标准选择器
            selectors = [
                "div[data-h5-type='offerCard']",
                "div.offer-list-row-offer",
                "div.offer-card",
                "div.J_offerCard"
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"使用选择器 '{selector}' 找到 {len(elements)} 个商品")
                    for element in elements[:10]:  # 只处理前10个
                        product_info = self._extract_product_details_from_element(element)
                        if product_info:
                            products.append(product_info)
                    break
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
            # 尝试多种方式查找可点击的商品
            clickable_selectors = [
                "div[data-h5-type='offerCard'] a",
                "div.offer-list-row-offer a",
                "div.offer-card a",
                "div.J_offerCard a",
                "a[href*='detail']",
                "a[href*='offer']"
            ]
            
            for selector in clickable_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                visible_links = [el for el in elements if el.is_displayed() and el.is_enabled()]
                
                if visible_links:
                    first_link = visible_links[0]
                    print(f"找到可点击的商品链接: {first_link.get_attribute('href')}")
                    
                    # 使用JavaScript点击，避免可能的遮挡问题
                    self.driver.execute_script("arguments[0].click();", first_link)
                    print("已点击第一个商品")
                    
                    # 等待新页面加载
                    time.sleep(3)
                    
                    # 保存商品详情页
                    self._save_page_source("product_detail_page.html")
                    print(f"当前URL: {self.driver.current_url}")
                    print(f"页面标题: {self.driver.title}")
                    return True
            
            print("未找到可点击的商品链接")
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
