#!/usr/bin/env python3
"""
快速测试脚本
运行基础测试并生成简单报告
"""

import subprocess
import sys
from pathlib import Path

def run_quick_tests():
    """运行快速测试"""
    print("🚀 运行AuraWell项目快速测试")
    print("=" * 50)
    
    # 切换到项目根目录
    project_root = Path(__file__).parent.parent
    
    # 运行基础测试
    print("📋 运行基础功能测试...")
    result1 = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_basic.py", 
        "-v", "--tb=short"
    ], cwd=project_root, capture_output=True, text=True)
    
    print("📋 运行快速测试（排除慢速测试）...")
    result2 = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-m", "not slow",
        "-v", "--tb=short", "--maxfail=5"
    ], cwd=project_root, capture_output=True, text=True)
    
    # 生成报告
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    print(f"基础测试结果: {'✅ 通过' if result1.returncode == 0 else '❌ 失败'}")
    if result1.returncode != 0:
        print("基础测试错误:")
        print(result1.stdout[-500:])  # 显示最后500个字符
    
    print(f"快速测试结果: {'✅ 通过' if result2.returncode == 0 else '⚠️ 部分失败'}")
    
    # 从输出中提取测试统计
    if "passed" in result2.stdout:
        lines = result2.stdout.split('\n')
        for line in lines:
            if "passed" in line and ("failed" in line or "error" in line or "skipped" in line):
                print(f"详细结果: {line.strip()}")
                break
    
    print("\n💡 提示:")
    print("- 在测试环境中，某些依赖外部服务的测试可能会失败，这是正常的")
    print("- 使用 'python -m pytest tests/test_basic.py -v' 运行基础测试")
    print("- 使用 './tests/run_tests.sh' 运行完整的交互式测试")
    
    return result1.returncode == 0 and result2.returncode == 0

if __name__ == "__main__":
    success = run_quick_tests()
    sys.exit(0 if success else 1)
