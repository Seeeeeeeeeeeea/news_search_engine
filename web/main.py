# -*- coding: utf-8 -*-
__author__ = 'lcl'

import sys
import os
import traceback # 用于打印详细报错

# 【修复1】添加路径，确保能找到 ../code 下的 search_engine.py
# 获取当前文件所在目录的上一级目录下的 code 目录
cur_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = cur_dir  # web目录就是当前文件所在目录
code_dir = os.path.join(os.path.dirname(cur_dir), 'code')

# 确保web目录在Python路径中（用于导入ai_summary和search_engine）
if web_dir not in sys.path:
    sys.path.insert(0, web_dir)
# 添加code目录到路径（用于导入其他模块，如果需要）
sys.path.append(code_dir)

from flask import Flask, render_template, request

# 如果这里报错，说明 search_engine.py 不在 ../code 里，或者文件名不对
try:
    from search_engine import SearchEngine
except ImportError:
    print(f"无法导入 search_engine，请确认 {code_dir} 目录下存在 search_engine.py")

# 导入AI总结模块
try:
    from ai_summary import AISummaryGenerator
    print("AI总结模块导入成功")
except ImportError as e:
    print(f"无法导入 ai_summary，AI总结功能将不可用。错误信息: {e}")
    print(f"当前Python路径: {sys.path[:5]}...")  # 只显示前5个路径
    import traceback
    traceback.print_exc()
    AISummaryGenerator = None
except Exception as e:
    print(f"导入 ai_summary 时发生其他错误: {e}")
    import traceback
    traceback.print_exc()
    AISummaryGenerator = None

import xml.etree.ElementTree as ET
import sqlite3
import configparser
import time
import jieba

app = Flask(__name__)

doc_dir_path = ''
db_path = ''
page = []
keys = ''
doc_id = [] # 初始化为空列表
checked = ['', '', ''] # 初始化checked列表

# 【修复2】建议使用绝对路径读取配置，防止路径错误
config_path = os.path.join(os.path.dirname(cur_dir), 'config.ini')

# 初始化AI总结生成器
if AISummaryGenerator:
    try:
        ai_summary_generator = AISummaryGenerator(config_path, 'utf-8')
    except Exception as e:
        print(f"初始化AI总结生成器失败: {e}")
        ai_summary_generator = None
else:
    ai_summary_generator = None

def init():
    global dir_path, db_path
    config = configparser.ConfigParser()
    config.read(config_path, 'utf-8')
    dir_path = config['DEFAULT']['doc_dir_path']
    db_path = config['DEFAULT']['db_path']


@app.route('/')
def main():
    init()
    return render_template('search.html', error=True)


# 读取表单数据，获得doc_ID
@app.route('/search/', methods=['POST'])
def search():
    try:
        global keys
        global checked
        checked = ['checked="true"', '', '']
        keys = request.form['key_word']
        
        if keys not in ['']:
            # 【修复3】time.clock() 在 Python 3.8 已被删除，改为 time.perf_counter()
            print(time.perf_counter()) 
            
            flag, page = searchidlist(keys)
            
            if flag == 0:
                return render_template('search.html', error=False)
            
            docs = cut_page(page, 0)
            print(time.perf_counter())
            
            # 生成AI总结
            ai_summary = None
            if ai_summary_generator and docs:
                try:
                    print(f"正在生成AI总结，关键词: {keys}, 新闻数量: {len(docs)}")
                    ai_summary = ai_summary_generator.generate_summary(keys, docs)
                    if ai_summary:
                        print(f"AI总结生成成功，长度: {len(ai_summary)} 字符")
                    else:
                        print("AI总结生成失败，返回None")
                except Exception as e:
                    print(f"生成AI总结时出错: {e}")
                    import traceback
                    traceback.print_exc()
                    ai_summary = None
            else:
                if not ai_summary_generator:
                    print("AI总结生成器未初始化")
                if not docs:
                    print("没有搜索结果，无法生成AI总结")
            
            return render_template('high_search.html', checked=checked, key=keys, docs=docs, page=page,
                                   error=True, ai_summary=ai_summary)
        else:
            return render_template('search.html', error=False)

    except Exception as e:
        # 【修复4】打印真实报错并返回内容，防止 Flask 崩溃
        print('!!!!!!!!!! Search Error !!!!!!!!!!')
        traceback.print_exc()
        return f"搜索出错，请检查终端报错信息。错误内容: {str(e)}"


