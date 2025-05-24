"""
浏览器工具模块

提供标签页管理、页面导航等浏览器相关的工具功能
"""

import time
from selenium import webdriver
from typing import Dict, Optional


class BrowserUtils:
    """浏览器工具类"""
    
    def __init__(self, driver: webdriver.Chrome):
        """
        初始化浏览器工具
        :param driver: WebDriver实例
        """
        self.driver = driver
    
    def open_new_tab(self) -> Optional[str]:
        """
        打开新标签页
        :return: 新标签页的窗口句柄，失败返回None
        """
        try:
            # 保存当前窗口句柄
            original_window = self.driver.current_window_handle
            
            # 打开新标签页
            self.driver.execute_script("window.open('');")
            
            # 获取所有窗口句柄
            all_windows = self.driver.window_handles
            
            # 找到新打开的窗口
            new_window = None
            for window in all_windows:
                if window != original_window:
                    new_window = window
                    break
            
            if new_window:
                print(f"✅ 成功打开新标签页: {new_window}")
                return new_window
            else:
                print("❌ 未能找到新标签页")
                return None
                
        except Exception as e:
            print(f"❌ 打开新标签页失败: {e}")
            return None
    
    def switch_to_tab(self, window_handle: str) -> bool:
        """
        切换到指定标签页
        :param window_handle: 窗口句柄
        :return: 是否成功切换
        """
        try:
            self.driver.switch_to.window(window_handle)
            print(f"✅ 成功切换到标签页: {window_handle}")
            return True
        except Exception as e:
            print(f"❌ 切换标签页失败: {e}")
            return False
    
    def close_tab(self, window_handle: str) -> bool:
        """
        关闭指定标签页
        :param window_handle: 窗口句柄
        :return: 是否成功关闭
        """
        try:
            # 切换到要关闭的标签页
            self.driver.switch_to.window(window_handle)
            # 关闭当前标签页
            self.driver.close()
            print(f"✅ 成功关闭标签页: {window_handle}")
            return True
        except Exception as e:
            print(f"❌ 关闭标签页失败: {e}")
            return False
    
    def get_current_tab_info(self) -> Dict[str, str]:
        """
        获取当前标签页信息
        :return: 包含URL、标题等信息的字典
        """
        try:
            return {
                'window_handle': self.driver.current_window_handle,
                'url': self.driver.current_url,
                'title': self.driver.title
            }
        except Exception as e:
            print(f"获取标签页信息失败: {e}")
            return {}
    
    def get_all_tabs(self) -> list:
        """
        获取所有标签页的窗口句柄
        :return: 窗口句柄列表
        """
        try:
            return self.driver.window_handles
        except Exception as e:
            print(f"获取标签页列表失败: {e}")
            return []
    
    def close_all_tabs_except_current(self):
        """关闭除当前标签页外的所有标签页"""
        try:
            current_handle = self.driver.current_window_handle
            all_handles = self.driver.window_handles
            
            for handle in all_handles:
                if handle != current_handle:
                    self.close_tab(handle)
                    
            # 确保切换回当前标签页
            self.switch_to_tab(current_handle)
            print("✅ 已关闭其他所有标签页")
            
        except Exception as e:
            print(f"❌ 关闭其他标签页失败: {e}")
    
    def navigate_to_url(self, url: str, wait_time: int = 3) -> bool:
        """
        导航到指定URL
        :param url: 目标URL
        :param wait_time: 等待时间（秒）
        :return: 是否成功导航
        """
        try:
            print(f"导航到: {url}")
            self.driver.get(url)
            time.sleep(wait_time)
            
            current_url = self.driver.current_url
            print(f"当前URL: {current_url}")
            return True
            
        except Exception as e:
            print(f"❌ 导航失败: {e}")
            return False
    
    def refresh_page(self, wait_time: int = 3):
        """
        刷新当前页面
        :param wait_time: 刷新后等待时间（秒）
        """
        try:
            print("刷新页面...")
            self.driver.refresh()
            time.sleep(wait_time)
            print("✅ 页面刷新完成")
        except Exception as e:
            print(f"❌ 页面刷新失败: {e}")
    
    def go_back(self, wait_time: int = 3):
        """
        返回上一页
        :param wait_time: 返回后等待时间（秒）
        """
        try:
            print("返回上一页...")
            self.driver.back()
            time.sleep(wait_time)
            print("✅ 已返回上一页")
        except Exception as e:
            print(f"❌ 返回上一页失败: {e}")
    
    def go_forward(self, wait_time: int = 3):
        """
        前进到下一页
        :param wait_time: 前进后等待时间（秒）
        """
        try:
            print("前进到下一页...")
            self.driver.forward()
            time.sleep(wait_time)
            print("✅ 已前进到下一页")
        except Exception as e:
            print(f"❌ 前进失败: {e}")
    
    def set_window_size(self, width: int = 1920, height: int = 1080):
        """
        设置窗口大小
        :param width: 窗口宽度
        :param height: 窗口高度
        """
        try:
            self.driver.set_window_size(width, height)
            print(f"✅ 窗口大小已设置为: {width}x{height}")
        except Exception as e:
            print(f"❌ 设置窗口大小失败: {e}")
    
    def maximize_window(self):
        """最大化窗口"""
        try:
            self.driver.maximize_window()
            print("✅ 窗口已最大化")
        except Exception as e:
            print(f"❌ 最大化窗口失败: {e}")
    
    def minimize_window(self):
        """最小化窗口"""
        try:
            self.driver.minimize_window()
            print("✅ 窗口已最小化")
        except Exception as e:
            print(f"❌ 最小化窗口失败: {e}")
    
    def execute_script(self, script: str, *args):
        """
        执行JavaScript脚本
        :param script: JavaScript代码
        :param args: 脚本参数
        :return: 脚本执行结果
        """
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            print(f"❌ 执行脚本失败: {e}")
            return None
    
    def scroll_to_top(self):
        """滚动到页面顶部"""
        self.execute_script("window.scrollTo(0, 0);")
        print("✅ 已滚动到页面顶部")
    
    def scroll_to_bottom(self):
        """滚动到页面底部"""
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("✅ 已滚动到页面底部")
    
    def scroll_by_pixels(self, x: int = 0, y: int = 500):
        """
        按像素滚动
        :param x: 水平滚动像素
        :param y: 垂直滚动像素
        """
        self.execute_script(f"window.scrollBy({x}, {y});")
        print(f"✅ 已滚动 ({x}, {y}) 像素")
