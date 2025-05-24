# 1688商品爬虫 - 重构版

## 🚀 项目简介

这是一个重构后的1688商品爬虫项目，采用模块化设计，具有更好的可维护性、可扩展性和可测试性。

## ✨ 主要特性

- 🧩 **模块化设计**: 15个专门模块，职责单一，高内聚低耦合
- 🧠 **智能搜索策略**: 支持直接URL搜索、传统首页搜索等多种策略
- 🔄 **缓存机制**: 智能的URL和Cookie缓存，提高搜索效率
- 🛡️ **反检测机制**: 多层反检测策略，降低被封风险
- 🎯 **弹窗处理**: 智能识别和处理各种弹窗
- 📊 **多格式导出**: 支持Excel和JSON格式导出
- 🔧 **配置驱动**: 所有配置集中管理，易于调整
- 📝 **完整日志**: 详细的日志记录，便于调试
- 🎮 **用户友好**: 交互式界面和批量处理模式

## 📁 项目结构

```
├── main.py                    # 主程序入口
├── keywords_example.txt       # 批量模式示例文件
├── src/                       # 源代码目录
│   ├── core/                  # 核心模块
│   │   ├── config.py         # 配置管理
│   │   └── crawler.py        # 主爬虫类
│   ├── drivers/               # 驱动管理
│   │   ├── webdriver_manager.py  # WebDriver管理
│   │   └── browser_utils.py      # 浏览器工具
│   ├── handlers/              # 处理器
│   │   ├── login_handler.py      # 登录处理
│   │   ├── popup_handler.py      # 弹窗检测
│   │   ├── popup_closer.py       # 弹窗关闭
│   │   └── page_handler.py       # 页面处理
│   ├── extractors/            # 数据提取器
│   │   ├── product_extractor.py  # 商品信息提取
│   │   └── page_analyzer.py      # 页面分析
│   ├── strategies/            # 搜索策略
│   │   ├── search_strategy.py    # 搜索策略
│   │   └── url_builder.py        # URL构造
│   └── utils/                 # 工具类
│       ├── cache_manager.py      # 缓存管理
│       ├── data_exporter.py      # 数据导出
│       └── helpers.py            # 通用工具
└── outputs/                   # 输出目录
    ├── excel/                 # Excel文件
    ├── json/                  # JSON文件
    ├── logs/                  # 日志文件
    └── html_debug/            # 调试HTML文件
```

## 🛠️ 安装依赖

```bash
pip install selenium pandas openpyxl webdriver-manager
```

## 🎮 使用方法

### 交互式模式

```bash
python main.py
```

程序会引导您选择：
- 搜索流程（智能/严格）
- 搜索关键词
- 爬取页数
- 站点版本（国际站/中文站）

### 批量模式

```bash
python main.py --batch keywords_example.txt
```

支持的参数：
- `--batch FILE`: 指定关键词文件
- `--site SITE`: 指定站点（1688 或 global）
- `--pages N`: 爬取页数
- `--flow FLOW`: 搜索流程（1=智能，2=严格）
- `--headless`: 无头模式运行

### 示例命令

```bash
# 批量处理，使用国际站，爬取2页，严格流程
python main.py --batch keywords.txt --site global --pages 2 --flow 2

# 无头模式运行
python main.py --headless

# 查看帮助
python main.py --help
```

## 🔧 配置说明

主要配置在 `src/core/config.py` 中：

```python
class CrawlerConfig:
    # 基础URL配置
    DEFAULT_BASE_URL = "https://www.1688.com"
    GLOBAL_BASE_URL = "https://global.1688.com"
    
    # 超时配置
    TIMEOUTS = {
        'page_load': 30,
        'element_wait': 15,
        'popup_wait': 5
    }
    
    # 商品选择器配置
    PRODUCT_SELECTORS = {
        'standard': [...],
        'xpath': [...]
    }
    
    # 弹窗选择器配置
    POPUP_SELECTORS = [...]
```

## 🎯 搜索策略

### 智能流程（推荐）
1. 优先使用缓存的成功URL
2. 构造多种搜索URL尝试
3. 失败时自动降级到传统搜索
4. 智能处理登录和弹窗

### 严格流程
1. 访问主页
2. 检查和处理弹窗
3. 用户确认
4. 执行搜索
5. 检查结果
6. 必要时在新标签页构造URL

## 📊 数据导出

支持两种格式：
- **Excel格式**: 包含中文列名，便于查看
- **JSON格式**: 便于程序处理

导出字段：
- 商品标题
- 价格
- 店铺名称
- 销量
- 商品链接
- 图片链接

## 🛡️ 反检测机制

- 随机User-Agent
- 随机延迟
- 隐藏WebDriver特征
- 模拟真实用户行为
- Cookie和会话管理

## 📝 日志系统

日志文件保存在 `outputs/logs/` 目录：
- 详细的操作记录
- 错误信息和堆栈跟踪
- 性能指标
- 调试信息

## 🔍 调试功能

- 自动保存问题页面HTML
- 详细的状态信息
- 页面分析功能
- 缓存状态查看

## 🚨 注意事项

1. **遵守网站规则**: 请遵守1688网站的robots.txt和使用条款
2. **合理使用频率**: 避免过于频繁的请求
3. **数据用途**: 仅用于学习和研究目的
4. **法律责任**: 使用者需承担相应的法律责任

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目仅供学习和研究使用。

## 🆚 重构对比

### 重构前
- 单一文件4500+行代码
- 功能耦合严重
- 难以维护和扩展
- 缺乏模块化设计

### 重构后
- 15个专门模块
- 职责单一，高内聚低耦合
- 易于维护和扩展
- 完整的配置管理
- 智能的搜索策略
- 强大的缓存机制

## 📞 支持

如有问题，请提交Issue或联系维护者。
