#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windows 11 兼容性测试运行器
运行所有修复后的RAG测试，验证在Windows 11上的兼容性
"""

import sys
import os
import subprocess
import time

def run_test(test_file, description):
    """
    运行单个测试文件
    """
    print(f"\n{'='*80}")
    print(f"🧪 运行测试: {description}")
    print(f"📁 文件: {test_file}")
    print(f"{'='*80}")
    
    try:
        start_time = time.time()
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=300)  # 5分钟超时
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ 测试通过 (耗时: {duration:.2f}秒)")
            if result.stdout:
                # 只显示最后几行输出
                lines = result.stdout.strip().split('\n')
                if len(lines) > 10:
                    print("📝 输出摘要:")
                    for line in lines[-5:]:
                        print(f"   {line}")
                else:
                    print("📝 完整输出:")
                    print(result.stdout)
            return True
        else:
            print(f"❌ 测试失败 (耗时: {duration:.2f}秒)")
            print(f"🔴 返回码: {result.returncode}")
            if result.stderr:
                print("🔴 错误信息:")
                print(result.stderr)
            if result.stdout:
                print("📝 输出信息:")
                print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ 测试超时 (超过5分钟)")
        return False
    except Exception as e:
        print(f"💥 测试执行异常: {e}")
        return False

def main():
    """
    主测试运行器
    """
    print("🚀 Windows 11 RAG测试套件")
    print("=" * 80)
    
    # 获取测试目录
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义测试列表 (按重要性排序)
    tests = [
        ("simple_test.py", "基础导入和依赖测试"),
        ("debug_test.py", "调试和环境变量测试"),
        ("test_file_analysis_windows.py", "文件分析功能测试"),
        ("test_reference_detection.py", "引用检测功能测试"),
        ("test_filtered_vectorization.py", "过滤向量化测试"),
        ("api_test.py", "API集成测试"),
        ("test_complete_workflow.py", "完整工作流程测试"),
    ]
    
    # 运行测试
    passed = 0
    failed = 0
    results = []
    
    for test_file, description in tests:
        test_path = os.path.join(test_dir, test_file)
        
        if not os.path.exists(test_path):
            print(f"⚠️  跳过测试: {test_file} (文件不存在)")
            continue
            
        success = run_test(test_path, description)
        results.append((test_file, description, success))
        
        if success:
            passed += 1
        else:
            failed += 1
            
        # 在测试之间稍作停顿
        time.sleep(1)
    
    # 输出总结
    print(f"\n{'='*80}")
    print("📊 测试结果总结")
    print(f"{'='*80}")
    
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"📈 总测试数: {total}")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📊 成功率: {success_rate:.1f}%")
    
    print(f"\n📋 详细结果:")
    for test_file, description, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {status} | {description}")
    
    # 给出建议
    print(f"\n💡 建议:")
    if success_rate >= 90:
        print("🎉 Windows 11兼容性优秀！所有主要功能正常工作。")
    elif success_rate >= 70:
        print("🟡 Windows 11兼容性良好，但有一些问题需要解决。")
    else:
        print("🔴 Windows 11兼容性需要改进，请检查失败的测试。")
    
    if failed > 0:
        print("🔧 对于失败的测试，请检查:")
        print("   - 环境变量配置 (.env文件)")
        print("   - 依赖包安装 (dashvector, 阿里云SDK等)")
        print("   - 文件路径问题")
        print("   - 网络连接和API访问")
    
    print(f"{'='*80}")
    
    return success_rate >= 70  # 70%以上认为测试通过

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
