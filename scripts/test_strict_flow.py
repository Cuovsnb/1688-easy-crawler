#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试严格流程搜索功能
按照用户要求的严格流程执行：
1. 登录主页
2. 检查弹窗
3. 提醒
4. 搜索
5. 提示
6. 如果出现登录页面无法直接搜索 → 在新页面构造URL
7. 搜索结果页面
8. 保存商品
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium_crawler import Alibaba1688SeleniumCrawler

def test_strict_flow_search():
    """测试严格流程搜索"""
    print("=== 测试严格流程搜索功能 ===\n")
    
    crawler = None
    try:
        print("1. 初始化爬虫...")
        crawler = Alibaba1688SeleniumCrawler(
            base_url="https://www.1688.com",
            headless=False  # 使用有界面模式便于观察
        )
        print("✅ 爬虫初始化成功\n")
        
        # 测试关键词
        test_keywords = [
            "手机壳",
            "数据线"
        ]
        
        for i, keyword in enumerate(test_keywords, 1):
            print(f"\n{'='*60}")
            print(f"测试 {i}/{len(test_keywords)}: 搜索关键词 '{keyword}'")
            print(f"{'='*60}")
            
            print("注意：这是严格流程测试，会有多个用户交互步骤")
            print("请根据提示进行操作")
            
            # 执行严格流程搜索
            products = crawler.search_products_strict_flow(keyword, pages=1)
            
            print(f"\n搜索结果总结:")
            print(f"关键词: {keyword}")
            print(f"找到商品数量: {len(products)}")
            
            if products:
                print("\n商品信息预览（前3个）:")
                for j, product in enumerate(products[:3], 1):
                    print(f"  {j}. 标题: {product.get('title', '无标题')[:40]}...")
                    print(f"     价格: {product.get('price', '无价格')}")
                    print(f"     店铺: {product.get('shop', '无店铺')}")
                    print(f"     链接: {product.get('url', '无链接')[:50]}...")
                    print()
            else:
                print("❌ 未找到商品")
            
            # 询问是否继续下一个关键词
            if i < len(test_keywords):
                continue_test = input(f"\n是否继续测试下一个关键词 '{test_keywords[i]}'？(1=是, 0=否): ").strip()
                if continue_test != '1':
                    print("用户选择停止测试")
                    break
        
        print("\n=== 严格流程搜索测试完成 ===")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if crawler and crawler.driver:
            print("\n测试完成，等待用户确认...")
            input("按 Enter 键关闭浏览器...")
            try:
                crawler.driver.quit()
                print("✅ 浏览器已关闭")
            except:
                pass

def test_new_tab_functionality():
    """测试新标签页功能"""
    print("=== 测试新标签页功能 ===\n")
    
    crawler = None
    try:
        print("1. 初始化爬虫...")
        crawler = Alibaba1688SeleniumCrawler(
            base_url="https://www.1688.com",
            headless=False
        )
        print("✅ 爬虫初始化成功\n")
        
        print("2. 访问主页...")
        crawler.driver.get("https://www.1688.com")
        time.sleep(3)
        
        print("3. 测试新标签页管理功能...")
        
        # 获取当前标签页信息
        original_tab_info = crawler._get_current_tab_info()
        print(f"原始标签页: {original_tab_info}")
        
        # 打开新标签页
        print("打开新标签页...")
        new_tab = crawler._open_new_tab()
        
        if new_tab:
            print(f"✅ 成功打开新标签页: {new_tab}")
            
            # 切换到新标签页
            print("切换到新标签页...")
            if crawler._switch_to_tab(new_tab):
                print("✅ 成功切换到新标签页")
                
                # 在新标签页中访问一个URL
                print("在新标签页中访问百度...")
                crawler.driver.get("https://www.baidu.com")
                time.sleep(2)
                
                new_tab_info = crawler._get_current_tab_info()
                print(f"新标签页信息: {new_tab_info}")
                
                # 测试在新标签页中构造搜索URL
                print("测试在新标签页中构造搜索URL...")
                keyword = "测试商品"
                success = crawler._try_direct_search_in_new_tab(keyword)
                print(f"新标签页URL构造结果: {'成功' if success else '失败'}")
                
            else:
                print("❌ 切换到新标签页失败")
        else:
            print("❌ 打开新标签页失败")
        
        print("\n=== 新标签页功能测试完成 ===")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if crawler and crawler.driver:
            print("\n测试完成，等待用户确认...")
            input("按 Enter 键关闭浏览器...")
            try:
                crawler.driver.quit()
                print("✅ 浏览器已关闭")
            except:
                pass

def test_login_page_detection():
    """测试登录页面检测功能"""
    print("=== 测试登录页面检测功能 ===\n")
    
    crawler = None
    try:
        print("1. 初始化爬虫...")
        crawler = Alibaba1688SeleniumCrawler(
            base_url="https://www.1688.com",
            headless=False
        )
        print("✅ 爬虫初始化成功\n")
        
        print("2. 访问1688主页...")
        crawler.driver.get("https://www.1688.com")
        time.sleep(3)
        
        print("3. 测试登录页面检测...")
        is_login_page = crawler._is_redirected_to_login()
        print(f"主页登录检测结果: {'是登录页面' if is_login_page else '不是登录页面'}")
        
        print("4. 尝试访问可能的登录页面...")
        # 这里可以尝试访问一些可能触发登录的URL
        test_urls = [
            "https://login.1688.com",
            "https://passport.1688.com"
        ]
        
        for url in test_urls:
            try:
                print(f"访问: {url}")
                crawler.driver.get(url)
                time.sleep(2)
                
                is_login = crawler._is_redirected_to_login()
                print(f"检测结果: {'是登录页面' if is_login else '不是登录页面'}")
                
            except Exception as e:
                print(f"访问 {url} 时出错: {e}")
        
        print("\n=== 登录页面检测测试完成 ===")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if crawler and crawler.driver:
            print("\n测试完成，等待用户确认...")
            input("按 Enter 键关闭浏览器...")
            try:
                crawler.driver.quit()
                print("✅ 浏览器已关闭")
            except:
                pass

if __name__ == "__main__":
    print("选择测试模式：")
    print("1. 严格流程搜索测试（完整流程）")
    print("2. 新标签页功能测试")
    print("3. 登录页面检测测试")
    print("4. 运行所有测试")
    
    choice = input("请输入选择 (1-4): ").strip()
    
    if choice == "1":
        test_strict_flow_search()
    elif choice == "2":
        test_new_tab_functionality()
    elif choice == "3":
        test_login_page_detection()
    elif choice == "4":
        print("运行所有测试...\n")
        test_login_page_detection()
        print("\n" + "="*50 + "\n")
        test_new_tab_functionality()
        print("\n" + "="*50 + "\n")
        test_strict_flow_search()
    else:
        print("无效选择，运行严格流程测试...")
        test_strict_flow_search()
