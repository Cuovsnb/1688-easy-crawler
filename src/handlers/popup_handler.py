"""
弹窗处理模块

负责检测和关闭各种类型的弹窗和广告
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from typing import List, Optional

from ..core.config import CrawlerConfig
from ..utils.helpers import save_page_source
from .popup_closer import PopupCloser


class PopupHandler:
    """弹窗处理器"""

    def __init__(self, driver: webdriver.Chrome, config: CrawlerConfig = None):
        """
        初始化弹窗处理器
        :param driver: WebDriver实例
        :param config: 爬虫配置对象
        """
        self.driver = driver
        self.config = config or CrawlerConfig()
        self.closer = PopupCloser(driver, config)

    def detect_popups(self, save_debug: bool = True) -> bool:
        """
        增强的弹窗检测，包括iframe检测和详细的调试信息
        :param save_debug: 是否保存调试信息
        :return: True表示检测到弹窗，False表示未检测到
        """
        try:
            print("开始增强弹窗检测...")

            if save_debug:
                # 保存页面源码用于调试
                save_page_source(self.driver, "popup_detection_debug.html", self.config.PATHS['html_debug'])
                print("已保存页面源码用于调试")

            # 1. 检测iframe中的弹窗
            print("检测iframe中的弹窗...")
            iframe_popup_found = self._detect_iframe_popups()
            if iframe_popup_found:
                print("在iframe中检测到弹窗")
                return True

            # 2. 检测主页面弹窗
            print("检测主页面弹窗...")
            main_popup_found = self._detect_main_page_popups()
            if main_popup_found:
                print("在主页面检测到弹窗")
                return True

            print("未检测到明显的弹窗元素")
            return False

        except Exception as e:
            print(f"检测弹窗时出错: {e}")
            logging.error(f"检测弹窗时出错: {e}")
            return False

    def detect_popups_silent(self) -> bool:
        """
        静默的弹窗检测，不输出详细信息
        :return: True表示检测到弹窗，False表示未检测到
        """
        try:
            # 1. 检测iframe中的弹窗
            if self._detect_iframe_popups_silent():
                return True

            # 2. 检测主页面弹窗
            if self._detect_main_page_popups_silent():
                return True

            return False

        except Exception:
            return False

    def close_popups_enhanced(self, save_debug: bool = True) -> bool:
        """
        增强的弹窗关闭方法，包括多种关闭策略和iframe处理
        :param save_debug: 是否保存调试信息
        :return: True表示成功关闭，False表示失败
        """
        try:
            print("开始增强弹窗关闭流程...")
            success = False

            if save_debug:
                # 保存关闭前的页面状态
                save_page_source(self.driver, "before_close_popup.html", self.config.PATHS['html_debug'])
                print("已保存关闭前页面状态")

            # 方法1: 处理iframe中的弹窗
            print("方法1: 尝试处理iframe中的弹窗...")
            if self.closer.close_iframe_popups():
                print("iframe弹窗关闭成功")
                success = True

            # 方法2: 专门处理AiBUY弹窗
            print("方法2: 尝试专门处理AiBUY弹窗...")
            if self.closer.close_aibuy_popup_enhanced():
                print("AiBUY弹窗关闭成功")
                success = True

            # 方法3: 点击关闭按钮
            print("方法3: 尝试点击关闭按钮...")
            if self.closer.click_close_buttons_enhanced():
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

            if save_debug:
                # 保存关闭后的页面状态
                save_page_source(self.driver, "after_close_popup.html", self.config.PATHS['html_debug'])
                print("已保存关闭后页面状态")

            return success

        except Exception as e:
            print(f"增强弹窗关闭失败: {e}")
            logging.error(f"增强弹窗关闭失败: {e}")
            return False

    def close_popups_enhanced_silent(self) -> bool:
        """
        静默的弹窗关闭方法，不输出详细信息
        :return: True表示成功关闭，False表示失败
        """
        try:
            success = False

            # 方法1: 处理iframe中的弹窗
            if self.closer.close_iframe_popups_silent():
                success = True

            # 方法2: 专门处理AiBUY弹窗
            if self.closer.close_aibuy_popup_silent():
                success = True

            # 方法3: 点击关闭按钮
            if self.closer.click_close_buttons_silent():
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

    def handle_search_page_popups_comprehensive(self, keyword: str):
        """
        综合处理搜索结果页面的弹窗 - 包含用户交互
        :param keyword: 搜索关键词，用于保存调试文件
        """
        try:
            print("=== 开始综合弹窗检查和处理 ===")

            # 等待页面稳定
            time.sleep(2)

            # 1. 自动检测弹窗
            print("1. 自动检测页面弹窗...")
            has_popup = self.detect_popups()

            if has_popup:
                print("✅ 自动检测到弹窗，开始自动关闭...")
                self.close_popups_enhanced()
                time.sleep(2)

                # 再次检测是否还有弹窗
                if self.detect_popups_silent():
                    print("⚠️ 自动关闭后仍有弹窗存在")
                else:
                    print("✅ 弹窗已成功自动关闭")
            else:
                print("❌ 自动检测未发现弹窗")

            # 2. 用户确认
            print("\n2. 用户确认弹窗状态...")
            user_sees_popup = input("您是否看到页面上有弹窗或广告？(1=是, 0=否): ").strip()

            if user_sees_popup == '1':
                print("用户确认有弹窗，进行5次自动清理尝试...")

                # 3. 连续5次尝试关闭弹窗
                popup_attempts = 0
                max_popup_attempts = 5

                while popup_attempts < max_popup_attempts:
                    popup_attempts += 1
                    print(f"第{popup_attempts}次清理弹窗...")

                    # 检测是否有弹窗
                    has_popup = self.detect_popups_silent()
                    if not has_popup:
                        print("✅ 检测不到弹窗，可能已清理完成")
                        break

                    # 尝试关闭弹窗
                    self.close_popups_enhanced_silent()
                    time.sleep(2)  # 等待页面响应

                # 4. 最终用户确认
                print(f"\n已完成{popup_attempts}次弹窗清理尝试")
                final_confirmation = input("弹窗是否已清理完成？(1=是, 0=否): ").strip()

                if final_confirmation == '1':
                    print("✅ 用户确认弹窗清理成功")
                else:
                    print("❌ 用户确认弹窗未完全清理")
                    print("请手动关闭剩余弹窗...")

                    # 倒计时等待用户手动处理
                    for i in range(5, 0, -1):
                        print(f"等待用户手动处理，倒计时 {i} 秒...")
                        time.sleep(1)

                    print("继续执行后续流程...")
            else:
                print("✅ 用户确认无弹窗，继续执行")

            # 5. 保存当前页面状态用于调试
            save_page_source(self.driver, f"after_popup_handling_{keyword}.html", self.config.PATHS['html_debug'])
            print(f"已保存弹窗处理后的页面状态")

            print("=== 弹窗检查和处理完成 ===\n")

        except Exception as e:
            print(f"综合弹窗处理时出错: {e}")
            logging.error(f"综合弹窗处理时出错: {e}")
            # 保存错误页面
            save_page_source(self.driver, f"popup_handling_error_{keyword}.html", self.config.PATHS['html_debug'])

    def _detect_iframe_popups(self) -> bool:
        """检测iframe中的弹窗"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"找到 {len(iframes)} 个iframe")

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
                    iframe_popup_found = self._check_iframe_popup_elements()

                    # 切回主文档
                    self.driver.switch_to.default_content()

                    if iframe_popup_found:
                        print(f"  在iframe {i+1} 中检测到弹窗")
                        return True
                    else:
                        print(f"  iframe {i+1} 中未检测到弹窗")

                except Exception as iframe_error:
                    print(f"  检测iframe {i+1} 时出错: {iframe_error}")
                    # 确保切回主文档
                    try:
                        self.driver.switch_to.default_content()
                    except:
                        pass
                    continue

            return False

        except Exception as e:
            print(f"检测iframe弹窗时出错: {e}")
            # 确保切回主文档
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def _check_iframe_popup_elements(self) -> bool:
        """在iframe中检查弹窗元素"""
        try:
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
                        # 转换为XPath
                        text = selector.split(":contains('")[1].split("')")[0]
                        tag = selector.split(":contains(")[0]
                        xpath_selector = f"//{tag}[contains(text(), '{text}')]"
                        elements = self.driver.find_elements(By.XPATH, xpath_selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    visible_elements = [el for el in elements if el.is_displayed()]
                    if visible_elements:
                        print(f"    在iframe中找到弹窗元素: {selector}")
                        return True
                except Exception:
                    continue

            return False

        except Exception:
            return False

    def _detect_iframe_popups_silent(self) -> bool:
        """静默检测iframe中的弹窗"""
        try:
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
                                self.driver.switch_to.default_content()
                                return True
                        except Exception:
                            continue

                    self.driver.switch_to.default_content()

                except Exception:
                    try:
                        self.driver.switch_to.default_content()
                    except:
                        pass
                    continue

            return False

        except Exception:
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def _detect_main_page_popups(self) -> bool:
        """检测主页面弹窗"""
        try:
            popup_found = False

            for selector in self.config.POPUP_SELECTORS:
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

                        # 显示元素详细信息
                        for i, el in enumerate(visible_elements[:3]):  # 最多显示3个
                            try:
                                element_text = el.text.strip()[:50]
                                element_class = el.get_attribute('class') or ''
                                element_id = el.get_attribute('id') or ''
                                print(f"  元素{i+1}: 文本='{element_text}', 类名='{element_class[:30]}', ID='{element_id}'")

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

            return popup_found

        except Exception as e:
            print(f"检测主页面弹窗时出错: {e}")
            return False

    def _detect_main_page_popups_silent(self) -> bool:
        """静默检测主页面弹窗"""
        try:
            for selector in self.config.POPUP_SELECTORS:
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

    def _try_keyboard_close(self) -> bool:
        """尝试键盘操作关闭弹窗"""
        try:
            print("尝试键盘操作关闭弹窗...")

            # 尝试ESC键
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            print("已发送ESC键")

            # 尝试多次ESC
            for i in range(3):
                actions.send_keys(Keys.ESCAPE).perform()
                time.sleep(0.5)

            return True

        except Exception as e:
            print(f"键盘操作失败: {e}")
            return False

    def _try_keyboard_close_silent(self) -> bool:
        """静默键盘操作关闭弹窗"""
        try:
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

            for i in range(3):
                actions.send_keys(Keys.ESCAPE).perform()
                time.sleep(0.5)

            return True

        except Exception:
            return False

    def _click_overlay_to_close(self) -> bool:
        """点击遮罩层关闭弹窗"""
        try:
            print("尝试点击遮罩层关闭弹窗...")

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
                        print(f"找到遮罩层: {selector}")
                        self.driver.execute_script("arguments[0].click();", visible_elements[0])
                        time.sleep(1)
                        return True

                except Exception:
                    continue

            return False

        except Exception as e:
            print(f"点击遮罩层失败: {e}")
            return False

    def _click_overlay_to_close_silent(self) -> bool:
        """静默点击遮罩层关闭弹窗"""
        try:
            overlay_selectors = [
                ".overlay", ".modal-backdrop", ".popup-overlay", ".dialog-overlay",
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

    def _javascript_force_close(self) -> bool:
        """JavaScript强制关闭弹窗"""
        try:
            print("尝试JavaScript强制关闭弹窗...")

            js_code = """
            var removed = 0;

            // 移除固定定位的元素
            var fixedElements = document.querySelectorAll('div[style*="position: fixed"], div[style*="position: absolute"]');
            fixedElements.forEach(function(el) {
                if (el.style.zIndex > 100) {
                    el.remove();
                    removed++;
                }
            });

            // 移除常见弹窗类
            var popupClasses = ['.modal', '.popup', '.dialog', '.overlay', '.next-dialog-wrapper'];
            popupClasses.forEach(function(className) {
                var elements = document.querySelectorAll(className);
                elements.forEach(function(el) {
                    if (el.offsetParent !== null) {
                        el.remove();
                        removed++;
                    }
                });
            });

            return removed;
            """

            removed_count = self.driver.execute_script(js_code)
            if removed_count > 0:
                print(f"JavaScript强制移除了{removed_count}个可能的弹窗元素")
                time.sleep(1)
                return True
            else:
                print("JavaScript未找到需要移除的弹窗元素")
                return False

        except Exception as e:
            print(f"JavaScript强制关闭失败: {e}")
            return False

    def _javascript_force_close_silent(self) -> bool:
        """静默JavaScript强制关闭弹窗"""
        try:
            js_code = """
            var removed = 0;
            var fixedElements = document.querySelectorAll('div[style*="position: fixed"], div[style*="position: absolute"]');
            fixedElements.forEach(function(el) {
                if (el.style.zIndex > 100) {
                    el.remove();
                    removed++;
                }
            });

            var popupClasses = ['.modal', '.popup', '.dialog', '.overlay', '.next-dialog-wrapper'];
            popupClasses.forEach(function(className) {
                var elements = document.querySelectorAll(className);
                elements.forEach(function(el) {
                    if (el.offsetParent !== null) {
                        el.remove();
                        removed++;
                    }
                });
            });

            return removed;
            """

            removed_count = self.driver.execute_script(js_code)
            return removed_count > 0

        except Exception:
            return False