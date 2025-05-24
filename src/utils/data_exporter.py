"""
数据导出模块

负责将爬取的数据导出为各种格式（Excel、CSV等）
"""

import os
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

from ..core.config import CrawlerConfig
from .helpers import safe_filename, ensure_directory_exists


class DataExporter:
    """数据导出器"""

    def __init__(self, config: CrawlerConfig = None):
        """
        初始化数据导出器
        :param config: 爬虫配置对象
        """
        self.config = config or CrawlerConfig()

        # 确保输出目录存在
        ensure_directory_exists(self.config.PATHS['excel'])
        ensure_directory_exists(self.config.PATHS['json'])

    def save_to_excel(self, products: List[Dict], keyword: str = 'products',
                     output_dir: Optional[str] = None) -> str:
        """
        保存商品信息到Excel文件
        :param products: 商品列表
        :param keyword: 搜索关键词，用于生成文件名
        :param output_dir: 输出目录，如果为None则使用配置中的默认目录
        :return: 保存的文件路径，如果保存失败则返回空字符串
        """
        try:
            if not products or not isinstance(products, list):
                print("没有有效的商品数据可保存")
                return ""

            # 验证和清理商品数据
            valid_products = self._validate_products(products)

            if not valid_products:
                print("没有有效的商品数据可保存")
                return ""

            print(f"\n准备保存 {len(valid_products)} 条商品数据...")

            # 创建DataFrame并清理数据
            df = pd.DataFrame(valid_products)

            # 重命名列名为中文
            df = df.rename(columns=self.config.EXPORT_CONFIG['column_mapping'])

            # 生成文件路径
            filepath = self._generate_excel_filepath(keyword, output_dir)

            # 保存到Excel
            df.to_excel(filepath, index=False, engine=self.config.EXPORT_CONFIG['excel_engine'])

            print(f"\n商品信息已保存到: {filepath}")

            # 尝试打开文件所在目录
            self._open_file_directory(filepath)

            return filepath

        except Exception as e:
            error_msg = f"保存Excel文件时出错: {str(e)}"
            logging.error(error_msg, exc_info=True)
            print(error_msg)
            return ""

    def save_to_csv(self, products: List[Dict], keyword: str = 'products',
                   output_dir: Optional[str] = None) -> str:
        """
        保存商品信息到CSV文件
        :param products: 商品列表
        :param keyword: 搜索关键词，用于生成文件名
        :param output_dir: 输出目录，如果为None则使用配置中的默认目录
        :return: 保存的文件路径，如果保存失败则返回空字符串
        """
        try:
            if not products or not isinstance(products, list):
                print("没有有效的商品数据可保存")
                return ""

            # 验证和清理商品数据
            valid_products = self._validate_products(products)

            if not valid_products:
                print("没有有效的商品数据可保存")
                return ""

            print(f"\n准备保存 {len(valid_products)} 条商品数据到CSV...")

            # 创建DataFrame并清理数据
            df = pd.DataFrame(valid_products)

            # 重命名列名为中文
            df = df.rename(columns=self.config.EXPORT_CONFIG['column_mapping'])

            # 生成文件路径
            filepath = self._generate_csv_filepath(keyword, output_dir)

            # 保存到CSV
            df.to_csv(filepath, index=False, encoding='utf-8-sig')

            print(f"\n商品信息已保存到: {filepath}")

            return filepath

        except Exception as e:
            error_msg = f"保存CSV文件时出错: {str(e)}"
            logging.error(error_msg, exc_info=True)
            print(error_msg)
            return ""

    def save_to_json(self, products: List[Dict], keyword: str = 'products',
                    output_dir: Optional[str] = None) -> str:
        """
        保存商品信息到JSON文件
        :param products: 商品列表
        :param keyword: 搜索关键词，用于生成文件名
        :param output_dir: 输出目录，如果为None则使用配置中的默认目录
        :return: 保存的文件路径，如果保存失败则返回空字符串
        """
        try:
            import json

            if not products or not isinstance(products, list):
                print("没有有效的商品数据可保存")
                return ""

            # 验证和清理商品数据
            valid_products = self._validate_products(products)

            if not valid_products:
                print("没有有效的商品数据可保存")
                return ""

            print(f"\n准备保存 {len(valid_products)} 条商品数据到JSON...")

            # 生成文件路径
            filepath = self._generate_json_filepath(keyword, output_dir)

            # 保存到JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(valid_products, f, ensure_ascii=False, indent=2)

            print(f"\n商品信息已保存到: {filepath}")

            return filepath

        except Exception as e:
            error_msg = f"保存JSON文件时出错: {str(e)}"
            logging.error(error_msg, exc_info=True)
            print(error_msg)
            return ""

    def _validate_products(self, products: List[Dict]) -> List[Dict]:
        """
        验证和清理商品数据
        :param products: 原始商品列表
        :return: 验证后的商品列表
        """
        valid_products = []

        for product in products:
            if isinstance(product, dict):
                # 检查必要字段
                title = product.get('title', '').strip()
                if title and title != '未知商品' and len(title) > 0:
                    # 过滤掉无效的商品
                    invalid_keywords = ['登录', '注册', '首页', '导航', '广告']
                    if not any(keyword in title.lower() for keyword in invalid_keywords):
                        valid_products.append(product)

        return valid_products

    def _generate_excel_filepath(self, keyword: str, output_dir: Optional[str] = None) -> str:
        """生成Excel文件路径"""
        output_dir = output_dir or self.config.PATHS['excel']
        ensure_directory_exists(output_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = safe_filename(keyword) or 'products'
        filename = f"1688_{safe_keyword}_{timestamp}.xlsx"

        return os.path.join(output_dir, filename)

    def _generate_csv_filepath(self, keyword: str, output_dir: Optional[str] = None) -> str:
        """生成CSV文件路径"""
        output_dir = output_dir or self.config.PATHS['excel']  # CSV也放在excel目录
        ensure_directory_exists(output_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = safe_filename(keyword) or 'products'
        filename = f"1688_{safe_keyword}_{timestamp}.csv"

        return os.path.join(output_dir, filename)

    def _generate_json_filepath(self, keyword: str, output_dir: Optional[str] = None) -> str:
        """生成JSON文件路径"""
        output_dir = output_dir or self.config.PATHS['json']
        ensure_directory_exists(output_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = safe_filename(keyword) or 'products'
        filename = f"1688_{safe_keyword}_{timestamp}.json"

        return os.path.join(output_dir, filename)

    def _open_file_directory(self, filepath: str):
        """尝试在文件管理器中打开文件所在目录"""
        try:
            directory = os.path.dirname(filepath)

            if os.name == 'nt':  # Windows
                os.startfile(directory)
            elif os.name == 'posix':  # macOS, Linux
                import subprocess
                if os.uname().sysname == 'Darwin':  # macOS
                    subprocess.Popen(['open', directory])
                else:  # Linux
                    subprocess.Popen(['xdg-open', directory])

        except Exception as e:
            print(f"打开文件所在目录时出错: {e}")

    def get_export_summary(self, products: List[Dict]) -> Dict[str, int]:
        """
        获取导出数据的摘要信息
        :param products: 商品列表
        :return: 摘要信息字典
        """
        if not products:
            return {'total': 0, 'valid': 0, 'invalid': 0}

        valid_products = self._validate_products(products)

        return {
            'total': len(products),
            'valid': len(valid_products),
            'invalid': len(products) - len(valid_products)
        }

    def export_multiple_formats(self, products: List[Dict], keyword: str = 'products',
                              formats: List[str] = None, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        同时导出多种格式
        :param products: 商品列表
        :param keyword: 搜索关键词
        :param formats: 要导出的格式列表，默认为['excel', 'csv']
        :param output_dir: 输出目录
        :return: 格式到文件路径的映射字典
        """
        formats = formats or ['excel', 'csv']
        results = {}

        for format_type in formats:
            if format_type.lower() == 'excel':
                filepath = self.save_to_excel(products, keyword, output_dir)
                if filepath:
                    results['excel'] = filepath
            elif format_type.lower() == 'csv':
                filepath = self.save_to_csv(products, keyword, output_dir)
                if filepath:
                    results['csv'] = filepath
            elif format_type.lower() == 'json':
                filepath = self.save_to_json(products, keyword, output_dir)
                if filepath:
                    results['json'] = filepath

        return results
