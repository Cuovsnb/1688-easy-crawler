# 1688 商品爬虫

这是一个简单的1688网站商品爬虫程序，可以搜索并抓取商品信息。

## 功能特点

- 支持按关键词搜索商品
- 支持多页爬取
- 自动处理反爬机制（随机User-Agent、请求延迟）
- 结果保存为Excel文件

## 环境要求

- Python 3.7+
- 依赖包见 `requirements.txt`

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
   ```bash
   python crawler_1688.py
   ```

2. 按照提示输入搜索关键词和要爬取的页数

3. 程序会自动将结果保存为Excel文件，文件名为 `1688_关键词_products.xlsx`

## 注意事项

1. 请合理设置爬取页数，避免对目标网站造成过大压力
2. 如果遇到反爬机制，可以尝试：
   - 增加请求间隔时间
   - 使用代理IP
   - 降低爬取速度

## 自定义配置

你可以在 `Alibaba1688Crawler` 类中修改以下参数：

- `base_url`: 1688搜索页面基础URL
- `get_random_delay()`: 调整请求延迟时间
- `session.headers`: 修改请求头信息

## 输出字段

- title: 商品标题
- price: 价格
- order_count: 成交数量
- supplier: 供应商
- location: 所在地
- link: 商品链接
