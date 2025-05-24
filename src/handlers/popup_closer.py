"""
弹窗关闭方法模块

包含各种弹窗关闭的具体实现方法
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from typing import List

from ..core.config import CrawlerConfig


class PopupCloser:
    """弹窗关闭器"""

    def __init__(self, driver: webdriver.Chrome, config: CrawlerConfig = None):
        """
        初始化弹窗关闭器
        :param driver: WebDriver实例
        :param config: 爬虫配置对象
        """
        self.driver = driver
        self.config = config or CrawlerConfig()

    def close_iframe_popups(self, silent: bool = False) -> bool:
        """
        关闭iframe中的弹窗
        :param silent: 是否以静默模式运行 (不打印日志)
        :return: True表示成功关闭，False表示失败
        """
        try:
            if not silent:
                print("开始关闭iframe中的弹窗...")
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            if not silent:
                print(f"找到 {len(iframes)} 个iframe")

            success = False
            for i, iframe in enumerate(iframes):
                try:
                    if not silent:
                        print(f"处理iframe {i+1}/{len(iframes)}")
                    self.driver.switch_to.frame(iframe)
                    if self._close_popup_in_current_frame(silent=silent):
                        if not silent:
                            print(f"  成功关闭iframe {i+1} 中的弹窗")
                        success = True
                    self.driver.switch_to.default_content()
                except Exception as iframe_error:
                    if not silent:
                        print(f"  处理iframe {i+1} 时出错: {iframe_error}")
                    try:
                        self.driver.switch_to.default_content()
                    except:
                        pass
                    continue
            return success
        except Exception as e:
            if not silent:
                print(f"关闭iframe弹窗时出错: {e}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def close_iframe_popups_silent(self) -> bool:
        """静默关闭iframe中的弹窗"""
        return self.close_iframe_popups(silent=True)

    def close_aibuy_popup_enhanced(self, silent: bool = False) -> bool:
        """
        增强的AiBUY弹窗处理方法
        :param silent: 是否以静默模式运行 (不打印日志)
        :return: True表示成功关闭，False表示失败
        """
        try:
            if not silent:
                print("开始增强AiBUY弹窗处理...")
            aibuy_texts = [
                '1688AiBUY', '1688 AiBUY', 'AiBUY',
                '官方跨境采购助手', '官方跨境采购助手来了',
                '立即下载', '汇聚转化', '跨境同款'
            ]
            success = False
            for text in aibuy_texts:
                try:
                    if not silent:
                        print(f"  查找包含文本 '{text}' 的元素...")
                    xpath_selector = f"//*[contains(text(), '{text}')]"
                    elements = self.driver.find_elements(By.XPATH, xpath_selector)
                    for element in elements:
                        if element.is_displayed():
                            if not silent:
                                print(f"    找到可见元素，尝试关闭...")
                            if self._find_and_click_close_in_container(element, silent=silent):
                                if not silent:
                                    print(f"    成功关闭包含 '{text}' 的弹窗")
                                success = True
                except Exception as e:
                    if not silent:
                        print(f"  处理文本 '{text}' 时出错: {e}")
                    continue
            if not silent:
                print("  通过样式特征查找AiBUY弹窗...")
            style_selectors = [
                "div[style*='position: fixed'][style*='z-index']",
                "div[style*='position: absolute'][style*='z-index']",
                "div[style*='position: fixed'][style*='top']"
            ]
            for selector in style_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [el for el in elements if el.is_displayed()]
                    for element in visible_elements:
                        element_text = element.text.lower()
                        if any(keyword in element_text for keyword in ['aibuy', '下载', '采购助手']):
                            if not silent:
                                print(f"    通过样式找到AiBUY弹窗，尝试关闭...")
                            if self._find_and_click_close_in_container(element, silent=silent):
                                if not silent:
                                    print(f"    成功关闭样式匹配的AiBUY弹窗")
                                success = True
                except Exception as e:
                    if not silent:
                        print(f"  处理样式选择器 '{selector}' 时出错: {e}")
                    continue
            return success
        except Exception as e:
            if not silent:
                print(f"增强AiBUY弹窗处理失败: {e}")
            return False

    def close_aibuy_popup_silent(self) -> bool:
        """静默处理AiBUY弹窗"""
        return self.close_aibuy_popup_enhanced(silent=True)

    def click_close_buttons_enhanced(self, silent: bool = False) -> bool:
        """
        增强的关闭按钮点击方法
        :param silent: 是否以静默模式运行 (不打印日志)
        :return: True表示成功关闭，False表示失败
        """
        try:
            if not silent:
                print("开始增强关闭按钮点击...")
            close_button_selectors = [
                "button[class*='close']", "span[class*='close']", "div[class*='close']", "a[class*='close']",
                ".next-dialog-close", ".ui-dialog-titlebar-close", ".modal-close", ".popup-close",
                "button:contains('×')", "span:contains('×')", "button:contains('X')",
                "button:contains('关闭')", "a:contains('关闭')",
                "button[aria-label*='close']", "button[title*='关闭']", "button[title*='close']"
            ]
            success = False
            for selector in close_button_selectors:
                try:
                    if not silent:
                        print(f"  尝试选择器: {selector}")
                    if ":contains(" in selector:
                        text = selector.split(":contains('")[1].split("')")[0]
                        tag = selector.split(":contains(")[0]
                        xpath_selector = f"//{tag}[contains(text(), '{text}')]"
                        elements = self.driver.find_elements(By.XPATH, xpath_selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [el for el in elements if el.is_displayed()]
                    if visible_elements:
                        if not silent:
                            print(f"    找到 {len(visible_elements)} 个可见的关闭按钮")
                        for i, button in enumerate(visible_elements[:3]):
                            try:
                                if not silent:
                                    print(f"    点击关闭按钮 {i+1}")
                                if self._click_element_multiple_ways(button, silent=silent):
                                    if not silent:
                                        print(f"    关闭按钮 {i+1} 点击成功")
                                    success = True
                                    time.sleep(1)
                            except Exception as click_error:
                                if not silent:
                                    print(f"    点击关闭按钮 {i+1} 失败: {click_error}")
                                continue
                except Exception as selector_error:
                    if not silent:
                        print(f"  选择器 '{selector}' 处理失败: {selector_error}")
                    continue
            return success
        except Exception as e:
            if not silent:
                print(f"增强关闭按钮点击失败: {e}")
            return False

    def click_close_buttons_silent(self) -> bool:
        """静默点击关闭按钮"""
        return self.click_close_buttons_enhanced(silent=True)

    def _close_popup_in_current_frame(self, silent: bool = False) -> bool:
        """在当前frame中关闭弹窗"""
        try:
            close_selectors = [
                "button[class*='close']", "span[class*='close']", "div[class*='close']",
                "button:contains('×')", "span:contains('×')", "button:contains('X')",
                "button:contains('关闭')", "a:contains('关闭')"
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
                    visible_elements = [el for el in elements if el.is_displayed()]
                    if visible_elements:
                        if self._click_element_multiple_ways(visible_elements[0], silent=silent):
                            return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def _close_popup_in_current_frame_silent(self) -> bool:
        """静默在当前frame中关闭弹窗"""
        return self._close_popup_in_current_frame(silent=True)

    def _find_and_click_close_in_container(self, container_element, silent: bool = False) -> bool:
        """在容器元素中查找并点击关闭按钮"""
        try:
            close_selectors = [
                ".//*[contains(@class, 'close')]", ".//*[contains(text(), '×')]", ".//*[contains(text(), 'X')]",
                ".//*[contains(text(), '关闭')]", ".//*[contains(@aria-label, 'close')]", ".//*[contains(@title, '关闭')]"
            ]
            for selector in close_selectors:
                try:
                    close_buttons = container_element.find_elements(By.XPATH, selector)
                    visible_buttons = [btn for btn in close_buttons if btn.is_displayed()]
                    if visible_buttons:
                        if not silent:
                            print(f"    在容器中找到关闭按钮: {selector}")
                        if self._click_element_multiple_ways(visible_buttons[0], silent=silent):
                            return True
                except Exception:
                    continue
            try:
                if not silent:
                    print("    未找到关闭按钮，尝试点击容器")
                if self._click_element_multiple_ways(container_element, silent=silent):
                    return True
            except Exception:
                pass
            return False
        except Exception:
            return False

    def _find_and_click_close_in_container_silent(self, container_element) -> bool:
        """静默在容器元素中查找并点击关闭按钮"""
        return self._find_and_click_close_in_container(container_element, silent=True)

    def _click_element_multiple_ways(self, element, silent: bool = False) -> bool:
        """尝试多种方式点击元素"""
        try:
            try:
                element.click()
                if not silent: print("      普通点击成功")
                return True
            except Exception: pass
            try:
                self.driver.execute_script("arguments[0].click();", element)
                if not silent: print("      JavaScript点击成功")
                return True
            except Exception: pass
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(element).click().perform()
                if not silent: print("      ActionChains点击成功")
                return True
            except Exception: pass
            try:
                element.send_keys(Keys.RETURN)
                if not silent: print("      回车键成功")
                return True
            except Exception: pass
            return False
        except Exception:
            return False

    def _click_element_multiple_ways_silent(self, element) -> bool:
        """静默尝试多种方式点击元素"""
        return self._click_element_multiple_ways(element, silent=True)