#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS功能单元测试运行器
运行所有OSS相关功能的单元测试
"""

import unittest
import os
import sys
import time
from io import StringIO

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 导入所有测试模块
from test_oss_utils import (
    TestOSSConfig, TestOSSManager, TestTimeUtils, TestOSSManagerIntegration
)
from test_file_index_manager import (
    TestFileIndexManager, TestFileIndexManagerTimeQueries, 
    TestFileIndexManagerErrorHandling, TestFileIndexManagerIntegration
)
from test_arxiv_api import (
    TestArxivXMLParsing, TestDownloadPDFToOSS, TestExportPapersToOSS,
    TestDownloadPDFLegacy, TestArxivAPIIntegration
)
from test_rag_extension_oss import (
    TestDocumentOSSMethods, TestDocumentContentFilter, TestDocumentFile2VectorDB
)
from test_batch_processing import (
    TestBatchProcessing, TestBatchProcessingErrorHandling
)


class TestResult:
    """测试结果统计类"""
    
    def __init__(self):
        self.total_tests = 0
        self.total_failures = 0
        self.total_errors = 0
        self.total_skipped = 0
        self.module_results = {}
        self.start_time = None
        self.end_time = None
    
    def add_module_result(self, module_name, result):
        """添加模块测试结果"""
        self.module_results[module_name] = {
            'tests': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
            'success': result.testsRun - len(result.failures) - len(result.errors)
        }
        
        self.total_tests += result.testsRun
        self.total_failures += len(result.failures)
        self.total_errors += len(result.errors)
        if hasattr(result, 'skipped'):
            self.total_skipped += len(result.skipped)
    
    def get_success_count(self):
        """获取成功测试数量"""
        return self.total_tests - self.total_failures - self.total_errors
    
    def get_success_rate(self):
        """获取成功率"""
        if self.total_tests == 0:
            return 0.0
        return (self.get_success_count() / self.total_tests) * 100
    
    def get_duration(self):
        """获取测试持续时间"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0


