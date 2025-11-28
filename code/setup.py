# -*- coding: utf-8 -*-
"""
Updated Setup Script (2025)
作者: 根据你的原版修改
"""

from spider import get_news_pool
from spider import crawl_news
from index_module import IndexModule
from recommendation_module import RecommendationModule
from datetime import datetime
import urllib.request
import configparser
import os
import sys

# ------------------ 获取网页最大页数 ------------------
def get_max_page(url, try_auto=True):
    """
    try_auto=True：如果网页包含 maxPage 会自动解析
    否则返回 None，需要手动指定
    """
    try:
        response = urllib.request.urlopen(url)
        html = response.read().decode("utf-8", "ignore")

        if try_auto and "maxPage" in html:
            part = html[html.find('maxPage'):]
            part = part[:part.find(';')]
            return int(part[part.find('=')+1:].strip())
        return None
    except Exception as e:
        print(f"⚠ maxPage 解析失败： {e}")
        return None


# ------------------ 爬取新闻 ------------------
def crawling(config):
    print(f"\n===============================================\n启动时间: {datetime.today()}\n===============================================\n")

    # ================== 修改这里 ==================
    root_url = "https://news.baidu.com"       # ← 主站
    list_url = "https://news.baidu.com/guonei?pn="  # ← 国内新闻翻页 URL
    max_page = get_max_page(root_url + ".shtml") or 10  # 默认 10 页
    print(f"📄 最大爬取页数：{max_page}")
    # =============================================

    # 构建新闻 URL 池
    news_pool = [list_url + str(i * 20) for i in range(max_page)]

    # 爬取新闻
    crawl_news(
        news_pool,
        140,   # 爬取新闻条数
        config['doc_dir_path'],
        config['doc_encoding']
    )
    print("🟩 新闻爬取完成\n")


# ------------------ 主程序 ------------------
if __name__ == "__main__":
    # 配置文件路径（绝对路径）
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.ini"))
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        sys.exit(1)

    # 读取配置
    config_parser = configparser.ConfigParser()
    read_files = config_parser.read(config_path, encoding="utf-8")
    if not read_files:
        print(f"❌ 配置文件读取失败: {config_path}")
        sys.exit(1)
    config = config_parser['DEFAULT']

    # 打印读取情况（调试用）
    print("🟢 正在加载配置文件:", config_path)
    print("默认字段:", dict(config))

    # 爬新闻
    crawling(config)

    # 建立索引
    print("🔍 开始建立索引...")
    im = IndexModule(config_path, "utf-8")
    im.construct_postings_lists()

    # 推荐阅读
    print("🔍 开始推荐新闻...")
    rm = RecommendationModule(config_path, "utf-8")
    rm.find_k_nearest(5, 25)

    print(f"===============================================\n完成时间: {datetime.today()}\n===============================================\n")
