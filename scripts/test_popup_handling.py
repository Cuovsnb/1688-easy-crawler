#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AiBUY弹窗处理功能
"""

import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium_crawler import Alibaba1688SeleniumCrawler

def test_popup_handling():
    """测试弹窗处理功能"""
    print("=== 测试AiBUY弹窗处理功能 ===")
    
    # 初始化爬虫（使用有界面模式以便观察）
    crawler = Alibaba1688SeleniumCrawler(
        base_url="https://www.1688.com",
        headless=False,  # 使用有界面模式
        user_data_dir=None
    )
    
    try:
        print("1. 访问1688主页...")
        crawler.driver.get("https://www.1688.com")
        time.sleep(3)
        
        print("2. 检测弹窗...")
        has_popup = crawler._detect_popups()
        print(f"检测结果: {'发现弹窗' if has_popup else '未发现弹窗'}")
        
        if has_popup:
            print("3. 尝试关闭弹窗...")
            
            # 测试AiBUY专门处理方法
            print("3.1 测试AiBUY专门处理方法...")
            aibuy_success = crawler._close_aibuy_popup()
            print(f"AiBUY处理结果: {'成功' if aibuy_success else '失败'}")
            
            # 测试通用关闭方法
            print("3.2 测试通用关闭方法...")
            general_success = crawler._close_popups_enhanced()
            print(f"通用处理结果: {'成功' if general_success else '失败'}")
            
            # 再次检测
            print("3.3 再次检测弹窗...")
            still_has_popup = crawler._detect_popups()
            print(f"处理后检测结果: {'仍有弹窗' if still_has_popup else '弹窗已清除'}")
            
        else:
            print("3. 未检测到弹窗，跳过关闭测试")
        
        print("4. 测试完成，等待5秒后关闭浏览器...")
        time.sleep(5)
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        
    finally:
        print("5. 关闭浏览器...")
        crawler.driver.quit()

def test_search_with_popup_handling():
    """测试搜索过程中的弹窗处理"""
    print("\n=== 测试搜索过程中的弹窗处理 ===")
    
    crawler = Alibaba1688SeleniumCrawler(
        base_url="https://www.1688.com",
        headless=False,
        user_data_dir=None
    )
    
    try:
        print("开始测试搜索流程中的弹窗处理...")
        
        # 执行搜索，这会触发完整的弹窗处理流程
        products = crawler.search_products("手机壳", pages=1)
        
        print(f"搜索完成，找到 {len(products)} 个商品")
        
        if products:
            print("前3个商品:")
            for i, product in enumerate(products[:3], 1):
                print(f"  {i}. {product.get('title', '无标题')}")
                print(f"     价格: {product.get('price', '无价格')}")
        
    except Exception as e:
        print(f"搜索测试过程中出错: {e}")
        
    finally:
        print("关闭浏览器...")
        crawler.driver.quit()

if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 仅测试弹窗处理功能")
    print("2. 测试完整搜索流程中的弹窗处理")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        test_popup_handling()
    elif choice == "2":
        test_search_with_popup_handling()
    else:
        print("无效选择，默认执行弹窗处理测试")
        test_popup_handling()
