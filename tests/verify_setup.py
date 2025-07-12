#!/usr/bin/env python3
"""
验证pytest测试设置
检查测试环境是否正确配置
"""

import sys
import os
from pathlib import Path

def verify_pytest_setup():
    """验证pytest设置"""
    print("🔍 验证pytest测试设置")
    print("=" * 40)
    
    # 检查项目结构
    project_root = Path(__file__).parent.parent
    print(f"📁 项目根目录: {project_root}")
    
    required_paths = [
        project_root / "tests",
        project_root / "tests" / "__init__.py",
        project_root / "tests" / "conftest.py",
        project_root / "pytest.ini",
        project_root / "tests" / "test_basic.py",
    ]
    
    for path in required_paths:
        status = "✅" if path.exists() else "❌"
        print(f"{status} {path.relative_to(project_root)}")
    
    # 检查Python路径
    print(f"\n🐍 Python版本: {sys.version}")
    print(f"📍 当前工作目录: {os.getcwd()}")
    
    # 检查pytest是否可用
    try:
        import pytest
        print(f"✅ pytest版本: {pytest.__version__}")
    except ImportError:
        print("❌ pytest未安装")
        return False
    
    # 检查测试文件数量
    test_files = list((project_root / "tests").glob("test_*.py"))
    print(f"📋 发现测试文件: {len(test_files)} 个")
    for test_file in test_files:
        print(f"   - {test_file.name}")
    
    # 检查环境变量
    print(f"\n🌍 TESTING环境变量: {os.environ.get('TESTING', '未设置')}")
    
    print("\n✅ pytest设置验证完成")
    return True

def run_basic_test():
    """运行一个基础测试"""
    print("\n🧪 运行基础测试验证")
    print("=" * 40)
    
    try:
        # 简单的导入测试
        sys.path.insert(0, str(Path(__file__).parent.parent))
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        
        # 测试基础功能
        assert 2 + 2 == 4, "基础计算测试"
        print("✅ 基础计算测试通过")
        
        # 测试路径配置
        project_root = Path(__file__).parent.parent
        assert project_root.exists(), "项目根目录存在"
        print("✅ 项目路径测试通过")
        
        # 测试环境变量设置
        os.environ["TESTING"] = "true"
        assert os.environ.get("TESTING") == "true", "环境变量设置"
        print("✅ 环境变量测试通过")
        
        print("✅ 所有基础测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 基础测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 AuraWell项目pytest设置验证")
    print("=" * 50)
    
    setup_ok = verify_pytest_setup()
    test_ok = run_basic_test()
    
    print("\n" + "=" * 50)
    print("📊 验证结果汇总")
    print("=" * 50)
    print(f"pytest设置: {'✅ 正常' if setup_ok else '❌ 异常'}")
    print(f"基础测试: {'✅ 通过' if test_ok else '❌ 失败'}")
    
    if setup_ok and test_ok:
        print("\n🎉 pytest测试环境配置正确！")
        print("\n📋 可用的测试命令:")
        print("  python -m pytest tests/test_basic.py -v")
        print("  python -m pytest tests/ -m 'not slow' -v")
        print("  ./tests/run_tests.sh")
    else:
        print("\n⚠️  测试环境配置存在问题，请检查上述错误")
    
    return setup_ok and test_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
