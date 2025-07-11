#!/usr/bin/env python3
"""
pytest测试运行脚本
提供便捷的测试运行方式
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_pytest(test_pattern=None, markers=None, verbose=True, coverage=False):
    """运行pytest测试"""
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    if markers:
        cmd.extend(["-m", markers])
    
    if test_pattern:
        if not test_pattern.startswith("tests/"):
            test_pattern = f"tests/{test_pattern}"
        cmd.append(test_pattern)
    else:
        cmd.append("tests/")
    
    print(f"运行命令: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)

def main():
    parser = argparse.ArgumentParser(description="运行AuraWell项目的pytest测试")
    parser.add_argument("--pattern", "-p", help="测试文件模式，如 'test_rag*'")
    parser.add_argument("--markers", "-m", help="测试标记，如 'rag' 或 'not slow'")
    parser.add_argument("--coverage", "-c", action="store_true", help="生成覆盖率报告")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    
    args = parser.parse_args()
    
    result = run_pytest(
        test_pattern=args.pattern,
        markers=args.markers,
        verbose=not args.quiet,
        coverage=args.coverage
    )
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
