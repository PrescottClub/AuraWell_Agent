"""
pytest配置文件
提供测试的全局配置和fixture
"""

import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src" / "aurawell"))
sys.path.insert(0, str(project_root / "src" / "aurawell" / "rag"))

@pytest.fixture(scope="session")
def project_root_path():
    """返回项目根目录路径"""
    return project_root

@pytest.fixture(scope="session")
def test_data_path():
    """返回测试数据目录路径"""
    return project_root / "src" / "aurawell" / "rag" / "testMaterials"

@pytest.fixture(scope="session")
def sample_pdf_file(test_data_path):
    """返回示例PDF文件路径"""
    pdf_file = test_data_path / "每日吃白糖别超40克.pdf"
    if pdf_file.exists():
        return str(pdf_file)
    return None

@pytest.fixture(scope="session")
def mock_context():
    """模拟阿里云FC的context对象"""
    class MockContext:
        def __init__(self):
            self.request_id = "test-request-id"
            self.function_name = "test-function"
            self.function_version = "LATEST"
            self.service_name = "test-service"
            self.service_version = "LATEST"
            self.region = "cn-hangzhou"
            self.account_id = "123456789"
    
    return MockContext()

@pytest.fixture(autouse=True)
def setup_test_environment():
    """自动设置测试环境"""
    # 设置测试环境变量
    os.environ["TESTING"] = "true"
    
    yield
    
    # 清理测试环境
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
