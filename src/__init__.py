"""
1688爬虫项目 - 重构版本

这是一个模块化的1688商品爬虫项目，将原来的单一大文件重构为多个专门的模块。

主要模块：
- core: 核心爬虫逻辑和配置
- drivers: WebDriver管理和浏览器工具
- handlers: 各种处理器（弹窗、登录、页面交互）
- extractors: 数据提取器
- utils: 工具类和辅助功能
- strategies: 搜索策略和URL构造
"""

__version__ = "2.0.0"
__author__ = "1688 Crawler Team"
