#!/usr/bin/env python3
"""
1688商品爬虫主程序

重构后的1688爬虫程序入口，提供用户友好的交互界面
"""

import sys
import os
import logging
from typing import Optional

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.crawler import Alibaba1688Crawler
from src.core.config import CrawlerConfig


def is_interactive() -> bool:
    """检查是否在交互式环境中运行"""
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except:
        return False


def get_user_input() -> tuple:
    """
    获取用户输入
    :return: (keyword, pages, base_url, flow_choice)
    """
    try:
        if not is_interactive():
            # 非交互式模式使用默认值
            print("🤖 非交互式模式，使用默认值...")
            return "手机", 1, "https://www.1688.com", "1"

        print("=" * 60)
        print("🚀 1688商品爬虫 - 重构版")
        print("=" * 60)

        # 选择搜索流程
        print("\n📋 选择搜索流程：")
        print("1. 智能流程（优先缓存URL，自动降级，推荐）")
        print("2. 严格流程（按指定步骤执行：主页→弹窗→搜索→新标签页URL构造）")
        print("3. 流程控制（严格按照process.txt文件步骤执行，用户确认每步）")
        flow_choice = input("请选择流程 (1-3, 默认: 1): ").strip() or "1"

        # 获取搜索关键词
        keyword = input("\n🔍 请输入要搜索的商品(默认: 手机): ").strip() or "手机"

        # 获取爬取页数
        pages_input = input("📄 请输入要爬取的页数(默认: 1): ").strip()
        pages = int(pages_input) if pages_input.isdigit() and int(pages_input) > 0 else 1

        # 选择站点版本
        print("\n🌐 选择站点版本：")
        print("1. 国际站 (global.1688.com)")
        print("2. 中文站 (1688.com)")
        site_choice = input("请选择站点 (1-2, 默认: 2): ").strip() or "2"

        if site_choice == "1":
            base_url = "https://global.1688.com"
        else:
            base_url = "https://www.1688.com"

        return keyword, pages, base_url, flow_choice

    except (EOFError, KeyboardInterrupt):
        # 如果输入被中断，使用默认值
        print("\n🤖 检测到输入中断，使用默认值...")
        return "手机", 1, "https://www.1688.com", "1"
    except Exception as e:
        print(f"❌ 获取用户输入时出错: {e}")
        return "手机", 1, "https://www.1688.com", "1"


def print_results_summary(products: list, keyword: str):
    """打印结果摘要"""
    if not products:
        print("\n❌ 未获取到商品数据")
        print("可能原因：")
        print("  1. 搜索条件无结果")
        print("  2. 需要登录或验证码")
        print("  3. 网站结构已更新")
        print("  4. 网络连接问题")
        return

    print(f"\n✅ 抓取完成！")
    print(f"📊 搜索关键词: {keyword}")
    print(f"📦 获取商品数量: {len(products)}")

    # 显示前几个商品的简要信息
    print(f"\n📋 商品预览（前3个）：")
    for i, product in enumerate(products[:3], 1):
        title = product.get('title', '未知商品')[:50]
        price = product.get('price', '价格面议')
        shop = product.get('shop', '未知店铺')[:20]
        print(f"  {i}. {title}... | {price} | {shop}")

    if len(products) > 3:
        print(f"  ... 还有 {len(products) - 3} 个商品")


def main():
    """主函数"""
    crawler = None

    try:
        # 获取用户输入
        keyword, pages, base_url, flow_choice = get_user_input()

        print(f"\n🔧 配置信息：")
        print(f"   搜索关键词: {keyword}")
        print(f"   爬取页数: {pages}")
        print(f"   使用站点: {base_url}")
        flow_names = {'1': '智能流程', '2': '严格流程', '3': '流程控制'}
        print(f"   搜索流程: {flow_names.get(flow_choice, '智能流程')}")

        # 创建配置对象
        config = CrawlerConfig()

        # 创建爬虫实例
        print(f"\n🚀 正在启动浏览器...")
        crawler = Alibaba1688Crawler(
            base_url=base_url,
            headless=False,  # 显示浏览器窗口
            config=config
        )

        # 执行搜索
        print(f"\n🔍 开始搜索...")
        if flow_choice == "2":
            print("📋 使用严格流程搜索...")
            print("⚠️  注意：此流程会有多个用户交互步骤，请根据提示操作")
            products = crawler.search_products_strict_flow(keyword, pages=pages)
        elif flow_choice == "3":
            print("🔄 使用流程控制搜索...")
            print("⚠️  注意：此流程会严格按照process.txt文件的步骤执行，每步都需要用户确认")
            products = crawler.search_products_with_process_control(keyword, pages=pages)
        else:
            print("🧠 使用智能流程搜索...")
            products = crawler.search_products(keyword, pages=pages)

        # 打印结果摘要
        print_results_summary(products, keyword)

        # 保存数据
        if products:
            print(f"\n💾 正在保存数据...")

            # 保存到Excel
            excel_filename = crawler.save_to_excel(products, keyword)
            if excel_filename:
                print(f"📊 Excel文件: {excel_filename}")

            # 保存到JSON
            json_filename = crawler.save_to_json(products, keyword)
            if json_filename:
                print(f"📄 JSON文件: {json_filename}")

            if excel_filename or json_filename:
                print("✅ 数据保存完成！")
            else:
                print("❌ 数据保存失败，请检查日志")

        # 显示爬虫状态
        if is_interactive():
            status = crawler.get_crawler_status()
            print(f"\n📈 爬虫状态:")
            print(f"   数据条数: {status.get('data_count', 0)}")
            print(f"   当前页面: {status.get('page_title', '未知')}")

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        logging.error(f"程序执行出错: {e}", exc_info=True)
    finally:
        # 清理资源
        if crawler:
            print(f"\n🧹 正在清理资源...")
            crawler.close()

        print("👋 程序结束")


