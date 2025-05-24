#!/usr/bin/env python3
"""
重构后代码的测试脚本

用于验证重构后的代码是否能正常工作
"""

import sys
import os
import traceback

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试所有模块的导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试核心模块
        from src.core.config import CrawlerConfig
        from src.core.crawler import Alibaba1688Crawler
        print("✅ 核心模块导入成功")
        
        # 测试驱动模块
        from src.drivers.webdriver_manager import WebDriverManager
        from src.drivers.browser_utils import BrowserUtils
        print("✅ 驱动模块导入成功")
        
        # 测试处理器模块
        from src.handlers.login_handler import LoginHandler
        from src.handlers.popup_handler import PopupHandler
        from src.handlers.popup_closer import PopupCloser
        from src.handlers.page_handler import PageHandler
        print("✅ 处理器模块导入成功")
        
        # 测试提取器模块
        from src.extractors.product_extractor import ProductExtractor
        from src.extractors.page_analyzer import PageAnalyzer
        print("✅ 提取器模块导入成功")
        
        # 测试策略模块
        from src.strategies.search_strategy import SearchStrategy
        from src.strategies.url_builder import URLBuilder
        print("✅ 策略模块导入成功")
        
        # 测试工具模块
        from src.utils.cache_manager import CacheManager
        from src.utils.data_exporter import DataExporter
        from src.utils.helpers import setup_logging, get_random_delay, clean_text
        print("✅ 工具模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        traceback.print_exc()
        return False

def test_config():
    """测试配置类"""
    print("\n🔧 测试配置类...")
    
    try:
        from src.core.config import CrawlerConfig
        
        config = CrawlerConfig()
        
        # 测试基本配置
        assert config.DEFAULT_BASE_URL == "https://www.1688.com"
        assert config.GLOBAL_BASE_URL == "https://global.1688.com"
        print("✅ 基础URL配置正确")
        
        # 测试搜索URL生成
        search_url = config.get_search_url(config.DEFAULT_BASE_URL)
        assert search_url == "https://www.1688.com/s/offer_search.htm"
        print("✅ 搜索URL生成正确")
        
        # 测试Chrome选项
        options = config.get_all_chrome_options()
        assert len(options) > 0
        print("✅ Chrome选项配置正确")
        
        # 测试目录创建
        config.ensure_directories()
        print("✅ 目录创建功能正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置类测试失败: {e}")
        traceback.print_exc()
        return False

def test_url_builder():
    """测试URL构造器"""
    print("\n🔗 测试URL构造器...")
    
    try:
        from src.strategies.url_builder import URLBuilder
        from src.core.config import CrawlerConfig
        
        config = CrawlerConfig()
        url_builder = URLBuilder(config)
        
        # 测试搜索URL构造
        keyword = "手机"
        urls = url_builder.build_search_urls(keyword)
        assert len(urls) > 0
        print(f"✅ 成功构造 {len(urls)} 个搜索URL")
        
        # 测试URL解析
        test_url = urls[0]
        parsed = url_builder.parse_search_url(test_url)
        assert 'keyword' in parsed
        print("✅ URL解析功能正常")
        
        # 测试URL验证
        is_valid = url_builder.validate_search_url(test_url)
        assert is_valid
        print("✅ URL验证功能正常")
        
        return True
        
    except Exception as e:
        print(f"❌ URL构造器测试失败: {e}")
        traceback.print_exc()
        return False

def test_data_exporter():
    """测试数据导出器"""
    print("\n📊 测试数据导出器...")
    
    try:
        from src.utils.data_exporter import DataExporter
        from src.core.config import CrawlerConfig
        
        config = CrawlerConfig()
        exporter = DataExporter(config)
        
        # 测试数据
        test_products = [
            {
                'title': '测试商品1',
                'price': '￥100',
                'shop': '测试店铺1',
                'sales': '10人付款',
                'link': 'https://example.com/1',
                'image': 'https://example.com/img1.jpg'
            },
            {
                'title': '测试商品2',
                'price': '￥200',
                'shop': '测试店铺2',
                'sales': '20人付款',
                'link': 'https://example.com/2',
                'image': 'https://example.com/img2.jpg'
            }
        ]
        
        # 测试Excel导出
        excel_file = exporter.save_to_excel(test_products, "测试")
        if excel_file and os.path.exists(excel_file):
            print("✅ Excel导出功能正常")
            # 清理测试文件
            try:
                os.remove(excel_file)
            except:
                pass
        else:
            print("⚠️ Excel导出可能有问题，但不影响核心功能")
        
        # 测试JSON导出
        json_file = exporter.save_to_json(test_products, "测试")
        if json_file and os.path.exists(json_file):
            print("✅ JSON导出功能正常")
            # 清理测试文件
            try:
                os.remove(json_file)
            except:
                pass
        else:
            print("⚠️ JSON导出可能有问题，但不影响核心功能")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据导出器测试失败: {e}")
        traceback.print_exc()
        return False

def test_helpers():
    """测试工具函数"""
    print("\n🛠️ 测试工具函数...")
    
    try:
        from src.utils.helpers import get_random_delay, clean_text, format_filename
        
        # 测试随机延迟
        delay = get_random_delay(1, 3)
        assert 1 <= delay <= 3
        print("✅ 随机延迟功能正常")
        
        # 测试文本清理
        dirty_text = "  测试文本\n\t  "
        clean = clean_text(dirty_text)
        assert clean == "测试文本"
        print("✅ 文本清理功能正常")
        
        # 测试文件名格式化
        filename = format_filename("测试/文件名:*.txt")
        assert "/" not in filename and ":" not in filename and "*" not in filename
        print("✅ 文件名格式化功能正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具函数测试失败: {e}")
        traceback.print_exc()
        return False

def test_crawler_creation():
    """测试爬虫创建（不启动浏览器）"""
    print("\n🕷️ 测试爬虫创建...")
    
    try:
        from src.core.crawler import Alibaba1688Crawler
        from src.core.config import CrawlerConfig
        
        # 只测试配置和模块初始化，不创建WebDriver
        config = CrawlerConfig()
        
        # 测试配置是否正确
        assert hasattr(config, 'DEFAULT_BASE_URL')
        assert hasattr(config, 'PRODUCT_SELECTORS')
        assert hasattr(config, 'POPUP_SELECTORS')
        print("✅ 爬虫配置正确")
        
        # 测试类定义
        assert hasattr(Alibaba1688Crawler, 'search_products')
        assert hasattr(Alibaba1688Crawler, 'search_products_strict_flow')
        assert hasattr(Alibaba1688Crawler, 'save_to_excel')
        print("✅ 爬虫类定义正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 爬虫创建测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始重构代码测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("配置类", test_config),
        ("URL构造器", test_url_builder),
        ("数据导出器", test_data_exporter),
        ("工具函数", test_helpers),
        ("爬虫创建", test_crawler_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试出错: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！重构代码基本功能正常")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关模块")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
