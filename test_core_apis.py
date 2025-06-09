#!/usr/bin/env python3
"""
AuraWell 核心API测试
验证LangChain迁移后的核心功能
"""

import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000"

async def test_core_functionality():
    """测试核心功能"""
    async with aiohttp.ClientSession() as session:
        results = []
        
        # 1. 系统健康检查
        logger.info("🧪 测试系统健康检查...")
        async with session.get(f"{BASE_URL}/api/v1/health") as response:
            if response.status == 200:
                logger.info("✅ 系统健康检查通过")
                results.append(("系统健康检查", True))
            else:
                logger.error("❌ 系统健康检查失败")
                results.append(("系统健康检查", False))
        
        # 2. 用户认证
        logger.info("🧪 测试用户认证...")
        auth_data = {"username": "test_user", "password": "test_password"}
        async with session.post(f"{BASE_URL}/api/v1/auth/login", json=auth_data) as response:
            if response.status == 200:
                auth_result = await response.json()
                token = auth_result.get("data", {}).get("access_token")
                if token:
                    logger.info("✅ 用户认证成功，获取到token")
                    results.append(("用户认证", True))
                    
                    # 3. 测试需要认证的API
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # 用户资料
                    logger.info("🧪 测试用户资料API...")
                    async with session.get(f"{BASE_URL}/api/v1/user/profile", headers=headers) as profile_response:
                        if profile_response.status == 200:
                            logger.info("✅ 用户资料API正常")
                            results.append(("用户资料API", True))
                        else:
                            logger.error("❌ 用户资料API失败")
                            results.append(("用户资料API", False))
                    
                    # 健康摘要
                    logger.info("🧪 测试健康摘要API...")
                    async with session.get(f"{BASE_URL}/api/v1/health/summary", headers=headers) as summary_response:
                        if summary_response.status == 200:
                            logger.info("✅ 健康摘要API正常")
                            results.append(("健康摘要API", True))
                        else:
                            logger.error("❌ 健康摘要API失败")
                            results.append(("健康摘要API", False))
                    
                    # 健康目标
                    logger.info("🧪 测试健康目标API...")
                    async with session.get(f"{BASE_URL}/api/v1/health/goals", headers=headers) as goals_response:
                        if goals_response.status == 200:
                            logger.info("✅ 健康目标API正常")
                            results.append(("健康目标API", True))
                        else:
                            logger.error("❌ 健康目标API失败")
                            results.append(("健康目标API", False))
                    
                    # 成就系统
                    logger.info("🧪 测试成就系统API...")
                    async with session.get(f"{BASE_URL}/api/v1/achievements", headers=headers) as achievements_response:
                        if achievements_response.status == 200:
                            logger.info("✅ 成就系统API正常")
                            results.append(("成就系统API", True))
                        else:
                            logger.error("❌ 成就系统API失败")
                            results.append(("成就系统API", False))
                    
                    # 聊天API（核心LangChain功能）
                    logger.info("🧪 测试聊天API（LangChain Agent）...")
                    chat_data = {"message": "你好，我想了解我的健康状况"}
                    try:
                        async with session.post(f"{BASE_URL}/api/v1/chat", json=chat_data, headers=headers) as chat_response:
                            if chat_response.status == 200:
                                chat_result = await chat_response.json()
                                if chat_result.get("reply"):
                                    logger.info("✅ 聊天API正常，LangChain Agent工作正常")
                                    results.append(("聊天API(LangChain)", True))
                                else:
                                    logger.error("❌ 聊天API响应格式异常")
                                    results.append(("聊天API(LangChain)", False))
                            else:
                                logger.error(f"❌ 聊天API失败，状态码: {chat_response.status}")
                                results.append(("聊天API(LangChain)", False))
                    except Exception as e:
                        logger.error(f"❌ 聊天API异常: {e}")
                        results.append(("聊天API(LangChain)", False))
                        
                else:
                    logger.error("❌ 认证成功但未获取到token")
                    results.append(("用户认证", False))
            else:
                logger.error("❌ 用户认证失败")
                results.append(("用户认证", False))
        
        # 4. API文档
        logger.info("🧪 测试API文档...")
        async with session.get(f"{BASE_URL}/openapi.json") as docs_response:
            if docs_response.status == 200:
                logger.info("✅ API文档正常")
                results.append(("API文档", True))
            else:
                logger.error("❌ API文档失败")
                results.append(("API文档", False))
        
        return results

async def main():
    """主函数"""
    print("🚀 AuraWell 核心API测试")
    print("验证LangChain迁移后的系统状态")
    print("-" * 50)
    
    try:
        results = await test_core_functionality()
        
        # 统计结果
        total_tests = len(results)
        passed_tests = sum(1 for _, success in results if success)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "="*60)
        print("🧪 核心API测试结果摘要")
        print("="*60)
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {success_rate:.1f}%")
        print("="*60)
        
        # 显示详细结果
        print("\n📋 详细测试结果:")
        for test_name, success in results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"  - {test_name}: {status}")
        
        # 判断是否可以推送
        if success_rate >= 70:  # 70%以上成功率
            print(f"\n🎉 核心功能测试通过！成功率: {success_rate:.1f}%")
            print("✅ 系统已准备好推送到GitHub")
            return True
        else:
            print(f"\n⚠️ 核心功能测试未完全通过，成功率: {success_rate:.1f}%")
            print("❌ 建议修复问题后再推送")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
