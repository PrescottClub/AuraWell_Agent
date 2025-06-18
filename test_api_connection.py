#!/usr/bin/env python3
"""
AuraWell API连接测试脚本
测试前后端链路是否正常连接
"""

import requests
import json

def test_api_endpoints():
    """测试主要的API端点"""
    base_url = "http://127.0.0.1:8001"
    headers = {"Authorization": "Bearer dev-test-token"}
    
    print("🚀 AuraWell API连接测试")
    print("=" * 50)
    
    # 1. 健康检查
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        print(f"✅ 健康检查: {response.status_code}")
        if response.status_code == 200:
            print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    # 2. 获取对话列表
    try:
        response = requests.get(f"{base_url}/api/v1/chat/conversations", headers=headers)
        print(f"✅ 获取对话列表: {response.status_code}")
        if response.status_code == 200:
            print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"❌ 获取对话列表失败: {e}")
    
    # 3. 创建对话
    try:
        data = {"type": "health_consultation", "title": "测试对话"}
        response = requests.post(f"{base_url}/api/v1/chat/conversation", json=data, headers=headers)
        print(f"✅ 创建对话: {response.status_code}")
        if response.status_code == 200:
            print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"❌ 创建对话失败: {e}")
    
    # 4. 发送消息
    try:
        data = {
            "message": "你好，我想咨询健康问题",
            "conversation_id": "test_conv_001",
            "user_id": "dev_user"
        }
        response = requests.post(f"{base_url}/api/v1/chat/message", json=data, headers=headers)
        print(f"✅ 发送消息: {response.status_code}")
        if response.status_code == 200:
            print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"❌ 发送消息失败: {e}")
    
    print("=" * 50)
    print("🎯 API测试完成")

if __name__ == "__main__":
    test_api_endpoints() 