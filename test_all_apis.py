#!/usr/bin/env python3
"""
AuraWell API 完整测试脚本
测试所有API端点，确认LangChain迁移后系统正常运行
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API基础配置
BASE_URL = "http://127.0.0.1:8000"
TEST_USER_ID = "test_user_123"
TEST_TOKEN = "test_token_for_api_testing"

class APITester:
    """API测试器"""
    
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, method: str, endpoint: str, data: Dict = None, 
                          headers: Dict = None, expected_status: int = 200) -> Dict[str, Any]:
        """测试单个API端点"""
        url = f"{BASE_URL}{endpoint}"
        test_name = f"{method} {endpoint}"
        
        try:
            logger.info(f"🧪 测试: {test_name}")
            start_time = time.time()
            
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    response_data = await response.json()
                    status = response.status
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    response_data = await response.json()
                    status = response.status
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, headers=headers) as response:
                    response_data = await response.json()
                    status = response.status
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response_time = time.time() - start_time
            
            # 判断测试结果
            success = status == expected_status
            result = {
                "test_name": test_name,
                "success": success,
                "status_code": status,
                "expected_status": expected_status,
                "response_time": round(response_time, 3),
                "response_data": response_data
            }
            
            if success:
                logger.info(f"✅ {test_name} - 状态码: {status}, 响应时间: {response_time:.3f}s")
            else:
                logger.error(f"❌ {test_name} - 期望状态码: {expected_status}, 实际: {status}")
                
            self.test_results.append(result)
            return result
            
        except Exception as e:
            logger.error(f"❌ {test_name} - 异常: {str(e)}")
            result = {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "response_time": 0
            }
            self.test_results.append(result)
            return result
    
    async def run_all_tests(self):
        """运行所有API测试"""
        logger.info("🚀 开始API测试...")

        # 1. 系统健康检查
        await self.test_endpoint("GET", "/api/v1/health")

        # 2. 认证相关测试
        auth_data = {
            "username": "test_user",
            "password": "test_password"
        }
        auth_result = await self.test_endpoint("POST", "/api/v1/auth/login", data=auth_data)

        # 获取真实的token
        real_token = TEST_TOKEN  # 默认token
        if auth_result.get("success") and auth_result.get("response_data"):
            token_data = auth_result["response_data"].get("data", {})
            if token_data.get("access_token"):
                real_token = token_data["access_token"]
                logger.info("✅ 获取到真实token，将用于后续测试")

        # 3. 聊天API测试（核心功能）
        chat_data = {
            "message": "你好，我想了解我的健康状况"
        }
        headers = {"Authorization": f"Bearer {real_token}"}
        await self.test_endpoint("POST", "/api/v1/chat", data=chat_data, headers=headers)
        
        # 4. 用户资料API测试
        await self.test_endpoint("GET", "/api/v1/user/profile", headers=headers)

        profile_update_data = {
            "display_name": "测试用户",
            "age": 25,
            "height_cm": 170.0,
            "weight_kg": 70.0
        }
        await self.test_endpoint("PUT", "/api/v1/user/profile", data=profile_update_data, headers=headers)

        # 5. 健康摘要API测试
        await self.test_endpoint("GET", "/api/v1/health/summary", headers=headers)
        await self.test_endpoint("GET", "/api/v1/health/summary?days=14", headers=headers)

        # 6. 健康目标API测试
        await self.test_endpoint("GET", "/api/v1/health/goals", headers=headers)

        goal_data = {
            "goal_type": "steps",
            "target_value": 10000,
            "target_unit": "steps/day",
            "target_date": "2025-02-01",
            "description": "每日步数目标"
        }
        await self.test_endpoint("POST", "/api/v1/health/goals", data=goal_data, headers=headers)

        # 7. 成就系统API测试
        await self.test_endpoint("GET", "/api/v1/achievements", headers=headers)
        
        # 8. API文档测试（跳过HTML响应的docs端点）
        await self.test_endpoint("GET", "/openapi.json", expected_status=200)
        
        # 9. 错误处理测试
        await self.test_endpoint("GET", "/api/v1/nonexistent", expected_status=404)
        
        logger.info("🏁 API测试完成")
        
    def generate_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.get("success", False))
        failed_tests = total_tests - passed_tests
        
        avg_response_time = sum(result.get("response_time", 0) for result in self.test_results) / total_tests if total_tests > 0 else 0
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
                "average_response_time": round(avg_response_time, 3)
            },
            "details": self.test_results
        }
        
        return report
    
    def print_summary(self):
        """打印测试摘要"""
        report = self.generate_report()
        summary = report["summary"]
        
        print("\n" + "="*60)
        print("🧪 API测试结果摘要")
        print("="*60)
        print(f"总测试数: {summary['total_tests']}")
        print(f"通过: {summary['passed']} ✅")
        print(f"失败: {summary['failed']} ❌")
        print(f"成功率: {summary['success_rate']}%")
        print(f"平均响应时间: {summary['average_response_time']}s")
        print("="*60)
        
        # 显示失败的测试
        failed_tests = [result for result in self.test_results if not result.get("success", False)]
        if failed_tests:
            print("\n❌ 失败的测试:")
            for test in failed_tests:
                print(f"  - {test['test_name']}: {test.get('error', '状态码不匹配')}")
        else:
            print("\n🎉 所有测试都通过了！")
        
        print("\n")

async def main():
    """主函数"""
    print("🚀 AuraWell API 完整测试")
    print("测试LangChain迁移后的系统状态")
    print("-" * 50)
    
    async with APITester() as tester:
        await tester.run_all_tests()
        tester.print_summary()
        
        # 保存详细报告
        report = tester.generate_report()
        with open("api_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("📄 详细测试报告已保存到: api_test_report.json")
        
        # 返回成功率用于判断是否可以推送
        return report["summary"]["success_rate"] >= 80  # 80%以上成功率才推送

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("✅ API测试通过，可以推送到GitHub")
    else:
        print("❌ API测试未通过，请修复问题后再推送")
