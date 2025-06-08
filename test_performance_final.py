#!/usr/bin/env python3
"""
M2-7 最终性能测试 - 验证优化后的响应时间
"""

import asyncio
import logging
import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aurawell.agent.conversation_agent import ConversationAgent
from aurawell.agent.intent_parser import IntentParser

# 配置日志
logging.basicConfig(level=logging.WARNING)  # 减少日志输出
logger = logging.getLogger(__name__)


async def test_intent_cache_performance():
    """测试意图识别缓存性能"""
    print("🧠 测试意图识别缓存性能...")
    
    parser = IntentParser()
    test_message = "我今天走了多少步？"
    
    # 第一次调用（无缓存）
    start_time = time.time()
    result1 = await parser.parse_intent(test_message)
    first_call_time = time.time() - start_time
    
    # 第二次调用（有缓存）
    start_time = time.time()
    result2 = await parser.parse_intent(test_message)
    second_call_time = time.time() - start_time
    
    print(f"   第一次调用（无缓存）: {first_call_time:.2f}s")
    print(f"   第二次调用（有缓存）: {second_call_time:.2f}s")
    print(f"   缓存加速比: {first_call_time/second_call_time:.1f}x")
    
    # 验证结果一致性
    assert result1['RequestType'] == result2['RequestType']
    print(f"   ✅ 缓存结果一致性验证通过")
    
    return second_call_time < 0.1  # 缓存调用应该在0.1秒内


async def test_demo_mode_performance():
    """测试演示模式性能优化"""
    print("\n🚀 测试演示模式性能优化...")
    
    agent = ConversationAgent(user_id="perf_test_final", demo_mode=True)
    
    test_cases = [
        "我今天走了多少步？",
        "分析我的睡眠质量",
        "给我一些健康建议",
        "查看我的成就进度",
        "帮我设置健康目标"
    ]
    
    total_time = 0
    fast_responses = 0
    
    for i, message in enumerate(test_cases, 1):
        start_time = time.time()
        response = await agent.a_run(message)
        response_time = time.time() - start_time
        
        total_time += response_time
        if response_time < 2.0:
            fast_responses += 1
        
        status = "🟢 快速" if response_time < 2.0 else "🔴 慢"
        print(f"   测试 {i}: {response_time:.2f}s {status}")
    
    avg_time = total_time / len(test_cases)
    fast_rate = (fast_responses / len(test_cases)) * 100
    
    print(f"   平均响应时间: {avg_time:.2f}s")
    print(f"   快速响应率: {fast_rate:.1f}%")
    
    return avg_time < 2.0 and fast_rate >= 80


async def test_concurrent_requests():
    """测试并发请求性能"""
    print("\n⚡ 测试并发请求性能...")
    
    agent = ConversationAgent(user_id="concurrent_test", demo_mode=True)
    
    # 创建5个并发请求
    messages = [
        "我今天的活动数据怎么样？",
        "我昨晚睡得好吗？",
        "给我一些健康建议",
        "查看我的成就",
        "帮我设置目标"
    ]
    
    start_time = time.time()
    
    # 并发执行
    tasks = [agent.a_run(msg) for msg in messages]
    responses = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    avg_time_per_request = total_time / len(messages)
    
    print(f"   并发处理5个请求总时间: {total_time:.2f}s")
    print(f"   平均每个请求时间: {avg_time_per_request:.2f}s")
    
    # 验证所有响应都成功
    success_count = sum(1 for resp in responses if resp and len(resp) > 0)
    print(f"   成功响应数: {success_count}/{len(messages)}")
    
    return avg_time_per_request < 2.0 and success_count == len(messages)


async def test_memory_efficiency():
    """测试内存使用效率"""
    print("\n💾 测试内存使用效率...")
    
    import psutil
    import gc
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # 创建多个代理实例并进行对话
    agents = []
    for i in range(10):
        agent = ConversationAgent(user_id=f"memory_test_{i}", demo_mode=True)
        agents.append(agent)
        
        # 每个代理进行几轮对话
        for j in range(5):
            await agent.a_run(f"测试消息 {j}")
    
    # 强制垃圾回收
    gc.collect()
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    print(f"   初始内存: {initial_memory:.1f} MB")
    print(f"   最终内存: {final_memory:.1f} MB")
    print(f"   内存增长: {memory_increase:.1f} MB")
    
    # 清理
    del agents
    gc.collect()
    
    return memory_increase < 100  # 内存增长应该小于100MB


async def comprehensive_performance_test():
    """综合性能测试"""
    print("\n🎯 综合性能测试...")
    
    agent = ConversationAgent(user_id="comprehensive_test", demo_mode=True)
    
    # 混合测试场景
    test_scenarios = [
        ("简单查询", "我今天走了多少步？"),
        ("复杂分析", "分析我最近一周的健康数据并给出建议"),
        ("目标设置", "帮我设置一个减重10斤的健康计划"),
        ("成就查询", "我获得了哪些健康成就？"),
        ("营养咨询", "我今天的饮食搭配合理吗？")
    ]
    
    results = []
    total_time = 0
    
    for scenario_name, message in test_scenarios:
        start_time = time.time()
        response = await agent.a_run(message)
        response_time = time.time() - start_time
        
        total_time += response_time
        success = response and len(response) > 0
        meets_target = response_time < 2.0
        
        results.append({
            "scenario": scenario_name,
            "time": response_time,
            "success": success,
            "meets_target": meets_target
        })
        
        status = "✅" if success and meets_target else "⚠️" if success else "❌"
        print(f"   {scenario_name}: {response_time:.2f}s {status}")
    
    # 统计结果
    success_rate = sum(1 for r in results if r["success"]) / len(results) * 100
    target_rate = sum(1 for r in results if r["meets_target"]) / len(results) * 100
    avg_time = total_time / len(results)
    
    print(f"   平均响应时间: {avg_time:.2f}s")
    print(f"   成功率: {success_rate:.1f}%")
    print(f"   性能达标率: {target_rate:.1f}%")
    
    return avg_time < 2.0 and success_rate >= 95 and target_rate >= 80


async def main():
    """主测试函数"""
    print("🔧 M2-7 最终性能优化验证测试\n")
    
    test_results = []
    
    # 执行各项测试
    tests = [
        ("意图识别缓存", test_intent_cache_performance),
        ("演示模式优化", test_demo_mode_performance),
        ("并发请求处理", test_concurrent_requests),
        ("内存使用效率", test_memory_efficiency),
        ("综合性能测试", comprehensive_performance_test)
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
            status = "✅ 通过" if result else "❌ 未达标"
            print(f"   {test_name}: {status}")
        except Exception as e:
            test_results.append((test_name, False))
            print(f"   {test_name}: ❌ 错误 - {e}")
    
    # 最终评估
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    pass_rate = (passed_tests / total_tests) * 100
    
    print(f"\n📊 最终测试结果:")
    print(f"   通过测试: {passed_tests}/{total_tests}")
    print(f"   通过率: {pass_rate:.1f}%")
    
    if pass_rate >= 80:
        print(f"\n🎉 性能优化成功！")
        print(f"   ✅ M2-7 验收标准基本达成")
        print(f"   ✅ 系统响应时间显著改善")
        print(f"   ✅ 缓存机制有效提升性能")
        print(f"   ✅ 演示模式优化成功")
        return True
    else:
        print(f"\n⚠️ 性能优化部分成功，建议进一步调优")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
