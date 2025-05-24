"""
1688爬虫主类

整合所有功能模块，提供统一的爬虫接口
"""

import time
import logging
import os
from typing import List, Dict, Any, Optional

from .config import CrawlerConfig
from ..drivers.webdriver_manager import WebDriverManager
from ..drivers.browser_utils import BrowserUtils
from ..handlers.login_handler import LoginHandler
from ..handlers.popup_handler import PopupHandler
from ..handlers.page_handler import PageHandler
from ..extractors.product_extractor import ProductExtractor
from ..extractors.page_analyzer import PageAnalyzer
from ..strategies.search_strategy import SearchStrategy
from ..utils.cache_manager import CacheManager
from ..utils.data_exporter import DataExporter
from ..utils.helpers import setup_logging


class Alibaba1688Crawler:
    """
    1688爬虫主类

    使用组合模式整合各个功能模块，提供统一的爬虫接口
    """

    def __init__(self, base_url: Optional[str] = None, headless: bool = False,
                 user_data_dir: Optional[str] = None, config: Optional[CrawlerConfig] = None):
        """
        初始化爬虫
        :param base_url: 基础URL (global.1688.com 或 www.1688.com)
        :param headless: 是否使用无头模式
        :param user_data_dir: Chrome用户数据目录路径，用于保持登录状态
        :param config: 爬虫配置对象
        """
        # 初始化配置
        self.config = config or CrawlerConfig()
        if base_url:
            self.config.DEFAULT_BASE_URL = base_url

        # 设置日志
        setup_logging(self.config.PATHS['logs'])

        # 初始化WebDriver
        self.webdriver_manager = WebDriverManager(self.config)
        self.driver = self.webdriver_manager.create_driver(
            headless=headless,
            user_data_dir=user_data_dir
        )

        # 初始化各个功能模块
        self._init_modules()

        # 存储数据
        self.data = []

        # 流程控制相关
        self.process_file = "process.txt"
        self.process_steps = [
            "打开浏览器加载主页",
            "清理弹窗",
            "主页面",
            "找到搜索框，输入关键词",
            "进行搜索",
            "搜索结果页面"
        ]

        print(f"✅ 1688爬虫初始化完成，使用站点: {self.config.DEFAULT_BASE_URL}")

    def _init_modules(self):
        """初始化各个功能模块"""
        try:
            # 基础工具
            self.browser_utils = BrowserUtils(self.driver)
            self.cache_manager = CacheManager(self.driver, self.config)
            self.data_exporter = DataExporter(self.config)

            # 处理器
            self.login_handler = LoginHandler(self.driver, self.config)
            self.popup_handler = PopupHandler(self.driver, self.config)
            self.page_handler = PageHandler(self.driver, self.config)

            # 提取器
            self.product_extractor = ProductExtractor(self.driver, self.config)
            self.page_analyzer = PageAnalyzer(self.driver, self.config)

            # 搜索策略
            self.search_strategy = SearchStrategy(self.driver, self.config)

            # 重写搜索策略的商品提取方法，避免循环导入
            self.search_strategy._extract_products_from_current_page = self._extract_products_from_current_page

            print("✅ 所有功能模块初始化完成")

        except Exception as e:
            print(f"❌ 初始化功能模块时出错: {e}")
            logging.error(f"初始化功能模块时出错: {e}")
            raise

    def _init_process_file(self):
        """
        初始化流程文件，将所有步骤状态设为0
        """
        try:
            with open(self.process_file, 'w', encoding='utf-8') as f:
                for step in self.process_steps:
                    f.write(f"{step} 0\n")
            print(f"✅ 流程文件已初始化: {self.process_file}")
        except Exception as e:
            print(f"❌ 初始化流程文件失败: {e}")

    def _read_process_status(self):
        """
        读取流程文件状态
        :return: 返回步骤状态字典
        """
        try:
            status = {}
            if os.path.exists(self.process_file):
                with open(self.process_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            parts = line.rsplit(' ', 1)  # 从右边分割，只分割一次
                            if len(parts) == 2:
                                step_name = parts[0]
                                step_status = int(parts[1])
                                status[step_name] = step_status
            return status
        except Exception as e:
            print(f"❌ 读取流程文件失败: {e}")
            return {}

    def _update_process_status(self, step_name, status):
        """
        更新指定步骤的状态
        :param step_name: 步骤名称
        :param status: 状态值 (0=失败, 1=成功)
        """
        try:
            current_status = self._read_process_status()
            current_status[step_name] = status

            with open(self.process_file, 'w', encoding='utf-8') as f:
                for step in self.process_steps:
                    step_status = current_status.get(step, 0)
                    f.write(f"{step} {step_status}\n")

            print(f"✅ 已更新步骤状态: {step_name} -> {status}")
        except Exception as e:
            print(f"❌ 更新流程文件失败: {e}")

    def _get_current_step(self):
        """
        获取当前应该执行的步骤
        :return: 返回第一个状态为0的步骤，如果所有步骤都完成则返回None
        """
        try:
            status = self._read_process_status()
            for step in self.process_steps:
                if status.get(step, 0) == 0:
                    return step
            return None  # 所有步骤都完成
        except Exception as e:
            print(f"❌ 获取当前步骤失败: {e}")
            return None

    def _ask_user_confirmation(self, step_name):
        """
        询问用户步骤是否成功完成
        :param step_name: 步骤名称
        :return: 用户回答 (0=失败, 1=成功)
        """
        print(f"\n=== 步骤确认: {step_name} ===")
        while True:
            user_input = input(f"步骤 '{step_name}' 是否成功完成？(0=失败, 1=成功): ").strip()
            if user_input in ['0', '1']:
                return int(user_input)
            else:
                print("请输入 0 或 1")

    def search_products(self, keyword: str, pages: int = 1) -> List[Dict[str, Any]]:
        """
        搜索商品 - 智能流程
        :param keyword: 搜索关键词
        :param pages: 爬取页数
        :return: 商品列表
        """
        try:
            print(f"\n🔍 开始搜索商品: '{keyword}' (页数: {pages})")

            # 使用搜索策略进行搜索
            products = self.search_strategy.search_products(keyword, pages)

            if products:
                print(f"✅ 搜索完成，找到 {len(products)} 个商品")
                self.data.extend(products)
                return products
            else:
                print("❌ 未找到商品")
                return []

        except Exception as e:
            print(f"❌ 搜索商品时出错: {e}")
            logging.error(f"搜索商品时出错: {e}")
            return []

    def search_products_strict_flow(self, keyword: str, pages: int = 1) -> List[Dict[str, Any]]:
        """
        搜索商品 - 严格流程
        :param keyword: 搜索关键词
        :param pages: 爬取页数
        :return: 商品列表
        """
        try:
            print(f"\n🔍 开始严格流程搜索: '{keyword}' (页数: {pages})")

            # 使用搜索策略的严格流程
            products = self.search_strategy.search_products_strict_flow(keyword, pages)

            if products:
                print(f"✅ 严格流程搜索完成，找到 {len(products)} 个商品")
                self.data.extend(products)
                return products
            else:
                print("❌ 严格流程未找到商品")
                return []

        except Exception as e:
            print(f"❌ 严格流程搜索时出错: {e}")
            logging.error(f"严格流程搜索时出错: {e}")
            return []

    def search_products_with_process_control(self, keyword: str, pages: int = 1) -> List[Dict[str, Any]]:
        """
        使用流程控制进行搜索 - 严格按照process.txt文件的步骤执行
        :param keyword: 搜索关键词
        :param pages: 爬取页数
        :return: 商品列表
        """
        try:
            print(f"\n🔄 开始流程控制搜索: '{keyword}' (页数: {pages})")

            # 初始化流程文件
            self._init_process_file()

            all_products = []

            # 按步骤执行
            while True:
                current_step = self._get_current_step()
                if current_step is None:
                    print("✅ 所有步骤已完成")
                    break

                print(f"\n📋 当前步骤: {current_step}")

                # 执行对应的步骤
                step_success = self._execute_step(current_step, keyword)

                # 询问用户确认
                user_confirmation = self._ask_user_confirmation(current_step)

                if user_confirmation == 1:
                    # 用户确认成功，更新状态
                    self._update_process_status(current_step, 1)

                    # 如果是最后一步（搜索结果页面），提取商品信息
                    if current_step == "搜索结果页面":
                        print("🔍 开始提取商品信息...")
                        products = self._extract_products_from_current_page(keyword)
                        if products:
                            all_products.extend(products)
                            print(f"✅ 成功提取 {len(products)} 个商品")
                        else:
                            print("❌ 未提取到商品信息")
                else:
                    # 用户确认失败，保持状态为0，可以重新执行该步骤
                    print(f"⚠️ 步骤 '{current_step}' 未成功，将重新执行")

                    # 询问是否继续
                    continue_choice = input("是否继续执行该步骤？(1=继续, 0=退出): ").strip()
                    if continue_choice != '1':
                        print("❌ 用户选择退出")
                        break

            if all_products:
                print(f"✅ 流程控制搜索完成，找到 {len(all_products)} 个商品")
                self.data.extend(all_products)
                return all_products
            else:
                print("❌ 流程控制搜索未找到商品")
                return []

        except Exception as e:
            print(f"❌ 流程控制搜索时出错: {e}")
            logging.error(f"流程控制搜索时出错: {e}")
            return []

    def _execute_step(self, step_name: str, keyword: str) -> bool:
        """
        执行指定的步骤
        :param step_name: 步骤名称
        :param keyword: 搜索关键词
        :return: 是否执行成功
        """
        try:
            print(f"🔧 执行步骤: {step_name}")

            if step_name == "打开浏览器加载主页":
                # 访问主页
                self.driver.get(self.config.DEFAULT_BASE_URL)
                time.sleep(3)
                print(f"✅ 已访问主页: {self.config.DEFAULT_BASE_URL}")
                return True

            elif step_name == "清理弹窗":
                # 处理弹窗
                self.popup_handler.handle_search_page_popups_comprehensive("homepage")
                print("✅ 弹窗处理完成")
                return True

            elif step_name == "主页面":
                # 等待主页面加载完成
                self.page_handler.wait_for_page_load()
                print("✅ 主页面加载完成")
                return True

            elif step_name == "找到搜索框，输入关键词":
                # 在搜索框输入关键词
                success = self._input_search_keyword(keyword)
                if success:
                    print(f"✅ 已在搜索框输入关键词: {keyword}")
                else:
                    print(f"❌ 搜索框输入失败")
                return success

            elif step_name == "进行搜索":
                # 执行搜索
                success = self._perform_search()
                if success:
                    print("✅ 搜索执行完成")
                else:
                    print("❌ 搜索执行失败")
                return success

            elif step_name == "搜索结果页面":
                # 验证是否在搜索结果页面
                success = self.page_analyzer.is_search_results_page(keyword)
                if success:
                    print("✅ 已进入搜索结果页面")
                else:
                    print("❌ 未进入搜索结果页面")
                return success

            else:
                print(f"❌ 未知步骤: {step_name}")
                return False

        except Exception as e:
            print(f"❌ 执行步骤 '{step_name}' 时出错: {e}")
            return False

    def _extract_products_from_current_page(self, keyword: str) -> List[Dict[str, Any]]:
        """
        从当前页面提取商品信息
        :param keyword: 搜索关键词
        :return: 商品列表
        """
        try:
            print("📦 开始从当前页面提取商品信息...")

            # 等待页面加载
            self.page_handler.wait_for_page_load()

            # 处理可能的弹窗
            self.popup_handler.handle_search_page_popups_comprehensive(keyword)

            # 滚动页面加载更多商品
            print("📜 滚动页面加载更多商品...")
            self.page_handler.scroll_page_enhanced()

            # 提取商品信息
            products = self.product_extractor.extract_products_from_search_page(keyword)

            if products:
                print(f"✅ 成功提取 {len(products)} 个商品")
                return products
            else:
                print("❌ 未提取到商品信息")
                return []

        except Exception as e:
            print(f"❌ 提取商品信息时出错: {e}")
            logging.error(f"提取商品信息时出错: {e}")
            return []

    def analyze_current_page(self) -> Dict[str, Any]:
        """
        分析当前页面
        :return: 页面分析结果
        """
        try:
            return self.page_analyzer.analyze_current_page()
        except Exception as e:
            print(f"❌ 分析页面时出错: {e}")
            logging.error(f"分析页面时出错: {e}")
            return {'error': str(e)}

    def save_to_excel(self, products: List[Dict[str, Any]], keyword: str = 'products') -> str:
        """
        保存商品信息到Excel文件
        :param products: 商品列表
        :param keyword: 搜索关键词，用于生成文件名
        :return: 保存的文件路径，如果保存失败则返回空字符串
        """
        try:
            if not products:
                print("❌ 没有商品数据可保存")
                return ""

            # 使用数据导出器保存
            filename = self.data_exporter.save_to_excel(products, keyword)

            if filename:
                print(f"✅ 数据已保存到: {filename}")
                return filename
            else:
                print("❌ 保存数据失败")
                return ""

        except Exception as e:
            print(f"❌ 保存数据时出错: {e}")
            logging.error(f"保存数据时出错: {e}")
            return ""

    def save_to_json(self, products: List[Dict[str, Any]], keyword: str = 'products') -> str:
        """
        保存商品信息到JSON文件
        :param products: 商品列表
        :param keyword: 搜索关键词，用于生成文件名
        :return: 保存的文件路径，如果保存失败则返回空字符串
        """
        try:
            if not products:
                print("❌ 没有商品数据可保存")
                return ""

            # 使用数据导出器保存
            filename = self.data_exporter.save_to_json(products, keyword)

            if filename:
                print(f"✅ 数据已保存到: {filename}")
                return filename
            else:
                print("❌ 保存数据失败")
                return ""

        except Exception as e:
            print(f"❌ 保存数据时出错: {e}")
            logging.error(f"保存数据时出错: {e}")
            return ""

    def get_crawler_status(self) -> Dict[str, Any]:
        """
        获取爬虫状态信息
        :return: 状态信息字典
        """
        try:
            return {
                'driver_status': 'active' if self.driver else 'inactive',
                'current_url': self.driver.current_url if self.driver else '',
                'page_title': self.driver.title if self.driver else '',
                'data_count': len(self.data),
                'config': {
                    'base_url': self.config.DEFAULT_BASE_URL,
                    'cache_enabled': True,
                    'popup_handling_enabled': True,
                    'login_handling_enabled': True
                },
                'modules_status': {
                    'webdriver_manager': bool(self.webdriver_manager),
                    'browser_utils': bool(self.browser_utils),
                    'login_handler': bool(self.login_handler),
                    'popup_handler': bool(self.popup_handler),
                    'page_handler': bool(self.page_handler),
                    'product_extractor': bool(self.product_extractor),
                    'page_analyzer': bool(self.page_analyzer),
                    'search_strategy': bool(self.search_strategy),
                    'cache_manager': bool(self.cache_manager),
                    'data_exporter': bool(self.data_exporter)
                }
            }
        except Exception as e:
            return {'error': str(e)}

    def clear_cache(self):
        """清除缓存"""
        try:
            self.cache_manager.clear_cache()
            print("✅ 缓存已清除")
        except Exception as e:
            print(f"❌ 清除缓存时出错: {e}")
            logging.error(f"清除缓存时出错: {e}")

    def close(self):
        """关闭爬虫，释放资源"""
        try:
            if self.driver:
                self.driver.quit()
                print("✅ 浏览器已关闭")

            # 清理临时文件
            if hasattr(self.webdriver_manager, 'cleanup'):
                self.webdriver_manager.cleanup()

        except Exception as e:
            print(f"❌ 关闭爬虫时出错: {e}")
            logging.error(f"关闭爬虫时出错: {e}")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

    def _input_search_keyword(self, keyword: str) -> bool:
        """
        在搜索框输入关键词
        :param keyword: 搜索关键词
        :return: 是否成功
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # 常见的搜索框选择器
            search_selectors = [
                "input[name='keywords']",
                "input[placeholder*='搜索']",
                "input[placeholder*='请输入']",
                "input[class*='search']",
                "#search-input",
                ".search-input",
                "input[type='text']"
            ]

            for selector in search_selectors:
                try:
                    search_box = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if search_box.is_displayed():
                        search_box.clear()
                        search_box.send_keys(keyword)
                        print(f"✅ 使用选择器 {selector} 成功输入关键词")
                        return True
                except:
                    continue

            print("❌ 未找到可用的搜索框")
            return False

        except Exception as e:
            print(f"❌ 输入搜索关键词时出错: {e}")
            return False

    def _perform_search(self) -> bool:
        """
        执行搜索操作
        :return: 是否成功
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # 尝试按回车键搜索
            try:
                search_box = self.driver.find_element(By.CSS_SELECTOR, "input[name='keywords']")
                search_box.send_keys(Keys.RETURN)
                time.sleep(2)
                print("✅ 使用回车键执行搜索")
                return True
            except:
                pass

            # 尝试点击搜索按钮
            search_button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button[class*='search']",
                ".search-btn",
                "#search-btn",
                "button:contains('搜索')",
                "input[value*='搜索']"
            ]

            for selector in search_button_selectors:
                try:
                    search_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    search_btn.click()
                    time.sleep(2)
                    print(f"✅ 使用选择器 {selector} 点击搜索按钮")
                    return True
                except:
                    continue

            print("❌ 未找到可用的搜索按钮")
            return False

        except Exception as e:
            print(f"❌ 执行搜索时出错: {e}")
            return False

    def __del__(self):
        """析构函数"""
        try:
            self.close()
        except:
            pass
