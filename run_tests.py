#!/usr/bin/env python3
"""
AuraWell 测试运行脚本
简化的测试运行入口，支持不同类型的测试
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n🧪 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="AuraWell 测试运行器")
    parser.add_argument(
        "--type", 
        choices=["all", "upgrade", "translation", "rag", "model", "acceptance", "unit"],
        default="all",
        help="测试类型"
    )
    parser.add_argument(
        "--install-deps", 
        action="store_true",
        help="自动安装测试依赖"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    # 确保在项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🚀 AuraWell 测试运行器")
    print(f"项目目录: {project_root}")
    print(f"测试类型: {args.type}")
    
    # 安装依赖
    if args.install_deps:
        print("\n📦 安装测试依赖...")
        if not run_command("pip install -r requirements.txt", "安装依赖"):
            return False
    
    # 设置Python路径
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "src")
    
    # 根据测试类型运行不同的测试
    success = True
    
    if args.type == "all":
        # 运行所有升级相关测试
        cmd = "python tests/run_upgrade_tests.py"
        success = run_command(cmd, "运行所有升级测试")
        
    elif args.type == "upgrade":
        # 运行升级功能测试
        tests = [
            "tests/test_translation_service.py",
            "tests/test_rag_upgrade.py", 
            "tests/test_model_fallback_service.py"
        ]
        for test in tests:
            if not run_command(f"python -m pytest {test} -v", f"运行 {test}"):
                success = False
                
    elif args.type == "translation":
        # 只运行翻译服务测试
        success = run_command(
            "python -m pytest tests/test_translation_service.py -v",
            "运行翻译服务测试"
        )
        
    elif args.type == "rag":
        # 只运行RAG升级测试
        success = run_command(
            "python -m pytest tests/test_rag_upgrade.py -v",
            "运行RAG升级测试"
        )
        
    elif args.type == "model":
        # 只运行多模型测试
        success = run_command(
            "python -m pytest tests/test_model_fallback_service.py -v",
            "运行多模型梯度服务测试"
        )
        
    elif args.type == "acceptance":
        # 只运行验收测试
        success = run_command(
            "python -m pytest tests/test_upgrade_acceptance.py -v",
            "运行升级验收测试"
        )
        
    elif args.type == "unit":
        # 运行所有单元测试
        success = run_command(
            "python -m pytest tests/ -v --tb=short",
            "运行所有单元测试"
        )
    
    # 显示结果
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试完成！所有测试都通过了。")
        print("\n📋 查看测试报告:")
        print("- 详细日志: tests/test_results.log")
        print("- 测试报告: tests/upgrade_test_report.txt")
        print("- 验收报告: tests/upgrade_acceptance_report.txt")
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
        print("\n🔧 故障排除建议:")
        print("1. 确保所有依赖已安装: pip install -r requirements.txt")
        print("2. 检查API密钥配置")
        print("3. 确认网络连接正常")
        print("4. 查看详细日志: tests/test_results.log")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
