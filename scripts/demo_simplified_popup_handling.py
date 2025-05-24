#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示简化的弹窗处理流程
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium_crawler import Alibaba1688SeleniumCrawler

def demo_simplified_popup_handling():
    """演示简化的弹窗处理流程"""
    print("=" * 60)
    print("1688 简化弹窗处理流程演示")
    print("=" * 60)
    
    # 创建爬虫实例
    crawler = Alibaba1688SeleniumCrawler(
        base_url="https://www.1688.com",
        headless=False  # 使用有界面模式便于观察
    )
    
    try:
        print("\n1. 访问1688主页...")
        crawler.driver.get("https://www.1688.com")
        time.sleep(3)
        
        print("\n2. 开始弹窗处理流程...")
        print("   (这里会显示简化的输出信息)")
        
        # 模拟5次弹窗清理尝试
        popup_attempts = 0
        max_popup_attempts = 5

        while popup_attempts < max_popup_attempts:
            popup_attempts += 1
            print(f"第{popup_attempts}次清理弹窗...")

            # 检测是否有弹窗
            has_popup = crawler._detect_popups_silent()
            if not has_popup:
                break

            # 尝试关闭弹窗
            crawler._close_popups_enhanced_silent()
            time.sleep(1)  # 等待页面响应

        # 5次尝试后询问用户
        print(f"已完成{popup_attempts}次弹窗清理尝试")
        
        print("\n3. 用户交互环节...")
        user_response = input("弹窗是否清理成功？(0=否, 1=成功): ").strip()

        if user_response == '1':
            print("✅ 用户确认弹窗清理成功，继续下一步...")
        else:
            print("❌ 用户确认弹窗未清理成功")
            print("请手动关闭页面上的弹窗...")
            
            # 倒计时5秒
            for i in range(5, 0, -1):
                print(f"倒计时 {i} 秒...")
                time.sleep(1)
            
            # 询问是否进入主页面成功
            main_page_response = input("是否已成功进入主页面？(0=否, 1=成功): ").strip()
            
            if main_page_response == '1':
                print("✅ 用户确认已成功进入主页面，继续下一步...")
            else:
                print("⚠️  用户确认未成功进入主页面，但继续执行...")

        print("\n4. 弹窗处理完成，开始搜索流程...")
        print("   (这里会继续执行搜索商品的逻辑)")
        
        print("\n=" * 60)
        print("演示完成！")
        print("=" * 60)
        
        # 等待用户确认
        input("\n按 Enter 键关闭浏览器...")
        
    except Exception as e:
        print(f"演示过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("关闭浏览器...")
        crawler.close()

def demo_full_search_process():
    """演示完整的搜索流程"""
    print("=" * 60)
    print("1688 完整搜索流程演示（包含简化弹窗处理）")
    print("=" * 60)
    
    crawler = Alibaba1688SeleniumCrawler(
        base_url="https://www.1688.com",
        headless=False
    )
    
    try:
        # 执行搜索（这会触发完整的弹窗处理流程）
        print("\n开始执行搜索流程...")
        print("关键词: 手机")
        
        products = crawler.search_products("手机", pages=1)
        
        print(f"\n搜索完成，找到 {len(products)} 个商品")
        
        if products:
            print("\n前3个商品:")
            for i, product in enumerate(products[:3], 1):
                print(f"{i}. {product.get('title', '无标题')}")
                print(f"   价格: {product.get('price', '无价格')}")
                print(f"   店铺: {product.get('shop', '无店铺')}")
                print()
        
    except Exception as e:
        print(f"搜索演示过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("关闭浏览器...")
        crawler.close()

if __name__ == "__main__":
    print("1688弹窗处理演示工具")
    print("=" * 50)
    
    choice = input("选择演示模式:\n1. 仅演示弹窗处理流程\n2. 演示完整搜索流程\n请输入 1 或 2: ").strip()
    
    if choice == "1":
        demo_simplified_popup_handling()
    elif choice == "2":
        demo_full_search_process()
    else:
        print("无效选择，默认执行弹窗处理演示")
        demo_simplified_popup_handling()
