"""
Prompt性能监控定时任务

负责定期执行Prompt性能分析和优化，支持：
- 每日性能分析报告
- 自动版本切换建议
- 异常检测和告警
- 性能趋势分析
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

from ..services.prompt_optimizer_service import prompt_optimizer_service
from ..services.prompt_version_service import prompt_version_service
from ..services.prompt_performance_service import prompt_performance_service

logger = logging.getLogger(__name__)


class PromptMonitoringTask:
    """Prompt性能监控定时任务"""
    
    def __init__(self):
        self.logger = logger
        self.is_running = False
        self.last_analysis_time = None
        
    async def run_daily_analysis(self) -> Dict[str, Any]:
        """
        运行每日性能分析
        
        Returns:
            分析结果摘要
        """
        if self.is_running:
            self.logger.warning("Daily analysis is already running, skipping...")
            return {"status": "skipped", "reason": "already_running"}
        
        self.is_running = True
        start_time = datetime.utcnow()
        
        try:
            self.logger.info("Starting daily prompt performance analysis")
            
            # 1. 运行性能分析
            analysis_result = await prompt_optimizer_service.run_daily_analysis()
            
            # 2. 检查版本性能并生成切换建议
            version_recommendations = await self._analyze_version_performance()
            
            # 3. 检测异常情况
            anomalies = await self._detect_anomalies()
            
            # 4. 生成综合报告
            report = await self._generate_daily_report(
                analysis_result, 
                version_recommendations, 
                anomalies
            )
            
            # 5. 保存报告
            await self._save_daily_report(report)
            
            # 6. 发送告警（如有需要）
            await self._send_alerts_if_needed(report)
            
            self.last_analysis_time = start_time
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            summary = {
                "status": "completed",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "analysis_result": analysis_result,
                "version_recommendations": version_recommendations,
                "anomalies_detected": len(anomalies),
                "report_generated": True
            }
            
            self.logger.info(f"Daily analysis completed in {duration:.2f} seconds")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error in daily analysis: {e}")
            return {
                "status": "error",
                "error": str(e),
                "start_time": start_time.isoformat(),
                "end_time": datetime.utcnow().isoformat()
            }
        finally:
            self.is_running = False
    
    async def _analyze_version_performance(self) -> List[Dict[str, Any]]:
        """分析版本性能并生成切换建议"""
        try:
            recommendations = []
            scenarios = ["health_advice"]  # 可扩展
            
            for scenario in scenarios:
                # 获取当前最佳版本
                current_best = await prompt_version_service.get_best_version(scenario)
                
                # 获取所有版本的性能数据
                versions_data = {}
                for version in ["v3_0", "v3_1", "v3_2_test"]:
                    try:
                        stats = await prompt_performance_service.get_performance_stats(
                            scenario, version, days=7
                        )
                        if stats.get('total_uses', 0) >= 5:  # 最少5次使用
                            versions_data[version] = stats
                    except Exception as e:
                        self.logger.warning(f"Failed to get stats for {version}: {e}")
                
                if len(versions_data) >= 2:
                    # 找出性能最佳的版本
                    best_version = max(
                        versions_data.keys(),
                        key=lambda v: (
                            versions_data[v].get('average_rating', 0) * 0.4 +
                            versions_data[v].get('average_relevance', 0) * 0.3 +
                            (1 - versions_data[v].get('error_rate_percent', 100) / 100) * 0.3
                        )
                    )
                    
                    if best_version != current_best:
                        performance_diff = self._calculate_performance_difference(
                            versions_data[current_best],
                            versions_data[best_version]
                        )
                        
                        if performance_diff > 0.1:  # 10%以上的性能提升
                            recommendations.append({
                                "scenario": scenario,
                                "current_version": current_best,
                                "recommended_version": best_version,
                                "performance_improvement": f"{performance_diff:.1%}",
                                "reason": "显著性能提升",
                                "confidence": "high" if performance_diff > 0.2 else "medium"
                            })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error analyzing version performance: {e}")
            return []
    
    async def _detect_anomalies(self) -> List[Dict[str, Any]]:
        """检测异常情况"""
        try:
            anomalies = []
            
            # 检查错误率异常
            stats = await prompt_performance_service.get_performance_stats(
                "health_advice", days=1
            )
            
            if stats.get('error_rate_percent', 0) > 10:
                anomalies.append({
                    "type": "high_error_rate",
                    "severity": "high",
                    "description": f"错误率异常高: {stats['error_rate_percent']:.1f}%",
                    "threshold": "10%",
                    "current_value": f"{stats['error_rate_percent']:.1f}%"
                })
            
            # 检查响应时间异常
            if stats.get('average_response_time_ms', 0) > 5000:
                anomalies.append({
                    "type": "slow_response",
                    "severity": "medium",
                    "description": f"响应时间过慢: {stats['average_response_time_ms']:.0f}ms",
                    "threshold": "5000ms",
                    "current_value": f"{stats['average_response_time_ms']:.0f}ms"
                })
            
            # 检查用户评分下降
            if stats.get('average_rating', 5) < 3.5:
                anomalies.append({
                    "type": "low_user_rating",
                    "severity": "high",
                    "description": f"用户评分过低: {stats['average_rating']:.1f}",
                    "threshold": "3.5",
                    "current_value": f"{stats['average_rating']:.1f}"
                })
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            return []
    
    async def _generate_daily_report(
        self, 
        analysis_result: Dict[str, Any],
        version_recommendations: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成每日报告"""
        
        report = {
            "report_date": datetime.utcnow().isoformat(),
            "report_type": "daily_prompt_performance",
            "summary": {
                "total_scenarios_analyzed": len(analysis_result.get('results', {})),
                "version_recommendations": len(version_recommendations),
                "anomalies_detected": len(anomalies),
                "overall_health": self._calculate_overall_health(analysis_result)
            },
            "analysis_details": analysis_result,
            "version_recommendations": version_recommendations,
            "anomalies": anomalies,
            "action_items": self._generate_action_items(version_recommendations, anomalies)
        }
        
        return report
    
    async def _save_daily_report(self, report: Dict[str, Any]):
        """保存每日报告"""
        try:
            # 这里可以保存到数据库或文件系统
            # 目前先记录到日志
            self.logger.info(f"Daily report generated: {json.dumps(report, indent=2, ensure_ascii=False)}")
        except Exception as e:
            self.logger.error(f"Error saving daily report: {e}")
    
    async def _send_alerts_if_needed(self, report: Dict[str, Any]):
        """发送告警（如有需要）"""
        try:
            high_severity_anomalies = [
                a for a in report.get('anomalies', []) 
                if a.get('severity') == 'high'
            ]
            
            if high_severity_anomalies:
                alert_message = f"🚨 Prompt性能告警\n\n检测到 {len(high_severity_anomalies)} 个高严重性异常:\n"
                for anomaly in high_severity_anomalies:
                    alert_message += f"- {anomaly['description']}\n"
                
                # 这里可以集成邮件、钉钉、微信等告警渠道
                self.logger.warning(f"ALERT: {alert_message}")
            
            # 检查是否有重要的版本切换建议
            high_confidence_recommendations = [
                r for r in report.get('version_recommendations', [])
                if r.get('confidence') == 'high'
            ]
            
            if high_confidence_recommendations:
                self.logger.info(f"发现 {len(high_confidence_recommendations)} 个高置信度版本切换建议")
                
        except Exception as e:
            self.logger.error(f"Error sending alerts: {e}")
    
    def _calculate_performance_difference(self, current_stats: Dict, new_stats: Dict) -> float:
        """计算性能差异"""
        try:
            current_score = (
                current_stats.get('average_rating', 0) * 0.4 +
                current_stats.get('average_relevance', 0) * 0.3 +
                (1 - current_stats.get('error_rate_percent', 100) / 100) * 0.3
            )
            
            new_score = (
                new_stats.get('average_rating', 0) * 0.4 +
                new_stats.get('average_relevance', 0) * 0.3 +
                (1 - new_stats.get('error_rate_percent', 100) / 100) * 0.3
            )
            
            return (new_score - current_score) / current_score if current_score > 0 else 0
            
        except Exception as e:
            self.logger.error(f"Error calculating performance difference: {e}")
            return 0
    
    def _calculate_overall_health(self, analysis_result: Dict[str, Any]) -> str:
        """计算整体健康度"""
        try:
            results = analysis_result.get('results', {})
            if not results:
                return "unknown"
            
            health_scores = []
            for scenario_result in results.values():
                if scenario_result.get('status') == 'completed':
                    health = scenario_result.get('overall_health', 'unknown')
                    if health == 'excellent':
                        health_scores.append(4)
                    elif health == 'good':
                        health_scores.append(3)
                    elif health == 'fair':
                        health_scores.append(2)
                    elif health == 'poor':
                        health_scores.append(1)
            
            if not health_scores:
                return "unknown"
            
            avg_score = sum(health_scores) / len(health_scores)
            
            if avg_score >= 3.5:
                return "excellent"
            elif avg_score >= 2.5:
                return "good"
            elif avg_score >= 1.5:
                return "fair"
            else:
                return "poor"
                
        except Exception as e:
            self.logger.error(f"Error calculating overall health: {e}")
            return "unknown"
    
    def _generate_action_items(
        self, 
        version_recommendations: List[Dict[str, Any]], 
        anomalies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """生成行动项"""
        action_items = []
        
        # 基于版本建议生成行动项
        for rec in version_recommendations:
            if rec.get('confidence') == 'high':
                action_items.append({
                    "priority": "high",
                    "type": "version_switch",
                    "title": f"切换到性能更优的版本 {rec['recommended_version']}",
                    "description": f"场景 {rec['scenario']} 可获得 {rec['performance_improvement']} 的性能提升",
                    "estimated_effort": "low"
                })
        
        # 基于异常生成行动项
        for anomaly in anomalies:
            if anomaly.get('severity') == 'high':
                action_items.append({
                    "priority": "high",
                    "type": "fix_anomaly",
                    "title": f"修复{anomaly['type']}问题",
                    "description": anomaly['description'],
                    "estimated_effort": "medium"
                })
        
        return action_items


# 全局实例
prompt_monitoring_task = PromptMonitoringTask()


# 定时任务调度函数
async def schedule_daily_analysis():
    """调度每日分析任务"""
    try:
        result = await prompt_monitoring_task.run_daily_analysis()
        logger.info(f"Scheduled daily analysis completed: {result['status']}")
        return result
    except Exception as e:
        logger.error(f"Error in scheduled daily analysis: {e}")
        return {"status": "error", "error": str(e)}
