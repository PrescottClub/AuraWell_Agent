#!/usr/bin/env python3
"""
测试真实DeepSeek API配置

验证您的DeepSeek API Key是否正确配置并能正常工作
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# 加载.env文件
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ 已加载.env文件: {env_path}")
else:
    print(f"⚠️ .env文件不存在: {env_path}")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_api_key_configuration():
    """测试API Key配置"""
    logger.info("=== 测试API Key配置 ===")
    
    # 检查环境变量
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        logger.error("❌ DASHSCOPE_API_KEY 未配置")
        return False
    
    if api_key.startswith('sk-56894de131e14831ba4bcf9232ddf525'):
        logger.info("✅ API Key 配置正确")
        return True
    else:
        logger.warning(f"⚠️ API Key 格式可能不正确: {api_key[:10]}...")
        return False


def test_service_factory_with_real_api():
    """测试ServiceFactory使用真实API"""
    logger.info("=== 测试ServiceFactory使用真实API ===")
    
    from aurawell.core.service_factory import ServiceClientFactory
    from aurawell.core.deepseek_client import DeepSeekClient
    
    # 重置工厂状态
    ServiceClientFactory.reset_clients()
    
    try:
        # 获取DeepSeek客户端
        client = ServiceClientFactory.get_deepseek_client()
        
        # 检查是否是真实客户端
        if isinstance(client, DeepSeekClient):
            logger.info("✅ 成功获取真实DeepSeek客户端")
            
            # 检查服务状态
            status = ServiceClientFactory.get_service_status()
            deepseek_status = status.get('deepseek', {})
            
            if deepseek_status.get('status') == 'live':
                logger.info("✅ DeepSeek服务状态: 真实API模式")
                return True
            else:
                logger.warning(f"⚠️ DeepSeek服务状态异常: {deepseek_status}")
                return False
        else:
            logger.error(f"❌ 获取到Mock客户端而非真实客户端: {type(client)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ ServiceFactory测试失败: {e}")
        return False


def test_real_ai_response():
    """测试真实AI响应"""
    logger.info("=== 测试真实AI响应 ===")
    
    from aurawell.core.service_factory import ServiceClientFactory
    
    try:
        client = ServiceClientFactory.get_deepseek_client()
        
        # 测试简单的健康咨询
        messages = [
            {
                "role": "system", 
                "content": "你是AuraWell的专业健康顾问，请提供简洁专业的健康建议。"
            },
            {
                "role": "user", 
                "content": "我想了解如何保持健康的作息时间，请给我一些建议。"
            }
        ]
        
        logger.info("正在调用DeepSeek API...")
        response = client.get_deepseek_response(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        if response and response.content:
            logger.info("✅ 成功获取AI响应")
            logger.info(f"📝 AI响应内容 (前100字符): {response.content[:100]}...")
            logger.info(f"🤖 使用模型: {response.model}")
            
            # 检查是否是真实响应（不包含Mock标识）
            if "[Mock响应]" not in response.content:
                logger.info("✅ 确认为真实AI响应")
                return True
            else:
                logger.warning("⚠️ 响应中包含Mock标识，可能配置有误")
                return False
        else:
            logger.error("❌ 未获取到有效响应")
            return False
            
    except Exception as e:
        logger.error(f"❌ AI响应测试失败: {e}")
        return False


def test_service_status_api():
    """测试服务状态API"""
    logger.info("=== 测试服务状态API ===")
    
    from aurawell.interfaces.service_status_api import (
        get_current_service_status,
        is_zero_config_mode,
        get_live_services,
        get_mock_services
    )
    
    try:
        # 获取服务状态
        status = get_current_service_status()
        live_services = get_live_services()
        mock_services = get_mock_services()
        zero_config = is_zero_config_mode()
        
        logger.info(f"📊 服务状态总览:")
        logger.info(f"  - 真实服务: {live_services}")
        logger.info(f"  - Mock服务: {mock_services}")
        logger.info(f"  - 零配置模式: {zero_config}")
        
        # 验证DeepSeek是否在真实服务列表中
        if 'deepseek' in live_services:
            logger.info("✅ DeepSeek已切换到真实API模式")
            return True
        else:
            logger.warning("⚠️ DeepSeek仍在Mock模式")
            return False
            
    except Exception as e:
        logger.error(f"❌ 服务状态API测试失败: {e}")
        return False


def test_health_service_integration():
    """测试健康服务集成"""
    logger.info("=== 测试健康服务集成 ===")
    
    try:
        from aurawell.langchain_agent.services.health_advice_service import HealthAdviceService
        from aurawell.core.deepseek_client import DeepSeekClient
        
        # 初始化健康建议服务
        health_service = HealthAdviceService()
        
        # 检查是否使用真实客户端
        if isinstance(health_service.deepseek_client, DeepSeekClient):
            logger.info("✅ 健康建议服务已使用真实DeepSeek客户端")
            
            # 测试健康建议生成
            messages = [
                {"role": "system", "content": "你是专业的健康顾问"},
                {"role": "user", "content": "我最近总是感觉疲劳，有什么改善建议吗？"}
            ]
            
            response = health_service.deepseek_client.get_deepseek_response(messages=messages)
            
            if response and response.content and "[Mock响应]" not in response.content:
                logger.info("✅ 健康服务真实AI响应正常")
                logger.info(f"📝 健康建议 (前80字符): {response.content[:80]}...")
                return True
            else:
                logger.warning("⚠️ 健康服务响应异常")
                return False
        else:
            logger.error("❌ 健康建议服务仍在使用Mock客户端")
            return False
            
    except Exception as e:
        logger.error(f"❌ 健康服务集成测试失败: {e}")
        return False


def main():
    """主函数"""
    logger.info("🚀 开始测试DeepSeek API配置...")
    
    tests = [
        ("API Key配置", test_api_key_configuration),
        ("ServiceFactory真实API", test_service_factory_with_real_api),
        ("真实AI响应", test_real_ai_response),
        ("服务状态API", test_service_status_api),
        ("健康服务集成", test_health_service_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} 通过")
            else:
                logger.error(f"❌ {test_name} 失败")
        except Exception as e:
            logger.error(f"❌ {test_name} 异常: {e}")
    
    logger.info(f"\n🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！DeepSeek API配置成功")
        logger.info("📋 配置总结:")
        logger.info("  ✅ DeepSeek AI: 真实API模式")
        logger.info("  🟡 MCP工具: Mock模式 (可添加API Key启用)")
        logger.info("  🟡 其他服务: Mock模式")
        logger.info("\n🚀 您现在可以享受真实AI驱动的健康建议服务！")
        return True
    else:
        logger.error("❌ 部分测试失败，请检查配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
