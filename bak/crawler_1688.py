import os
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from typing import List, Dict, Optional

class Alibaba1688Crawler:
    """
    1688网站爬虫类
    """
    
    def __init__(self):
        self.base_url = "https://s.1688.com"
        self.ua = UserAgent()
        self.session = requests.Session()
        
        # 更新请求头，模拟浏览器
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Sec-GPC': '1'
        })
    
    def get_random_delay(self) -> float:
        """获取随机延迟时间"""
        # 增加随机延迟，避免请求过快
        delay = random.uniform(2, 5)
        print(f"等待 {delay:.2f} 秒...")
        return delay
    
    def search_products(self, keyword: str, pages: int = 1) -> List[Dict]:
        """
        搜索商品
        :param keyword: 搜索关键词
        :param pages: 爬取页数
        :return: 商品列表
        """
        all_products = []
        
        for page in range(1, pages + 1):
            print(f"正在爬取第 {page} 页...")
            
            # 构建搜索URL
            params = {
                'keywords': keyword,
                'page': page,
                'beginPage': page * 60 - 59  # 1688的页码计算方式
            }
            
            try:
                # 更新Referer头
                if page > 1:
                    self.session.headers.update({
                        'Referer': f"{self.base_url}/s/offer_search.htm?keywords={keyword}&page={page-1}"
                    })
                
                # 随机延迟，避免请求过快
                time.sleep(self.get_random_delay())
                
                # 发送请求
                print(f"发送请求: {self.base_url}/s/offer_search.htm")
                print(f"参数: {params}")
                
                response = self.session.get(
                    f"{self.base_url}/s/offer_search.htm",
                    params=params,
                    timeout=15,
                    allow_redirects=True
                )
                response.encoding = 'utf-8'  # 确保使用UTF-8编码
                
                # 保存响应内容用于调试
                with open(f'page_{page}.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                print(f"状态码: {response.status_code}")
                response.raise_for_status()
                
                # 解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 尝试不同的选择器
                items = (soup.select('.space-offer-card-box') or 
                        soup.select('.J_offerCard') or
                        soup.select('.offer-list-row'))
                
                if not items:
                    print("未找到商品列表，可能触发了反爬机制或页面结构已更改")
                    print("请检查保存的HTML文件以获取更多信息")
                    break
                
                print(f"找到 {len(items)} 个商品")
                
                # 提取商品信息
                for item in items:
                    try:
                        title_elem = (item.select_one('.title') or 
                                    item.select_one('.offer-title') or
                                    item.select_one('.title-text'))
                        
                        price_elem = (item.select_one('.price') or 
                                     item.select_one('.price-text'))
                        
                        order_elem = (item.select_one('.sale-num') or 
                                     item.select_one('.sale-text'))
                        
                        supplier_elem = (item.select_one('.company-name') or 
                                       item.select_one('.company-text'))
                        
                        location_elem = (item.select_one('.location') or 
                                       item.select_one('.location-text'))
                        
                        link_elem = (item.select_one('a.title') or 
                                   item.select_one('a.offer-title') or
                                   item.select_one('a.title-text'))
                        
                        product = {
                            'title': title_elem.get_text(strip=True) if title_elem else 'N/A',
                            'price': price_elem.get_text(strip=True) if price_elem else 'N/A',
                            'order_count': order_elem.get_text(strip=True) if order_elem else '0',
                            'supplier': supplier_elem.get_text(strip=True) if supplier_elem else 'N/A',
                            'location': location_elem.get_text(strip=True) if location_elem else 'N/A',
                            'link': 'https:' + link_elem['href'] if link_elem and 'href' in link_elem.attrs else 'N/A'
                        }
                        all_products.append(product)
                        
                        # 打印一些信息以便调试
                        print(f"找到商品: {product.get('title', 'N/A')}")
                        
                    except Exception as e:
                        print(f"解析商品信息时出错: {e}")
                        continue
                
            except requests.RequestException as e:
                print(f"请求出错: {e}")
                print(f"响应内容: {e.response.text[:500] if hasattr(e, 'response') and e.response else '无响应'}")
                break
            except Exception as e:
                print(f"发生未知错误: {e}")
                import traceback
                traceback.print_exc()
                break
        
        return all_products
    
    def save_to_excel(self, products: List[Dict], filename: str = '1688_products.xlsx'):
        """
        保存商品信息到Excel文件
        :param products: 商品列表
        :param filename: 保存文件名
        """
        if not products:
            print("没有数据可保存")
            return
        
        try:
            df = pd.DataFrame(products)
            df.to_excel(filename, index=False, engine='openpyxl')
            print(f"数据已保存到 {os.path.abspath(filename)}")
        except Exception as e:
            print(f"保存文件时出错: {e}")


def get_input(prompt, default=""):
    try:
        # 尝试使用input函数获取输入
        return input(prompt)
    except (EOFError, UnicodeDecodeError):
        # 如果出现编码问题，尝试使用sys.stdin.readline()
        import sys
        if sys.stdin.isatty():
            # 如果是交互式终端
            sys.stdout.write(prompt)
            sys.stdout.flush()
            return sys.stdin.readline().strip()
        else:
            # 如果是重定向输入
            return default

def main():
    # 创建爬虫实例
    crawler = Alibaba1688Crawler()
    
    # 搜索关键词
    try:
        keyword = get_input("请输入要搜索的商品关键词: ")
        if not keyword:
            keyword = "手机"  # 默认搜索关键词
            print(f"使用默认关键词: {keyword}")
            
        pages_input = get_input("请输入要爬取的页数(默认为1): ")
        try:
            pages = int(pages_input) if pages_input.strip() else 1
        except ValueError:
            print("输入的不是有效数字，将爬取1页")
            pages = 1
        
        # 开始爬取
        print(f"开始爬取 '{keyword}' 的商品信息，共 {pages} 页...")
        products = crawler.search_products(keyword, pages)
        
        # 保存结果
        if products:
            # 创建有效的文件名
            import re
            safe_keyword = re.sub(r'[\\/*?:"<>|]', "_", keyword)
            filename = f"1688_{safe_keyword}_products.xlsx"
            crawler.save_to_excel(products, filename)
            print(f"共爬取到 {len(products)} 条商品信息，已保存到: {filename}")
        else:
            print("未获取到商品信息，请检查网络连接或关键词是否正确")
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"发生错误: {e}")
    
    # 等待用户按回车键退出
    get_input("\n按回车键退出...")


if __name__ == "__main__":
    main()
