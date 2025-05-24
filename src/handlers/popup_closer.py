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

    def close_iframe_popups(self) -> bool:
        """
        关闭iframe中的弹窗
        :return: True表示成功关闭，False表示失败
        """
        try:
            print("开始关闭iframe中的弹窗...")
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"找到 {len(iframes)} 个iframe")

            success = False
            for i, iframe in enumerate(iframes):
                try:
                    print(f"处理iframe {i+1}/{len(iframes)}")

                    # 切换到iframe
                    self.driver.switch_to.frame(iframe)

                    # 尝试关闭iframe中的弹窗
                    if self._close_popup_in_current_frame():
                        print(f"  成功关闭iframe {i+1} 中的弹窗")
                        success = True

                    # 切回主文档
                    self.driver.switch_to.default_content()

                except Exception as iframe_error:
                    print(f"  处理iframe {i+1} 时出错: {iframe_error}")
                    # 确保切回主文档
                    try:
                        self.driver.switch_to.default_content()
                    except:
                        pass
                    continue

            return success

        except Exception as e:
            print(f"关闭iframe弹窗时出错: {e}")
            # 确保切回主文档
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def close_iframe_popups_silent(self) -> bool:
        """静默关闭iframe中的弹窗"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            success = False

            for iframe in iframes:
                try:
                    self.driver.switch_to.frame(iframe)
                    if self._close_popup_in_current_frame_silent():
                        success = True
                    self.driver.switch_to.default_content()
                except Exception:
                    try:
                        self.driver.switch_to.default_content()
                    except:
                        pass
                    continue

            return success

        except Exception:
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def close_aibuy_popup_enhanced(self) -> bool:
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

            success = False
            for text in aibuy_texts:
                try:
                    print(f"  查找包含文本 '{text}' 的元素...")
                    xpath_selector = f"//*[contains(text(), '{text}')]"
                    elements = self.driver.find_elements(By.XPATH, xpath_selector)

                    for element in elements:
                        if element.is_displayed():
                            print(f"    找到可见元素，尝试关闭...")
                            if self._find_and_click_close_in_container(element):
                                print(f"    成功关闭包含 '{text}' 的弹窗")
                                success = True

                except Exception as e:
                    print(f"  处理文本 '{text}' 时出错: {e}")
                    continue

            # 2. 通过样式特征查找
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
                            print(f"    通过样式找到AiBUY弹窗，尝试关闭...")
                            if self._find_and_click_close_in_container(element):
                                print(f"    成功关闭样式匹配的AiBUY弹窗")
                                success = True

                except Exception as e:
                    print(f"  处理样式选择器 '{selector}' 时出错: {e}")
                    continue

            return success

        except Exception as e:
            print(f"增强AiBUY弹窗处理失败: {e}")
            return False

    def close_aibuy_popup_silent(self) -> bool:
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
                    visible_elements = [el for el in elements if el.is_displayed()]

                    for element in visible_elements:
                        element_text = element.text.lower()
                        if any(keyword in element_text for keyword in ['aibuy', '下载', '采购助手']):
                            if self._find_and_click_close_in_container_silent(element):
                                return True
                except Exception:
                    continue

            return False

        except Exception:
            return False

    def click_close_buttons_enhanced(self) -> bool:
        """
        增强的关闭按钮点击方法
        :return: True表示成功关闭，False表示失败
        """
        try:
            print("开始增强关闭按钮点击...")

            close_button_selectors = [
                # 通用关闭按钮
                "button[class*='close']",
                "span[class*='close']",
                "div[class*='close']",
                "a[class*='close']",
                # 特定的关闭按钮
                ".next-dialog-close",
                ".ui-dialog-titlebar-close",
                ".modal-close",
                ".popup-close",
                # 通过文本查找
                "button:contains('×')",
                "span:contains('×')",
                "button:contains('X')",
                "button:contains('关闭')",
                "a:contains('关闭')",
                # 通过属性查找
                "button[aria-label*='close']",
                "button[title*='关闭']",
                "button[title*='close']"
            ]

            success = False
            for selector in close_button_selectors:
                try:
                    print(f"  尝试选择器: {selector}")

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
                        print(f"    找到 {len(visible_elements)} 个可见的关闭按钮")

                        for i, button in enumerate(visible_elements[:3]):  # 最多尝试3个
                            try:
                                print(f"    点击关闭按钮 {i+1}")

                                # 尝试多种点击方式
                                if self._click_element_multiple_ways(button):
                                    print(f"    关闭按钮 {i+1} 点击成功")
                                    success = True
                                    time.sleep(1)  # 等待弹窗关闭

                            except Exception as click_error:
                                print(f"    点击关闭按钮 {i+1} 失败: {click_error}")
                                continue

                except Exception as selector_error:
                    print(f"  选择器 '{selector}' 处理失败: {selector_error}")
                    continue

            return success

        except Exception as e:
            print(f"增强关闭按钮点击失败: {e}")
            return False

    def click_close_buttons_silent(self) -> bool:
        """静默点击关闭按钮"""
        try:
            close_button_selectors = [
                "button[class*='close']", "span[class*='close']", "div[class*='close']",
                ".next-dialog-close", ".ui-dialog-titlebar-close", ".modal-close",
                "button[aria-label*='close']", "button[title*='关闭']"
            ]

            for selector in close_button_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [el for el in elements if el.is_displayed()]

                    for button in visible_elements[:2]:  # 最多尝试2个
                        try:
                            if self._click_element_multiple_ways_silent(button):
                                time.sleep(1)
                                return True
                        except Exception:
                            continue

                except Exception:
                    continue

            return False

        except Exception:
            return False

    def _close_popup_in_current_frame(self) -> bool:
        """在当前frame中关闭弹窗"""
        try:
            # 查找关闭按钮
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
                        self._click_element_multiple_ways(visible_elements[0])
                        return True
                except Exception:
                    continue

            return False

        except Exception:
            return False

    def _close_popup_in_current_frame_silent(self) -> bool:
        """静默在当前frame中关闭弹窗"""
        try:
            close_selectors = [
                "button[class*='close']", "span[class*='close']", "div[class*='close']",
                "button[aria-label*='close']", "button[title*='关闭']"
            ]

            for selector in close_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [el for el in elements if el.is_displayed()]
                    if visible_elements:
                        self._click_element_multiple_ways_silent(visible_elements[0])
                        return True
                except Exception:
                    continue

            return False

        except Exception:
            return False

    def _find_and_click_close_in_container(self, container_element) -> bool:
        """在容器元素中查找并点击关闭按钮"""
        try:
            # 在容器内查找关闭按钮
            close_selectors = [
                ".//*[contains(@class, 'close')]",
                ".//*[contains(text(), '×')]",
                ".//*[contains(text(), 'X')]",
                ".//*[contains(text(), '关闭')]",
                ".//*[contains(@aria-label, 'close')]",
                ".//*[contains(@title, '关闭')]"
            ]

            for selector in close_selectors:
                try:
                    close_buttons = container_element.find_elements(By.XPATH, selector)
                    visible_buttons = [btn for btn in close_buttons if btn.is_displayed()]

                    if visible_buttons:
                        print(f"    在容器中找到关闭按钮: {selector}")
                        if self._click_element_multiple_ways(visible_buttons[0]):
                            return True

                except Exception:
                    continue

            # 如果没找到关闭按钮，尝试点击容器本身
            try:
                print("    未找到关闭按钮，尝试点击容器")
                if self._click_element_multiple_ways(container_element):
                    return True
            except Exception:
                pass

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
                ".//*[contains(@aria-label, 'close')]"
            ]

            for selector in close_selectors:
                try:
                    close_buttons = container_element.find_elements(By.XPATH, selector)
                    visible_buttons = [btn for btn in close_buttons if btn.is_displayed()]

                    if visible_buttons:
                        if self._click_element_multiple_ways_silent(visible_buttons[0]):
                            return True
                except Exception:
                    continue

            # 尝试点击容器本身
            try:
                if self._click_element_multiple_ways_silent(container_element):
                    return True
            except Exception:
                pass

            return False

        except Exception:
            return False

    def _click_element_multiple_ways(self, element) -> bool:
        """尝试多种方式点击元素"""
        try:
            # 方法1: 普通点击
            try:
                element.click()
                print("      普通点击成功")
                return True
            except Exception:
                pass

            # 方法2: JavaScript点击
            try:
                self.driver.execute_script("arguments[0].click();", element)
                print("      JavaScript点击成功")
                return True
            except Exception:
                pass

            # 方法3: ActionChains点击
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(element).click().perform()
                print("      ActionChains点击成功")
                return True
            except Exception:
                pass

            # 方法4: 发送回车键
            try:
                element.send_keys(Keys.RETURN)
                print("      回车键成功")
                return True
            except Exception:
                pass

            return False

        except Exception:
            return False

    def _click_element_multiple_ways_silent(self, element) -> bool:
        """静默尝试多种方式点击元素"""
        try:
            # 普通点击
            try:
                element.click()
                return True
            except Exception:
                pass

            # JavaScript点击
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                pass

            # ActionChains点击
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(element).click().perform()
                return True
            except Exception:
                pass

            # 发送回车键
            try:
                element.send_keys(Keys.RETURN)
                return True
            except Exception:
                pass

            return False

        except Exception:
            return False