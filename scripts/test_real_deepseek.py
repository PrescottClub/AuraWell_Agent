#!/usr/bin/env python3
"""
DeepSeek API 真实连接验证脚本
==========================

此脚本验证AuraWell Agent与真实DeepSeek API的连接能力。

执行要求：
1. 成功加载环境变量中的API密钥
2. 成功发送测试请求到DeepSeek API
3. 在控制台打印DeepSeek的真实回复

测试标准：显示DeepSeek AI的真实响应
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv(dotenv_path='.env', override=True)

from src.aurawell.core.deepseek_client import DeepSeekClient
from src.aurawell.config.settings import settings


async def test_deepseek_api():
    """
    测试真实DeepSeek API连接
    """
    print("🚀 启动DeepSeek API真实连接验证...")
    print("=" * 60)
    
    # 1. 验证API密钥加载
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 错误：未找到DEEPSEEK_API_KEY环境变量")
        print("请确保.env文件存在且包含有效的API密钥")
        return False
        
    print(f"✅ API密钥已加载: {api_key[:8]}...{api_key[-8:]}")
    
    # 2. 验证设置配置
    print(f"✅ 配置验证:")
    print(f"   - 基础URL: {settings.DEEPSEEK_BASE_URL}")
    print(f"   - 默认模型: {settings.DEEPSEEK_DEFAULT_MODEL}")
    print(f"   - 最大Tokens: {settings.DEEPSEEK_MAX_TOKENS}")
    
    # 3. 创建DeepSeek客户端
    try:
        async with DeepSeekClient(api_key=api_key) as client:
            print("✅ DeepSeek客户端初始化成功")
            
            # 4. 发送测试请求
            print("\n🧠 向DeepSeek AI发送测试请求...")
            test_messages = [
                {
                    "role": "user",
                    "content": "你好，请介绍一下你自己，包括你的能力和特点。"
                }
            ]
            
            # 执行真实API调用
            print("⏳ 等待DeepSeek响应...")
            response = await client.get_deepseek_response(
                messages=test_messages,
                max_tokens=500,
                temperature=0.7
            )
            
            # 5. 打印成功结果
            print("\n🎉 DeepSeek API测试成功！")
            print("=" * 60)
            print("📝 DeepSeek AI的真实回复:")
            print("-" * 60)
            print(response)
            print("-" * 60)
            
            return True
            
    except Exception as e:
        print(f"❌ DeepSeek API测试失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        return False


async def test_deepseek_health_advice():
    """
    测试DeepSeek健康建议功能
    """
    print("\n🏥 测试DeepSeek健康建议功能...")
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    try:
        async with DeepSeekClient(api_key=api_key) as client:
            # 测试健康建议生成
            health_query = "我最近睡眠质量不好，经常失眠，请给我一些改善睡眠的建议。"
            
            print(f"🤔 健康查询: {health_query}")
            print("⏳ 等待DeepSeek健康建议...")
            
            advice = await client.generate_health_advice(
                user_query=health_query,
                max_tokens=600
            )
            
            print("\n💡 DeepSeek健康建议:")
            print("-" * 60)
            print(advice)
            print("-" * 60)
            
            return True
            
    except Exception as e:
        print(f"❌ 健康建议测试失败: {e}")
        return False


async def main():
    """
    主验证函数
    """
    print("🎯 AuraWell Agent - DeepSeek API真实连接验证")
    print("🔥 Phoenix项目第三阶段 - 接入真实世界")
    print("⚡ 任务：验证AI Agent的真实智能")
    print("=" * 80)
    
    # 基础API测试
    basic_test_success = await test_deepseek_api()
    
    if basic_test_success:
        # 健康建议测试
        health_test_success = await test_deepseek_health_advice()
        
        if health_test_success:
            print("\n🏆 所有测试通过！AuraWell Agent已具备真实AI能力！")
            print("🚀 准备进入Task 3.2.1 - Apple Health真实API集成")
            print("🧠 准备进入Task 3.3.1 - Orchestrator智能强化")
            return True
    
    print("\n💥 验证失败，请检查配置后重试")
    return False


if __name__ == "__main__":
    """
    脚本入口点
    """
    try:
        result = asyncio.run(main())
        exit_code = 0 if result else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 未预期错误: {e}")
        sys.exit(1) 