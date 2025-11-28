# -*- coding: utf-8 -*-
"""
AI总结模块 - 使用AI API对搜索结果进行总结
支持OpenAI API和其他AI服务
"""

import os
import configparser
import requests
import json
import urllib3
from typing import List, Dict, Optional

# 尝试导入 OpenAI 客户端库
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("警告: openai 库未安装，将使用 requests 方式调用API")
    print("请运行: pip install openai")

# 禁用SSL警告（如果使用verify=False）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AISummaryGenerator:
    """AI总结生成器"""
    
    def __init__(self, config_path: str, config_encoding: str = 'utf-8'):
        """
        初始化AI总结生成器
        
        Args:
            config_path: 配置文件路径
            config_encoding: 配置文件编码
        """
        self.config_path = config_path
        self.config_encoding = config_encoding
        self.config = configparser.ConfigParser()
        self.config.read(config_path, config_encoding)
        
        # 读取AI配置
        self.api_type = self.config.get('AI', 'api_type', fallback='openai').lower()
        self.api_key = self.config.get('AI', 'api_key', fallback='').strip('"\'')  # 去除引号
        self.api_base = self.config.get('AI', 'api_base', fallback='').strip('"\'')  # 去除引号
        self.model = self.config.get('AI', 'model', fallback='gpt-3.5-turbo').strip('"\'')  # 去除引号
        self.max_tokens = int(self.config.get('AI', 'max_tokens', fallback='500'))
        self.enabled = self.config.getboolean('AI', 'enabled', fallback=False)
        
    def generate_summary(self, keyword: str, news_list: List[Dict]) -> Optional[str]:
        """
        根据搜索关键词和相关新闻生成总结
        
        Args:
            keyword: 搜索关键词
            news_list: 新闻列表，每个元素包含title, snippet等字段
            
        Returns:
            AI生成的总结文本，如果失败则返回None
        """
        if not self.enabled or not self.api_key:
            return None
            
        try:
            # 构建提示词
            prompt = self._build_prompt(keyword, news_list)
            print(f"调试: 提示词长度: {len(prompt)} 字符")
            
            # 根据API类型调用不同的方法
            if self.api_type == 'openai':
                result = self._call_openai_api(prompt)
                if result:
                    print(f"调试: AI总结生成成功")
                else:
                    print(f"调试: AI总结生成失败，返回None")
                return result
            elif self.api_type == 'custom':
                result = self._call_custom_api(prompt)
                if result:
                    print(f"调试: AI总结生成成功")
                else:
                    print(f"调试: AI总结生成失败，返回None")
                return result
            else:
                print(f"不支持的API类型: {self.api_type}")
                return None
                
        except Exception as e:
            print(f"AI总结生成异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _build_prompt(self, keyword: str, news_list: List[Dict]) -> str:
        """
        构建AI提示词
        
        Args:
            keyword: 搜索关键词
            news_list: 新闻列表
            
        Returns:
            构建好的提示词
        """
        # 限制新闻数量，避免token过多
        max_news = min(10, len(news_list))
        news_texts = []
        
        for i, news in enumerate(news_list[:max_news]):
            title = news.get('title', '')
            snippet = news.get('snippet', '')
            news_texts.append(f"{i+1}. {title}\n   {snippet}")
        
        news_content = "\n\n".join(news_texts)
        
        prompt = f"""请根据以下搜索关键词和相关新闻，生成一个简洁的总结（200-300字）。

搜索关键词：{keyword}

相关新闻：
{news_content}

请用中文总结这些新闻的主要内容，突出与关键词相关的重点信息。"""
        
        return prompt
    
    def _call_openai_api(self, prompt: str) -> Optional[str]:
        """
        调用OpenAI兼容API（支持ModelScope等）
        
        Args:
            prompt: 提示词
            
        Returns:
            AI生成的文本
        """
        try:
            # 清理api_base
            api_base_clean = ""
            if self.api_base:
                api_base_clean = self.api_base.strip()
                # 去除首尾的引号
                while api_base_clean.startswith(('"', "'")):
                    api_base_clean = api_base_clean[1:]
                while api_base_clean.endswith(('"', "'")):
                    api_base_clean = api_base_clean[:-1]
                api_base_clean = api_base_clean.strip()
                # 去除尾部斜杠
                if api_base_clean.endswith('/'):
                    api_base_clean = api_base_clean.rstrip('/')
            
            # 使用OpenAI客户端库（如果可用）
            if OPENAI_AVAILABLE:
                try:
                    # 初始化OpenAI客户端
                    client = OpenAI(
                        api_key=self.api_key,
                        base_url=api_base_clean if api_base_clean else None
                    )
                    
                    print(f"调试: 使用OpenAI客户端库")
                    print(f"调试: API Base: {api_base_clean if api_base_clean else '默认'}")
                    print(f"调试: 模型: {self.model}")
                    
                    # 调用API（stream=False表示一次性返回完整响应）
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "你是一个专业的新闻总结助手，擅长从多篇相关新闻中提取关键信息并生成简洁准确的总结。"
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        max_tokens=self.max_tokens,
                        temperature=0.7,
                        stream=False  # 一次性返回完整响应，不分段
                    )
                    
                    # 提取响应内容
                    if response.choices and len(response.choices) > 0:
                        content = response.choices[0].message.content.strip()
                        print(f"调试: 成功获取AI总结，长度: {len(content)} 字符")
                        return content
                    else:
                        print(f"调试: 响应中没有choices或choices为空")
                        return None
                        
                except Exception as e:
                    print(f"OpenAI客户端调用失败: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
                    return None
            else:
                # 回退到requests方式（兼容旧代码）
                print("警告: 使用requests方式调用API（建议安装openai库）")
                return self._call_openai_api_requests(prompt)
                
        except Exception as e:
            print(f"调用OpenAI API时出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _call_openai_api_requests(self, prompt: str) -> Optional[str]:
        """
        使用requests方式调用OpenAI兼容API（备用方法）
        
        Args:
            prompt: 提示词
            
        Returns:
            AI生成的文本
        """
        try:
            # 清理api_base
            api_base_clean = ""
            if self.api_base:
                api_base_clean = self.api_base.strip()
                while api_base_clean.startswith(('"', "'")):
                    api_base_clean = api_base_clean[1:]
                while api_base_clean.endswith(('"', "'")):
                    api_base_clean = api_base_clean[:-1]
                api_base_clean = api_base_clean.strip()
                if api_base_clean.endswith('/'):
                    api_base_clean = api_base_clean.rstrip('/')
            
            # 构建API URL
            if api_base_clean:
                if 'chat/completions' in api_base_clean:
                    api_url = api_base_clean
                elif api_base_clean.endswith('/v1'):
                    api_url = f"{api_base_clean}/chat/completions"
                else:
                    api_url = f"{api_base_clean}/v1/chat/completions"
            else:
                api_url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的新闻总结助手，擅长从多篇相关新闻中提取关键信息并生成简洁准确的总结。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": 0.7
            }
            
            # 禁用代理
            env_proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 
                            'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy']
            saved_proxy_vars = {}
            for var in env_proxy_vars:
                if var in os.environ:
                    saved_proxy_vars[var] = os.environ[var]
                    del os.environ[var]
            
            try:
                session = requests.Session()
                session.trust_env = False
                from requests.adapters import HTTPAdapter
                adapter = HTTPAdapter(max_retries=0)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                
                response = session.post(
                    api_url,
                    headers=headers,
                    json=data,
                    timeout=30,
                    proxies={'http': None, 'https': None},
                    verify=False,
                    stream=False
                )
            finally:
                for var, value in saved_proxy_vars.items():
                    os.environ[var] = value
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content'].strip()
                    return content
                return None
            else:
                print(f"API调用失败: {response.status_code}")
                print(f"响应: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"requests方式调用失败: {e}")
            return None
    
    def _call_custom_api(self, prompt: str) -> Optional[str]:
        """
        调用自定义API（可扩展支持其他AI服务）
        
        Args:
            prompt: 提示词
            
        Returns:
            AI生成的文本
        """
        try:
            # 这里可以扩展支持其他AI服务，如百度文心、阿里通义等
            # 示例：支持兼容OpenAI格式的自定义API
            api_url = self.api_base if self.api_base else "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.max_tokens
            }
            
            # 彻底禁用代理和SSL验证以避免连接问题
            # 清除环境变量中的代理设置
            env_proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 
                            'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy']
            saved_proxy_vars = {}
            for var in env_proxy_vars:
                if var in os.environ:
                    saved_proxy_vars[var] = os.environ[var]
                    del os.environ[var]
            
            try:
                # 创建Session并禁用从环境变量读取代理
                session = requests.Session()
                session.trust_env = False  # 不从环境变量读取代理
                
                # 确保一次性发送完整请求，不分段
                # 禁用自动重试，避免多次调用（Google API有请求限制）
                from requests.adapters import HTTPAdapter
                adapter = HTTPAdapter(max_retries=0)  # 不重试，避免多次调用
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                
                # 一次性发送完整请求
                response = session.post(
                    api_url,
                    headers=headers,
                    json=data,  # 一次性发送完整JSON数据
                    timeout=30,
                    proxies={'http': None, 'https': None},  # 明确禁用代理
                    verify=False,  # 禁用SSL验证
                    stream=False  # 确保一次性接收完整响应，不分段
                )
            finally:
                # 恢复环境变量（如果需要）
                for var, value in saved_proxy_vars.items():
                    os.environ[var] = value
            
            if response.status_code == 200:
                result = response.json()
                # 尝试不同的响应格式
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
                elif 'text' in result:
                    return result['text'].strip()
                else:
                    return str(result).strip()
            else:
                print(f"自定义API调用失败: {response.status_code}, {response.text}")
                return None
                
        except Exception as e:
            print(f"调用自定义API时出错: {e}")
            return None


if __name__ == "__main__":
    # 测试代码
    import os
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(cur_dir), 'config.ini')
    
    generator = AISummaryGenerator(config_path)
    
    # 测试数据
    test_news = [
        {
            'title': '北京雾霾天气持续',
            'snippet': '北京市今日空气质量指数达到严重污染级别，市民出行需注意防护……'
        },
        {
            'title': '环保部门加强雾霾治理',
            'snippet': '环保部门表示将采取多项措施治理雾霾，包括限行、工厂停产等……'
        }
    ]
    
    summary = generator.generate_summary('北京雾霾', test_news)
    print(f"生成的总结：\n{summary}")

