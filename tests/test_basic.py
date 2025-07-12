"""
基础功能测试
确保pytest配置正确工作
"""

import pytest
import sys
import os
from pathlib import Path


class TestBasicFunctionality:
    """基础功能测试类"""
    
    def test_python_version(self):
        """测试Python版本"""
        assert sys.version_info >= (3, 8), "Python版本应该>=3.8"
    
    def test_project_structure(self, project_root_path):
        """测试项目结构"""
        assert project_root_path.exists(), "项目根目录应该存在"
        assert (project_root_path / "src").exists(), "src目录应该存在"
        assert (project_root_path / "tests").exists(), "tests目录应该存在"
    
    def test_test_data_path(self, test_data_path):
        """测试测试数据路径"""
        # 测试数据路径可能不存在，这是正常的
        if test_data_path.exists():
            assert test_data_path.is_dir(), "测试数据路径应该是目录"
    
    def test_sample_pdf_file(self, sample_pdf_file):
        """测试示例PDF文件"""
        if sample_pdf_file:
            assert os.path.exists(sample_pdf_file), "示例PDF文件应该存在"
            assert sample_pdf_file.endswith('.pdf'), "应该是PDF文件"
    
    def test_mock_context(self, mock_context):
        """测试模拟context对象"""
        assert hasattr(mock_context, 'request_id'), "mock_context应该有request_id属性"
        assert hasattr(mock_context, 'function_name'), "mock_context应该有function_name属性"
    
    @pytest.mark.parametrize("value,expected", [
        (1, True),
        (0, False),
        (-1, False),
        (100, True),
    ])
    def test_parametrized_example(self, value, expected):
        """参数化测试示例"""
        result = value > 0
        assert result == expected


class TestEnvironment:
    """环境测试类"""
    
    def test_testing_environment_variable(self):
        """测试环境变量设置"""
        assert os.environ.get("TESTING") == "true", "应该设置TESTING环境变量"
    
    def test_import_paths(self):
        """测试导入路径"""
        # 测试是否能正确导入项目模块
        import sys
        
        # 检查项目路径是否在sys.path中
        project_paths = [path for path in sys.path if 'AuraWell' in path]
        assert len(project_paths) > 0, "项目路径应该在sys.path中"


@pytest.mark.unit
class TestUnitExample:
    """单元测试示例"""
    
    def test_simple_calculation(self):
        """简单计算测试"""
        assert 2 + 2 == 4
        assert 10 * 3 == 30
        assert 15 / 3 == 5
    
    def test_string_operations(self):
        """字符串操作测试"""
        text = "AuraWell"
        assert text.lower() == "aurawell"
        assert text.upper() == "AURAWELL"
        assert len(text) == 8


@pytest.mark.slow
class TestSlowExample:
    """慢速测试示例"""
    
    def test_slow_operation(self):
        """慢速操作测试"""
        import time
        start_time = time.time()
        time.sleep(0.1)  # 模拟慢速操作
        end_time = time.time()
        
        assert end_time - start_time >= 0.1, "操作应该至少耗时0.1秒"
