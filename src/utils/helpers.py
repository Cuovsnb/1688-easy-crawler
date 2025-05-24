"""
通用工具函数模块

提供各种通用的辅助功能
"""

import os
import time
import random
import logging
from datetime import datetime
from selenium import webdriver
from typing import Optional


def get_random_delay(min_seconds: float = 2, max_seconds: float = 5) -> float:
    """
    获取随机延迟时间并执行等待
    :param min_seconds: 最小等待秒数
    :param max_seconds: 最大等待秒数
    :return: 实际等待的秒数
    """
    delay = random.uniform(min_seconds, max_seconds)
    print(f"等待 {delay:.2f} 秒...")
    time.sleep(delay)
    return delay


def save_page_source(driver: webdriver.Chrome, filename: str, directory: str = "html") -> bool:
    """
    保存页面源代码用于调试
    :param driver: WebDriver实例
    :param filename: 文件名
    :param directory: 保存目录
    :return: 是否保存成功
    """
    try:
        # 确保目录存在
        os.makedirs(directory, exist_ok=True)

        # 构建完整文件路径
        filepath = os.path.join(directory, filename)

        # 保存页面源代码
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)

        print(f"已保存页面源代码到 {filepath}")
        return True

    except Exception as e:
        print(f"保存页面源代码时出错: {e}")
        logging.error(f"保存页面源代码失败: {e}")
        return False


def generate_timestamp_filename(prefix: str, keyword: str = "", extension: str = "html") -> str:
    """
    生成带时间戳的文件名
    :param prefix: 文件名前缀
    :param keyword: 关键词（可选）
    :param extension: 文件扩展名
    :return: 生成的文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if keyword:
        # 清理关键词，只保留字母数字和常用符号
        safe_keyword = "".join([c for c in str(keyword) if c.isalnum() or c in ' _-']).strip()
        return f"{prefix}_{safe_keyword}_{timestamp}.{extension}"
    else:
        return f"{prefix}_{timestamp}.{extension}"


def safe_filename(filename: str) -> str:
    """
    生成安全的文件名，移除或替换不安全的字符
    :param filename: 原始文件名
    :return: 安全的文件名
    """
    # 定义不安全的字符
    unsafe_chars = '<>:"/\\|?*'

    # 替换不安全字符
    safe_name = filename
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')

    # 移除多余的空格和下划线
    safe_name = '_'.join(safe_name.split())

    return safe_name


def ensure_directory_exists(directory: str) -> bool:
    """
    确保目录存在，如果不存在则创建
    :param directory: 目录路径
    :return: 是否成功
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败: {e}")
        logging.error(f"创建目录失败: {e}")
        return False


def format_price(price_text: str) -> str:
    """
    格式化价格文本
    :param price_text: 原始价格文本
    :return: 格式化后的价格
    """
    if not price_text:
        return "价格面议"

    # 移除多余的空白字符
    price = price_text.strip()

    # 如果为空，返回默认值
    if not price:
        return "价格面议"

    return price


def clean_text(text: str) -> str:
    """
    清理文本，移除多余的空白字符和特殊字符
    :param text: 原始文本
    :return: 清理后的文本
    """
    if not text:
        return ""

    # 移除多余的空白字符
    cleaned = ' '.join(text.split())

    # 移除一些常见的特殊字符
    cleaned = cleaned.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

    return cleaned.strip()


def is_valid_url(url: str) -> bool:
    """
    检查URL是否有效
    :param url: URL字符串
    :return: 是否有效
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()
    return url.startswith(('http://', 'https://')) and len(url) > 10


def extract_domain(url: str) -> Optional[str]:
    """
    从URL中提取域名
    :param url: URL字符串
    :return: 域名，如果提取失败返回None
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def wait_for_condition(condition_func, timeout: int = 10, interval: float = 0.5) -> bool:
    """
    等待条件满足
    :param condition_func: 条件函数，返回True表示条件满足
    :param timeout: 超时时间（秒）
    :param interval: 检查间隔（秒）
    :return: 是否在超时前条件满足
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            if condition_func():
                return True
        except Exception:
            pass

        time.sleep(interval)

    return False


def retry_on_exception(func, max_retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    在异常时重试函数执行
    :param func: 要执行的函数
    :param max_retries: 最大重试次数
    :param delay: 重试间隔（秒）
    :param exceptions: 需要重试的异常类型
    :return: 函数执行结果
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                print(f"执行失败，{delay}秒后重试 (第{attempt + 1}/{max_retries}次): {e}")
                time.sleep(delay)
            else:
                print(f"重试{max_retries}次后仍然失败: {e}")

    # 如果所有重试都失败，抛出最后一个异常
    if last_exception:
        raise last_exception


def log_function_call(func_name: str, *args, **kwargs):
    """
    记录函数调用日志
    :param func_name: 函数名
    :param args: 位置参数
    :param kwargs: 关键字参数
    """
    args_str = ', '.join([str(arg) for arg in args])
    kwargs_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])

    all_args = []
    if args_str:
        all_args.append(args_str)
    if kwargs_str:
        all_args.append(kwargs_str)

    params_str = ', '.join(all_args)
    print(f"调用函数: {func_name}({params_str})")


def measure_execution_time(func):
    """
    装饰器：测量函数执行时间
    :param func: 要测量的函数
    :return: 装饰后的函数
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"函数 {func.__name__} 执行时间: {execution_time:.2f} 秒")
        return result
    return wrapper


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    截断字符串到指定长度
    :param text: 原始字符串
    :param max_length: 最大长度
    :param suffix: 截断后的后缀
    :return: 截断后的字符串
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def setup_logging(log_file: str = "crawler.log", level: int = logging.INFO):
    """
    设置日志配置
    :param log_file: 日志文件路径
    :param level: 日志级别
    """
    try:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # 配置日志格式
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        # 配置日志
        logging.basicConfig(
            level=level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        print(f"日志配置完成，日志文件: {log_file}")

    except Exception as e:
        print(f"设置日志配置时出错: {e}")


def format_filename(filename: str) -> str:
    """
    格式化文件名，移除不安全的字符
    :param filename: 原始文件名
    :return: 格式化后的文件名
    """
    # 定义不安全的字符
    unsafe_chars = '<>:"/\\|?*'

    # 替换不安全字符
    safe_name = filename
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')

    # 移除多余的空格和下划线
    safe_name = '_'.join(safe_name.split())

    # 限制文件名长度
    if len(safe_name) > 200:
        safe_name = safe_name[:200]

    return safe_name
