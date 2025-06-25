"""
AuraWell 测试配置文件
pytest conftest.py - 全局测试设置和fixture
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# 设置测试环境变量
os.environ.update({
    "ENVIRONMENT": "test",
    "DATABASE_URL": "sqlite:///test_aurawell.db",
    "SECRET_KEY": "test-secret-key",
    "DASHSCOPE_API_KEY": "test-api-key",
    "TESTING": "true"
})

@pytest.fixture(scope="session")
def event_loop():
    """创建一个事件循环用于整个测试会话"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_user_data():
    """模拟用户数据"""
    return {
        "user_id": "test_user_123",
        "name": "张三",
        "age": 30,
        "gender": "male",
        "height": 175,
        "weight": 70,
        "activity_level": "moderate",
        "goal": "weight_loss"
    }

@pytest.fixture
def mock_health_data():
    """模拟健康数据"""
    return {
        "bmi": 22.86,
        "bmr": 1680,
        "tdee": 2310,
        "ideal_weight_range": (63, 77),
        "daily_calories": 1850
    }

@pytest.fixture
def mock_api_response():
    """模拟API响应"""
    return {
        "status": "success",
        "data": {
            "advice": "建议每天进行30分钟中等强度运动",
            "nutrition": {"protein": 140, "carbs": 200, "fat": 60},
            "exercise": {"type": "cardio", "duration": 30, "intensity": "moderate"}
        }
    }

# 测试标记定义
pytest_plugins = []

def pytest_configure(config):
    """Pytest配置"""
    config.addinivalue_line(
        "markers", "unit: 单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试"
    )
    config.addinivalue_line(
        "markers", "api: API测试"
    )
    config.addinivalue_line(
        "markers", "performance: 性能测试"
    )
    config.addinivalue_line(
        "markers", "deployment: 部署测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试"
    ) 