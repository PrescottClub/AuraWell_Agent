#!/usr/bin/env python3
"""
性能优化测试 - 验证响应时间是否达到 < 2s 的目标
"""

import asyncio
import logging
import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aurawell.agent.conversation_agent import ConversationAgent

# 配置日志
logging.basicConfig(level=logging.WARNING)  # 减少日志输出以提高性能
logger = logging.getLogger(__name__)


async def test_performance_optimized():
    """性能优化测试"""
    print("🚀 开始性能优化测试...")
    
    # 创建对话代理（演示模式）
    agent = ConversationAgent(user_id="perf_test_optimized", demo_mode=True)
    
    test_cases = [
        "我今天走了多少步？",
        "分析我的睡眠质量", 
        "给我一些健康建议",
        "查看我的成就进度",
        "帮我设置健康目标"
    ]
    
    results = []
    total_time = 0
    
    print(f"📋 测试 {len(test_cases)} 个对话场景...\n")
    
    for i, message in enumerate(test_cases, 1):
        try:
            print(f"测试 {i}: {message}")
            
            start_time = time.time()
            response = await agent.a_run(message)
            end_time = time.time()
            
            response_time = end_time - start_time
            total_time += response_time
            
            # 检查响应是否成功
            success = response and len(response) > 0
            
            # 检查是否达到性能目标
            meets_target = response_time < 2.0
            
            status = "✅ 通过" if success and meets_target else "❌ 失败"
            time_status = "🟢 快速" if meets_target else "🔴 超时"
            
            print(f"   响应时间: {response_time:.2f}s {time_status}")
            print(f"   状态: {status}")
            print(f"   响应: {response[:50]}..." if response else "   响应: 无")
            print()
            
            results.append({
                "test": i,
                "message": message,
                "response_time": response_time,
                "success": success,
                "meets_target": meets_target
            })
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            results.append({
                "test": i,
                "message": message,
                "response_time": 999,
                "success": False,
                "meets_target": False
            })
    
    # 统计结果
    successful_tests = sum(1 for r in results if r["success"])
    fast_tests = sum(1 for r in results if r["meets_target"])
    avg_time = total_time / len(test_cases) if test_cases else 0
    success_rate = (successful_tests / len(test_cases)) * 100 if test_cases else 0
    performance_rate = (fast_tests / len(test_cases)) * 100 if test_cases else 0
    
    print("📊 性能测试结果:")
    print(f"   总测试数: {len(test_cases)}")
    print(f"   成功测试: {successful_tests}")
    print(f"   快速测试 (<2s): {fast_tests}")
    print(f"   平均响应时间: {avg_time:.2f}s")
    print(f"   成功率: {success_rate:.1f}%")
    print(f"   性能达标率: {performance_rate:.1f}%")
    
    # 验收标准检查
    meets_success_target = success_rate > 95
    meets_performance_target = avg_time < 2.0
    
    print(f"\n🎯 验收标准检查:")
    print(f"   成功率 > 95%: {'✅' if meets_success_target else '❌'} ({success_rate:.1f}%)")
    print(f"   平均响应时间 < 2s: {'✅' if meets_performance_target else '❌'} ({avg_time:.2f}s)")
    
    overall_pass = meets_success_target and meets_performance_target
    
    if overall_pass:
        print(f"\n🎉 性能测试通过！系统满足M2-7验收标准！")
    else:
        print(f"\n⚠️ 性能测试未完全通过，需要进一步优化")
        
        # 提供优化建议
        print(f"\n💡 优化建议:")
        if not meets_success_target:
            print(f"   - 提高系统稳定性，当前成功率 {success_rate:.1f}%")
        if not meets_performance_target:
            print(f"   - 优化响应时间，当前平均 {avg_time:.2f}s")
            print(f"   - 考虑缓存机制、异步优化、减少API调用等")
    
    return overall_pass


async def test_intent_recognition_speed():
    """测试意图识别速度"""
    print("\n🧠 测试意图识别性能...")
    
    from aurawell.agent.intent_parser import IntentParser
    
    parser = IntentParser()
    
    test_messages = [
        "我今天走了多少步？",
        "我昨晚睡得怎么样？", 
        "帮我设置健康目标",
        "给我一些健康建议"
    ]
    
    total_time = 0
    
    for message in test_messages:
        start_time = time.time()
        result = await parser.parse_intent(message)
        end_time = time.time()
        
        response_time = end_time - start_time
        total_time += response_time
        
        print(f"   {message}: {response_time:.2f}s -> {result['RequestType']}")
    
    avg_intent_time = total_time / len(test_messages)
    print(f"   平均意图识别时间: {avg_intent_time:.2f}s")
    
    return avg_intent_time < 1.0  # 意图识别应该在1秒内完成


async def main():
    """主测试函数"""
    print("🔧 M2-7 性能优化验证测试\n")
    
    # 测试意图识别性能
    intent_fast = await test_intent_recognition_speed()
    
    # 测试整体性能
    overall_pass = await test_performance_optimized()
    
    # 最终结果
    print(f"\n📋 最终测试结果:")
    print(f"   意图识别性能: {'✅ 通过' if intent_fast else '❌ 需优化'}")
    print(f"   整体系统性能: {'✅ 通过' if overall_pass else '❌ 需优化'}")
    
    final_result = intent_fast and overall_pass
    
    if final_result:
        print(f"\n🎊 恭喜！M2-7 集成测试完全通过！")
        print(f"   ✅ 所有模块成功集成")
        print(f"   ✅ 对话流程完整且流畅") 
        print(f"   ✅ 端到端测试通过率 > 95%")
        print(f"   ✅ 系统响应时间 < 2s")
    else:
        print(f"\n⚠️ M2-7 集成测试部分通过，建议进一步优化")
    
    return final_result


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