def run_module_tests(module_name, test_classes, verbose=True):
    """运行指定模块的测试"""
    print(f"\n{'='*60}")
    print(f"🧪 运行 {module_name} 模块测试")
    print(f"{'='*60}")
    
    # 创建测试套件
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # 运行测试
    if verbose:
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    else:
        # 静默模式，只收集结果
        runner = unittest.TextTestRunner(verbosity=0, stream=StringIO())
    
    result = runner.run(suite)
    
    # 输出模块结果摘要
    success_count = result.testsRun - len(result.failures) - len(result.errors)
    print(f"\n📊 {module_name} 模块测试结果:")
    print(f"  总测试数: {result.testsRun}")
    print(f"  成功: {success_count}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result


def run_all_tests(verbose=True, stop_on_failure=False):
    """运行所有OSS功能测试"""
    print("🚀 开始运行OSS功能单元测试套件")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_result = TestResult()
    test_result.start_time = time.time()
    
    # 定义测试模块和对应的测试类
    test_modules = [
        ("OSS工具模块", [TestOSSConfig, TestOSSManager, TestTimeUtils, TestOSSManagerIntegration]),
        ("文件索引管理器", [TestFileIndexManager, TestFileIndexManagerTimeQueries, 
                      TestFileIndexManagerErrorHandling, TestFileIndexManagerIntegration]),
        ("arXiv API", [TestArxivXMLParsing, TestDownloadPDFToOSS, TestExportPapersToOSS,
                      TestDownloadPDFLegacy, TestArxivAPIIntegration]),
        ("RAG扩展OSS功能", [TestDocumentOSSMethods, TestDocumentContentFilter, TestDocumentFile2VectorDB]),
        ("批量处理功能", [TestBatchProcessing, TestBatchProcessingErrorHandling])
    ]
    
    failed_modules = []
    
    # 运行每个模块的测试
    for module_name, test_classes in test_modules:
        try:
            result = run_module_tests(module_name, test_classes, verbose)
            test_result.add_module_result(module_name, result)
            
            # 如果有失败且设置了stop_on_failure，则停止
            if stop_on_failure and (result.failures or result.errors):
                failed_modules.append(module_name)
                print(f"⚠️  {module_name} 模块测试失败，停止后续测试")
                break
            elif result.failures or result.errors:
                failed_modules.append(module_name)
                
        except Exception as e:
            print(f"❌ {module_name} 模块测试运行异常: {e}")
            failed_modules.append(module_name)
            if stop_on_failure:
                break
    
    test_result.end_time = time.time()
    
    # 输出总体测试结果
    print_test_summary(test_result, failed_modules)
    
    return test_result


def print_test_summary(test_result, failed_modules):
    """打印测试结果摘要"""
    print("\n" + "="*80)
    print("📊 OSS功能单元测试总结报告")
    print("="*80)
    
    # 总体统计
    print(f"⏱️  测试持续时间: {test_result.get_duration():.2f} 秒")
    print(f"📈 总体统计:")
    print(f"  总测试数: {test_result.total_tests}")
    print(f"  成功: {test_result.get_success_count()}")
    print(f"  失败: {test_result.total_failures}")
    print(f"  错误: {test_result.total_errors}")
    print(f"  成功率: {test_result.get_success_rate():.1f}%")
    
    # 各模块详细结果
    print(f"\n📋 各模块测试结果:")
    for module_name, result in test_result.module_results.items():
        status = "✅" if result['failures'] == 0 and result['errors'] == 0 else "❌"
        success_rate = (result['success'] / result['tests'] * 100) if result['tests'] > 0 else 0
        print(f"  {status} {module_name}: {result['success']}/{result['tests']} ({success_rate:.1f}%)")
        
        if result['failures'] > 0 or result['errors'] > 0:
            print(f"    失败: {result['failures']}, 错误: {result['errors']}")
    
    # 失败模块汇总
    if failed_modules:
        print(f"\n⚠️  需要关注的模块:")
        for module in failed_modules:
            print(f"  - {module}")
    
    # 总体评估
    print(f"\n🎯 总体评估:")
    if test_result.total_failures == 0 and test_result.total_errors == 0:
        print("  🎉 所有测试通过！OSS功能实现完全正确")
    elif test_result.get_success_rate() >= 90:
        print("  ✅ 测试大部分通过，OSS功能基本正常")
    elif test_result.get_success_rate() >= 70:
        print("  ⚠️  部分测试失败，需要检查和修复")
    else:
        print("  ❌ 大量测试失败，需要重点关注和修复")
    
    # 建议
    print(f"\n💡 建议:")
    if failed_modules:
        print("  1. 优先修复失败的测试用例")
        print("  2. 检查相关模块的实现逻辑")
        print("  3. 验证环境配置和依赖")
    else:
        print("  1. 继续保持代码质量")
        print("  2. 考虑添加更多边界情况测试")
        print("  3. 定期运行测试确保功能稳定")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OSS功能单元测试运行器')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='详细输出模式')
    parser.add_argument('--stop-on-failure', '-s', action='store_true',
                       help='遇到失败时停止测试')
    parser.add_argument('--module', '-m', type=str,
                       help='只运行指定模块的测试')
    
    args = parser.parse_args()
    
    if args.module:
        # 运行指定模块的测试
        module_map = {
            'oss': [TestOSSConfig, TestOSSManager, TestTimeUtils, TestOSSManagerIntegration],
            'index': [TestFileIndexManager, TestFileIndexManagerTimeQueries, 
                     TestFileIndexManagerErrorHandling, TestFileIndexManagerIntegration],
            'arxiv': [TestArxivXMLParsing, TestDownloadPDFToOSS, TestExportPapersToOSS,
                     TestDownloadPDFLegacy, TestArxivAPIIntegration],
            'rag': [TestDocumentOSSMethods, TestDocumentContentFilter, TestDocumentFile2VectorDB],
            'batch': [TestBatchProcessing, TestBatchProcessingErrorHandling]
        }
        
        if args.module in module_map:
            result = run_module_tests(args.module, module_map[args.module], args.verbose)
            print(f"\n模块 '{args.module}' 测试完成")
        else:
            print(f"未知模块: {args.module}")
            print(f"可用模块: {', '.join(module_map.keys())}")
    else:
        # 运行所有测试
        run_all_tests(verbose=args.verbose, stop_on_failure=args.stop_on_failure)


if __name__ == '__main__':
    main()
