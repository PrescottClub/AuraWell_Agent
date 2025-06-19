#!/usr/bin/env python3
"""
测试DeepSeek客户端配置
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.append('src')

from aurawell.core.deepseek_client import DeepSeekClient
from aurawell.config.settings import AuraWellSettings

def test_deepseek_config():
    """测试DeepSeek配置"""
    print("🔧 测试DeepSeek配置...")
    
    # 检查环境变量
    print(f"DEEPSEEK_API_KEY: {'✅ 已设置' if os.getenv('DEEPSEEK_API_KEY') else '❌ 未设置'}")
    print(f"DEEPSEEK_BASE_URL: {os.getenv('DEEPSEEK_BASE_URL', '默认值')}")
    print(f"DEEPSEEK_DEFAULT_MODEL: {os.getenv('DEEPSEEK_DEFAULT_MODEL', '默认值')}")
    
    # 检查设置类
    print(f"\n📋 AuraWellSettings配置:")
    print(f"API Key: {'✅ 已设置' if AuraWellSettings.DEEPSEEK_API_KEY else '❌ 未设置'}")
    print(f"Base URL: {AuraWellSettings.DEEPSEEK_BASE_URL}")
    print(f"Default Model: {AuraWellSettings.DEEPSEEK_DEFAULT_MODEL}")
    
    # 尝试初始化客户端
    try:
        print(f"\n🚀 尝试初始化DeepSeek客户端...")
        client = DeepSeekClient()
        print("✅ DeepSeek客户端初始化成功！")
        
        # 测试简单API调用
        print(f"\n💬 测试API调用...")
        messages = [{"role": "user", "content": "你好，请简单回复一下"}]
        response = client.get_deepseek_response(messages, max_tokens=50)
        print(f"✅ API调用成功！")
        print(f"回复: {response.content}")
        
    except Exception as e:
        print(f"❌ DeepSeek客户端初始化失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_deepseek_config()
