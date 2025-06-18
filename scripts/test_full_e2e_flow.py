#!/usr/bin/env python3
"""
AuraWell 凤凰计划 Task 3.3.1 - 端到端完整流程验证脚本

这是凤凰计划的最终决战验证脚本！
验证完整的健康分析价值闭环：
数据获取 → AI分析 → 洞察生成 → 健康计划 → 个性化报告

唯一输入：用户ID
唯一输出：完整的个性化健康报告

Phoenix Project - Final E2E Validation Script
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aurawell.core.orchestrator_v2 import AuraWellOrchestrator, ComprehensiveHealthReport
from aurawell.core.deepseek_client import DeepSeekClient
from aurawell.integrations.apple_health_client import AppleHealthClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class E2EHealthAnalysisValidator:
    """
    端到端健康分析验证器
    
    验证从数据获取到最终报告生成的完整流程
    """
    
    def __init__(self):
        """Initialize the E2E validator"""
        self.orchestrator = None
        self.test_results = {
            "test_start_time": datetime.now(timezone.utc).isoformat(),
            "test_status": "PENDING",
            "phases": {},
            "final_report": None,
            "errors": [],
            "performance_metrics": {}
        }
        
    async def initialize_components(self) -> bool:
        """
        Initialize all required components
        
        Returns:
            True if all components initialized successfully
        """
        logger.info("🔧 初始化AuraWell核心组件...")
        
        try:
            # Initialize DeepSeek client
            deepseek_client = DeepSeekClient()
            logger.info("✅ DeepSeek AI客户端初始化成功")
            
            # Initialize Apple Health client
            apple_health_client = AppleHealthClient()
            logger.info("✅ Apple Health客户端初始化成功")
            
            # Initialize Orchestrator with both clients
            self.orchestrator = AuraWellOrchestrator(
                deepseek_client=deepseek_client,
                apple_health_client=apple_health_client
            )
            logger.info("✅ AuraWell Orchestrator v2 初始化成功")
            
            self.test_results["phases"]["component_initialization"] = {
                "status": "SUCCESS",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": "所有核心组件成功初始化"
            }
            
            return True
            
        except Exception as e:
            error_msg = f"组件初始化失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results["errors"].append(error_msg)
            self.test_results["phases"]["component_initialization"] = {
                "status": "FAILED",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": error_msg
            }
            return False
    
    async def test_data_fetching(self, user_id: str) -> bool:
        """
        测试数据获取能力
        
        Args:
            user_id: 测试用户ID
            
        Returns:
            True if data fetching successful
        """
        logger.info(f"📊 测试健康数据获取能力 (用户: {user_id})...")
        
        try:
            start_time = datetime.now()
            
            # Test Apple Health data fetching
            apple_client = self.orchestrator.apple_health_client
            
            # Test multiple data types
            test_tasks = [
                apple_client.get_user_profile(user_id),
                apple_client.get_activity_data(user_id, "2025-01-11", "2025-01-18"),
                apple_client.get_sleep_analysis(user_id, "2025-01-11", "2025-01-18"),
                apple_client.get_health_samples(user_id, "HKQuantityTypeIdentifierHeartRate", "2025-01-11", "2025-01-18")
            ]
            
            results = await asyncio.gather(*test_tasks, return_exceptions=True)
            
            # Analyze results
            successful_fetches = sum(1 for r in results if not isinstance(r, Exception))
            total_fetches = len(results)
            
            fetch_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ 数据获取测试完成: {successful_fetches}/{total_fetches} 成功")
            logger.info(f"⚡ 数据获取耗时: {fetch_time:.2f}秒")
            
            self.test_results["phases"]["data_fetching"] = {
                "status": "SUCCESS" if successful_fetches > 0 else "PARTIAL",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "successful_fetches": successful_fetches,
                "total_fetches": total_fetches,
                "fetch_time_seconds": fetch_time,
                "details": "健康数据获取测试完成"
            }
            
            self.test_results["performance_metrics"]["data_fetch_time"] = fetch_time
            
            return successful_fetches > 0
            
        except Exception as e:
            error_msg = f"数据获取测试失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results["errors"].append(error_msg)
            self.test_results["phases"]["data_fetching"] = {
                "status": "FAILED",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": error_msg
            }
            return False
    
    async def test_ai_analysis(self, user_id: str) -> bool:
        """
        测试AI分析能力
        
        Args:
            user_id: 测试用户ID
            
        Returns:
            True if AI analysis successful
        """
        logger.info("🧠 测试DeepSeek AI分析能力...")
        
        try:
            start_time = datetime.now()
            
            # Test DeepSeek AI with health context
            deepseek_client = self.orchestrator.deepseek_client
            
            test_messages = [
                {
                    "role": "system",
                    "content": "你是AuraWell的健康分析专家。"
                },
                {
                    "role": "user", 
                    "content": "请分析一个用户的健康状况：30岁男性，最近7天平均步数8000步，平均睡眠6.5小时。请提供健康建议。"
                }
            ]
            
            response = await deepseek_client.get_deepseek_response(
                messages=test_messages,
                model="deepseek-reasoner",
                temperature=0.3
            )
            
            ai_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ AI分析测试完成")
            logger.info(f"⚡ AI分析耗时: {ai_time:.2f}秒")
            logger.info(f"📄 AI回复长度: {len(response.content)}字符")
            
            self.test_results["phases"]["ai_analysis"] = {
                "status": "SUCCESS",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ai_response_length": len(response.content),
                "ai_analysis_time_seconds": ai_time,
                "details": "DeepSeek AI分析测试成功"
            }
            
            self.test_results["performance_metrics"]["ai_analysis_time"] = ai_time
            
            return True
            
        except Exception as e:
            error_msg = f"AI分析测试失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results["errors"].append(error_msg)
            self.test_results["phases"]["ai_analysis"] = {
                "status": "FAILED",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": error_msg
            }
            return False
    
    async def test_comprehensive_analysis(self, user_id: str) -> Optional[ComprehensiveHealthReport]:
        """
        测试完整的健康分析流程
        
        Args:
            user_id: 测试用户ID
            
        Returns:
            ComprehensiveHealthReport if successful, None otherwise
        """
        logger.info(f"🎯 执行完整健康分析流程 (用户: {user_id})...")
        
        try:
            start_time = datetime.now()
            
            # Execute the complete E2E analysis
            report = await self.orchestrator.analyze_user_comprehensive_health(
                user_id=user_id,
                days_back=7,
                include_ai_analysis=True,
                generate_health_plan=True
            )
            
            analysis_time = (datetime.now() - start_time).total_seconds()
            
            # Validate report completeness
            validation_results = self._validate_report_completeness(report)
            
            logger.info(f"✅ 完整健康分析完成")
            logger.info(f"⚡ 分析总耗时: {analysis_time:.2f}秒")
            logger.info(f"📊 生成洞察数量: {len(report.insights)}")
            logger.info(f"💡 生成建议数量: {len(report.recommendations)}")
            logger.info(f"⚠️ 风险因素数量: {len(report.risk_factors)}")
            logger.info(f"🎯 置信度分数: {report.confidence_score:.2f}")
            
            self.test_results["phases"]["comprehensive_analysis"] = {
                "status": "SUCCESS",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_analysis_time_seconds": analysis_time,
                "insights_generated": len(report.insights),
                "recommendations_generated": len(report.recommendations),
                "risk_factors_identified": len(report.risk_factors),
                "confidence_score": report.confidence_score,
                "validation_results": validation_results,
                "details": "完整E2E健康分析成功"
            }
            
            self.test_results["performance_metrics"]["total_analysis_time"] = analysis_time
            self.test_results["final_report"] = self._serialize_report_summary(report)
            
            return report
            
        except Exception as e:
            error_msg = f"完整健康分析失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results["errors"].append(error_msg)
            self.test_results["phases"]["comprehensive_analysis"] = {
                "status": "FAILED",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": error_msg
            }
            return None
    
    def _validate_report_completeness(self, report: ComprehensiveHealthReport) -> Dict[str, bool]:
        """Validate that the report contains all expected components"""
        return {
            "has_user_id": bool(report.user_id),
            "has_data_summary": bool(report.data_summary),
            "has_insights": len(report.insights) > 0,
            "has_ai_analysis": bool(report.ai_analysis),
            "has_recommendations": len(report.recommendations) > 0,
            "has_health_plan": report.health_plan is not None,
            "has_confidence_score": 0 <= report.confidence_score <= 1
        }
    
    def _serialize_report_summary(self, report: ComprehensiveHealthReport) -> Dict[str, Any]:
        """Create a serializable summary of the report"""
        return {
            "user_id": report.user_id,
            "generated_at": report.generated_at.isoformat(),
            "insights_count": len(report.insights),
            "recommendations_count": len(report.recommendations),
            "risk_factors_count": len(report.risk_factors),
            "confidence_score": report.confidence_score,
            "has_health_plan": report.health_plan is not None,
            "ai_analysis_preview": report.ai_analysis[:200] + "..." if len(report.ai_analysis) > 200 else report.ai_analysis,
            "data_summary": report.data_summary
        }
    
    async def run_full_e2e_test(self, user_id: str = "test_user_001") -> Dict[str, Any]:
        """
        运行完整的端到端测试流程
        
        Args:
            user_id: 测试用户ID
            
        Returns:
            Complete test results
        """
        logger.info("🚀 启动AuraWell凤凰计划E2E验证测试...")
        logger.info("=" * 60)
        
        test_start = datetime.now()
        
        try:
            # Phase 1: Initialize components
            logger.info("📋 阶段1: 组件初始化")
            if not await self.initialize_components():
                self.test_results["test_status"] = "FAILED"
                return self.test_results
            
            # Phase 2: Test data fetching
            logger.info("\n📋 阶段2: 数据获取测试")
            if not await self.test_data_fetching(user_id):
                logger.warning("⚠️ 数据获取测试部分失败，但继续进行...")
            
            # Phase 3: Test AI analysis
            logger.info("\n📋 阶段3: AI分析测试")
            if not await self.test_ai_analysis(user_id):
                logger.warning("⚠️ AI分析测试失败，但继续进行...")
            
            # Phase 4: Complete E2E analysis
            logger.info("\n📋 阶段4: 完整E2E分析")
            final_report = await self.test_comprehensive_analysis(user_id)
            
            # Calculate overall test results
            total_test_time = (datetime.now() - test_start).total_seconds()
            
            if final_report:
                self.test_results["test_status"] = "SUCCESS"
                logger.info("🎉 E2E测试完全成功！")
            else:
                self.test_results["test_status"] = "PARTIAL"
                logger.warning("⚠️ E2E测试部分成功")
            
            self.test_results["test_end_time"] = datetime.now(timezone.utc).isoformat()
            self.test_results["total_test_time_seconds"] = total_test_time
            self.test_results["performance_metrics"]["total_test_time"] = total_test_time
            
            logger.info(f"⚡ 总测试耗时: {total_test_time:.2f}秒")
            logger.info("=" * 60)
            
            return self.test_results
            
        except Exception as e:
            error_msg = f"E2E测试执行失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results["errors"].append(error_msg)
            self.test_results["test_status"] = "FAILED"
            self.test_results["test_end_time"] = datetime.now(timezone.utc).isoformat()
            return self.test_results
    
    def generate_test_report(self, output_file: Optional[str] = None) -> str:
        """
        生成详细的测试报告
        
        Args:
            output_file: Optional output file path
            
        Returns:
            Report file path
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"e2e_test_report_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 测试报告已生成: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"生成测试报告失败: {e}")
            return ""


