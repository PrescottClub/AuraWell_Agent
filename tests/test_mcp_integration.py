#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP智能工具系统集成测试
测试新的健康咨询智能响应框架
"""

import sys
import os
import asyncio
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from aurawell.langchain_agent.agent import HealthAdviceAgent
from aurawell.langchain_agent.mcp_tools_manager import MCPToolsManager
from aurawell.langchain_agent.mcp_interface import MCPInterface
from aurawell.models.user_profile import UserProfile
from aurawell.models.health_data_model import UnifiedHealthProfile


class MCPIntegrationTester:
    """MCP智能工具系统集成测试器"""
    
    def __init__(self):
        self.agent = HealthAdviceAgent(user_id="test_user_001")
        self.mcp_tools = MCPToolsManager()
        self.mcp_interface = MCPInterface()
        
    def create_test_user_profile(self) -> UserProfile:
        """创建测试用户档案"""
        from aurawell.models.enums import Gender, ActivityLevel, HealthGoal
        return UserProfile(
            user_id="test_user_001",
            email="test@example.com",
            display_name="张小明",
            age=28,
            gender=Gender.MALE,
            height_cm=175.0,
            weight_kg=75.0,
            activity_level=ActivityLevel.MODERATELY_ACTIVE,
            primary_goal=HealthGoal.WEIGHT_LOSS,
            target_weight_kg=70.0,
            daily_steps_goal=10000,
            daily_calories_goal=2200,
            sleep_duration_goal_hours=8.0,
            weekly_exercise_goal_minutes=150,
            timezone="Asia/Shanghai",
            preferred_units="metric",
            data_sharing_consent=True,
            analytics_consent=True
        )
    
    def create_test_health_metrics(self) -> UnifiedHealthProfile:
        """创建测试健康指标"""
        return UnifiedHealthProfile(
            user_id="test_user_001",
            age=28,
            gender="male",
            height_cm=175.0,
            weight_kg=75.0,
            daily_steps_goal=10000,
            daily_calories_goal=2200.0,
            sleep_target_hours=8.0,
            avg_daily_steps=8500,
            avg_sleep_hours=7.5,
            avg_daily_calories=2400.0
        )
    
    async def test_intent_analysis(self):
        """测试意图分析功能"""
        print("🔍 测试意图分析功能...")
        
        test_queries = [
            "我想分析一下我的健康数据趋势",
            "能帮我制定一个减重计划吗？",
            "我需要营养搭配建议",
            "想了解最新的运动科学研究",
            "帮我做个全面的健康评估"
        ]
        
        for query in test_queries:
            print(f"\n📝 测试查询: {query}")
            intent = self.mcp_tools.intent_analyzer.analyze_intent(query)
            print(f"📊 识别意图: {intent}")
            
            # 测试工具选择
            selected_tools = self.mcp_tools.intent_analyzer.get_recommended_tools(intent)
            print(f"🛠️ 推荐工具: {selected_tools}")
            
    async def test_workflow_execution(self):
        """测试工作流执行"""
        print("\n🔄 测试工作流执行...")
        
        # 测试健康分析工作流
        print("\n📊 测试健康分析工作流")
        workflow_result = await self.mcp_tools.execute_workflow(
            workflow_name="health_analysis",
            user_input="分析我的BMI和健康趋势",
            context={
                "user_profile": self.create_test_user_profile().dict(),
                "health_metrics": self.create_test_health_metrics().dict()
            }
        )
        print(f"✅ 工作流结果: {json.dumps(workflow_result, ensure_ascii=False, indent=2)}")
        
    async def test_mcp_tool_calls(self):
        """测试MCP工具调用"""
        print("\n🛠️ 测试MCP工具调用...")
        
        # 测试计算器工具
        print("\n🧮 测试计算器工具")
        bmi_result = await self.mcp_interface.calculator.calculate("BMI = 75 / (1.75^2)")
        print(f"BMI计算结果: {bmi_result}")
        
        # 测试数据库查询工具
        print("\n🗄️ 测试数据库查询工具")
        db_result = await self.mcp_interface.database_sqlite.query("SELECT * FROM user_health_profiles LIMIT 1")
        print(f"数据库查询结果: {db_result}")
        
        # 测试搜索工具
        print("\n🔍 测试搜索工具")
        search_result = await self.mcp_interface.brave_search.search("健康饮食最新研究 2024")
        print(f"搜索结果: {search_result}")
        
    async def test_agent_response(self):
        """测试智能助手完整响应"""
        print("\n🤖 测试智能助手完整响应...")
        
        # 创建测试上下文
        user_profile = self.create_test_user_profile()
        health_metrics = self.create_test_health_metrics()
        
        test_query = "我想制定一个科学的减重计划，需要包含饮食、运动和进度跟踪"
        
        print(f"📝 用户查询: {test_query}")
        print("🔄 正在生成智能响应...")
        
                 try:
             response = await self.agent.process_message(
                 message=test_query,
                 context={
                     "user_profile": user_profile.dict(),
                     "health_metrics": health_metrics.dict(),
                     "conversation_history": []
                 }
             )
            
            print("\n✅ 智能响应结果:")
            print("=" * 80)
            print(response.get("advice", "未获得建议"))
            print("=" * 80)
            
            # 检查是否包含MCP工具调用信息
            if "tool_calls" in response:
                print(f"\n🛠️ 使用的MCP工具: {response['tool_calls']}")
            
            if "workflow_results" in response:
                print(f"\n🔄 工作流执行结果: {response['workflow_results']}")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始MCP智能工具系统集成测试")
        print("=" * 80)
        
        try:
            await self.test_intent_analysis()
            await self.test_workflow_execution()
            await self.test_mcp_tool_calls()
            await self.test_agent_response()
            
            print("\n✅ 所有测试完成!")
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()


async def main():
    """主测试函数"""
    tester = MCPIntegrationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main()) 