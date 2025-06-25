# AuraWell 测试目录

## 🧪 测试框架

本项目使用 pytest 作为主要测试框架，支持：
- 单元测试（Unit Tests）
- 集成测试（Integration Tests）
- API 测试（API Tests）
- 性能测试（Performance Tests）
- 部署验证测试（Deployment Tests）

## 📁 目录结构

```
tests/
├── __init__.py                 # 测试包初始化
├── README.md                   # 本文件
├── conftest.py                 # pytest 配置文件
├── test_unit/                  # 单元测试
│   ├── test_models/            # 数据模型测试
│   ├── test_services/          # 服务层测试
│   └── test_utils/             # 工具函数测试
├── test_integration/           # 集成测试
│   ├── test_database/          # 数据库集成测试
│   ├── test_api_endpoints/     # API端点集成测试
│   └── test_external_apis/     # 外部API集成测试
├── test_api/                   # API测试
│   ├── test_health_endpoints/  # 健康数据API测试
│   ├── test_user_endpoints/    # 用户管理API测试
│   └── test_chat_endpoints/    # 聊天功能API测试
├── test_performance/           # 性能测试
│   ├── test_load/              # 负载测试
│   ├── test_stress/            # 压力测试
│   └── test_benchmark/         # 基准测试
└── test_deployment/            # 部署验证测试
    ├── test_frontend/          # 前端部署测试
    ├── test_backend/           # 后端部署测试
    └── test_infrastructure/    # 基础设施测试
```

## 🚀 运行测试

### 运行所有测试
```bash
pytest tests/
```

### 运行特定类型的测试
```bash
# 单元测试
pytest tests/test_unit/

# 集成测试
pytest tests/test_integration/

# API测试
pytest tests/test_api/

# 性能测试
pytest tests/test_performance/

# 部署验证测试
pytest tests/test_deployment/
```

### 运行特定文件的测试
```bash
pytest tests/test_unit/test_models/test_user_model.py
```

### 运行带有覆盖率报告的测试
```bash
pytest tests/ --cov=src/aurawell --cov-report=html
```

## 📋 测试编写规范

### 命名规范
- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试方法：`test_*`

### 测试示例

```python
import pytest
from src.aurawell.models.user_profile import UserProfile

class TestUserProfile:
    """用户画像模型测试类"""
    
    def test_create_user_profile(self):
        """测试创建用户画像"""
        profile = UserProfile(
            name="张三",
            age=25,
            gender="male"
        )
        assert profile.name == "张三"
        assert profile.age == 25
        assert profile.gender == "male"
    
    def test_calculate_bmi(self):
        """测试BMI计算"""
        profile = UserProfile(
            name="张三",
            height=175,
            weight=70
        )
        bmi = profile.calculate_bmi()
        assert abs(bmi - 22.86) < 0.01
```

## 🔧 测试配置

### pytest.ini 配置
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: 单元测试
    integration: 集成测试
    api: API测试
    performance: 性能测试
    deployment: 部署测试
    slow: 慢速测试
```

## 🎯 测试最佳实践

1. **测试隔离**：每个测试应该独立运行，不依赖其他测试
2. **清理数据**：使用 fixture 确保测试数据的清理
3. **明确断言**：每个测试应该有明确的断言
4. **描述性命名**：测试名称应该清楚描述测试的内容
5. **测试覆盖率**：争取达到80%以上的代码覆盖率

## 📊 测试报告

测试运行后会生成以下报告：
- 控制台输出：测试结果摘要
- HTML覆盖率报告：`htmlcov/index.html`
- JUnit XML：用于CI/CD集成

## 🔄 CI/CD 集成

测试自动化集成在GitHub Actions中：
- 每次push都会运行基础测试
- 每次PR都会运行完整测试套件
- 部署前会运行部署验证测试

## 🐛 调试测试

### 调试失败的测试
```bash
# 详细输出
pytest tests/test_specific.py -v -s

# 在第一次失败时停止
pytest tests/ -x

# 只运行失败的测试
pytest tests/ --lf
```

### 使用pytest-pdb进行调试
```bash
pytest tests/test_specific.py --pdb
``` 