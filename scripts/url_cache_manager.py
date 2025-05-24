#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688成功URL缓存管理工具
用于管理和维护成功的搜索URL缓存
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class URLCacheManager:
    def __init__(self, cache_file="successful_urls.txt"):
        self.cache_file = cache_file
        self.ensure_cache_file_exists()
    
    def ensure_cache_file_exists(self):
        """确保缓存文件存在"""
        if not os.path.exists(self.cache_file):
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                f.write("# 1688成功URL缓存文件\n")
                f.write("# 格式: 关键词|成功的URL|时间戳|备注\n")
                f.write("# 示例: 手机|https://s.1688.com/selloffer/offer_search.htm?keywords=%E6%89%8B%E6%9C%BA|2024-01-01 12:00:00|直接访问成功\n\n")
            print(f"已创建缓存文件: {self.cache_file}")
    
    def load_cache(self):
        """加载缓存数据"""
        cache_data = []
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('|')
                        if len(parts) >= 3:
                            cache_data.append({
                                'line_num': line_num,
                                'keyword': parts[0].strip(),
                                'url': parts[1].strip(),
                                'timestamp': parts[2].strip(),
                                'note': parts[3].strip() if len(parts) > 3 else '',
                                'raw_line': line
                            })
            return cache_data
        except Exception as e:
            print(f"加载缓存文件失败: {e}")
            return []
    
    def display_cache(self):
        """显示缓存内容"""
        cache_data = self.load_cache()
        if not cache_data:
            print("缓存文件为空或无有效记录")
            return
        
        print(f"\n=== 缓存文件内容 ({len(cache_data)} 条记录) ===")
        print(f"{'序号':<4} {'关键词':<15} {'时间戳':<20} {'备注':<15} {'URL'}")
        print("-" * 100)
        
        for i, item in enumerate(cache_data, 1):
            url_display = item['url'][:50] + "..." if len(item['url']) > 50 else item['url']
            print(f"{i:<4} {item['keyword']:<15} {item['timestamp']:<20} {item['note']:<15} {url_display}")
    
    def add_url(self, keyword, url, note="手动添加"):
        """添加新的URL到缓存"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 检查是否已存在
        cache_data = self.load_cache()
        existing = [item for item in cache_data if item['keyword'] == keyword]
        
        if existing:
            choice = input(f"关键词 '{keyword}' 已存在缓存。是否覆盖? (y/n): ").strip().lower()
            if choice != 'y':
                print("取消添加")
                return False
            
            # 删除现有记录
            self.remove_url(keyword, silent=True)
        
        # 添加新记录
        new_record = f"{keyword}|{url}|{timestamp}|{note}\n"
        
        try:
            with open(self.cache_file, 'a', encoding='utf-8') as f:
                f.write(new_record)
            print(f"✅ 已添加: {keyword} -> {url[:50]}...")
            return True
        except Exception as e:
            print(f"❌ 添加失败: {e}")
            return False
    
    def remove_url(self, keyword, silent=False):
        """删除指定关键词的URL"""
        try:
            # 读取所有行
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 过滤掉要删除的行
            new_lines = []
            removed_count = 0
            
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    parts = line.split('|')
                    if len(parts) >= 2 and parts[0].strip() == keyword:
                        removed_count += 1
                        if not silent:
                            print(f"删除: {line.strip()}")
                        continue
                new_lines.append(line)
            
            # 写回文件
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            if not silent:
                print(f"✅ 已删除 {removed_count} 条记录")
            return True
            
        except Exception as e:
            if not silent:
                print(f"❌ 删除失败: {e}")
            return False
    
    def test_url(self, keyword):
        """测试指定关键词的缓存URL是否有效"""
        cache_data = self.load_cache()
        target_item = None
        
        for item in cache_data:
            if item['keyword'] == keyword:
                target_item = item
                break
        
        if not target_item:
            print(f"未找到关键词 '{keyword}' 的缓存URL")
            return False
        
        print(f"测试URL: {target_item['url']}")
        print("注意: 这里只是显示URL，实际测试需要在爬虫中进行")
        return True
    
    def clean_cache(self):
        """清理缓存文件"""
        choice = input("确定要清空所有缓存记录吗? (y/n): ").strip().lower()
        if choice == 'y':
            try:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    f.write("# 1688成功URL缓存文件\n")
                    f.write("# 格式: 关键词|成功的URL|时间戳|备注\n")
                    f.write("# 示例: 手机|https://s.1688.com/selloffer/offer_search.htm?keywords=%E6%89%8B%E6%9C%BA|2024-01-01 12:00:00|直接访问成功\n\n")
                print("✅ 缓存已清空")
                return True
            except Exception as e:
                print(f"❌ 清空失败: {e}")
                return False
        else:
            print("取消清空操作")
            return False

def main():
    """主函数"""
    manager = URLCacheManager()
    
    while True:
        print("\n=== 1688 URL缓存管理工具 ===")
        print("1. 查看缓存")
        print("2. 添加URL")
        print("3. 删除URL")
        print("4. 测试URL")
        print("5. 清空缓存")
        print("6. 退出")
        
        choice = input("\n请选择操作 (1-6): ").strip()
        
        if choice == '1':
            manager.display_cache()
            
        elif choice == '2':
            keyword = input("请输入关键词: ").strip()
            url = input("请输入URL: ").strip()
            note = input("请输入备注 (可选): ").strip() or "手动添加"
            
            if keyword and url:
                manager.add_url(keyword, url, note)
            else:
                print("关键词和URL不能为空")
                
        elif choice == '3':
            keyword = input("请输入要删除的关键词: ").strip()
            if keyword:
                manager.remove_url(keyword)
            else:
                print("关键词不能为空")
                
        elif choice == '4':
            keyword = input("请输入要测试的关键词: ").strip()
            if keyword:
                manager.test_url(keyword)
            else:
                print("关键词不能为空")
                
        elif choice == '5':
            manager.clean_cache()
            
        elif choice == '6':
            print("退出程序")
            break
            
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()
