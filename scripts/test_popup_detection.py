#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试弹窗检测和关闭功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium_crawler import Alibaba1688SeleniumCrawler

def test_popup_detection():
    """测试弹窗检测和关闭功能"""
    print("开始测试弹窗检测和关闭功能...")

    # 创建爬虫实例
    crawler = Alibaba1688SeleniumCrawler(
        base_url="https://www.1688.com",
        headless=False  # 使用有界面模式便于观察
    )

    try:
        print("访问1688主页...")
        crawler.driver.get("https://www.1688.com")
        time.sleep(3)

        print("\n=== 测试静默弹窗检测功能 ===")

        # 测试静默弹窗检测
        has_popup = crawler._detect_popups_silent()
        print(f"静默弹窗检测结果: {has_popup}")

        if has_popup:
            print("\n=== 测试静默弹窗关闭功能 ===")

            # 模拟5次清理尝试
            for i in range(1, 6):
                print(f"第{i}次清理弹窗...")
                close_success = crawler._close_popups_enhanced_silent()
                time.sleep(1)

                # 检测是否还有弹窗
                still_has_popup = crawler._detect_popups_silent()
                if not still_has_popup:
                    print(f"第{i}次清理后未检测到弹窗")
                    break

            print(f"已完成5次弹窗清理尝试")

            # 模拟用户交互
            print("\n=== 模拟用户交互 ===")
            print("弹窗是否清理成功？(0=否, 1=成功)")
            print("请查看浏览器页面并输入相应数字...")
        else:
            print("未检测到弹窗，跳过清理测试")

        print("\n=== 测试完成 ===")
        print("请查看浏览器页面，确认弹窗处理效果")

        # 等待用户确认
        input("按 Enter 键继续...")

    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("关闭浏览器...")
        crawler.close()

def test_search_with_popup_handling():
    """测试完整的搜索流程（包含弹窗处理）"""
    print("开始测试完整搜索流程...")

    crawler = Alibaba1688SeleniumCrawler(
        base_url="https://www.1688.com",
        headless=False
    )

    try:
        # 执行搜索（这会触发完整的弹窗处理流程）
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
        print(f"搜索测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("关闭浏览器...")
        crawler.close()

if __name__ == "__main__":
    print("1688弹窗处理测试工具")
    print("=" * 50)

    choice = input("选择测试模式:\n1. 仅测试弹窗检测和关闭\n2. 测试完整搜索流程\n请输入 1 或 2: ").strip()

    if choice == "1":
        test_popup_detection()
    elif choice == "2":
        test_search_with_popup_handling()
    else:
        print("无效选择，默认执行弹窗检测测试")
        test_popup_detection()
