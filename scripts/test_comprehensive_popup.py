#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试综合弹窗检测和处理功能
验证新的弹窗处理流程是否正常工作
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium_crawler import Alibaba1688SeleniumCrawler

def test_comprehensive_popup_handling():
    """测试综合弹窗处理功能"""
    print("=== 测试综合弹窗处理功能 ===\n")
    
    crawler = None
    try:
        print("1. 初始化爬虫...")
        crawler = Alibaba1688SeleniumCrawler(
            base_url="https://www.1688.com",
            headless=False  # 使用有界面模式便于观察
        )
        print("✅ 爬虫初始化成功\n")
        
        print("2. 测试直接URL搜索（包含新的弹窗处理）...")
        keyword = "手机壳"
        
        # 检查URL缓存
        print("检查URL缓存...")
        cached_url = crawler._get_cached_url(keyword)
        if cached_url:
            print(f"发现缓存URL: {cached_url[:50]}...")
        else:
            print("未发现缓存URL，将尝试构造新URL")
        
        # 尝试直接URL搜索
        print("\n3. 执行直接URL搜索...")
        if crawler._try_direct_search_url(keyword):
            print("✅ 直接URL搜索成功")
            
            print("\n4. 执行综合弹窗处理...")
            print("注意：这里会有用户交互，请根据提示操作")
            crawler._handle_search_page_popups_comprehensive(keyword)
            
            print("\n5. 检查页面最终状态...")
            current_url = crawler.driver.current_url
            page_title = crawler.driver.title
            print(f"当前URL: {current_url}")
            print(f"页面标题: {page_title}")
            
            # 最终静默检查
            print("\n6. 最终静默弹窗检查...")
            if crawler._detect_popups_silent():
                print("⚠️ 仍检测到弹窗")
            else:
                print("✅ 无弹窗，页面清洁")
                
            print("\n7. 测试商品提取（验证页面可用性）...")
            try:
                products = crawler._extract_products_from_search_page(keyword)
                print(f"成功提取 {len(products)} 个商品")
                if products:
                    print("前3个商品预览：")
                    for i, product in enumerate(products[:3], 1):
                        print(f"  {i}. {product.get('title', '无标题')[:30]}...")
            except Exception as e:
                print(f"商品提取测试失败: {e}")
                
        else:
            print("❌ 直接URL搜索失败")
            print("这可能是正常的，特别是首次使用时")
        
        print("\n=== 综合弹窗处理测试完成 ===")
        
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

def test_full_search_workflow():
    """测试完整的搜索工作流程（包含弹窗处理）"""
    print("=== 测试完整搜索工作流程 ===\n")
    
    crawler = None
    try:
        print("1. 初始化爬虫...")
        crawler = Alibaba1688SeleniumCrawler(
            base_url="https://www.1688.com",
            headless=False
        )
        print("✅ 爬虫初始化成功\n")
        
        print("2. 执行完整搜索流程...")
        keyword = "数据线"
        
        print(f"搜索关键词: {keyword}")
        print("注意：这个测试会包含完整的用户交互流程")
        
        # 执行完整搜索
        products = crawler.search_products(keyword, pages=1)
        
        print(f"\n搜索结果: 找到 {len(products)} 个商品")
        
        if products:
            print("\n商品信息预览：")
            for i, product in enumerate(products[:5], 1):
                print(f"{i}. 标题: {product.get('title', '无标题')[:40]}...")
                print(f"   价格: {product.get('price', '无价格')}")
                print(f"   店铺: {product.get('shop', '无店铺')}")
                print(f"   链接: {product.get('url', '无链接')[:50]}...")
                print()
        else:
            print("未找到商品，可能需要检查页面状态")
        
        print("=== 完整搜索工作流程测试完成 ===")
        
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

def test_popup_detection_only():
    """仅测试弹窗检测功能"""
    print("=== 仅测试弹窗检测功能 ===\n")
    
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
        
        print("3. 测试各种弹窗检测方法...")
        
        # 详细检测
        print("--- 详细弹窗检测 ---")
        has_popup_detailed = crawler._detect_popups()
        print(f"详细检测结果: {'发现弹窗' if has_popup_detailed else '未发现弹窗'}")
        
        # 静默检测
        print("\n--- 静默弹窗检测 ---")
        has_popup_silent = crawler._detect_popups_silent()
        print(f"静默检测结果: {'发现弹窗' if has_popup_silent else '未发现弹窗'}")
        
        # iframe检测
        print("\n--- iframe弹窗检测 ---")
        iframe_popup = crawler._detect_iframe_popups()
        print(f"iframe检测结果: {'发现弹窗' if iframe_popup else '未发现弹窗'}")
        
        print("\n=== 弹窗检测测试完成 ===")
        
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
    print("1. 综合弹窗处理测试（推荐）")
    print("2. 完整搜索工作流程测试")
    print("3. 仅弹窗检测测试")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == "1":
        test_comprehensive_popup_handling()
    elif choice == "2":
        test_full_search_workflow()
    elif choice == "3":
        test_popup_detection_only()
    else:
        print("无效选择，运行综合测试...")
        test_comprehensive_popup_handling()
