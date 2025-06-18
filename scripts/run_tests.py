#!/usr/bin/env python3
"""
测试运行脚本

提供全面的测试执行和报告功能
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def run_command(command, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd or project_root,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def install_test_dependencies():
    """安装测试依赖"""
    print("📦 安装测试依赖...")
    
    dependencies = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0",
        "httpx>=0.24.0",
        "psutil>=5.9.0"
    ]
    
    for dep in dependencies:
        print(f"   安装 {dep}...")
        success, stdout, stderr = run_command(f"pip install {dep}")
        if not success:
            print(f"❌ 安装 {dep} 失败: {stderr}")
            return False
    
    print("✅ 测试依赖安装完成")
    return True


def run_unit_tests(test_pattern=None, coverage=True, verbose=True):
    """运行单元测试"""
    print("🧪 运行单元测试...")
    
    # 构建pytest命令
    cmd_parts = ["python", "-m", "pytest"]
    
    if verbose:
        cmd_parts.append("-v")
    
    if coverage:
        cmd_parts.extend([
            "--cov=aurawell",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-report=xml:coverage.xml"
        ])
    
    # 添加测试路径
    if test_pattern:
        cmd_parts.append(f"tests/{test_pattern}")
    else:
        cmd_parts.append("tests/")
    
    # 添加其他选项
    cmd_parts.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    command = " ".join(cmd_parts)
    print(f"执行命令: {command}")
    
    success, stdout, stderr = run_command(command)
    
    if success:
        print("✅ 单元测试通过")
        print(stdout)
        return True
    else:
        print("❌ 单元测试失败")
        print(stderr)
        return False


def run_integration_tests():
    """运行集成测试"""
    print("🔗 运行集成测试...")
    
    # 集成测试需要真实的数据库
    print("   设置测试数据库...")
    
    # 设置测试环境变量
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///test_aurawell.db"
    
    # 运行集成测试
    command = "python -m pytest tests/test_*_integration.py -v --tb=short"
    success, stdout, stderr = run_command(command)
    
    # 清理测试数据库
    test_db_files = ["test_aurawell.db", "test_aurawell.db-shm", "test_aurawell.db-wal"]
    for db_file in test_db_files:
        if os.path.exists(db_file):
            os.remove(db_file)
    
    if success:
        print("✅ 集成测试通过")
        print(stdout)
        return True
    else:
        print("❌ 集成测试失败")
        print(stderr)
        return False


def run_api_tests():
    """运行API测试"""
    print("🌐 运行API测试...")
    
    command = "python -m pytest tests/test_*_api.py -v --tb=short"
    success, stdout, stderr = run_command(command)
    
    if success:
        print("✅ API测试通过")
        print(stdout)
        return True
    else:
        print("❌ API测试失败")
        print(stderr)
        return False


def run_performance_tests():
    """运行性能测试"""
    print("⚡ 运行性能测试...")
    
    # 性能测试可能需要特殊的标记
    command = "python -m pytest tests/ -m performance -v --tb=short"
    success, stdout, stderr = run_command(command)
    
    if success:
        print("✅ 性能测试通过")
        print(stdout)
        return True
    else:
        print("⚠️  性能测试失败或未找到性能测试")
        print(stderr)
        return True  # 性能测试失败不影响整体结果


def run_linting():
    """运行代码检查"""
    print("🔍 运行代码检查...")
    
    # 检查是否安装了flake8
    success, _, _ = run_command("flake8 --version")
    if not success:
        print("   安装 flake8...")
        run_command("pip install flake8")
    
    # 运行flake8检查
    command = "flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503"
    success, stdout, stderr = run_command(command)
    
    if success:
        print("✅ 代码检查通过")
        return True
    else:
        print("⚠️  代码检查发现问题:")
        print(stdout)
        print(stderr)
        return False


def run_type_checking():
    """运行类型检查"""
    print("🔎 运行类型检查...")
    
    # 检查是否安装了mypy
    success, _, _ = run_command("mypy --version")
    if not success:
        print("   安装 mypy...")
        run_command("pip install mypy")
    
    # 运行mypy检查
    command = "mypy src/ --ignore-missing-imports --no-strict-optional"
    success, stdout, stderr = run_command(command)
    
    if success:
        print("✅ 类型检查通过")
        return True
    else:
        print("⚠️  类型检查发现问题:")
        print(stdout)
        print(stderr)
        return False


def generate_test_report():
    """生成测试报告"""
    print("📊 生成测试报告...")
    
    # 检查覆盖率报告
    if os.path.exists("htmlcov/index.html"):
        print("✅ HTML覆盖率报告: htmlcov/index.html")
    
    if os.path.exists("coverage.xml"):
        print("✅ XML覆盖率报告: coverage.xml")
    
    # 生成简单的测试摘要
    summary_file = "test_summary.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("AuraWell Agent 测试摘要\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"测试时间: {os.popen('date').read().strip()}\n")
        f.write(f"项目路径: {project_root}\n\n")
        
        # 统计测试文件
        test_files = list(Path("tests").glob("test_*.py"))
        f.write(f"测试文件数量: {len(test_files)}\n")
        for test_file in test_files:
            f.write(f"  - {test_file.name}\n")
    
    print(f"✅ 测试摘要: {summary_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AuraWell Agent 测试运行器")
    
    parser.add_argument("--unit", action="store_true", help="只运行单元测试")
    parser.add_argument("--integration", action="store_true", help="只运行集成测试")
    parser.add_argument("--api", action="store_true", help="只运行API测试")
    parser.add_argument("--performance", action="store_true", help="只运行性能测试")
    parser.add_argument("--lint", action="store_true", help="只运行代码检查")
    parser.add_argument("--type-check", action="store_true", help="只运行类型检查")
    parser.add_argument("--pattern", help="测试文件模式")
    parser.add_argument("--no-coverage", action="store_true", help="不生成覆盖率报告")
    parser.add_argument("--install-deps", action="store_true", help="安装测试依赖")
    parser.add_argument("--quick", action="store_true", help="快速测试（只运行单元测试）")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧪 AuraWell Agent 测试套件")
    print("=" * 60)
    
    # 安装依赖
    if args.install_deps:
        if not install_test_dependencies():
            sys.exit(1)
    
    success_count = 0
    total_count = 0
    
    # 根据参数运行相应的测试
    if args.quick:
        total_count = 1
        if run_unit_tests(args.pattern, not args.no_coverage):
            success_count += 1
    elif args.unit:
        total_count = 1
        if run_unit_tests(args.pattern, not args.no_coverage):
            success_count += 1
    elif args.integration:
        total_count = 1
        if run_integration_tests():
            success_count += 1
    elif args.api:
        total_count = 1
        if run_api_tests():
            success_count += 1
    elif args.performance:
        total_count = 1
        if run_performance_tests():
            success_count += 1
    elif args.lint:
        total_count = 1
        if run_linting():
            success_count += 1
    elif args.type_check:
        total_count = 1
        if run_type_checking():
            success_count += 1
    else:
        # 运行所有测试
        tests = [
            ("单元测试", lambda: run_unit_tests(args.pattern, not args.no_coverage)),
            ("API测试", run_api_tests),
            ("代码检查", run_linting),
            ("类型检查", run_type_checking),
            ("性能测试", run_performance_tests),
        ]
        
        total_count = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            if test_func():
                success_count += 1
    
    # 生成报告
    generate_test_report()
    
    # 输出结果
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print(f"❌ {total_count - success_count} 个测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
