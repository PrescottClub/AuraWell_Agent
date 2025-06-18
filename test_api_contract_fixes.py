#!/usr/bin/env python3
"""
API契约修复验证脚本
测试前后端API对齐修复是否成功
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, List

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

class APIContractTester:
    """API契约测试器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def login(self) -> bool:
        """登录获取认证token"""
        try:
            login_data = {
                "username": "test_user",
                "password": "test_password"
            }
            
            async with self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    print("✅ 登录成功")
                    return True
                else:
                    print(f"❌ 登录失败: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def test_chat_history_alias(self) -> bool:
        """测试聊天历史路径别名"""
        print("\n🔍 测试聊天历史路径别名...")
        
        try:
            # 测试新的别名路径
            conversation_id = "test_conv_123"
            async with self.session.get(
                f"{self.base_url}/chat/conversations/{conversation_id}/messages?limit=10",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 聊天历史别名路径正常: {data.get('message', 'No message')}")
                    return True
                else:
                    print(f"❌ 聊天历史别名路径失败: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ 聊天历史别名测试异常: {e}")
            return False
    
    async def test_user_health_goals_crud(self) -> bool:
        """测试用户健康目标CRUD操作"""
        print("\n🔍 测试用户健康目标CRUD...")
        
        try:
            # 1. 创建健康目标
            goal_data = {
                "title": "测试减重目标",
                "description": "3个月减重5kg",
                "type": "weight_loss",
                "target_value": 5.0,
                "current_value": 0.0,
                "unit": "kg",
                "target_date": "2024-09-17",
                "status": "active"
            }
            
            async with self.session.post(
                f"{self.base_url}/user/health-goals",
                json=goal_data,
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    create_data = await response.json()
                    goal_id = create_data.get("id")
                    print(f"✅ 创建健康目标成功: {goal_id}")
                else:
                    print(f"❌ 创建健康目标失败: {response.status}")
                    return False
            
            # 2. 更新健康目标
            update_data = {
                **goal_data,
                "current_value": 2.0,
                "description": "已减重2kg，继续努力"
            }
            
            async with self.session.put(
                f"{self.base_url}/user/health-goals/{goal_id}",
                json=update_data,
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    print("✅ 更新健康目标成功")
                else:
                    print(f"❌ 更新健康目标失败: {response.status}")
                    return False
            
            # 3. 删除健康目标
            async with self.session.delete(
                f"{self.base_url}/user/health-goals/{goal_id}",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    print("✅ 删除健康目标成功")
                    return True
                else:
                    print(f"❌ 删除健康目标失败: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ 健康目标CRUD测试异常: {e}")
            return False
    
    async def test_frontend_compatible_endpoints(self) -> bool:
        """测试前端兼容性端点"""
        print("\n🔍 测试前端兼容性端点...")
        
        endpoints_to_test = [
            ("/user/profile/frontend", "GET"),
            ("/health/summary/frontend", "GET"),
        ]
        
        success_count = 0
        
        for endpoint, method in endpoints_to_test:
            try:
                if method == "GET":
                    async with self.session.get(
                        f"{self.base_url}{endpoint}",
                        headers=self.get_headers()
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            if "success" in data and "data" in data and "message" in data:
                                print(f"✅ {endpoint} 前端兼容格式正确")
                                success_count += 1
                            else:
                                print(f"❌ {endpoint} 响应格式不符合前端期望")
                        else:
                            print(f"❌ {endpoint} 请求失败: {response.status}")
            except Exception as e:
                print(f"❌ {endpoint} 测试异常: {e}")
        
        return success_count == len(endpoints_to_test)
    
    async def test_chat_message_api(self) -> bool:
        """测试聊天消息API"""
        print("\n🔍 测试聊天消息API...")
        
        try:
            message_data = {
                "message": "你好，我想了解健康建议",
                "conversation_id": None,
                "user_id": "test_user",
                "family_member_id": None
            }
            
            async with self.session.post(
                f"{self.base_url}/chat/message",
                json=message_data,
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "reply" in data and "conversation_id" in data:
                        print("✅ 聊天消息API正常")
                        return True
                    else:
                        print(f"❌ 聊天消息响应格式异常: {data}")
                        return False
                else:
                    print(f"❌ 聊天消息API失败: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ 聊天消息API测试异常: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """运行所有测试"""
        print("🚀 开始API契约修复验证...")
        
        results = {}
        
        # 登录测试
        results["login"] = await self.login()
        
        if not results["login"]:
            print("❌ 登录失败，跳过需要认证的测试")
            return results
        
        # 各项功能测试
        results["chat_history_alias"] = await self.test_chat_history_alias()
        results["health_goals_crud"] = await self.test_user_health_goals_crud()
        results["frontend_compatible"] = await self.test_frontend_compatible_endpoints()
        results["chat_message"] = await self.test_chat_message_api()
        
        return results
    
    def print_test_summary(self, results: Dict[str, bool]):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("📊 API契约修复验证结果摘要")
        print("="*60)
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for test_name, passed in results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"{test_name:25} {status}")
        
        print("-"*60)
        print(f"总计: {passed_tests}/{total_tests} 测试通过")
        
        if passed_tests == total_tests:
            print("🎉 所有API契约修复验证通过！")
        else:
            print("⚠️  部分测试失败，需要进一步检查")


async def main():
    """主函数"""
    async with APIContractTester() as tester:
        results = await tester.run_all_tests()
        tester.print_test_summary(results)


if __name__ == "__main__":
    asyncio.run(main())
