# -*- coding: utf-8 -*-
"""
列出 ModelScope API 支持的模型
"""

import requests
import json
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ModelScope API 基础URL
base_url = "https://api-inference.modelscope.cn/v1"

print("=" * 80)
print("ModelScope API 模型列表")
print("=" * 80)
print()
print("注意: ModelScope API 使用 OpenAI 兼容格式")
print(f"API 基础URL: {base_url}")
print()
print("=" * 80)
print("常用推荐模型:")
print("=" * 80)
print()

# 常用模型列表（根据 ModelScope 文档）
common_models = [
    {
        "id": "Qwen/Qwen2.5-Coder-32B-Instruct",
        "name": "Qwen2.5-Coder-32B-Instruct",
        "description": "32B参数代码生成模型，适合代码相关任务",
        "type": "代码生成"
    },
    {
        "id": "Qwen/Qwen2.5-72B-Instruct",
        "name": "Qwen2.5-72B-Instruct",
        "description": "72B参数通用对话模型，性能强大",
        "type": "通用对话"
    },
    {
        "id": "Qwen/Qwen2.5-32B-Instruct",
        "name": "Qwen2.5-32B-Instruct",
        "description": "32B参数通用对话模型，平衡性能和速度",
        "type": "通用对话"
    },
    {
        "id": "Qwen/Qwen2.5-14B-Instruct",
        "name": "Qwen2.5-14B-Instruct",
        "description": "14B参数通用对话模型，速度快",
        "type": "通用对话"
    },
    {
        "id": "Qwen/Qwen2.5-7B-Instruct",
        "name": "Qwen2.5-7B-Instruct",
        "description": "7B参数通用对话模型，速度快，适合快速响应",
        "type": "通用对话"
    },
    {
        "id": "Qwen/Qwen2.5-1.5B-Instruct",
        "name": "Qwen2.5-1.5B-Instruct",
        "description": "1.5B参数轻量级模型，速度最快",
        "type": "通用对话"
    },
    {
        "id": "deepseek-ai/DeepSeek-V2.5",
        "name": "DeepSeek-V2.5",
        "description": "DeepSeek V2.5 模型",
        "type": "通用对话"
    },
    {
        "id": "01-ai/Yi-1.5-34B-Chat",
        "name": "Yi-1.5-34B-Chat",
        "description": "Yi 1.5 34B 对话模型",
        "type": "通用对话"
    },
]

for i, model in enumerate(common_models, 1):
    print(f"{i}. {model['name']}")
    print(f"   模型ID: {model['id']}")
    print(f"   类型: {model['type']}")
    print(f"   描述: {model['description']}")
    print()

print("=" * 80)
print("配置说明:")
print("=" * 80)
print()
print("在 config.ini 中配置:")
print()
print("[AI]")
print("enabled = true")
print("api_type = openai")
print("api_key = YOUR_MODELSCOPE_ACCESS_TOKEN")
print("api_base = https://api-inference.modelscope.cn/v1")
print("model = Qwen/Qwen2.5-7B-Instruct  # 推荐用于文本总结")
print("max_tokens = 2000")
print()
print("=" * 80)
print("获取 Access Token:")
print("=" * 80)
print("1. 访问 https://modelscope.cn/")
print("2. 注册/登录账号")
print("3. 在个人中心获取 Access Token")
print("=" * 80)

