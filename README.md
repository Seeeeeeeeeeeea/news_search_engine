# 📰 News Search Engine (中文新闻搜索引擎)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-green)](https://flask.palletsprojects.com/)
[![Jieba](https://img.shields.io/badge/NLP-jieba-orange)](https://github.com/fxsjy/jieba)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

基于 **Flask** 和 **jieba** 构建的轻量级中文新闻搜索引擎。本项目实现了从数据爬取、索引构建到检索排序的全流程，并集成了 AI 模型（OpenAI / ModelScope）实现智能摘要生成。

旨在演示小规模中文语料的全文检索、TF-IDF/BM25 排序算法以及大模型应用能力。

如果本项目对你有帮助，欢迎点个 ⭐ **Star** 支持！

---

## ✨ 功能概览

- 🔍 **全文检索**：基于 BM25 算法的高效中文关键词检索。
- 🤖 **AI 智能摘要**：集成 ModelScope/OpenAI 接口，自动为搜索结果生成精炼摘要。
- 📑 **完整阅览**：提供新闻详情页、关键词高亮及分页浏览功能。
- 📊 **多维排序**：支持按“相关度”、“发布时间”或“热度”对结果进行排序。
- 🕷️ **自动化数据流**：包含一键爬虫与索引构建脚本。

## 🛠️ 技术栈

| 模块 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **后端框架** | Flask | Python 3.8+ Web 服务 |
| **中文分词** | jieba | 精确模式分词 |
| **检索算法** | BM25 | 相比 TF-IDF 具有更好的相关性评分 |
| **AI 服务** | OpenAI / ModelScope | 用于生成新闻摘要（可配置） |
| **数据存储** | SQLite | 轻量级数据库，无需额外配置 |
| **前端模板** | Jinja2 + HTML/CSS | 简洁的响应式界面 |

## 🚀 快速开始

### 1. 环境准备

确保您的环境中已安装 Python 3.8 或更高版本。

```bash
git clone https://github.com/Seeeeeeeeeeeea/news_search_engine
cd news_search_engine
pip install -r requirements.txt
```

### 2. 数据初始化 (重要)

首次运行前，请按下列顺序执行：

1. 先运行爬虫脚本，默认爬取最近 5 天的新闻：

```powershell
# 确保根目录下 config.ini 已配置正确
python code/spider.chinanews.com.py
```

2. 然后执行一键初始化脚本，自动构建索引并生成推荐数据：

```powershell
python code/setup.py
```

提示：`code/spider.chinanews.com.py` 脚本默认会抓取最近 5 天（脚本内有 `timedelta(days=-5)`），如需更改抓取时间范围，请在脚本中调整 `start_date`/`end_date` 的计算方式。

### 3. 启动服务

```bash
cd web
python main.py
```

启动成功后，在浏览器访问：[http://127.0.0.1:5000](http://127.0.0.1:5000)

## ⚙️ 配置说明

项目根目录下的 `config.ini` 控制了核心参数。

### 基础配置
```ini
[DEFAULT]
doc_dir_path = ./data/news/       # 新闻数据存储路径
db_path = ./data/ir.db            # 数据库路径
stop_words_path = ./data/stop_words.txt
# BM25 算法参数 (根据语料调整)
k1 = 1.5
b = 0.75
```

### AI 摘要配置
如需启用 AI 摘要，请修改 `[AI]` 部分：

```ini
[AI]
enabled = true                    # true 开启, false 关闭
api_type = openai                 # 可选: openai 或 modelscope
api_base = https://api.openai.com/v1
api_key = your_api_key_here       # 填入你的 API Key
model = gpt-3.5-turbo             # 模型名称
```

## 📂 项目结构

```text
news-search-engine/
├── code/                   # 核心逻辑
│   ├── index_module.py     # 倒排索引构建
│   ├── spider.*.py         # 爬虫脚本
│   └── setup.py            # 一键初始化脚本
├── data/                   # 数据仓库
│   ├── news/               # 爬取的 XML 新闻文件
│   ├── ir.db               # SQLite 数据库
│   └── ...                 # 停用词表、IDF 表等
├── web/                    # Web 应用
│   ├── static/             # CSS/JS 资源
│   ├── templates/          # HTML 模板
│   └── main.py             # Flask 入口
├── config.ini              # 配置文件
├── requirements.txt        # 依赖列表
├── LICENSE                 # 许可证文件
└── README.md               # 项目说明
```

## 🔌 API 简述

后端提供以下 API 供前端或第三方调用：

- **搜索**：`GET /search/`
  - 参数：`key_word` (搜索词)
- **分页**：`GET /search/page/<page_no>/`
  - 参数：`page_no` (页码)
- **详情**：`GET /search/<id>/`
  - 参数：`id` (新闻文档 ID)

## 📝 开发指南

1. **Web 开发**：在 `web/main.py` 修改路由，`web/templates/` 修改页面样式。
2. **算法优化**：核心检索逻辑位于 `code/` 目录下，修改后建议重新运行 `setup.py` 更新索引。

## 👨‍💻 作者

**Jiahhao Yang (杨佳豪)**

- 📧 Email: jhyang2369@stu.xidian.edu.cn

## 📄 许可证

本项目基于 [MIT License](LICENSE) 协议开源。

---

## 🤝 致谢

本项目受到 [news-search-engine](https://github.com/01joy/news-search-engine) 的启发，感谢原作者！

