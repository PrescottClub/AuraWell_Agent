#!/usr/bin/env python3
"""
AuraWell Phase IV - WebSocket Streaming Tests

测试WebSocket流式交互功能：
- WebSocket连接建立
- 流式健康建议
- 状态管理（sending → streaming → done）
- 并发连接测试
"""

import asyncio
import json
import websockets
from datetime import datetime
import aiohttp


async def test_websocket_basic():
    """基础WebSocket连接测试"""
    print("📡 测试WebSocket基础连接...")
    
    uri = "ws://localhost:8000/ws/chat/test_user_001"
    
    try:
        async with websockets.connect(uri) as websocket:
            # 接收欢迎消息
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"✅ 连接成功: {welcome_data['message']}")
            
            return True
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


async def test_websocket_streaming():
    """测试WebSocket流式健康建议"""
    print("🤖 测试WebSocket流式健康建议...")
    
    uri = "ws://localhost:8000/ws/chat/test_user_002"
    
    try:
        async with websockets.connect(uri) as websocket:
            # 跳过欢迎消息
            await websocket.recv()
            
            # 发送健康咨询消息
            message = {
                "type": "health_chat",
                "data": {
                    "message": "我最近总是感觉疲劳，请给我一些健康建议",
                    "context": {"mood": "tired", "sleep_hours": 6}
                },
                "conversation_id": "test_conv_001"
            }
            
            await websocket.send(json.dumps(message, ensure_ascii=False))
            print("📤 已发送健康咨询消息")
            
            # 收集流式响应
            tokens = []
            statuses = []
            timeout = 30
            
            while len(tokens) < 100 and len(statuses) < 5:  # 限制接收数量避免无限等待
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "chat_stream":
                        tokens.append(data.get("delta", ""))
                    elif data.get("type") == "status_update":
                        statuses.append(data.get("status"))
                        print(f"📊 状态更新: {data.get('status')} - {data.get('message', '')}")
                        
                        if data.get("status") == "done":
                            break
                            
                except asyncio.TimeoutError:
                    print("⏱️ 响应超时，结束测试")
                    break
            
            print(f"✅ 流式测试完成:")
            print(f"  - 收到token数量: {len(tokens)}")
            print(f"  - 状态更新次数: {len(statuses)}")
            print(f"  - 前3个token: {tokens[:3]}")
            print(f"  - 状态序列: {statuses}")
            
            # 验证状态管理
            expected_statuses = ["sending", "streaming", "done"]
            status_check = all(status in statuses for status in expected_statuses)
            
            return len(tokens) > 0 and status_check
            
    except Exception as e:
        print(f"❌ 流式测试失败: {e}")
        return False


async def test_concurrent_websocket():
    """测试并发WebSocket连接"""
    print("🔀 测试并发WebSocket连接...")
    
    async def single_connection(user_id):
        uri = f"ws://localhost:8000/ws/chat/{user_id}"
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.recv()  # 欢迎消息
                
                # 发送状态查询
                message = {"type": "get_status", "data": {}}
                await websocket.send(json.dumps(message))
                
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                return f"{user_id}: ✅"
        except Exception as e:
            return f"{user_id}: ❌ {e}"
    
    # 创建10个并发连接
    tasks = []
    for i in range(10):
        user_id = f"concurrent_user_{i+1:02d}"
        tasks.append(single_connection(user_id))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = sum(1 for r in results if "✅" in str(r))
    print(f"✅ 并发测试结果: {success_count}/10 连接成功")
    
    for result in results:
        print(f"  {result}")
    
    return success_count >= 8  # 80%成功率


async def main():
    """主测试函数"""
    print("🌟 AuraWell Phase IV - WebSocket 流式交互测试")
    print("=" * 60)
    
    # 检查服务器状态
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/v1/health") as response:
                if response.status == 200:
                    print("✅ API服务器运行正常")
                else:
                    print("❌ API服务器响应异常")
                    return
    except Exception as e:
        print(f"❌ 无法连接到API服务器: {e}")
        print("请确保API服务器在 http://localhost:8000 上运行")
        return
    
    # 运行测试
    test_results = []
    
    # 测试1: 基础连接
    result1 = await test_websocket_basic()
    test_results.append(("基础连接", result1))
    
    # 测试2: 流式健康建议
    result2 = await test_websocket_streaming()
    test_results.append(("流式健康建议", result2))
    
    # 测试3: 并发连接
    result3 = await test_concurrent_websocket()
    test_results.append(("并发连接", result3))
    
    # 测试总结
    print("\n" + "=" * 60)
    print("📊 Phase IV WebSocket 测试总结:")
    
    passed = 0
    for test_name, success in test_results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1
    
    overall_success = passed / len(test_results) * 100
    print(f"\n🎯 总体成功率: {overall_success:.1f}% ({passed}/{len(test_results)})")
    
    if overall_success >= 80:
        print("🏆 Phase IV WebSocket 测试 PASSED!")
    else:
        print("⚠️ Phase IV WebSocket 测试需要修复!")
    
    # 保存测试报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "timestamp": timestamp,
        "tests": [
            {"name": name, "success": success} 
            for name, success in test_results
        ],
        "overall_success_rate": overall_success,
        "passed": overall_success >= 80
    }
    
    report_file = f"phase_iv_websocket_test_{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 测试报告已保存: {report_file}")


if __name__ == "__main__":
    asyncio.run(main()) 