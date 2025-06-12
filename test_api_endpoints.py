#!/usr/bin/env python3
"""
API端点测试脚本
测试新添加的API端点功能
"""

import asyncio
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from aurawell.interfaces.api_interface import app

def test_api_endpoints():
    """测试API端点"""
    client = TestClient(app)
    
    print("🚀 开始测试API端点...")
    
    # 1. 测试用户注册
    print("\n1. 测试用户注册...")
    register_data = {
        "username": "test_user_new",
        "email": "test@example.com",
        "password": "test_password123",
        "health_data": {
            "age": 25,
            "gender": "male",
            "height": 175,
            "weight": 70,
            "activity_level": "moderately_active"
        }
    }
    
    response = client.post("/api/v1/auth/register", json=register_data)
    print(f"注册响应状态: {response.status_code}")
    if response.status_code == 200:
        print("✅ 用户注册成功")
        print(f"响应: {response.json()}")
    else:
        print(f"❌ 用户注册失败: {response.text}")
    
    # 2. 测试用户登录
    print("\n2. 测试用户登录...")
    login_data = {
        "username": "test_user",
        "password": "test_password"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    print(f"登录响应状态: {response.status_code}")
    
    token = None
    if response.status_code == 200:
        print("✅ 用户登录成功")
        login_response = response.json()
        token = login_response.get("data", {}).get("access_token")
        print(f"获取到Token: {token[:20]}..." if token else "未获取到Token")
    else:
        print(f"❌ 用户登录失败: {response.text}")
        return
    
    # 设置认证头
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # 3. 测试获取用户档案
    print("\n3. 测试获取用户档案...")
    response = client.get("/api/v1/user/profile", headers=headers)
    print(f"获取档案响应状态: {response.status_code}")
    if response.status_code == 200:
        print("✅ 获取用户档案成功")
        profile_data = response.json()
        print(f"用户ID: {profile_data.get('user_id', 'N/A')}")
        print(f"用户名: {profile_data.get('display_name', 'N/A')}")
    else:
        print(f"❌ 获取用户档案失败: {response.text}")
    
    # 4. 测试更新用户档案
    print("\n4. 测试更新用户档案...")
    update_data = {
        "display_name": "测试用户",
        "age": 28,
        "height_cm": 175.0,
        "weight_kg": 72.0
    }
    
    response = client.put("/api/v1/user/profile", json=update_data, headers=headers)
    print(f"更新档案响应状态: {response.status_code}")
    if response.status_code == 200:
        print("✅ 更新用户档案成功")
    else:
        print(f"❌ 更新用户档案失败: {response.text}")
    
    # 5. 测试获取健康数据
    print("\n5. 测试获取健康数据...")
    response = client.get("/api/v1/user/health-data", headers=headers)
    print(f"获取健康数据响应状态: {response.status_code}")
    if response.status_code == 200:
        print("✅ 获取健康数据成功")
        health_data = response.json()
        print(f"BMI: {health_data.get('bmi', 'N/A')}")
        print(f"BMI分类: {health_data.get('bmi_category', 'N/A')}")
    else:
        print(f"❌ 获取健康数据失败: {response.text}")
    
    # 6. 测试获取健康目标
    print("\n6. 测试获取健康目标...")
    response = client.get("/api/v1/user/health-goals", headers=headers)
    print(f"获取健康目标响应状态: {response.status_code}")
    if response.status_code == 200:
        print("✅ 获取健康目标成功")
        goals_data = response.json()
        print(f"目标数量: {goals_data.get('total_count', 0)}")
    else:
        print(f"❌ 获取健康目标失败: {response.text}")
    
    # 7. 测试创建健康目标
    print("\n7. 测试创建健康目标...")
    goal_data = {
        "title": "减重目标",
        "description": "在3个月内减重5公斤",
        "type": "weight_loss",
        "target_value": 5.0,
        "current_value": 0.0,
        "unit": "kg",
        "target_date": "2024-12-31",
        "status": "active"
    }
    
    response = client.post("/api/v1/user/health-goals", json=goal_data, headers=headers)
    print(f"创建健康目标响应状态: {response.status_code}")
    if response.status_code == 200:
        print("✅ 创建健康目标成功")
    else:
        print(f"❌ 创建健康目标失败: {response.text}")
    
    # 8. 测试获取健康计划
    print("\n8. 测试获取健康计划...")
    response = client.get("/api/v1/health-plan/plans", headers=headers)
    print(f"获取健康计划响应状态: {response.status_code}")
    if response.status_code == 200:
        print("✅ 获取健康计划成功")
        plans_data = response.json()
        print(f"计划数量: {plans_data.get('total_count', 0)}")
    else:
        print(f"❌ 获取健康计划失败: {response.text}")
    
    # 9. 测试生成健康计划
    print("\n9. 测试生成健康计划...")
    plan_request = {
        "goals": ["减重", "增强体质"],
        "modules": ["diet", "exercise", "weight"],
        "duration_days": 30,
        "user_preferences": {
            "dietary_restrictions": ["无"],
            "exercise_preference": "中等强度"
        }
    }
    
    response = client.post("/api/v1/health-plan/generate", json=plan_request, headers=headers)
    print(f"生成健康计划响应状态: {response.status_code}")
    if response.status_code == 200:
        print("✅ 生成健康计划成功")
        plan_data = response.json()
        plan = plan_data.get('plan', {})
        print(f"计划标题: {plan.get('title', 'N/A')}")
        print(f"模块数量: {len(plan.get('modules', []))}")
    else:
        print(f"❌ 生成健康计划失败: {response.text}")
    
    # 10. 测试聊天功能
    print("\n10. 测试聊天功能...")
    chat_data = {
        "message": "我想了解如何制定健康的饮食计划"
    }
    
    response = client.post("/api/v1/chat", json=chat_data, headers=headers)
    print(f"聊天响应状态: {response.status_code}")
    if response.status_code == 200:
        print("✅ 聊天功能正常")
        chat_response = response.json()
        print(f"AI回复: {chat_response.get('reply', 'N/A')[:100]}...")
    else:
        print(f"❌ 聊天功能失败: {response.text}")
    
    print("\n🎉 API端点测试完成!")

if __name__ == "__main__":
    test_api_endpoints()
