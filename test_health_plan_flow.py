#!/usr/bin/env python3
"""
健康计划功能测试脚本

测试健康计划的创建、获取和显示流程
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime


class HealthPlanTester:
    """健康计划功能测试器"""
    
    def __init__(self, base_url="http://127.0.0.1:8001"):
        self.base_url = base_url
        self.session = None
        self.test_user_id = "dev_user_001"
        self.auth_token = "dev-test-token"  # 开发环境测试token
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_check(self):
        """测试API健康状态"""
        print("🔍 测试API健康状态...")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API健康状态正常: {data['message']}")
                    return True
                else:
                    print(f"❌ API健康检查失败: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ API连接失败: {e}")
            return False
    
    async def test_get_empty_plans(self):
        """测试获取空的计划列表"""
        print("\n🔍 测试获取空的计划列表...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with self.session.get(
                f"{self.base_url}/api/v1/health-plan/plans",
                headers=headers
            ) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        print(f"   响应数据: {data}")
                        # API返回的plans在根级别，不在data字段中
                        plans = data.get('plans', [])
                        print(f"✅ 成功获取计划列表，当前计划数量: {len(plans)}")
                        return plans
                    except Exception as json_error:
                        text = await response.text()
                        print(f"   响应内容: {text}")
                        print(f"   JSON解析失败: {json_error}")
                        return []
                else:
                    print(f"❌ 获取计划列表失败: {response.status}")
                    text = await response.text()
                    print(f"   错误详情: {text}")
                    return []
        except Exception as e:
            print(f"❌ 获取计划列表异常: {e}")
            import traceback
            print(f"   异常详情: {traceback.format_exc()}")
            return []
    
    async def test_create_plan(self):
        """测试创建健康计划"""
        print("\n🔍 测试创建健康计划...")
        
        plan_request = {
            "goals": ["减重", "增强体质"],
            "modules": ["diet", "exercise", "weight"],
            "duration_days": 30,
            "user_preferences": {
                "dietary_restrictions": ["vegetarian"],
                "exercise_level": "beginner",
                "available_time": "30-60 minutes"
            }
        }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/health-plan/generate",
                headers=headers,
                json=plan_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   创建计划响应: {data}")
                    # 检查不同的响应格式
                    plan = data.get('plan')
                    if plan:
                        print(f"✅ 成功创建健康计划:")
                        print(f"   计划ID: {plan.get('plan_id')}")
                        print(f"   标题: {plan.get('title')}")
                        print(f"   描述: {plan.get('description')}")
                        print(f"   模块数量: {len(plan.get('modules', []))}")
                        print(f"   持续天数: {plan.get('duration_days')}")
                        return plan
                    else:
                        print("❌ 创建计划成功但未返回计划数据")
                        return None
                else:
                    print(f"❌ 创建计划失败: {response.status}")
                    text = await response.text()
                    print(f"   错误详情: {text}")
                    return None
        except Exception as e:
            print(f"❌ 创建计划异常: {e}")
            import traceback
            print(f"   异常详情: {traceback.format_exc()}")
            return None
    
    async def test_get_plans_after_creation(self):
        """测试创建计划后获取计划列表"""
        print("\n🔍 测试创建计划后获取计划列表...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with self.session.get(
                f"{self.base_url}/api/v1/health-plan/plans",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # API返回的plans在根级别
                    plans = data.get('plans', [])
                    print(f"✅ 成功获取计划列表，当前计划数量: {len(plans)}")
                    
                    for i, plan in enumerate(plans, 1):
                        print(f"   计划 {i}:")
                        print(f"     ID: {plan.get('plan_id')}")
                        print(f"     标题: {plan.get('title')}")
                        print(f"     状态: {plan.get('status')}")
                        print(f"     进度: {plan.get('progress')}%")
                        print(f"     模块: {[m.get('module_type') for m in plan.get('modules', [])]}")
                    
                    return plans
                else:
                    print(f"❌ 获取计划列表失败: {response.status}")
                    return []
        except Exception as e:
            print(f"❌ 获取计划列表异常: {e}")
            return []
    
    async def test_get_plan_detail(self, plan_id):
        """测试获取计划详情"""
        print(f"\n🔍 测试获取计划详情 (ID: {plan_id})...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with self.session.get(
                f"{self.base_url}/api/v1/health-plan/plans/{plan_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    plan = data.get('data', {}).get('plan')
                    if plan:
                        print(f"✅ 成功获取计划详情:")
                        print(f"   标题: {plan.get('title')}")
                        print(f"   描述: {plan.get('description')}")
                        print(f"   状态: {plan.get('status')}")
                        print(f"   进度: {plan.get('progress')}%")
                        
                        modules = plan.get('modules', [])
                        print(f"   模块详情 ({len(modules)}个):")
                        for module in modules:
                            print(f"     - {module.get('title')} ({module.get('module_type')})")
                            print(f"       描述: {module.get('description')}")
                        
                        return plan
                    else:
                        print("❌ 获取计划详情成功但未返回计划数据")
                        return None
                else:
                    print(f"❌ 获取计划详情失败: {response.status}")
                    return None
        except Exception as e:
            print(f"❌ 获取计划详情异常: {e}")
            return None
    
    async def run_full_test(self):
        """运行完整的测试流程"""
        print("🚀 开始健康计划功能测试")
        print("=" * 60)
        
        # 1. 测试API健康状态
        if not await self.test_health_check():
            print("❌ API不可用，测试终止")
            return False
        
        # 2. 测试获取空的计划列表
        initial_plans = await self.test_get_empty_plans()
        initial_count = len(initial_plans)
        
        # 3. 测试创建健康计划
        created_plan = await self.test_create_plan()
        if not created_plan:
            print("❌ 计划创建失败，测试终止")
            return False
        
        # 4. 测试创建后获取计划列表
        updated_plans = await self.test_get_plans_after_creation()
        updated_count = len(updated_plans)
        
        # 验证计划数量是否增加
        if updated_count > initial_count:
            print(f"✅ 计划列表更新成功，计划数量从 {initial_count} 增加到 {updated_count}")
        else:
            print(f"⚠️  计划数量未增加，可能存在问题 (初始: {initial_count}, 当前: {updated_count})")
        
        # 5. 测试获取计划详情
        if created_plan and created_plan.get('plan_id'):
            plan_detail = await self.test_get_plan_detail(created_plan['plan_id'])
            if plan_detail:
                print("✅ 计划详情获取成功")
            else:
                print("❌ 计划详情获取失败")
        
        print("\n" + "=" * 60)
        print("🎉 健康计划功能测试完成")
        
        # 总结
        print(f"\n📊 测试总结:")
        print(f"   初始计划数量: {initial_count}")
        print(f"   创建计划: {'成功' if created_plan else '失败'}")
        print(f"   最终计划数量: {updated_count}")
        print(f"   数据持久化: {'成功' if updated_count > initial_count else '可能失败'}")
        
        return True


async def main():
    """主函数"""
    print("🏥 AuraWell 健康计划功能测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    async with HealthPlanTester() as tester:
        success = await tester.run_full_test()
        
        if success:
            print("\n✅ 所有测试完成")
        else:
            print("\n❌ 测试过程中出现错误")
            sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)
