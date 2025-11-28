# -*- coding: utf-8 -*-
"""
测试AI模块导入
"""

import sys
import os

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"当前工作目录: {os.getcwd()}")
print(f"脚本所在目录: {current_dir}")
print(f"Python路径: {sys.path[:3]}...")
print()

# 测试导入requests
print("1. 测试导入requests模块...")
try:
    import requests
    print(f"   ✓ requests模块导入成功，版本: {requests.__version__}")
except ImportError as e:
    print(f"   ✗ requests模块导入失败: {e}")
    print("   请运行: pip install requests")
    sys.exit(1)

# 测试导入ai_summary
print("\n2. 测试导入ai_summary模块...")
try:
    from ai_summary import AISummaryGenerator
    print("   ✓ ai_summary模块导入成功")
except ImportError as e:
    print(f"   ✗ ai_summary模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"   ✗ 导入时发生其他错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试初始化
print("\n3. 测试初始化AISummaryGenerator...")
try:
    config_path = os.path.join(os.path.dirname(current_dir), 'config.ini')
    print(f"   配置文件路径: {config_path}")
    
    if not os.path.exists(config_path):
        print(f"   ✗ 配置文件不存在: {config_path}")
        sys.exit(1)
    
    generator = AISummaryGenerator(config_path, 'utf-8')
    print("   ✓ AISummaryGenerator初始化成功")
    print(f"   - API类型: {generator.api_type}")
    print(f"   - 模型: {generator.model}")
    print(f"   - 已启用: {generator.enabled}")
    print(f"   - API Key已配置: {'是' if generator.api_key and generator.api_key != 'your_api_key_here' else '否'}")
    
except Exception as e:
    print(f"   ✗ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ 所有测试通过！AI模块可以正常使用。")

