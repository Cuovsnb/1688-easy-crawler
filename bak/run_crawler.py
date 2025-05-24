from crawler_1688 import Alibaba1688Crawler

def main():
    # 创建爬虫实例
    crawler = Alibaba1688Crawler()
    
    # 设置默认值
    keyword = "手机"  # 默认搜索关键词
    pages = 1         # 默认爬取1页
    
    print(f"开始爬取 '{keyword}' 的商品信息，共 {pages} 页...")
    
    # 开始爬取
    products = crawler.search_products(keyword, pages)
    
    # 保存结果
    if products:
        # 创建有效的文件名
        import re
        safe_keyword = re.sub(r'[\\/*?:"<>|]', "_", keyword)
        filename = f"1688_{safe_keyword}_products.xlsx"
        crawler.save_to_excel(products, filename)
        print(f"共爬取到 {len(products)} 条商品信息，已保存到: {filename}")
    else:
        print("未获取到商品信息，请检查网络连接或关键词是否正确")

if __name__ == "__main__":
    main()
