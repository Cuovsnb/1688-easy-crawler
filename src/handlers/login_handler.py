"""
登录处理模块

负责检测和处理登录相关的页面和弹窗
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional

from ..core.config import CrawlerConfig
from ..utils.helpers import save_page_source


class LoginHandler:
    """登录处理器"""
    
    def __init__(self, driver: webdriver.Chrome, config: CrawlerConfig = None):
        """
        初始化登录处理器
        :param driver: WebDriver实例
        :param config: 爬虫配置对象
        """
        self.driver = driver
        self.config = config or CrawlerConfig()
    
    def is_login_page(self) -> bool:
        """
        检查当前是否是登录页面
        :return: True表示是登录页面
        """
        try:
            current_url = self.driver.current_url.lower()
            page_title = self.driver.title.lower()
            
            # 检查URL中的登录相关关键词
            for indicator in self.config.LOGIN_INDICATORS['url_keywords']:
                if indicator in current_url:
                    print(f"检测到登录页面URL关键词: {indicator}")
                    return True
            
            # 检查标题中的登录相关关键词
            for keyword in self.config.LOGIN_INDICATORS['title_keywords']:
                if keyword in page_title:
                    print(f"检测到登录页面标题关键词: {keyword}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"检查登录页面时出错: {e}")
            logging.error(f"检查登录页面时出错: {e}")
            return False
    
    def is_redirected_to_login(self) -> bool:
        """
        检查当前页面是否被重定向到登录页面（增强版）
        :return: True表示是登录页面，False表示不是
        """
        try:
            current_url = self.driver.current_url.lower()
            page_title = self.driver.title.lower()
            
            # 检查URL
            for keyword in self.config.LOGIN_INDICATORS['url_keywords']:
                if keyword in current_url:
                    print(f"检测到登录页面URL关键词: {keyword}")
                    return True
            
            # 检查标题
            for keyword in self.config.LOGIN_INDICATORS['title_keywords']:
                if keyword in page_title:
                    print(f"检测到登录页面标题关键词: {keyword}")
                    return True
            
            # 检查页面元素
            login_selectors = [
                "input[type='password']",  # 密码输入框
                "div.login-dialog-wrap",   # 1688登录弹窗
                "form[action*='login']",   # 登录表单
                "div[class*='login']",     # 登录相关div
                "button[class*='login']",  # 登录按钮
                "a[href*='login']"         # 登录链接
            ]
            
            login_elements_found = 0
            for selector in login_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [el for el in elements if el.is_displayed()]
                    if visible_elements:
                        login_elements_found += 1
                        print(f"检测到登录页面元素: {selector} (共{len(visible_elements)}个)")
                except:
                    continue
            
            # 如果找到2个或以上登录相关元素，认为是登录页面
            if login_elements_found >= 2:
                print(f"检测到{login_elements_found}个登录相关元素，判定为登录页面")
                return True
            
            return False
            
        except Exception as e:
            print(f"检查登录页面时出错: {e}")
            logging.error(f"检查登录页面时出错: {e}")
            return False
    
    def handle_login(self, username: Optional[str] = None, password: Optional[str] = None, 
                    timeout: int = None) -> bool:
        """
        处理登录页面
        :param username: 用户名（可选）
        :param password: 密码（可选）
        :param timeout: 登录超时时间（秒），如果为None则使用配置中的默认值
        :return: 是否登录成功
        """
        timeout = timeout or self.config.TIMEOUTS['login_timeout']
        
        if not self.is_login_page():
            print("当前页面不是登录页面，无需登录")
            return True
        
        print("\n=== 检测到登录页面 ===")
        print("请按照以下步骤操作：")
        print("1. 在浏览器中完成登录")
        print(f"2. 您有 {timeout} 秒时间完成登录")
        print("3. 登录成功后程序会自动继续\n")
        
        # 保存当前URL用于检测页面变化
        current_url = self.driver.current_url
        
        try:
            # 等待页面URL变化或超时
            start_time = time.time()
            while time.time() - start_time < timeout:
                if not self.is_login_page() and self.driver.current_url != current_url:
                    print("\n=== 登录成功 ===")
                    print(f"已重定向到: {self.driver.current_url}")
                    time.sleep(2)  # 等待页面完全加载
                    return True
                
                # 检查是否有验证码或其他提示
                self._check_login_errors()
                self._check_captcha_requirement()
                
                time.sleep(1)  # 每秒检查一次
                
                # 显示剩余时间
                remaining = int(timeout - (time.time() - start_time))
                if remaining % 10 == 0 and remaining > 0:
                    print(f"剩余时间: {remaining}秒...")
            
            # 检查最终状态
            if self.is_login_page():
                print("\n=== 登录超时 ===")
                print("可能的原因：")
                print("1. 未在指定时间内完成登录")
                print("2. 需要验证码但未处理")
                print("3. 登录信息有误")
                print("4. 网络连接问题")
                
                # 保存当前页面用于调试
                save_page_source(self.driver, "login_error.html", self.config.PATHS['html_debug'])
                print("\n已保存登录页面用于调试")
                
                return False
            
            return True
            
        except Exception as e:
            print(f"\n登录过程中发生错误: {str(e)}")
            logging.error(f"登录过程中发生错误: {e}", exc_info=True)
            return False
    
    def _check_login_errors(self):
        """检查登录错误信息"""
        try:
            error_selectors = [
                ".error-message", ".error-msg", ".msg-error",
                ".login-error", ".alert-error", ".notice-error"
            ]
            
            for selector in error_selectors:
                try:
                    error_msg = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if error_msg and error_msg.is_displayed():
                        print(f"\n登录错误: {error_msg.text}")
                        break
                except:
                    continue
                    
        except Exception:
            pass
    
    def _check_captcha_requirement(self):
        """检查是否需要验证码"""
        try:
            captcha_selectors = [
                ".nc-container", ".captcha-container", ".captcha-box",
                ".verify-code", ".verification-code", ".slider-verify"
            ]
            
            for selector in captcha_selectors:
                try:
                    captcha = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if captcha and captcha.is_displayed():
                        print("\n=== 需要完成验证码验证 ===")
                        return True
                except:
                    continue
                    
            return False
            
        except Exception:
            return False
    
    def detect_login_modal(self) -> bool:
        """
        检测登录弹窗
        :return: True表示检测到登录弹窗
        """
        try:
            login_modal_selectors = [
                ".login-dialog", ".J_LoginBox", ".login-container",
                ".login-wrap", ".login-dialog-container", ".login-box",
                ".login-modal", ".sign-flow", ".sign-flow-dialog",
                ".next-dialog", ".next-overlay-wrapper", ".sufei-dialog"
            ]
            
            for selector in login_modal_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_modals = [el for el in elements if el.is_displayed()]
                    if visible_modals:
                        print(f"检测到可见的登录弹窗: {selector}")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"检测登录弹窗时出错: {e}")
            logging.error(f"检测登录弹窗时出错: {e}")
            return False
    
    def wait_for_login_completion(self, timeout: int = None) -> bool:
        """
        等待登录完成
        :param timeout: 超时时间（秒）
        :return: 是否登录成功
        """
        timeout = timeout or self.config.TIMEOUTS['login_timeout']
        
        try:
            # 使用WebDriverWait等待页面不再是登录页面
            wait = WebDriverWait(self.driver, timeout)
            
            def not_login_page(driver):
                return not self.is_login_page()
            
            wait.until(not_login_page)
            print("✅ 登录完成")
            return True
            
        except Exception as e:
            print(f"等待登录完成超时: {e}")
            return False
    
    def auto_fill_login(self, username: str, password: str) -> bool:
        """
        自动填写登录信息（如果可能）
        :param username: 用户名
        :param password: 密码
        :return: 是否成功填写
        """
        try:
            # 查找用户名输入框
            username_selectors = [
                "input[name='username']", "input[name='loginId']",
                "input[name='account']", "input[type='text']",
                "input[placeholder*='用户名']", "input[placeholder*='账号']"
            ]
            
            username_input = None
            for selector in username_selectors:
                try:
                    username_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if username_input.is_displayed():
                        break
                except:
                    continue
            
            if not username_input:
                print("未找到用户名输入框")
                return False
            
            # 查找密码输入框
            password_input = None
            try:
                password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            except:
                print("未找到密码输入框")
                return False
            
            # 填写登录信息
            username_input.clear()
            username_input.send_keys(username)
            time.sleep(0.5)
            
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(0.5)
            
            print("✅ 已自动填写登录信息")
            return True
            
        except Exception as e:
            print(f"自动填写登录信息失败: {e}")
            logging.error(f"自动填写登录信息失败: {e}")
            return False
