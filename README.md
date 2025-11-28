# News Search Engine

基于 Flask 和 jieba 的中文新闻搜索引擎，支持 BM25 检索和 AI 自动摘要。该项目用于演示小规模中文语料的全文检索、排序与智能摘要能力。

如果本项目对你有帮助，欢迎点个 ⭐ Star 支持。

## 功能概览

- 全文检索：基于 BM25 的中文关键词检索
- AI 摘要：集成 ModelScope 接口调用Qwen2.5-7B模型进行结果摘要（可选）
- 新闻展示：完整新闻详情页面与分页浏览
- 排序与筛选：按照相关度、时间或热度排序

## 技术栈

- 后端：Flask（Python 3.8+）
- 分词：jieba
- 检索算法：BM25
- AI 服务：OpenAI / ModelScope（可配置）
- 存储：SQLite
- 模板：Jinja2 + HTML/CSS

## 快速开始

### 基本配置

- Python 3.8+

### 安装与运行

```powershell
git clone https://github.com/Seeeeeeeeeeeea/news_search_engine
cd news_search_engine
pip install -r requirements.txt
cd web
python main.py
```

然后在浏览器中打开 `http://127.0.0.1:5000`。

## 数据更新

运行爬虫更新新闻数据：

```powershell
python code/spider.chinanews.com.py
```

重新构建索引：

```powershell
python code/index_module.py
```

### 配置

编辑项目根目录下的 `config.ini`：

```ini
[DEFAULT]
doc_dir_path = ./data/news/
doc_encoding = utf-8
stop_words_path = ./data/stop_words.txt
idf_path = ./data/idf.txt
db_path = ./data/ir.db

# BM25 参数示例
k1 = 1.5
b = 0.75
n = 2449
avg_l = 279.09064924458966

[AI]
enabled = true
api_type = openai
api_base = https://api.openai.com/v1
api_key = your_api_key_here
model = ai_model_name
```

根据需要修改 AI 配置以启用或禁用自动摘要功能。

## 项目结构（简要）

```
news-search-engine/
├─ code/               # 索引、爬虫与检索核心代码
├─ data/               # 数据与辅助文件（XML、idf、停用词、数据库）
├─ web/                # Flask Web 应用（入口：web/main.py）
├─ config.ini          # 配置文件
├─ requirements.txt    # 依赖
└─ README.md           # 项目说明
```

## 使用说明

- 搜索：在首页输入关键词并提交，支持中文分词
- 结果页：支持分页与排序，点击标题查看新闻详情
- AI 摘要：如果启用，会对结果生成简短摘要展示



## API（简要）

- 搜索接口：`GET/POST /search/`，参数：`key_word`
- 新闻详情：`GET /search/<id>/`，参数：`id`
- 分页：`GET /search/page/<page_no>/`，参数：`page_no`

## 开发指南

1. 在 `web/` 中添加或修改路由与视图
2. 更新模板：`web/templates/`
3. 修改索引或检索逻辑请在 `code/` 中实现并测试

## 作者

**Jiahhao Yang (杨佳豪)**

📧 jhyang2369@stu.xidian.edu.cn

---

## 致谢

特别感谢项目 `https://github.com/01joy/news-search-engine` 的支持与启发。