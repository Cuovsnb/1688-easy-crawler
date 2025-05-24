#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试绕过登录页面的改进方案
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium_crawler import Alibaba1688SeleniumCrawler

def test_bypass_login():
    """测试绕过登录页面的功能"""
    print("=== 测试绕过登录页面功能（包含URL缓存） ===\n")

    # 创建爬虫实例
    crawler = None
    try:
        print("1. 初始化爬虫...")
        crawler = Alibaba1688SeleniumCrawler(
            base_url="https://www.1688.com",
            headless=False,  # 使用有界面模式便于观察
            user_data_dir=None  # 不使用用户数据目录
        )
        print("✅ 爬虫初始化成功\n")

        # 测试关键词
        test_keywords = [
            "手机壳",
            "数据线",
            "蓝牙耳机"
        ]

        print("2. 检查URL缓存文件...")
        try:
            url_cache = crawler._load_successful_urls()
            if url_cache:
                print(f"发现 {len(url_cache)} 个缓存URL:")
                for keyword, url in url_cache.items():
                    print(f"  - {keyword}: {url[:80]}...")
            else:
                print("未发现缓存URL，将尝试新的搜索")
        except Exception as e:
            print(f"加载URL缓存时出错: {e}")
        print()

        for i, keyword in enumerate(test_keywords, 1):
            print(f"=== 测试 {i}/{len(test_keywords)}: 搜索关键词 '{keyword}' ===")

            try:
                # 执行搜索
                products = crawler.search_products(keyword, pages=1)

                if products:
                    print(f"✅ 成功绕过登录，找到 {len(products)} 个商品")

                    # 显示前3个商品
                    print("\n前3个商品信息：")
                    for j, product in enumerate(products[:3], 1):
                        print(f"  {j}. 标题: {product.get('title', '无标题')[:50]}...")
                        print(f"     价格: {product.get('price', '无价格')}")
                        print(f"     店铺: {product.get('shop', '无店铺')}")
                        print(f"     链接: {product.get('url', '无链接')[:80]}...")
                        print()

                    # 测试成功，保存Cookie
                    crawler._save_cookies(f"success_cookies_{keyword}.json")
                    print(f"✅ 已保存成功的Cookie到 success_cookies_{keyword}.json")

                else:
                    print(f"❌ 搜索 '{keyword}' 失败，可能被重定向到登录页面")

                    # 检查当前页面状态
                    current_url = crawler.driver.current_url
                    page_title = crawler.driver.title
                    print(f"当前URL: {current_url}")
                    print(f"页面标题: {page_title}")

                    # 保存错误页面
                    crawler._save_page_source(f"error_page_{keyword}.html")
                    print(f"已保存错误页面到 error_page_{keyword}.html")

            except Exception as e:
                print(f"❌ 测试关键词 '{keyword}' 时出错: {e}")
                import traceback
                traceback.print_exc()

            print(f"=== 测试 {i} 完成 ===\n")

            # 如果不是最后一个测试，等待一下
            if i < len(test_keywords):
                print("等待5秒后进行下一个测试...")
                time.sleep(5)

        print("=== 所有测试完成 ===")

    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理资源
        if crawler and crawler.driver:
            print("\n正在关闭浏览器...")
            try:
                crawler.driver.quit()
                print("✅ 浏览器已关闭")
            except:
                pass

def test_direct_url_access():
    """测试直接URL访问功能"""
    print("=== 测试直接URL访问功能 ===\n")

    crawler = None
    try:
        print("1. 初始化爬虫...")
        crawler = Alibaba1688SeleniumCrawler(
            base_url="https://www.1688.com",
            headless=False
        )
        print("✅ 爬虫初始化成功\n")

        # 测试直接URL访问
        test_keyword = "手机壳"
        print(f"2. 测试直接URL访问搜索 '{test_keyword}'...")

        success = crawler._try_direct_search_url(test_keyword)

        if success:
            print("✅ 直接URL访问成功")

            # 检查页面状态
            current_url = crawler.driver.current_url
            page_title = crawler.driver.title
            print(f"当前URL: {current_url}")
            print(f"页面标题: {page_title}")

            # 尝试提取商品
            products = crawler._extract_products_from_search_page(test_keyword)
            print(f"提取到 {len(products)} 个商品")

        else:
            print("❌ 直接URL访问失败")

            # 检查失败原因
            current_url = crawler.driver.current_url
            page_title = crawler.driver.title
            print(f"当前URL: {current_url}")
            print(f"页面标题: {page_title}")

            if crawler._is_redirected_to_login():
                print("原因: 被重定向到登录页面")
            else:
                print("原因: 其他未知原因")

    except Exception as e:
        print(f"❌ 测试直接URL访问时出错: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if crawler and crawler.driver:
            print("\n正在关闭浏览器...")
            try:
                crawler.driver.quit()
                print("✅ 浏览器已关闭")
            except:
                pass

if __name__ == "__main__":
    print("选择测试模式：")
    print("1. 完整测试（包含多个关键词）")
    print("2. 直接URL访问测试")
    print("3. 两个测试都运行")

    choice = input("请输入选择 (1/2/3): ").strip()

    if choice == "1":
        test_bypass_login()
    elif choice == "2":
        test_direct_url_access()
    elif choice == "3":
        test_direct_url_access()
        print("\n" + "="*50 + "\n")
        test_bypass_login()
    else:
        print("无效选择，运行完整测试...")
        test_bypass_login()
