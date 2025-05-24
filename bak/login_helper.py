import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginHelper:
    """
    1688登录助手
    """
    
    def __init__(self, driver):
        self.driver = driver
    
    def is_login_page(self) -> bool:
        """检查当前是否是登录页面"""
        try:
            return "login.taobao.com" in self.driver.current_url or "login.1688.com" in self.driver.current_url
        except:
            return False
    
    def handle_login(self, username: str = None, password: str = None, timeout: int = 60):
        """
        处理登录页面
        :param username: 用户名（可选）
        :param password: 密码（可选）
        :param timeout: 登录超时时间（秒）
        :return: 是否登录成功
        """
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
                try:
                    error_msg = self.driver.find_element(By.CSS_SELECTOR, ".error-message, .error-msg, .msg-error")
                    if error_msg and error_msg.is_displayed():
                        print(f"\n登录错误: {error_msg.text}")
                except:
                    pass
                    
                # 检查是否需要验证码
                try:
                    captcha = self.driver.find_element(By.CSS_SELECTOR, ".nc-container, .captcha-container")
                    if captcha and captcha.is_displayed():
                        print("\n=== 需要完成验证码验证 ===")
                except:
                    pass
                    
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
                with open("login_error.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("\n已保存登录页面到 login_error.html 用于调试")
                
                return False
            
            return True
            
        except Exception as e:
            print(f"\n登录过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