async def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AuraWell 凤凰计划 E2E 验证测试")
    parser.add_argument("--user-id", default="test_user_phoenix", help="测试用户ID")
    parser.add_argument("--output", default=None, help="测试报告输出文件")
    parser.add_argument("--verbose", action="store_true", help="详细日志输出")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create validator and run tests
    validator = E2EHealthAnalysisValidator()
    
    # Run the complete E2E test
    test_results = await validator.run_full_e2e_test(args.user_id)
    
    # Generate test report
    report_file = validator.generate_test_report(args.output)
    
    # Print summary
    print("\n" + "=" * 80)
    print("🏥 AURAWELL 凤凰计划 E2E 测试总结")
    print("=" * 80)
    print(f"📊 测试状态: {test_results['test_status']}")
    print(f"⚡ 总耗时: {test_results.get('total_test_time_seconds', 0):.2f}秒")
    print(f"📈 性能指标: {test_results.get('performance_metrics', {})}")
    print(f"❌ 错误数量: {len(test_results.get('errors', []))}")
    
    if test_results.get("final_report"):
        final_report = test_results["final_report"]
        print(f"🎯 最终报告: 用户{final_report['user_id']}")
        print(f"📊 洞察数量: {final_report['insights_count']}")
        print(f"💡 建议数量: {final_report['recommendations_count']}")
        print(f"🎯 置信度: {final_report['confidence_score']:.2f}")
    
    if report_file:
        print(f"📄 详细报告: {report_file}")
    
    print("=" * 80)
    
    # Return appropriate exit code
    if test_results["test_status"] == "SUCCESS":
        print("🎉 凤凰计划E2E验证完全成功！AuraWell Agent已浴火重生！")
        return 0
    elif test_results["test_status"] == "PARTIAL":
        print("⚠️ 凤凰计划E2E验证部分成功")
        return 1
    else:
        print("❌ 凤凰计划E2E验证失败")
        return 2


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main())) 