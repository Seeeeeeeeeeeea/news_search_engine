# -*- coding: utf-8 -*-
"""
AI总结模块 - 适配 ModelScope 及 OpenAI 兼容接口
"""

import os
import configparser
from typing import List, Dict, Optional

# 按照你的规范导入 OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("错误: 未安装 openai 库，请运行 pip install openai")

class AISummaryGenerator:
    """AI总结生成器 (基于 OpenAI 官方 SDK)"""
    
    def __init__(self, config_path: str, config_encoding: str = 'utf-8'):
        if not os.path.exists(config_path):
            print(f"严重警告: 配置文件不存在 -> {config_path}")
        
        self.config = configparser.ConfigParser()
        self.config.read(config_path, config_encoding)
        
        # 1. 读取配置
        self.enabled = self.config.getboolean('AI', 'enabled', fallback=False)
        self.api_key = self.config.get('AI', 'api_key', fallback='').strip('"\' ')
        
        # ModelScope Base URL
        self.api_base = self.config.get('AI', 'api_base', fallback='https://api-inference.modelscope.cn/v1/').strip('"\' ')
        
        # ModelScope Model ID
        self.model = self.config.get('AI', 'model', fallback='Qwen/Qwen2.5-Coder-32B-Instruct').strip('"\' ')
        self.max_tokens = int(self.config.get('AI', 'max_tokens', fallback='1000'))

    def generate_summary(self, keyword: str, news_list: List[Dict]) -> Optional[str]:
        """生成总结的主入口"""
        if not self.enabled:
            return None
        if not OPENAI_AVAILABLE:
            print("AI功能已启用但未安装openai库")
            return None

        # 2. 构建 Prompt
        prompt = self._build_prompt(keyword, news_list)
        
        # 3. 调用 API
        return self._call_ai_api(prompt)

    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """使用 OpenAI SDK 调用 API"""
        try:
            # 实例化客户端 (严格按照你的导入规范)
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )

            # 发起请求 (stream=False 适合总结任务)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个专业的新闻总结助手，请简明扼要地总结用户提供的新闻内容。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                max_tokens=self.max_tokens,
                stream=False
            )

            # 获取结果
            if response.choices:
                return response.choices[0].message.content.strip()
            return None

        except Exception as e:
            print(f"AI API 调用失败: {e},请检查api密钥是否正确,并关闭代理")
            return None

    def _build_prompt(self, keyword: str, news_list: List[Dict]) -> str:
        """构建提示词"""
        if not news_list:
            return ""
            
        target_news = news_list[:10]
        news_content = []
        
        for i, news in enumerate(target_news):
            title = news.get('title', '无标题').strip()
            snippet = news.get('snippet', '无摘要').strip()
            news_content.append(f"{i+1}. {title}\n   摘要: {snippet}")

        return f"""
请根据以下搜索关键词和相关新闻，生成一段简练的总结（200字左右）。

关键词：{keyword}

相关新闻：
{chr(10).join(news_content)}

请直接输出总结内容，不要包含客套话。
"""

if __name__ == "__main__":
    # --- 路径修正逻辑 ---
    # 获取当前脚本所在的绝对目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取上一级目录
    parent_dir = os.path.dirname(current_dir)
    # 拼接 config.ini 路径
    config_path = os.path.join(parent_dir, 'config.ini')

    print(f"正在读取配置文件: {config_path}")
    
    if os.path.exists(config_path):
        generator = AISummaryGenerator(config_path)
        
        if generator.enabled:
            print("AI功能已启用，正在测试连接...")
            # 模拟数据
            test_data = [
                {'title': 'Python 3.13 发布', 'snippet': 'Python 3.13 带来了移除 GIL 的实验性支持...'},
                {'title': 'AI 编程助手评测', 'snippet': '对比了 Copilot, Cursor 和 ModelScope 的编码能力...'}
            ]
            
            summary = generator.generate_summary("Python 更新", test_data)
            
            print("\n" + "="*20 + " 生成结果 " + "="*20)
            print(summary if summary else "生成失败")
            print("="*50)
        else:
            print("config.ini 中 [AI] enabled = False，跳过测试。")
    else:
        print(f"\n❌ 错误: 找不到配置文件!\n请检查路径是否正确: {config_path}")