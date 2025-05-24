#!/usr/bin/env python3
"""
测试流程控制功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.crawler import Alibaba1688Crawler
from src.core.config import CrawlerConfig

def test_process_control():
    """测试流程控制功能"""
    print("🧪 测试流程控制功能")
    
    # 创建爬虫实例
    config = CrawlerConfig()
    crawler = Alibaba1688Crawler(
        base_url="https://www.1688.com",
        headless=False,
        config=config
    )
    
    try:
        # 测试流程控制方法
        print("\n📋 测试流程控制文件操作...")
        
        # 初始化流程文件
        crawler._init_process_file()
        
        # 读取流程状态
        status = crawler._read_process_status()
        print(f"初始状态: {status}")
        
        # 更新一个步骤状态
        crawler._update_process_status("打开浏览器加载主页", 1)
        
        # 再次读取状态
        status = crawler._read_process_status()
        print(f"更新后状态: {status}")
        
        # 获取当前步骤
        current_step = crawler._get_current_step()
        print(f"当前步骤: {current_step}")
        
        print("✅ 流程控制功能测试通过")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        crawler.close()

if __name__ == "__main__":
    test_process_control()
