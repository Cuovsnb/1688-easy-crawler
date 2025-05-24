"""
页面处理模块

负责页面滚动、等待、验证和交互等功能
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from typing import Optional

from ..core.config import CrawlerConfig
from ..utils.helpers import save_page_source, get_random_delay


class PageHandler:
    """页面处理器"""
    
    def __init__(self, driver: webdriver.Chrome, config: CrawlerConfig = None):
        """
        初始化页面处理器
        :param driver: WebDriver实例
        :param config: 爬虫配置对象
        """
        self.driver = driver
        self.config = config or CrawlerConfig()
    
    def scroll_page_enhanced(self) -> bool:
        """
        增强的页面滚动功能
        :return: 是否成功滚动
        """
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
                
                # 尝试触发更多内容加载
                try:
                    # 1. 查找并点击"加载更多"按钮
                    load_more_selectors = [
                        "button:contains('加载更多')",
                        "a:contains('加载更多')",
                        "button:contains('更多')",
                        ".load-more",
                        ".more-btn",
                        ".next-page"
                    ]
                    
                    load_more_clicked = False
                    for selector in load_more_selectors:
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
                                print(f"找到加载更多按钮: {selector}")
                                visible_elements[0].click()
                                load_more_clicked = True
                                time.sleep(2)
                                break
                        except Exception:
                            continue
                    
                    # 2. 如果没有找到加载更多按钮，尝试模拟滚动触发无限滚动
                    if not load_more_clicked:
                        print("未找到加载更多按钮，尝试模拟用户滚动行为...")
                        # 模拟真实用户的滚动行为
                        for micro_scroll in range(3):
                            scroll_position = self.driver.execute_script("return window.pageYOffset;")
                            self.driver.execute_script(f"window.scrollTo(0, {scroll_position + 200});")
                            time.sleep(0.5)
                        
                        # 滚动到底部并等待
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        
                        # 再次尝试小幅滚动
                        self.driver.execute_script("window.scrollBy(0, 100);")
                        time.sleep(1)
                        self.driver.execute_script("window.scrollBy(0, -50);")
                        time.sleep(1)
                
                except Exception as e:
                    print(f"尝试触发更多内容加载时出错: {e}")
                
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
            logging.error(f"增强滚动时出错: {e}")
            return False
    
    def scroll_page_basic(self) -> bool:
        """
        基础页面滚动功能
        :return: 是否成功滚动
        """
        try:
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
            
            # 滚动回页面顶部
            self.driver.execute_script("window.scrollTo(0, 0);")
            print("滚动完成，已回到页面顶部")
            
            return True
            
        except Exception as e:
            print(f"滚动页面时出错: {e}")
            logging.error(f"滚动页面时出错: {e}")
            return False
    
    def wait_for_element(self, selector: str, timeout: int = None) -> bool:
        """
        等待元素出现
        :param selector: CSS选择器
        :param timeout: 超时时间（秒），如果为None则使用配置中的默认值
        :return: 是否找到元素
        """
        timeout = timeout or self.config.TIMEOUTS['element_wait']
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except TimeoutException:
            print(f"等待元素超时: {selector}")
            return False
    
    def wait_for_page_load(self, timeout: int = None) -> bool:
        """
        等待页面加载完成
        :param timeout: 超时时间（秒），如果为None则使用配置中的默认值
        :return: 是否加载完成
        """
        timeout = timeout or self.config.TIMEOUTS['page_load']
        
        try:
            # 等待页面加载状态为complete
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            print("页面加载完成")
            return True
        except TimeoutException:
            print(f"页面加载超时（{timeout}秒）")
            return False
    
    def check_captcha(self) -> bool:
        """
        检查页面是否有验证码或需要手动处理的情况
        :return: True表示需要手动处理，False表示可以继续自动化
        """
        try:
            print("检查页面是否有验证码或需要手动处理的情况...")
            
            # 1. 检查滑动验证码
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
                    save_page_source(self.driver, "captcha_detected.html", self.config.PATHS['html_debug'])
                    return True  # 表明需要手动干预
            
            # 2. 检查iframe中的验证码
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
                            save_page_source(self.driver, "iframe_captcha_detected.html", self.config.PATHS['html_debug'])
                            return True  # 表明需要手动干预
                    except:
                        pass
                    finally:
                        # 切回主文档
                        self.driver.switch_to.default_content()
            except Exception as e:
                print(f"检查iframe时出错: {e}")
            
            # 3. 检查页面是否重定向到登录页
            current_url = self.driver.current_url.lower()
            for url in self.config.LOGIN_INDICATORS['url_keywords']:
                if url in current_url:
                    print(f"检测到页面已重定向到登录相关URL: {current_url}")
                    save_page_source(self.driver, "login_page_redirect_detected.html", self.config.PATHS['html_debug'])
                    return True  # 表明需要手动干预
            
            return False
            
        except Exception as e:
            error_msg = f"检查验证码时出错: {e}"
            print(error_msg)
            logging.error(error_msg, exc_info=True)
            # 保存当前页面用于调试
            save_page_source(self.driver, "captcha_error.html", self.config.PATHS['html_debug'])
            return False
    
    def verify_search_results_page(self, keyword: str, is_subsequent_page: bool = False) -> bool:
        """
        验证当前页面是否为有效的搜索结果页面
        :param keyword: 搜索关键词
        :param is_subsequent_page: 是否为后续页面（非首页）
        :return: 是否为有效的搜索结果页面
        """
        try:
            print(f"验证搜索结果页面 (关键词: '{keyword}', 后续页面: {is_subsequent_page})")
            
            current_url = self.driver.current_url
            page_title = self.driver.title
            print(f"当前URL: {current_url}")
            print(f"页面标题: {page_title}")
            
            # 1. 检查URL路径是否正确
            is_correct_path = False
            search_path_indicators = [
                '/s/offer_search.htm',
                '/offer_search',
                '/search',
                '/s/',
                'offer_search'
            ]
            
            for indicator in search_path_indicators:
                if indicator in current_url:
                    print(f"✅ URL路径验证通过: {indicator}")
                    is_correct_path = True
                    break
            
            if not is_correct_path and not is_subsequent_page:
                print("❌ URL路径验证失败，不是搜索结果页面")
            
            # 2. 检查关键词是否在URL或页面中
            keyword_present = False
            if keyword.lower() in current_url.lower() or keyword.lower() in page_title.lower():
                print(f"✅ 关键词验证通过: '{keyword}' 在URL或标题中")
                keyword_present = True
            else:
                print(f"❌ 关键词验证失败: '{keyword}' 不在URL或标题中")
            
            # 3. 检查是否有商品列表元素
            product_list_found = False
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
                print("✅ 商品列表容器验证通过")
                product_list_found = True
            except TimeoutException:
                current_url_for_debug = self.driver.current_url
                page_title_for_debug = self.driver.title
                print(f"❌ 超时：等待商品列表容器元素超时。URL: {current_url_for_debug}, Title: {page_title_for_debug}")
                if not is_subsequent_page:  # 如果是首次加载搜索页，这通常意味着失败
                    save_page_source(self.driver, f"timeout_no_product_container_initial_{keyword}.html", self.config.PATHS['html_debug'])
                    return False
                # 对于后续页面，可能是最后一页无商品，允许继续其他检查
                print("后续页面未找到商品列表容器，可能为空页或最后一页。")
            
            # 综合判断
            final_verdict = (is_correct_path or is_subsequent_page) and keyword_present and product_list_found
            # 对于后续页面，如果路径和关键词仍在，但列表为空（可能是最后一页），也算通过
            if is_subsequent_page and (is_correct_path and keyword_present) and not product_list_found:
                print("后续页面，路径和关键词匹配但未找到商品列表元素，可能为空页或最后一页，暂时通过。")
                final_verdict = True
            
            print(f"搜索结果页验证结果: {final_verdict}")
            return final_verdict
            
        except Exception as e:
            print(f"验证搜索结果页面时出错: {e}")
            logging.error(f"验证搜索结果页面时出错: {e}")
            return False
    
    def go_to_next_page(self) -> bool:
        """
        跳转到下一页
        :return: 是否成功跳转
        """
        try:
            next_page_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".fui-next"))
            )
            next_page_btn.click()
            print("✅ 成功点击下一页按钮")
            return True
        except TimeoutException:
            print("❌ 未找到下一页按钮或按钮不可点击")
            return False
        except Exception as e:
            print(f"❌ 跳转下一页时出错: {e}")
            logging.error(f"跳转下一页时出错: {e}")
            return False
