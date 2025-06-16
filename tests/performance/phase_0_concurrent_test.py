#!/usr/bin/env python3
"""
AuraWell Phase 0 - 并发回归快检
测试20并发请求，验证P99 < 300ms
"""

import asyncio
import aiohttp
import time
import statistics
import json
from typing import List, Dict, Any
from datetime import datetime

class Phase0ConcurrentTest:
    """Phase 0 并发测试类"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.concurrent_requests = 20
        self.target_p99_ms = 300
        
    async def test_endpoint(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET", 
                           headers: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """测试单个端点"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                async with session.get(url, headers=headers) as response:
                    status = response.status
                    result = await response.text()
            elif method == "POST":
                async with session.post(url, headers=headers, json=data) as response:
                    status = response.status
                    result = await response.text()
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = (time.time() - start_time) * 1000  # ms
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status": status,
                "response_time_ms": response_time,
                "success": 200 <= status < 300,
                "error": None
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "endpoint": endpoint,
                "method": method,
                "status": 0,
                "response_time_ms": response_time,
                "success": False,
                "error": str(e)
            }
    
    async def run_concurrent_tests(self) -> List[Dict[str, Any]]:
        """运行并发测试"""
        print(f"🚀 开始{self.concurrent_requests}并发测试...")
        print(f"🎯 目标P99响应时间: < {self.target_p99_ms}ms")
        print()
        
        # 定义测试端点 - 使用不需要认证的公开端点
        test_endpoints = [
            {"endpoint": "/", "method": "GET"},
            {"endpoint": "/api/v1/health", "method": "GET"},
            {"endpoint": "/docs", "method": "GET"},
            {"endpoint": "/openapi.json", "method": "GET"},
        ]
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            for endpoint_config in test_endpoints:
                print(f"📊 测试端点: {endpoint_config['method']} {endpoint_config['endpoint']}")
                
                # 创建并发任务
                tasks = []
                for i in range(self.concurrent_requests):
                    task = self.test_endpoint(
                        session=session,
                        endpoint=endpoint_config["endpoint"],
                        method=endpoint_config["method"]
                    )
                    tasks.append(task)
                
                # 并发执行
                start_time = time.time()
                endpoint_results = await asyncio.gather(*tasks, return_exceptions=True)
                total_time = time.time() - start_time
                
                # 处理结果
                valid_results = []
                for result in endpoint_results:
                    if isinstance(result, dict):
                        valid_results.append(result)
                        results.append(result)
                    else:
                        # 异常情况
                        error_result = {
                            "endpoint": endpoint_config["endpoint"],
                            "method": endpoint_config["method"],
                            "status": 0,
                            "response_time_ms": 0,
                            "success": False,
                            "error": str(result)
                        }
                        results.append(error_result)
                        valid_results.append(error_result)
                
                # 计算统计信息
                response_times = [r["response_time_ms"] for r in valid_results]
                success_count = sum(1 for r in valid_results if r["success"])
                
                if response_times:
                    avg_time = statistics.mean(response_times)
                    p50_time = statistics.median(response_times)
                    p90_time = statistics.quantiles(response_times, n=10)[8] if len(response_times) >= 10 else max(response_times)
                    p99_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times)
                    max_time = max(response_times)
                    min_time = min(response_times)
                else:
                    avg_time = p50_time = p90_time = p99_time = max_time = min_time = 0
                
                # 输出结果
                print(f"  ✅ 成功: {success_count}/{self.concurrent_requests}")
                print(f"  ⏱️  总耗时: {total_time:.3f}s")
                print(f"  📈 响应时间统计:")
                print(f"    - 最小值: {min_time:.1f}ms")
                print(f"    - 平均值: {avg_time:.1f}ms")
                print(f"    - 中位数: {p50_time:.1f}ms")
                print(f"    - P90: {p90_time:.1f}ms")
                print(f"    - P99: {p99_time:.1f}ms")
                print(f"    - 最大值: {max_time:.1f}ms")
                
                # 检查是否满足P99要求
                if p99_time <= self.target_p99_ms:
                    print(f"  🎉 P99达标: {p99_time:.1f}ms <= {self.target_p99_ms}ms")
                else:
                    print(f"  ❌ P99超标: {p99_time:.1f}ms > {self.target_p99_ms}ms")
                
                print()
                
        return results
    
    def analyze_results(self, results: List[Dict[str, Any]]):
        """分析测试结果"""
        print("📊 === Phase 0 并发测试结果分析 ===")
        print()
        
        # 按端点分组
        endpoint_stats = {}
        for result in results:
            endpoint = f"{result['method']} {result['endpoint']}"
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    "total": 0,
                    "success": 0,
                    "response_times": []
                }
            
            endpoint_stats[endpoint]["total"] += 1
            if result["success"]:
                endpoint_stats[endpoint]["success"] += 1
            endpoint_stats[endpoint]["response_times"].append(result["response_time_ms"])
        
        # 计算整体统计
        all_response_times = [r["response_time_ms"] for r in results if r["success"]]
        total_requests = len(results)
        total_success = sum(1 for r in results if r["success"])
        
        if all_response_times:
            overall_p99 = statistics.quantiles(all_response_times, n=100)[98] if len(all_response_times) >= 100 else max(all_response_times)
            overall_avg = statistics.mean(all_response_times)
        else:
            overall_p99 = overall_avg = 0
        
        print(f"🎯 整体性能指标:")
        print(f"  - 总请求数: {total_requests}")
        print(f"  - 成功请求数: {total_success}")
        print(f"  - 成功率: {(total_success/total_requests)*100:.1f}%")
        print(f"  - 整体平均响应时间: {overall_avg:.1f}ms")
        print(f"  - 整体P99响应时间: {overall_p99:.1f}ms")
        print()
        
        # 判断是否通过
        success_rate = (total_success / total_requests) * 100
        passed = success_rate >= 95 and overall_p99 <= self.target_p99_ms
        
        if passed:
            print("🎉 Phase 0 并发测试 PASSED!")
            print(f"  ✅ 成功率: {success_rate:.1f}% >= 95%")
            print(f"  ✅ P99响应时间: {overall_p99:.1f}ms <= {self.target_p99_ms}ms")
        else:
            print("❌ Phase 0 并发测试 FAILED!")
            if success_rate < 95:
                print(f"  ❌ 成功率不达标: {success_rate:.1f}% < 95%")
            if overall_p99 > self.target_p99_ms:
                print(f"  ❌ P99响应时间超标: {overall_p99:.1f}ms > {self.target_p99_ms}ms")
        
        print()
        return passed

async def main():
    """主函数"""
    print("🌟 AuraWell Phase 0 - 并发回归快检")
    print("=" * 60)
    print()
    
    tester = Phase0ConcurrentTest()
    
    try:
        # 运行并发测试
        results = await tester.run_concurrent_tests()
        
        # 分析结果
        passed = tester.analyze_results(results)
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"phase_0_report_{timestamp}.json"
        
        report = {
            "timestamp": timestamp,
            "test_config": {
                "concurrent_requests": tester.concurrent_requests,
                "target_p99_ms": tester.target_p99_ms
            },
            "results": results,
            "passed": passed
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 测试报告已保存: {report_file}")
        
        if passed:
            print("🏆 Phase 0 测试通过，可以继续执行 Phase IV!")
        else:
            print("⚠️ Phase 0 测试失败，请修复问题后重试!")
            
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 