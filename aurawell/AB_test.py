#!/usr/bin/env python3
"""
AuraWell AB测试文件
用于快速测试不同模型的调用效果

使用方法:
python aurawell/AB_test.py --model deepseek-v3
python aurawell/AB_test.py --model qwen-turbo
python aurawell/AB_test.py --compare
"""

import os
import sys
import argparse
import asyncio
import time
from typing import Dict, List, Optional
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.aurawell.core.deepseek_client import DeepSeekClient
from src.aurawell.services.model_fallback_service import get_model_fallback_service


class ABTestRunner:
    """AB测试运行器"""
    
    def __init__(self):
        self.test_queries = [
            "请简单介绍一下健康饮食的基本原则",
            "如何制定一个适合上班族的运动计划？",
            "高血压患者在饮食上需要注意什么？",
            "请解释一下什么是BMI，如何计算？",
            "失眠的常见原因有哪些？如何改善睡眠质量？"
        ]
        
    async def test_single_model(self, model_name: str) -> Dict:
        """测试单个模型"""
        print(f"\n🧪 测试模型: {model_name}")
        print("=" * 50)
        
        results = {
            "model": model_name,
            "tests": [],
            "total_time": 0,
            "success_count": 0,
            "error_count": 0
        }
        
        try:
            # 创建客户端
            client = DeepSeekClient()
            
            for i, query in enumerate(self.test_queries, 1):
                print(f"\n📝 测试 {i}/{len(self.test_queries)}: {query[:50]}...")
                
                start_time = time.time()
                test_result = {
                    "query": query,
                    "success": False,
                    "response": "",
                    "response_time": 0,
                    "error": None
                }
                
                try:
                    # 构建消息
                    messages = [
                        {"role": "system", "content": "你是一个专业的健康顾问，请提供准确、实用的健康建议。"},
                        {"role": "user", "content": query}
                    ]
                    
                    # 调用模型
                    response = client.get_deepseek_response(
                        messages=messages,
                        model_name=model_name,
                        temperature=0.7,
                        max_tokens=512
                    )
                    
                    test_result["success"] = True
                    test_result["response"] = response.content[:200] + "..." if len(response.content) > 200 else response.content
                    test_result["response_time"] = time.time() - start_time
                    results["success_count"] += 1
                    
                    print(f"✅ 成功 ({test_result['response_time']:.2f}s)")
                    print(f"📄 响应: {test_result['response'][:100]}...")
                    
                except Exception as e:
                    test_result["error"] = str(e)
                    test_result["response_time"] = time.time() - start_time
                    results["error_count"] += 1
                    
                    print(f"❌ 失败 ({test_result['response_time']:.2f}s): {str(e)[:100]}")
                
                results["tests"].append(test_result)
                results["total_time"] += test_result["response_time"]
                
                # 避免请求过于频繁
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ 模型初始化失败: {e}")
            results["init_error"] = str(e)
        
        return results
    
    async def compare_models(self) -> Dict:
        """比较多个模型"""
        print("\n🔄 开始AB对比测试")
        print("=" * 60)
        
        models_to_test = [
            os.getenv("DEEPSEEK_SERIES_V3", "deepseek-v3"),
            os.getenv("QWEN_FAST", "qwen-turbo")
        ]
        
        comparison_results = {
            "models": models_to_test,
            "results": {},
            "summary": {}
        }
        
        # 测试每个模型
        for model in models_to_test:
            results = await self.test_single_model(model)
            comparison_results["results"][model] = results
        
        # 生成对比总结
        comparison_results["summary"] = self._generate_comparison_summary(comparison_results["results"])
        
        return comparison_results
    
    def _generate_comparison_summary(self, results: Dict) -> Dict:
        """生成对比总结"""
        summary = {
            "best_performance": None,
            "best_reliability": None,
            "recommendations": []
        }
        
        # 计算平均响应时间
        avg_times = {}
        success_rates = {}
        
        for model, result in results.items():
            if result["success_count"] > 0:
                avg_times[model] = result["total_time"] / len(result["tests"])
                success_rates[model] = result["success_count"] / len(result["tests"])
            else:
                avg_times[model] = float('inf')
                success_rates[model] = 0
        
        # 找出最佳性能模型（响应时间最短）
        if avg_times:
            summary["best_performance"] = min(avg_times.keys(), key=lambda k: avg_times[k])
        
        # 找出最佳可靠性模型（成功率最高）
        if success_rates:
            summary["best_reliability"] = max(success_rates.keys(), key=lambda k: success_rates[k])
        
        # 生成建议
        for model, result in results.items():
            if result["success_count"] == len(result["tests"]):
                summary["recommendations"].append(f"✅ {model}: 100%成功率，平均响应时间{avg_times[model]:.2f}s")
            elif result["success_count"] > 0:
                summary["recommendations"].append(f"⚠️ {model}: {success_rates[model]*100:.1f}%成功率，平均响应时间{avg_times[model]:.2f}s")
            else:
                summary["recommendations"].append(f"❌ {model}: 完全失败")
        
        return summary
    
    def print_results(self, results: Dict):
        """打印测试结果"""
        if "results" in results:  # 对比测试结果
            print("\n📊 AB测试对比结果")
            print("=" * 60)
            
            for model, result in results["results"].items():
                print(f"\n🤖 模型: {model}")
                print(f"   成功: {result['success_count']}/{len(result['tests'])}")
                print(f"   总耗时: {result['total_time']:.2f}s")
                if result['success_count'] > 0:
                    print(f"   平均响应时间: {result['total_time']/len(result['tests']):.2f}s")
            
            print(f"\n🏆 测试总结:")
            summary = results["summary"]
            if summary["best_performance"]:
                print(f"   最佳性能: {summary['best_performance']}")
            if summary["best_reliability"]:
                print(f"   最佳可靠性: {summary['best_reliability']}")
            
            print(f"\n💡 建议:")
            for rec in summary["recommendations"]:
                print(f"   {rec}")
                
        else:  # 单模型测试结果
            print(f"\n📊 模型 {results['model']} 测试结果")
            print("=" * 50)
            print(f"成功: {results['success_count']}/{len(results['tests'])}")
            print(f"失败: {results['error_count']}/{len(results['tests'])}")
            print(f"总耗时: {results['total_time']:.2f}s")
            if results['success_count'] > 0:
                print(f"平均响应时间: {results['total_time']/len(results['tests']):.2f}s")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AuraWell AB测试工具")
    parser.add_argument("--model", type=str, help="指定要测试的模型名称")
    parser.add_argument("--compare", action="store_true", help="对比测试多个模型")
    parser.add_argument("--output", type=str, help="保存结果到JSON文件")
    
    args = parser.parse_args()
    
    runner = ABTestRunner()
    
    if args.compare:
        results = await runner.compare_models()
    elif args.model:
        results = await runner.test_single_model(args.model)
    else:
        # 默认测试当前配置的模型
        default_model = os.getenv("DEEPSEEK_SERIES_V3", "deepseek-v3")
        print(f"🎯 使用默认模型: {default_model}")
        results = await runner.test_single_model(default_model)
    
    # 打印结果
    runner.print_results(results)
    
    # 保存结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
