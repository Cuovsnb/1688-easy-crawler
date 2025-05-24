"""
商品信息提取模块

负责从搜索结果页面提取商品信息，支持多种提取策略
"""

import re
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import List, Dict, Optional, Any

from ..core.config import CrawlerConfig
from ..utils.helpers import clean_text


class ProductExtractor:
    """商品信息提取器"""

    def __init__(self, driver: webdriver.Chrome, config: CrawlerConfig = None):
        """
        初始化商品信息提取器
        :param driver: WebDriver实例
        :param config: 爬虫配置对象
        """
        self.driver = driver
        self.config = config or CrawlerConfig()

    def extract_products_from_search_page(self, keyword: str) -> List[Dict[str, Any]]:
        """
        从搜索结果页面提取商品信息
        :param keyword: 搜索关键词
        :return: 商品列表
        """
        try:
            print("开始从搜索结果页面提取商品信息...")

            # 等待页面加载
            time.sleep(2)

            # 提取商品信息
            print("开始提取商品信息...")
            all_found_products = []

            print("\n===== 方式1: 使用标准选择器查找商品 =====")
            products_method1 = self.extract_products_method1()

            print("\n===== 方式2: 使用XPath查找商品 =====")
            products_method2 = self.extract_products_method2()

            print("\n===== 方式3: 使用JavaScript查找商品 =====")
            products_method3 = self.extract_products_method3()

            print("\n===== 方式4: 使用更宽泛的选择器查找商品 =====")
            products_method4 = self.extract_products_method4()

            print("\n===== 方式5: 使用数据属性查找商品 =====")
            products_method5 = self.extract_products_method5()

            # 合并所有方式的结果
            all_methods = [
                ("方式1", products_method1),
                ("方式2", products_method2),
                ("方式3", products_method3),
                ("方式4", products_method4),
                ("方式5", products_method5)
            ]

            for method_name, products in all_methods:
                if products:
                    print(f"{method_name} 找到 {len(products)} 个商品")
                    all_found_products.extend(products)
                else:
                    print(f"{method_name} 未找到商品")

            # 去重处理
            unique_products = self._remove_duplicates(all_found_products)
            print(f"\n总共找到 {len(all_found_products)} 个商品，去重后 {len(unique_products)} 个")

            return unique_products

        except Exception as e:
            print(f"从搜索结果页面提取商品信息时出错: {e}")
            logging.error(f"从搜索结果页面提取商品信息时出错: {e}")
            return []

    def extract_products_method1(self) -> List[Dict[str, Any]]:
        """方式1: 使用标准CSS选择器查找商品"""
        products = []
        try:
            # 使用配置中的标准选择器
            for selector in self.config.PRODUCT_SELECTORS['standard']:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"使用选择器 '{selector}' 找到 {len(elements)} 个商品")
                    for element in elements[:10]:  # 限制处理数量
                        product_info = self.extract_product_details_from_element(element)
                        if product_info:
                            products.append(product_info)
                    break  # 找到商品后就停止尝试其他选择器

            # 如果标准选择器都没找到商品，尝试通过价格文本定位
            if not products:
                print("尝试通过价格文本定位商品...")
                elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '元') or contains(text(), '￥')]")
                print(f"通过价格文本定位到 {len(elements)} 个可能的商品元素")

                for element in elements[:30]:  # 尝试更多元素
                    try:
                        # 尝试向上找到可能的商品容器
                        parent = element
                        for _ in range(3):  # 向上查找3层父元素
                            if parent:
                                parent = parent.find_element(By.XPATH, "..")
                                product_info = self.extract_product_details_from_element(parent)
                                if product_info:
                                    products.append(product_info)
                                    break
                    except:
                        continue

        except Exception as e:
            print(f"方式1提取商品时出错: {e}")
            logging.error(f"方式1提取商品时出错: {e}")

        return products

    def extract_products_method2(self) -> List[Dict[str, Any]]:
        """方式2: 使用XPath查找商品"""
        products = []
        try:
            # 使用配置中的XPath选择器
            for xpath in self.config.PRODUCT_SELECTORS['xpath']:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements:
                    print(f"使用XPath '{xpath}' 找到 {len(elements)} 个商品")
                    for element in elements[:10]:  # 只处理前10个
                        product_info = self.extract_product_details_from_element(element)
                        if product_info:
                            products.append(product_info)
                    break

        except Exception as e:
            print(f"方式2提取商品时出错: {e}")
            logging.error(f"方式2提取商品时出错: {e}")

        return products

    def extract_products_method3(self) -> List[Dict[str, Any]]:
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

            if js_result:
                print(f"JavaScript方法找到 {len(js_result)} 个商品")
                for item in js_result:
                    product_info = {
                        'title': clean_text(item.get('title', '')),
                        'price': self._format_price(item.get('price', '')),
                        'shop': '未知店铺',
                        'sales': '0人付款',
                        'link': item.get('link', ''),
                        'image': '',
                        'source': 'JavaScript提取'
                    }
                    if product_info['title']:
                        products.append(product_info)

        except Exception as e:
            print(f"方式3提取商品时出错: {e}")
            logging.error(f"方式3提取商品时出错: {e}")

        return products

    def extract_products_method4(self) -> List[Dict[str, Any]]:
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
                        element_class = element.get_attribute('class') or ''
                        if 'card' in element_class or 'item' in element_class:
                            product_info = self.extract_product_details_from_element(element)
                            if product_info:
                                products.append(product_info)
                    if products:
                        break

        except Exception as e:
            print(f"方式4提取商品时出错: {e}")
            logging.error(f"方式4提取商品时出错: {e}")

        return products

    def extract_products_method5(self) -> List[Dict[str, Any]]:
        """方式5: 使用数据属性查找商品"""
        products = []
        try:
            data_attribute_selectors = [
                "div[data-spm*='offer']",
                "a[data-productid]",
                "div[data-offerid]",
                "*[data-tracker-type='product']",
                "li[data-itemid]",
                "div[data-p_idx]", # Common in some Alibaba layouts
                "div[data-expo-type='offer']", # Another common one
                "div[data-widget-type='offer']"
            ]

            for selector in data_attribute_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"使用数据属性选择器 '{selector}' 找到 {len(elements)} 个商品")
                        for element in elements[:20]:  # Process up to 20 elements
                            product_details = self.extract_product_details_from_element(element)
                            if product_details:
                                products.append(product_details)
                        if products: # If this selector yielded results, no need to try others in this method
                            break 
                except Exception as el_ex:
                    # Log selector specific error, but continue to next selector
                    logging.warning(f"方式5提取时，选择器 '{selector}' 出错: {el_ex}")
                    continue # Try next selector

        except Exception as e:
            print(f"方式5提取商品时出错: {e}")
            logging.error(f"方式5提取商品时出错: {e}")
        
        return products

    def extract_product_details_from_element(self, element) -> Optional[Dict[str, Any]]:
        """从元素中提取商品详细信息"""
        product_info = {
            'title': '',
            'price': '',
            'shop': '',
            'sales': '0人付款',
            'link': '',
            'image': '',
            'source': '元素提取'
        }

        try:
            # 1. 提取标题
            title_selectors = [
                "a[title]",  # 优先查找有title属性的链接
                "*[class*='title']",
                "*[class*='name']",
                "*[class*='subject']",
                "h3", "h4", "h5",  # 标题标签
                "a[href*='offer']",  # 商品链接
                ".offer-title",
                ".product-title",
                ".item-title"
            ]

            for selector in title_selectors:
                try:
                    title_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for title_el in title_elements:
                        # 优先使用title属性
                        title_text = title_el.get_attribute('title')
                        if not title_text:
                            title_text = title_el.text.strip()

                        if title_text and len(title_text) > 3 and len(title_text) < 200:
                            # 过滤掉明显不是商品标题的文本
                            if not any(keyword in title_text.lower() for keyword in ['登录', '注册', '首页', '导航', '搜索', '筛选']):
                                product_info['title'] = clean_text(title_text)
                                break
                    if product_info['title']:
                        break
                except:
                    continue

            # 2. 提取价格
            price_selectors = [
                "*[class*='price']",
                "*[class*='Price']",
                "*[class*='money']",
                "*[class*='cost']",
                "*[class*='amount']",
                ".price-range",
                ".unit-price"
            ]

            for selector in price_selectors:
                try:
                    price_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for price_el in price_elements:
                        price_text = price_el.text.strip()
                        if price_text and any(char in price_text for char in ['￥', '元', '¥', '.']):
                            product_info['price'] = self._format_price(price_text)
                            break
                    if product_info['price']:
                        break
                except:
                    continue

            # 如果没找到价格，尝试XPath查找
            if not product_info['price']:
                try:
                    xpath_selector = ".//*[contains(text(), '￥') or contains(text(), '元') or contains(text(), '¥')]"
                    price_elements = element.find_elements(By.XPATH, xpath_selector)
                    for price_el in price_elements:
                        price_text = price_el.text.strip()
                        if price_text:
                            product_info['price'] = self._format_price(price_text)
                            break
                except:
                    pass

            # 3. 提取店铺名称
            shop_selectors = [
                "*[class*='shop']",
                "*[class*='store']",
                "*[class*='seller']",
                "*[class*='company']",
                ".shop-name",
                ".store-name",
                ".seller-name",
                ".company-name"
            ]

            for selector in shop_selectors:
                try:
                    shop_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for shop_el in shop_elements:
                        shop_text = shop_el.text.strip()
                        if shop_text and len(shop_text) > 1 and len(shop_text) < 100:
                            product_info['shop'] = clean_text(shop_text)
                            break
                    if product_info['shop']:
                        break
                except:
                    continue

            # 4. 提取商品链接
            link_selectors = [
                "a[href*='offer']",
                "a[href*='detail']",
                "a[href*='product']"
            ]

            for selector in link_selectors:
                try:
                    link_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    if link_elements:
                        href = link_elements[0].get_attribute('href')
                        if href and 'offer' in href:
                            product_info['link'] = href
                            break
                except:
                    continue

            # 5. 提取商品图片
            try:
                img_elements = element.find_elements(By.CSS_SELECTOR, "img")
                for img_el in img_elements:
                    src = img_el.get_attribute('src')
                    if src and ('jpg' in src or 'png' in src or 'jpeg' in src):
                        product_info['image'] = src
                        break
            except:
                pass

            # 6. 提取销量信息
            sales_selectors = [
                "*[class*='sale']",
                "*[class*='sold']",
                "*[class*='deal']",
                "*[class*='buy']",
                ".sale-count",
                ".sold-count",
                ".deal-cnt"
            ]

            for selector in sales_selectors:
                try:
                    sales_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for sales_el in sales_elements:
                        sales_text = sales_el.text.strip()
                        if sales_text and ('人' in sales_text or '笔' in sales_text or '件' in sales_text):
                            product_info['sales'] = clean_text(sales_text)
                            break
                    if product_info['sales'] != '0人付款':
                        break
                except:
                    continue

            # 验证提取的信息质量
            if product_info['title'] and (product_info['price'] or product_info['shop'] or product_info['link']):
                return product_info
            else:
                return None

        except Exception as e:
            print(f"从元素中提取商品详细信息时出错: {e}")
            logging.error(f"从元素中提取商品详细信息时出错: {e}")
            return None

    def _format_price(self, price_text: str) -> str:
        """格式化价格文本"""
        if not price_text:
            return "价格面议"

        try:
            # 提取数字和价格符号
            price_match = re.search(r'[￥¥]?[\d,]+\.?\d*', price_text)
            if price_match:
                return price_match.group()
            else:
                return clean_text(price_text) if price_text.strip() else "价格面议"
        except:
            return "价格面议"

    def _remove_duplicates(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去除重复的商品"""
        seen_titles = set()
        seen_links = set()
        unique_products = []

        for product in products:
            title = product.get('title', '').strip()
            link = product.get('link', '').strip()

            # 基于标题和链接去重
            title_key = title.lower() if title else ''
            link_key = link if link else ''

            if title_key and title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_products.append(product)
            elif link_key and link_key not in seen_links:
                seen_links.add(link_key)
                unique_products.append(product)

        return unique_products

    def find_products_elements(self) -> List:
        """查找商品元素"""
        # 尝试多种选择器定位商品元素
        for selector in self.config.PRODUCT_SELECTORS['standard']:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"使用选择器 '{selector}' 找到 {len(elements)} 个商品元素")
                    return elements
            except Exception as e:
                print(f"使用选择器 '{selector}' 时出错: {e}")

        print("未找到商品元素，请检查页面结构或选择器")
        return []

    def extract_product_info_safe(self, item) -> Optional[Dict[str, Any]]:
        """
        安全地从商品元素中提取信息
        :param item: 商品元素
        :return: 商品信息字典，如果提取失败则返回None
        """
        try:
            # 尝试多种选择器获取标题
            title = None
            title_selectors = [
                ("title", "a"),
                ("title", ".offer-title"),
                ("title", ".title-text"),
                ("alt", "img"),
                ("data-logs-value", "a")
            ]

            for attr, selector in title_selectors:
                try:
                    elem = item.find_element(By.CSS_SELECTOR, selector) if selector != "a" else item.find_element(By.TAG_NAME, "a")
                    if attr == "title":
                        title = elem.get_attribute("title") or elem.text.strip()
                    else:
                        title = elem.get_attribute(attr) or elem.text.strip()
                    if title and len(title) > 2:  # 确保标题有效
                        break
                except:
                    continue

            if not title:
                return None

            # 获取链接
            link_elem = self._find_element_safe(item, "a[href*='offer'], a[href*='detail']")
            link = link_elem.get_attribute('href') if link_elem else "#"

            # 获取价格
            price_elem = self._find_element_safe(item, ".price, .offer-price, .price-text, .price strong")
            price = self._format_price(price_elem.text.strip()) if price_elem else "价格面议"

            # 获取店铺名称
            shop_elem = self._find_element_safe(item, ".shop-name, .seller, .company-name a, .company-name")
            shop = shop_elem.text.strip() if shop_elem else "未知店铺"

            # 获取销量
            sales_elem = self._find_element_safe(item, ".sale, .sale-count, .sold-count, .deal-cnt")
            sales = sales_elem.text.strip() if sales_elem else "0人付款"

            # 获取商品图片
            img_elem = self._find_element_safe(item, "img")
            image = img_elem.get_attribute('src') if img_elem else ""

            return {
                'title': clean_text(title),
                'price': price,
                'shop': clean_text(shop),
                'sales': clean_text(sales),
                'link': link,
                'image': image,
                'source': '安全提取'
            }

        except Exception as e:
            logging.error(f"提取商品信息时出错: {e}")
            return None

    def _find_element_safe(self, parent, selector):
        """安全地查找元素"""
        try:
            return parent.find_element(By.CSS_SELECTOR, selector)
        except:
            return None