def searchidlist(key, selected=0):
    global page
    global doc_id
    # 这里也要用绝对路径的 config_path
    se = SearchEngine(config_path, 'utf-8')
    flag, id_scores = se.search(key, selected)
    # 返回docid列表
    doc_id = [i for i, s in id_scores]
    page = []
    # 修复分页逻辑防止报错
    if len(doc_id) > 0:
        for i in range(1, (len(doc_id) // 10 + 2)):
            page.append(i)
    else:
        page = [1]
    return flag, page


def cut_page(page, no):
    # 增加安全性检查
    if not doc_id:
        return []
    # 简单的分页切片
    start_idx = no * 10
    end_idx = start_idx + 10
    # 确保不越界（虽然切片会自动处理，但为了逻辑清晰）
    target_ids = doc_id[start_idx:end_idx]
    docs = find(target_ids)
    return docs


# 将需要的数据以字典形式打包传递给search函数
def find(docid, extra=False):
    docs = []
    global dir_path, db_path
    
    # 确保 init 被调用过
    if not dir_path or not db_path:
        init()

    for id in docid:
        try:
            xml_path = os.path.join(dir_path, '%s.xml' % id)
            root = ET.parse(xml_path).getroot()
            url = root.find('url').text
            title = root.find('title').text
            body = root.find('body').text
            snippet = (root.find('body').text[0:120] + '……') if root.find('body').text else ""
            time_val = root.find('datetime').text.split(' ')[0]
            datetime_val = root.find('datetime').text
            doc = {'url': url, 'title': title, 'snippet': snippet, 'datetime': datetime_val, 'time': time_val, 'body': body,
                   'id': id, 'extra': []}
            if extra:
                temp_doc = get_k_nearest(db_path, id)
                if temp_doc:
                    for i in temp_doc:
                        try:
                            root = ET.parse(os.path.join(dir_path, '%s.xml' % i)).getroot()
                            title = root.find('title').text
                            doc['extra'].append({'id': i, 'title': title})
                        except:
                            continue
            docs.append(doc)
        except Exception as e:
            print(f"读取文件 {id}.xml 失败: {e}")
            continue
    return docs


@app.route('/search/page/<page_no>/', methods=['GET'])
def next_page(page_no):
    try:
        page_no = int(page_no)
        docs = cut_page(page, (page_no-1))
        
        # 生成AI总结（只在第一页显示，避免重复生成）
        ai_summary = None
        if page_no == 1 and ai_summary_generator and docs:
            try:
                ai_summary = ai_summary_generator.generate_summary(keys, docs)
            except Exception as e:
                print(f"生成AI总结时出错: {e}")
                ai_summary = None
        
        return render_template('high_search.html', checked=checked, key=keys, docs=docs, page=page,
                               error=True, ai_summary=ai_summary)
    except Exception as e:
        print('next error')
        traceback.print_exc()
        return "Next page error"


@app.route('/search/<key>/', methods=['POST'])
def high_search(key):
    try:
        selected = int(request.form['order'])
        for i in range(3):
            if i == selected:
                checked[i] = 'checked="true"'
            else:
                checked[i] = ''
        flag, page = searchidlist(key, selected)
        if flag == 0:
            return render_template('search.html', error=False)
        docs = cut_page(page, 0)
        
        # 生成AI总结
        ai_summary = None
        if ai_summary_generator and docs:
            try:
                ai_summary = ai_summary_generator.generate_summary(key, docs)
            except Exception as e:
                print(f"生成AI总结时出错: {e}")
                ai_summary = None
        
        return render_template('high_search.html', checked=checked, key=keys, docs=docs, page=page,
                               error=True, ai_summary=ai_summary)
    except Exception as e:
        print('high search error')
        traceback.print_exc()
        return "High search error"


@app.route('/search/<id>/', methods=['GET', 'POST'])
def content(id):
    try:
        doc = find([id], extra=True)
        if not doc:
             return "Document not found"
        return render_template('content.html', doc=doc[0])
    except Exception as e:
        print('content error')
        traceback.print_exc()
        return "Content loading error"


def get_k_nearest(db_path, docid, k=5):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM knearest WHERE id=?", (docid,))
        docs = c.fetchone()
        conn.close()
        if docs:
            return docs[1: 1 + (k if k < 5 else 5)]  # max = 5
        else:
            return []
    except Exception as e:
        print(f"Database error: {e}")
        return []


if __name__ == '__main__':
    jieba.initialize()
    # 开启 Debug 模式，这样网页上也能看到报错
    app.run(debug=True)