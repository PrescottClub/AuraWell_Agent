#!/usr/bin/env python3
"""
AuraWell 升级测试运行脚本
运行所有升级相关的测试并生成报告
"""

import os
import sys
import unittest
import logging
from datetime import datetime
import subprocess

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'test_results.log'))
    ]
)
logger = logging.getLogger(__name__)


def run_test_suite(test_module_name, description):
    """运行指定的测试套件"""
    logger.info(f"🧪 开始运行 {description}")
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        # 导入测试模块
        test_module = __import__(test_module_name)
        
        # 创建测试套件
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        
        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # 返回测试结果
        return {
            'module': test_module_name,
            'description': description,
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success': result.wasSuccessful()
        }
        
    except Exception as e:
        logger.error(f"❌ 运行 {description} 时发生错误: {e}")
        return {
            'module': test_module_name,
            'description': description,
            'tests_run': 0,
            'failures': 0,
            'errors': 1,
            'success': False,
            'error': str(e)
        }


def check_dependencies():
    """检查测试依赖"""
    logger.info("🔍 检查测试依赖...")
    
    required_packages = [
        'torch',
        'transformers', 
        'langdetect',
        'pytest',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"⚠️ {package} 未安装")
    
    if missing_packages:
        logger.warning(f"缺少依赖包: {missing_packages}")
        print(f"\n⚠️ 缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    logger.info("✅ 所有依赖检查通过")
    return True


def install_dependencies():
    """安装缺失的依赖"""
    logger.info("📦 安装升级所需的依赖...")
    
    try:
        # 安装requirements.txt中的新依赖
        requirements_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
        
        if os.path.exists(requirements_path):
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', requirements_path
            ], check=True)
            logger.info("✅ 依赖安装完成")
            return True
        else:
            logger.error("❌ requirements.txt 文件不存在")
            return False
            
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ 依赖安装失败: {e}")
        return False


def generate_test_report(results):
    """生成测试报告"""
    logger.info("📊 生成测试报告...")
    
    total_tests = sum(r['tests_run'] for r in results)
    total_failures = sum(r['failures'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    successful_suites = sum(1 for r in results if r['success'])
    
    report = f"""
=== AuraWell 升级测试报告 ===
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

总体统计:
- 测试套件数: {len(results)}
- 成功套件数: {successful_suites}
- 总测试数: {total_tests}
- 失败测试数: {total_failures}
- 错误测试数: {total_errors}
- 总体成功率: {((total_tests - total_failures - total_errors) / max(total_tests, 1) * 100):.1f}%

详细结果:
"""
    
    for result in results:
        status = "✅ 通过" if result['success'] else "❌ 失败"
        report += f"""
{result['description']}: {status}
  - 模块: {result['module']}
  - 测试数: {result['tests_run']}
  - 失败数: {result['failures']}
  - 错误数: {result['errors']}
"""
        if 'error' in result:
            report += f"  - 错误信息: {result['error']}\n"
    
    report += f"""
=== 升级验收结论 ===
{'🎉 所有测试通过，升级验收成功！' if successful_suites == len(results) and total_failures == 0 and total_errors == 0 else '⚠️ 部分测试失败，需要检查和修复'}

=== 建议 ===
"""
    
    if total_failures > 0 or total_errors > 0:
        report += """
1. 检查失败的测试用例
2. 确认API密钥配置正确
3. 验证网络连接和服务可用性
4. 查看详细日志文件: tests/test_results.log
"""
    else:
        report += """
1. 升级功能已通过所有测试
2. 可以进行生产环境部署
3. 建议进行端到端集成测试
4. 监控生产环境性能指标
"""
    
    # 保存报告
    report_path = os.path.join(os.path.dirname(__file__), 'upgrade_test_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    logger.info(f"测试报告已保存到: {report_path}")
    
    return successful_suites == len(results) and total_failures == 0 and total_errors == 0


def main():
    """主函数"""
    print("🚀 AuraWell 升级测试开始")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查依赖
    if not check_dependencies():
        print("\n❓ 是否要自动安装缺失的依赖? (y/n): ", end="")
        choice = input().lower().strip()
        if choice == 'y':
            if not install_dependencies():
                print("❌ 依赖安装失败，测试终止")
                return False
        else:
            print("❌ 缺少必要依赖，测试终止")
            return False
    
    # 定义测试套件
    test_suites = [
        ('test_translation_service', '翻译服务测试'),
        ('test_rag_upgrade', 'RAG模块升级测试'),
        ('test_model_fallback_service', '多模型梯度服务测试'),
        ('test_upgrade_acceptance', '升级验收测试')
    ]
    
    # 运行所有测试
    results = []
    for module_name, description in test_suites:
        result = run_test_suite(module_name, description)
        results.append(result)
    
    # 生成报告
    success = generate_test_report(results)
    
    print(f"\n🏁 测试完成")
    if success:
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请查看报告")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
