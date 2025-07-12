"""
Prompt智能优化服务

负责自动化分析Prompt性能并生成优化建议，支持：
- 自动化性能分析
- 版本对比和推荐
- 优化建议生成
- 定时任务调度
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from .prompt_performance_service import prompt_performance_service
from .prompt_version_service import prompt_version_service

logger = logging.getLogger(__name__)


@dataclass
class OptimizationRecommendation:
    """优化建议数据类"""
    priority: str  # 'high', 'medium', 'low'
    category: str  # 'performance', 'quality', 'reliability'
    title: str
    description: str
    expected_improvement: str
    implementation_effort: str  # 'low', 'medium', 'high'


@dataclass
class PerformanceAnalysisReport:
    """性能分析报告数据类"""
    scenario: str
    analysis_date: datetime
    total_versions: int
    best_version: str
    worst_version: str
    overall_health: str  # 'excellent', 'good', 'fair', 'poor'
    key_metrics: Dict[str, Any]
    recommendations: List[OptimizationRecommendation]
    version_comparison: Dict[str, Any]


class PromptOptimizerService:
    """Prompt智能优化服务"""
    
    def __init__(self):
        self.logger = logger
        self._analysis_cache = {}
    
    async def analyze_scenario_performance(
        self,
        scenario: str,
        days: int = 30,
        min_samples: int = 10
    ) -> PerformanceAnalysisReport:
        """
        分析场景性能并生成报告
        
        Args:
            scenario: 场景名称
            days: 分析天数
            min_samples: 最小样本数
            
        Returns:
            性能分析报告
        """
        try:
            self.logger.info(f"Starting performance analysis for scenario: {scenario}")
            
            # 获取所有版本的性能数据
            versions_data = await self._get_all_versions_performance(scenario, days)
            
            if not versions_data:
                return self._create_empty_report(scenario)
            
            # 过滤掉样本数不足的版本
            valid_versions = {
                v: data for v, data in versions_data.items()
                if data.get('total_uses', 0) >= min_samples
            }
            
            if not valid_versions:
                return self._create_insufficient_data_report(scenario, versions_data)
            
            # 分析最佳和最差版本
            best_version, worst_version = self._identify_best_worst_versions(valid_versions)
            
            # 计算整体健康度
            overall_health = self._calculate_overall_health(valid_versions)
            
            # 生成优化建议
            recommendations = await self._generate_recommendations(scenario, valid_versions)
            
            # 创建版本对比数据
            version_comparison = self._create_version_comparison(valid_versions)
            
            # 计算关键指标
            key_metrics = self._calculate_key_metrics(valid_versions)
            
            report = PerformanceAnalysisReport(
                scenario=scenario,
                analysis_date=datetime.utcnow(),
                total_versions=len(versions_data),
                best_version=best_version,
                worst_version=worst_version,
                overall_health=overall_health,
                key_metrics=key_metrics,
                recommendations=recommendations,
                version_comparison=version_comparison
            )
            
            self.logger.info(f"Performance analysis completed for {scenario}: {overall_health} health")
            return report
            
        except Exception as e:
            self.logger.error(f"Error analyzing scenario performance: {e}")
            return self._create_error_report(scenario, str(e))
    
    async def generate_optimization_suggestions(
        self,
        scenario: str,
        target_metric: str = "overall",
        improvement_threshold: float = 0.1
    ) -> List[OptimizationRecommendation]:
        """
        生成优化建议
        
        Args:
            scenario: 场景名称
            target_metric: 目标指标
            improvement_threshold: 改进阈值
            
        Returns:
            优化建议列表
        """
        try:
            # 获取性能数据
            versions_data = await self._get_all_versions_performance(scenario, 30)
            
            recommendations = []
            
            # 分析用户评分
            avg_ratings = [data.get('average_rating', 0) for data in versions_data.values() if data.get('average_rating')]
            if avg_ratings and sum(avg_ratings) / len(avg_ratings) < 4.0:
                recommendations.append(OptimizationRecommendation(
                    priority='high',
                    category='quality',
                    title='提升用户满意度',
                    description='当前平均用户评分低于4.0，建议优化回答质量和相关性',
                    expected_improvement='用户评分提升0.5-1.0分',
                    implementation_effort='medium'
                ))
            
            # 分析响应时间
            avg_times = [data.get('average_response_time_ms', 0) for data in versions_data.values() if data.get('average_response_time_ms')]
            if avg_times and sum(avg_times) / len(avg_times) > 3000:
                recommendations.append(OptimizationRecommendation(
                    priority='medium',
                    category='performance',
                    title='优化响应速度',
                    description='平均响应时间超过3秒，建议优化Prompt长度和工具调用策略',
                    expected_improvement='响应时间减少30-50%',
                    implementation_effort='low'
                ))
            
            # 分析错误率
            error_rates = [data.get('error_rate_percent', 0) for data in versions_data.values() if data.get('error_rate_percent') is not None]
            if error_rates and sum(error_rates) / len(error_rates) > 5.0:
                recommendations.append(OptimizationRecommendation(
                    priority='high',
                    category='reliability',
                    title='降低错误率',
                    description='错误率超过5%，建议增强错误处理和输入验证',
                    expected_improvement='错误率降低至2%以下',
                    implementation_effort='medium'
                ))
            
            # 分析工具成功率
            tool_rates = [data.get('tool_success_rate', 0) for data in versions_data.values() if data.get('tool_success_rate')]
            if tool_rates and sum(tool_rates) / len(tool_rates) < 0.9:
                recommendations.append(OptimizationRecommendation(
                    priority='medium',
                    category='performance',
                    title='提升工具调用成功率',
                    description='工具调用成功率低于90%，建议优化工具调用逻辑和参数验证',
                    expected_improvement='工具成功率提升至95%以上',
                    implementation_effort='medium'
                ))
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating optimization suggestions: {e}")
            return []
    
    async def run_daily_analysis(self) -> Dict[str, Any]:
        """
        运行每日性能分析任务
        
        Returns:
            分析结果摘要
        """
        try:
            self.logger.info("Starting daily prompt performance analysis")
            
            scenarios = ["health_advice"]  # 可扩展到更多场景
            results = {}
            
            for scenario in scenarios:
                try:
                    # 分析场景性能
                    report = await self.analyze_scenario_performance(scenario)
                    
                    # 更新版本性能数据
                    await self._update_version_performance_scores(scenario)
                    
                    # 检查是否需要调整A/B测试
                    await self._check_ab_test_adjustments(scenario, report)
                    
                    results[scenario] = {
                        'status': 'completed',
                        'overall_health': report.overall_health,
                        'best_version': report.best_version,
                        'recommendations_count': len(report.recommendations),
                        'analysis_date': report.analysis_date.isoformat()
                    }
                    
                except Exception as e:
                    self.logger.error(f"Error analyzing scenario {scenario}: {e}")
                    results[scenario] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            summary = {
                'analysis_date': datetime.utcnow().isoformat(),
                'scenarios_analyzed': len(scenarios),
                'successful_analyses': len([r for r in results.values() if r.get('status') == 'completed']),
                'results': results
            }
            
            self.logger.info(f"Daily analysis completed: {summary['successful_analyses']}/{summary['scenarios_analyzed']} scenarios")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error in daily analysis: {e}")
            return {
                'analysis_date': datetime.utcnow().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    async def _get_all_versions_performance(self, scenario: str, days: int) -> Dict[str, Dict[str, Any]]:
        """
        从数据库获取所有版本的性能数据

        Args:
            scenario: 场景名称
            days: 统计天数

        Returns:
            版本性能数据字典
        """
        try:
            from ..database.connection import get_async_session
            from ..database.models import PromptVersionDB, PromptPerformanceLogDB
            from sqlalchemy import select, func, and_
            from datetime import datetime, timedelta

            results = {}
            since_date = datetime.utcnow() - timedelta(days=days)

            async with get_async_session() as session:
                # 查询所有活跃版本
                version_stmt = select(PromptVersionDB).where(
                    and_(
                        PromptVersionDB.scenario == scenario,
                        PromptVersionDB.is_active == True
                    )
                )
                version_result = await session.execute(version_stmt)
                versions = version_result.scalars().all()

                # 为每个版本聚合性能数据
                for version_record in versions:
                    version = version_record.version

                    # 聚合性能日志数据
                    perf_stmt = select(
                        func.count(PromptPerformanceLogDB.id).label('total_uses'),
                        func.avg(PromptPerformanceLogDB.user_rating).label('avg_rating'),
                        func.avg(PromptPerformanceLogDB.response_relevance).label('avg_relevance'),
                        func.avg(PromptPerformanceLogDB.response_helpfulness).label('avg_helpfulness'),
                        func.avg(PromptPerformanceLogDB.response_accuracy).label('avg_accuracy'),
                        func.avg(PromptPerformanceLogDB.response_time_ms).label('avg_response_time'),
                        func.avg(PromptPerformanceLogDB.tool_call_success.cast(sa.Float)).label('tool_success_rate'),
                        func.sum(PromptPerformanceLogDB.error_occurred.cast(sa.Integer)).label('error_count')
                    ).where(
                        and_(
                            PromptPerformanceLogDB.prompt_scenario == scenario,
                            PromptPerformanceLogDB.prompt_version == version,
                            PromptPerformanceLogDB.created_at >= since_date
                        )
                    )

                    perf_result = await session.execute(perf_stmt)
                    stats = perf_result.first()

                    if stats and stats.total_uses > 0:
                        # 计算错误率
                        error_rate = (stats.error_count / stats.total_uses * 100) if stats.total_uses > 0 else 0

                        # 计算综合性能分数
                        performance_score = self._calculate_composite_score({
                            'average_rating': stats.avg_rating,
                            'average_relevance': stats.avg_relevance,
                            'tool_success_rate': stats.tool_success_rate,
                            'error_rate_percent': error_rate
                        })

                        results[version] = {
                            'total_uses': stats.total_uses,
                            'average_rating': round(stats.avg_rating, 2) if stats.avg_rating else None,
                            'average_relevance': round(stats.avg_relevance, 3) if stats.avg_relevance else None,
                            'average_helpfulness': round(stats.avg_helpfulness, 3) if stats.avg_helpfulness else None,
                            'average_accuracy': round(stats.avg_accuracy, 3) if stats.avg_accuracy else None,
                            'average_response_time_ms': round(stats.avg_response_time, 1) if stats.avg_response_time else None,
                            'tool_success_rate': round(stats.tool_success_rate, 3) if stats.tool_success_rate else None,
                            'error_rate_percent': round(error_rate, 2),
                            'performance_score': round(performance_score, 3),
                            'version_metadata': {
                                'name': version_record.name,
                                'description': version_record.description,
                                'is_experimental': version_record.is_experimental,
                                'created_at': version_record.created_at.isoformat() if version_record.created_at else None
                            }
                        }

                        self.logger.debug(f"Aggregated performance data for {scenario}_{version}: {stats.total_uses} samples")

            return results

        except Exception as e:
            self.logger.error(f"Error getting versions performance from database: {e}")
            # 降级到服务调用
            return await self._get_versions_performance_fallback(scenario, days)

    async def _get_versions_performance_fallback(self, scenario: str, days: int) -> Dict[str, Dict[str, Any]]:
        """降级方案：通过服务获取性能数据"""
        versions = ["v3_0", "v3_1", "v3_2_test"]
        results = {}

        for version in versions:
            try:
                stats = await prompt_performance_service.get_performance_stats(scenario, version, days)
                if stats and stats.get('total_uses', 0) > 0:
                    results[version] = stats
            except Exception as e:
                self.logger.warning(f"Failed to get stats for {version}: {e}")

        return results

    def _calculate_composite_score(self, metrics: Dict[str, Any]) -> float:
        """
        计算综合性能分数

        Args:
            metrics: 性能指标字典

        Returns:
            综合分数 (0-1)
        """
        try:
            score = 0.0
            weight_sum = 0.0

            # 用户评分权重 40%
            if metrics.get('average_rating'):
                score += (metrics['average_rating'] / 5.0) * 0.4
                weight_sum += 0.4

            # 响应相关性权重 25%
            if metrics.get('average_relevance'):
                score += metrics['average_relevance'] * 0.25
                weight_sum += 0.25

            # 工具成功率权重 20%
            if metrics.get('tool_success_rate'):
                score += metrics['tool_success_rate'] * 0.2
                weight_sum += 0.2

            # 错误率权重 15% (反向)
            if metrics.get('error_rate_percent') is not None:
                error_score = max(0, 1 - (metrics['error_rate_percent'] / 100))
                score += error_score * 0.15
                weight_sum += 0.15

            # 标准化分数
            return score / weight_sum if weight_sum > 0 else 0.0

        except Exception as e:
            self.logger.error(f"Error calculating composite score: {e}")
            return 0.0
    
    def _identify_best_worst_versions(self, versions_data: Dict[str, Dict[str, Any]]) -> Tuple[str, str]:
        """识别最佳和最差版本"""
        if not versions_data:
            return "unknown", "unknown"
        
        # 基于综合评分排序
        sorted_versions = sorted(
            versions_data.items(),
            key=lambda x: (
                x[1].get('average_rating', 0) * 0.4 +
                x[1].get('average_relevance', 0) * 0.3 +
                x[1].get('tool_success_rate', 0) * 0.2 +
                (1 - x[1].get('error_rate_percent', 100) / 100) * 0.1
            ),
            reverse=True
        )
        
        best_version = sorted_versions[0][0]
        worst_version = sorted_versions[-1][0]
        
        return best_version, worst_version
    
    def _calculate_overall_health(self, versions_data: Dict[str, Dict[str, Any]]) -> str:
        """计算整体健康度"""
        if not versions_data:
            return "unknown"
        
        # 计算平均指标
        total_versions = len(versions_data)
        avg_rating = sum(data.get('average_rating', 0) for data in versions_data.values()) / total_versions
        avg_error_rate = sum(data.get('error_rate_percent', 0) for data in versions_data.values()) / total_versions
        
        if avg_rating >= 4.5 and avg_error_rate <= 2:
            return "excellent"
        elif avg_rating >= 4.0 and avg_error_rate <= 5:
            return "good"
        elif avg_rating >= 3.5 and avg_error_rate <= 10:
            return "fair"
        else:
            return "poor"
    
    async def _generate_recommendations(self, scenario: str, versions_data: Dict[str, Dict[str, Any]]) -> List[OptimizationRecommendation]:
        """生成优化建议"""
        return await self.generate_optimization_suggestions(scenario)
    
    def _create_version_comparison(self, versions_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """创建版本对比数据"""
        return {
            'versions': list(versions_data.keys()),
            'metrics': {
                'average_rating': {v: data.get('average_rating') for v, data in versions_data.items()},
                'error_rate': {v: data.get('error_rate_percent') for v, data in versions_data.items()},
                'response_time': {v: data.get('average_response_time_ms') for v, data in versions_data.items()}
            }
        }
    
    def _calculate_key_metrics(self, versions_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """计算关键指标"""
        total_uses = sum(data.get('total_uses', 0) for data in versions_data.values())
        avg_rating = sum(data.get('average_rating', 0) for data in versions_data.values()) / len(versions_data) if versions_data else 0
        avg_error_rate = sum(data.get('error_rate_percent', 0) for data in versions_data.values()) / len(versions_data) if versions_data else 0
        
        return {
            'total_uses': total_uses,
            'average_rating': round(avg_rating, 2),
            'average_error_rate': round(avg_error_rate, 2),
            'active_versions': len(versions_data)
        }
    
    def _create_empty_report(self, scenario: str) -> PerformanceAnalysisReport:
        """创建空报告"""
        return PerformanceAnalysisReport(
            scenario=scenario,
            analysis_date=datetime.utcnow(),
            total_versions=0,
            best_version="unknown",
            worst_version="unknown",
            overall_health="unknown",
            key_metrics={},
            recommendations=[],
            version_comparison={}
        )
    
    def _create_insufficient_data_report(self, scenario: str, versions_data: Dict) -> PerformanceAnalysisReport:
        """创建数据不足报告"""
        return PerformanceAnalysisReport(
            scenario=scenario,
            analysis_date=datetime.utcnow(),
            total_versions=len(versions_data),
            best_version="insufficient_data",
            worst_version="insufficient_data",
            overall_health="insufficient_data",
            key_metrics={'note': 'Insufficient data for analysis'},
            recommendations=[OptimizationRecommendation(
                priority='low',
                category='data',
                title='增加数据样本',
                description='当前数据样本不足以进行可靠的性能分析',
                expected_improvement='获得更准确的性能洞察',
                implementation_effort='low'
            )],
            version_comparison={}
        )
    
    def _create_error_report(self, scenario: str, error: str) -> PerformanceAnalysisReport:
        """创建错误报告"""
        return PerformanceAnalysisReport(
            scenario=scenario,
            analysis_date=datetime.utcnow(),
            total_versions=0,
            best_version="error",
            worst_version="error",
            overall_health="error",
            key_metrics={'error': error},
            recommendations=[],
            version_comparison={}
        )
    
    async def _update_version_performance_scores(self, scenario: str):
        """更新版本性能分数"""
        try:
            versions_data = await self._get_all_versions_performance(scenario, 30)
            for version, data in versions_data.items():
                await prompt_version_service.update_version_performance(scenario, version, data)
        except Exception as e:
            self.logger.error(f"Error updating version performance scores: {e}")
    
    async def _check_ab_test_adjustments(self, scenario: str, report: PerformanceAnalysisReport):
        """检查是否需要调整A/B测试"""
        try:
            # 如果最佳版本明显优于其他版本，可以考虑调整流量分配
            # 这里可以实现更复杂的A/B测试优化逻辑
            pass
        except Exception as e:
            self.logger.error(f"Error checking A/B test adjustments: {e}")


# 全局实例
prompt_optimizer_service = PromptOptimizerService()