def run_batch_mode(keywords: list, base_url: str = "https://www.1688.com",
                   pages: int = 1, flow_choice: str = "1"):
    """
    批量模式运行
    :param keywords: 关键词列表
    :param base_url: 基础URL
    :param pages: 爬取页数
    :param flow_choice: 流程选择
    """
    print(f"🔄 批量模式：处理 {len(keywords)} 个关键词")

    config = CrawlerConfig()

    with Alibaba1688Crawler(base_url=base_url, headless=False, config=config) as crawler:
        for i, keyword in enumerate(keywords, 1):
            try:
                print(f"\n📍 [{i}/{len(keywords)}] 处理关键词: {keyword}")

                if flow_choice == "2":
                    products = crawler.search_products_strict_flow(keyword, pages=pages)
                elif flow_choice == "3":
                    products = crawler.search_products_with_process_control(keyword, pages=pages)
                else:
                    products = crawler.search_products(keyword, pages=pages)

                if products:
                    # 保存数据
                    excel_filename = crawler.save_to_excel(products, keyword)
                    json_filename = crawler.save_to_json(products, keyword)

                    print(f"✅ {keyword}: 获取 {len(products)} 个商品")
                    if excel_filename:
                        print(f"   📊 Excel: {excel_filename}")
                    if json_filename:
                        print(f"   📄 JSON: {json_filename}")
                else:
                    print(f"❌ {keyword}: 未获取到商品")

            except Exception as e:
                print(f"❌ 处理关键词 '{keyword}' 时出错: {e}")
                logging.error(f"处理关键词 '{keyword}' 时出错: {e}")
                continue

    print("🎉 批量处理完成！")


def show_help():
    """显示帮助信息"""
    help_text = """
🚀 1688商品爬虫 - 重构版

用法:
    python main.py                    # 交互式模式
    python main.py --help            # 显示帮助
    python main.py --batch keywords.txt  # 批量模式

参数说明:
    --help          显示此帮助信息
    --batch FILE    批量模式，从文件读取关键词列表
    --headless      无头模式运行
    --site SITE     指定站点 (1688 或 global)
    --pages N       爬取页数 (默认: 1)
    --flow FLOW     搜索流程 (1=智能, 2=严格, 3=流程控制, 默认: 1)

示例:
    python main.py --batch keywords.txt --site 1688 --pages 2
    python main.py --headless --flow 2

批量模式文件格式:
    每行一个关键词，例如：
    手机
    电脑
    耳机
    """
    print(help_text)


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        if "--help" in sys.argv or "-h" in sys.argv:
            show_help()
            sys.exit(0)
        elif "--batch" in sys.argv:
            try:
                batch_index = sys.argv.index("--batch")
                if batch_index + 1 < len(sys.argv):
                    keywords_file = sys.argv[batch_index + 1]

                    # 读取关键词文件
                    with open(keywords_file, 'r', encoding='utf-8') as f:
                        keywords = [line.strip() for line in f if line.strip()]

                    # 解析其他参数
                    base_url = "https://www.1688.com"
                    if "--site" in sys.argv:
                        site_index = sys.argv.index("--site")
                        if site_index + 1 < len(sys.argv):
                            site = sys.argv[site_index + 1]
                            if site.lower() == "global":
                                base_url = "https://global.1688.com"

                    pages = 1
                    if "--pages" in sys.argv:
                        pages_index = sys.argv.index("--pages")
                        if pages_index + 1 < len(sys.argv):
                            pages = int(sys.argv[pages_index + 1])

                    flow_choice = "1"
                    if "--flow" in sys.argv:
                        flow_index = sys.argv.index("--flow")
                        if flow_index + 1 < len(sys.argv):
                            flow_choice = sys.argv[flow_index + 1]

                    # 运行批量模式
                    run_batch_mode(keywords, base_url, pages, flow_choice)
                else:
                    print("❌ --batch 参数需要指定关键词文件")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ 批量模式出错: {e}")
                sys.exit(1)
        else:
            print("❌ 未知参数，使用 --help 查看帮助")
            sys.exit(1)
    else:
        # 交互式模式
        main()
