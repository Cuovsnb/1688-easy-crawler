"""
核心模块 - 包含主要的爬虫逻辑和配置管理
"""

from .crawler import Alibaba1688Crawler
from .config import CrawlerConfig

__all__ = ['Alibaba1688Crawler', 'CrawlerConfig']
