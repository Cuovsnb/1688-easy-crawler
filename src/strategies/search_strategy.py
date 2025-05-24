"""
搜索策略模块

提供不同的搜索策略，包括直接URL搜索、传统首页搜索等
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import Optional, List, Dict, Any

from ..core.config import CrawlerConfig
from ..utils.cache_manager import CacheManager
from ..utils.helpers import get_random_delay
from ..handlers.login_handler import LoginHandler
from ..handlers.popup_handler import PopupHandler
from ..handlers.page_handler import PageHandler
from ..drivers.browser_utils import BrowserUtils
from .url_builder import URLBuilder


class SearchStrategy:
    """搜索策略类"""

    def __init__(self, driver: webdriver.Chrome, config: CrawlerConfig = None):
        """
        初始化搜索策略
        :param driver: WebDriver实例
        :param config: 爬虫配置对象
        """
        self.driver = driver
        self.config = config or CrawlerConfig()

        # 初始化各种处理器
        self.cache_manager = CacheManager(driver, config)
        self.login_handler = LoginHandler(driver, config)
        self.popup_handler = PopupHandler(driver, config)
        self.page_handler = PageHandler(driver, config)
        self.browser_utils = BrowserUtils(driver)
        self.url_builder = URLBuilder(config)

    def search_products(self, keyword: str, pages: int = 1) -> List[Dict[str, Any]]:
        """
        主要的搜索方法，使用智能策略选择最佳搜索方式
        :param keyword: 搜索关键词
        :param pages: 爬取页数
        :return: 商品列表
        """
        print(f"\n开始搜索商品: '{keyword}'")

        # 设置反检测
        self._apply_anti_detection()

        try:
            # 策略1: 优先使用直接URL搜索
            if self._try_direct_url_search(keyword):
                print("✅ 直接URL搜索成功")
                # 处理搜索结果页面的弹窗
                self.popup_handler.handle_search_page_popups_comprehensive(keyword)
                return self._extract_products_from_current_page(keyword)

            # 策略2: 传统首页搜索
            print("直接URL搜索失败，尝试传统搜索方式...")
            if self._try_homepage_search(keyword):
                print("✅ 传统搜索成功")
                return self._extract_products_from_current_page(keyword)

            print("❌ 所有搜索策略都失败了")
            return []

        except Exception as e:
            print(f"搜索过程中出错: {e}")
            logging.error(f"搜索过程中出错: {e}")
            return []

    def search_products_strict_flow(self, keyword: str, pages: int = 1) -> List[Dict[str, Any]]:
        """
        严格按照指定流程进行搜索
        :param keyword: 搜索关键词
        :param pages: 爬取页数
        :return: 商品列表
        """
        print(f"\n=== 开始严格流程搜索: '{keyword}' ===")

        try:
            # 步骤1: 访问主页
            print("\n【步骤1】访问1688主页...")
            if not self._visit_homepage():
                print("❌ 访问主页失败")
                return []

            # 步骤2: 检查弹窗
            print("\n【步骤2】检查和处理弹窗...")
            self.popup_handler.handle_search_page_popups_comprehensive("homepage")

            # 步骤3: 用户提醒
            print("\n【步骤3】用户确认...")
            input("请确认页面已正常加载且无弹窗干扰，然后按 Enter 键继续...")

            # 步骤4: 执行搜索
            print(f"\n【步骤4】执行搜索: '{keyword}'...")
            if not self._perform_search_from_homepage(keyword):
                print("❌ 主页搜索失败")
                return []

            # 步骤5: 检查搜索结果
            print("\n【步骤5】检查搜索结果...")
            time.sleep(get_random_delay(3, 5))

            # 检查是否被重定向到登录页面
            if self.login_handler.is_login_page():
                print("❌ 检测到登录页面，尝试新标签页搜索")

                # 步骤6: 在新标签页构造URL
                print("\n【步骤6】在新标签页中构造搜索URL...")
                if self._try_direct_search_in_new_tab(keyword):
                    print("✅ 新标签页URL构造成功")
                else:
                    print("❌ 新标签页URL构造失败")
                    return []

            # 验证搜索结果页面
            if not self.page_handler.verify_search_results_page(keyword):
                print("❌ 搜索结果页面验证失败")
                return []

            print("✅ 搜索成功，开始提取商品信息")
            return self._extract_products_from_current_page(keyword)

        except Exception as e:
            print(f"严格流程搜索时出错: {e}")
            logging.error(f"严格流程搜索时出错: {e}")
            return []

    def _try_direct_url_search(self, keyword: str) -> bool:
        """
        尝试直接URL搜索
        :param keyword: 搜索关键词
        :return: 是否成功
        """
        try:
            print("=== 尝试直接URL搜索 ===")

            # 1. 优先尝试缓存的URL
            cached_url = self.cache_manager.get_cached_url(keyword)
            if cached_url:
                print(f"🎯 使用缓存URL: {cached_url}")
                if self._try_cached_url(cached_url, keyword):
                    return True

            # 2. 构造新的搜索URL
            print("构造新的搜索URL...")
            search_urls = self.url_builder.build_search_urls(keyword)

            for i, url in enumerate(search_urls, 1):
                print(f"尝试URL {i}/{len(search_urls)}: {url}")

                if self._try_search_url(url, keyword):
                    # 保存成功的URL到缓存
                    self.cache_manager.save_successful_url(keyword, url)
                    return True

            print("所有直接URL搜索都失败")
            return False

        except Exception as e:
            print(f"直接URL搜索时出错: {e}")
            logging.error(f"直接URL搜索时出错: {e}")
            return False

    def _try_cached_url(self, cached_url: str, keyword: str) -> bool:
        """尝试使用缓存的URL"""
        try:
            # 先访问主页设置基本Cookie
            print("先访问主页设置基本Cookie...")
            self.driver.get(self.config.DEFAULT_BASE_URL)
            time.sleep(2)

            # 尝试加载保存的Cookie
            self.cache_manager.load_cookies()
            time.sleep(1)

            # 访问缓存的URL
            self.driver.get(cached_url)
            time.sleep(get_random_delay(3, 6))

            # 检查结果
            if self.login_handler.is_login_page():
                print("❌ 缓存URL被重定向到登录页面")
                return False

            if self.page_handler.verify_search_results_page(keyword):
                print("✅ 缓存URL访问成功")
                # 更新缓存时间戳
                self.cache_manager.save_successful_url(keyword, cached_url)
                return True

            print("❌ 缓存URL不是有效的搜索结果页面")
            return False

        except Exception as e:
            print(f"使用缓存URL时出错: {e}")
            return False

    def _try_search_url(self, url: str, keyword: str) -> bool:
        """尝试访问搜索URL"""
        try:
            # 访问搜索URL
            self.driver.get(url)
            time.sleep(get_random_delay(3, 6))

            # 检查是否被重定向到登录页面
            if self.login_handler.is_login_page():
                print("❌ 被重定向到登录页面")
                return False

            # 检查是否是有效的搜索结果页面
            if self.page_handler.verify_search_results_page(keyword):
                print("✅ 成功访问搜索结果页面")
                # 保存成功的Cookie
                self.cache_manager.save_cookies()
                return True

            print("❌ 不是有效的搜索结果页面")
            return False

        except Exception as e:
            print(f"访问搜索URL时出错: {e}")
            return False

    def _try_homepage_search(self, keyword: str) -> bool:
        """
        尝试传统的首页搜索
        :param keyword: 搜索关键词
        :return: 是否成功
        """
        try:
            print("=== 尝试传统首页搜索 ===")

            # 1. 访问主页
            if not self._visit_homepage():
                return False

            # 2. 检查是否需要登录
            if self.login_handler.is_login_page():
                print("检测到需要登录...")
                if not self.login_handler.handle_login():
                    print("❌ 登录失败")
                    return False

            # 3. 处理首页弹窗
            print("处理首页弹窗...")
            self.popup_handler.close_popups_enhanced_silent()

            # 4. 执行搜索
            if not self._perform_search_from_homepage(keyword):
                print("❌ 首页搜索操作失败")
                return False

            # 5. 等待搜索结果加载
            time.sleep(get_random_delay(3, 5))

            # 6. 验证搜索结果
            if self.login_handler.is_login_page():
                print("❌ 搜索后被重定向到登录页面")
                # 尝试在新标签页构造URL
                return self._try_direct_search_in_new_tab(keyword)

            if self.page_handler.verify_search_results_page(keyword):
                print("✅ 传统搜索成功")
                return True

            print("❌ 搜索结果页面验证失败")
            return False

        except Exception as e:
            print(f"传统首页搜索时出错: {e}")
            logging.error(f"传统首页搜索时出错: {e}")
            return False

    def _visit_homepage(self) -> bool:
        """访问主页"""
        try:
            print(f"访问主页: {self.config.DEFAULT_BASE_URL}")
            self.driver.get(self.config.DEFAULT_BASE_URL)
            time.sleep(get_random_delay(3, 5))

            # 等待页面加载
            if not self.page_handler.wait_for_page_load():
                print("❌ 主页加载超时")
                return False

            print("✅ 主页访问成功")
            return True

        except Exception as e:
            print(f"访问主页时出错: {e}")
            return False

    def _perform_search_from_homepage(self, keyword: str) -> bool:
        """在首页执行搜索操作"""
        try:
            print(f"在首页搜索: '{keyword}'")

            # 搜索框选择器
            search_box_selectors = [
                "input[name='keywords']",
                "input[placeholder*='搜索']",
                "input[placeholder*='Search']",
                "input.search-input",
                "input[type='search']",
                "input.next-input",
                ".search-box input",
                "#J_searchInput",
                "#q",
                ".search-bar input",
                ".mod-searchbar-main input",
                "div.input-wrap input",
                "input.searchbar-input",
                "input.searchbar-keyword",
                "input[role='searchbox']"
            ]

            search_box = None
            for selector in search_box_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [el for el in elements if el.is_displayed()]
                    if visible_elements:
                        search_box = visible_elements[0]
                        print(f"找到搜索框: {selector}")
                        break
                except Exception:
                    continue

            if not search_box:
                print("❌ 未找到搜索框")
                return False

            # 清空搜索框并输入关键词
            search_box.clear()
            search_box.send_keys(keyword)
            time.sleep(1)

            # 查找搜索按钮
            search_button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button.search-btn",
                "button.btn-search",
                ".search-button",
                ".search-btn",
                "button:contains('搜索')",
                "button:contains('Search')",
                ".mod-searchbar-btn",
                ".searchbar-btn"
            ]

            search_button = None
            for selector in search_button_selectors:
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
                        search_button = visible_elements[0]
                        print(f"找到搜索按钮: {selector}")
                        break
                except Exception:
                    continue

            # 执行搜索
            if search_button:
                search_button.click()
                print("✅ 点击搜索按钮")
            else:
                # 如果没找到搜索按钮，尝试按回车键
                from selenium.webdriver.common.keys import Keys
                search_box.send_keys(Keys.RETURN)
                print("✅ 按回车键搜索")

            return True

        except Exception as e:
            print(f"首页搜索操作时出错: {e}")
            return False

    def _try_direct_search_in_new_tab(self, keyword: str) -> bool:
        """在新标签页中尝试直接构造搜索URL"""
        try:
            print("=== 在新标签页中尝试直接构造搜索URL ===")

            # 保存原始标签页
            original_tab = self.driver.current_window_handle
            print(f"原始标签页: {original_tab}")

            # 打开新标签页
            new_tab = self.browser_utils.open_new_tab()
            if not new_tab:
                print("❌ 无法打开新标签页")
                return False

            # 切换到新标签页
            if not self.browser_utils.switch_to_tab(new_tab):
                print("❌ 无法切换到新标签页")
                return False

            print("✅ 已切换到新标签页，开始构造搜索URL...")

            # 在新标签页中尝试直接URL访问
            success = self._try_direct_url_in_current_tab(keyword)

            if success:
                print("✅ 新标签页中URL构造成功")
                # 关闭原始标签页（登录页面）
                try:
                    self.browser_utils.close_tab(original_tab)
                    print("✅ 已关闭原始标签页（登录页面）")
                except:
                    print("⚠️ 关闭原始标签页时出错，但继续执行")
                return True
            else:
                print("❌ 新标签页中URL构造失败")
                # 切换回原始标签页
                self.browser_utils.switch_to_tab(original_tab)
                # 关闭失败的新标签页
                try:
                    self.browser_utils.close_tab(new_tab)
                except:
                    pass
                return False

        except Exception as e:
            print(f"❌ 在新标签页中构造URL时出错: {e}")
            return False

    def _try_direct_url_in_current_tab(self, keyword: str) -> bool:
        """在当前标签页中尝试直接构造搜索URL"""
        try:
            search_urls = self.url_builder.build_search_urls(keyword)

            for i, url in enumerate(search_urls, 1):
                try:
                    print(f"尝试URL {i}/{len(search_urls)}: {url}")

                    # 访问搜索URL
                    self.driver.get(url)
                    time.sleep(get_random_delay(3, 6))

                    # 检查是否成功
                    if self.login_handler.is_login_page():
                        print(f"❌ URL {i} 被重定向到登录页面")
                        continue

                    # 检查是否是有效的搜索结果页面
                    if self.page_handler.verify_search_results_page(keyword):
                        print(f"✅ URL {i} 成功访问搜索结果页面")
                        # 保存成功的URL到缓存
                        self.cache_manager.save_successful_url(keyword, url)
                        return True
                    else:
                        print(f"❌ URL {i} 不是有效的搜索结果页面")

                except Exception as e:
                    print(f"❌ URL {i} 访问失败: {e}")
                    continue

            print("所有URL构造尝试都失败")
            return False

        except Exception as e:
            print(f"在当前标签页构造URL时出错: {e}")
            return False

    def _extract_products_from_current_page(self, keyword: str) -> List[Dict[str, Any]]:
        """从当前页面提取商品信息"""
        try:
            # 这里应该调用ProductExtractor来提取商品
            # 为了避免循环导入，我们在这里只返回一个占位符
            # 实际实现中，这个方法会在主爬虫类中被重写
            print("提取商品信息...")
            return []

        except Exception as e:
            print(f"提取商品信息时出错: {e}")
            logging.error(f"提取商品信息时出错: {e}")
            return []

    def _apply_anti_detection(self):
        """应用反检测设置"""
        try:
            # 设置更真实的请求头
            self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """)

            # 添加更真实的请求头
            import random
            user_agent = random.choice(self.config.USER_AGENTS)
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent
            })

        except Exception as e:
            print(f"应用反检测设置时出错: {e}")

    def get_search_strategy_info(self) -> Dict[str, Any]:
        """获取搜索策略信息"""
        return {
            'available_strategies': [
                'direct_url_search',
                'homepage_search',
                'strict_flow_search'
            ],
            'cache_enabled': True,
            'anti_detection_enabled': True,
            'popup_handling_enabled': True,
            'login_handling_enabled': True
        }
