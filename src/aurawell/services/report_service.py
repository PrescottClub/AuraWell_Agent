"""
健康报告服务
生成多成员家庭健康数据的聚合报告
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ..config.health_constants import get_health_constant, get_category_constants

logger = logging.getLogger(__name__)


class HealthReportService:
    """健康报告服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def generate_report(
        self, 
        members: List[str], 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """
        生成家庭成员健康报告
        
        Args:
            members: 家庭成员ID列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            包含健康报告数据的字典
        """
        try:
            # Validate input parameters
            if not members:
                raise ValueError("At least one member required")
            
            max_members = get_health_constant("reports", "MAX_MEMBERS_PER_REPORT", 10)
            if len(members) > max_members:
                raise ValueError(f"Maximum {max_members} members allowed")
            
            self.logger.info(f"Generating health report for {len(members)} members from {start_date} to {end_date}")
            
            # 解析日期
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Validate date range
            if start_dt > end_dt:
                raise ValueError("Invalid date range: start_date must be before end_date")
            
            duration_days = (end_dt - start_dt).days + 1
            
            # 模拟聚合健康数据
            aggregated_data = await self._aggregate_health_data(members, start_dt, end_dt)
            
            # 生成趋势分析
            trends = await self._analyze_trends(aggregated_data, duration_days)
            
            # 生成关键指标摘要
            summary = await self._generate_key_metrics_summary(aggregated_data)
            
            # 检查异常提醒
            alerts = await self._check_health_alerts(aggregated_data, members)
            
            report = {
                "report_id": f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generation_time": datetime.now().isoformat(),
                "period": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "duration_days": duration_days
                },
                "members": members,
                "member_count": len(members),
                "summary": summary,
                "trends": trends,
                "alerts": alerts,
                "aggregated_data": aggregated_data,
                "metadata": {
                    "generated_by": "HealthReportService",
                    "version": get_health_constant("reports", "REPORT_VERSION", "3.0.0")
                }
            }
            
            self.logger.info(f"Health report generated successfully: {report['report_id']}")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate health report: {e}")
            raise
    
    async def _aggregate_health_data(
        self, 
        members: List[str], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """聚合健康数据"""
        # 获取健康常量
        steps_base = get_health_constant("steps", "MODERATE_ACTIVITY_BASE", 8500)
        steps_samples = get_health_constant("steps", "VARIANCE_SAMPLES", [8500, 9200, 7800])
        calories_base = get_health_constant("calories", "DAILY_BURN_BASE", 2100)
        calories_samples = get_health_constant("calories", "MODERATE_BURN_SAMPLES", [2100, 2300, 1900])
        activity_minutes_base = get_health_constant("calories", "ACTIVITY_MINUTES_BASE", 45)
        
        # 模拟数据聚合
        return {
            "activity": {
                "total_steps": sum(steps_samples * len(members)),
                "avg_daily_steps": steps_base,
                "total_calories_burned": sum(calories_samples * len(members)),
                "avg_daily_calories": calories_base,
                "active_days": (end_date - start_date).days,
                "by_member": {
                    member_id: {
                        "steps": steps_base + (i * 200),
                        "calories": calories_base + (i * 50),
                        "active_minutes": activity_minutes_base + (i * 5)
                    } for i, member_id in enumerate(members)
                }
            },
            "sleep": {
                "avg_sleep_hours": 7.5,
                "total_sleep_sessions": len(members) * 7,
                "avg_sleep_quality": 85.2,
                "by_member": {
                    member_id: {
                        "avg_duration": 7.5 + (i * 0.2),
                        "avg_quality": 85 + (i * 2),
                        "deep_sleep_percentage": 20 + (i * 1)
                    } for i, member_id in enumerate(members)
                }
            },
            "weight": {
                "avg_weight_change": -0.5,  # kg
                "members_losing_weight": len(members) // 2,
                "members_gaining_weight": len(members) // 4,
                "by_member": {
                    member_id: {
                        "weight_change": -0.5 + (i * 0.3),
                        "bmi_change": -0.2 + (i * 0.1)
                    } for i, member_id in enumerate(members)
                }
            },
            "nutrition": {
                "avg_calorie_intake": 2000,
                "avg_protein_intake": 80,  # grams
                "avg_carb_intake": 250,    # grams
                "by_member": {
                    member_id: {
                        "daily_calories": 2000 + (i * 100),
                        "protein_grams": 80 + (i * 5),
                        "carb_grams": 250 + (i * 20)
                    } for i, member_id in enumerate(members)
                }
            },
            "heart_rate": {
                "avg_resting_hr": 68,
                "avg_max_hr": 150,
                "by_member": {
                    member_id: {
                        "resting_hr": 68 + (i * 2),
                        "max_hr": 150 + (i * 5),
                        "avg_hr": 85 + (i * 3)
                    } for i, member_id in enumerate(members)
                }
            }
        }
    
    async def _analyze_trends(self, data: Dict[str, Any], duration_days: int) -> Dict[str, Any]:
        """分析趋势数据"""
        return {
            "activity_trends": {
                "steps_trend": "increasing",  # increasing, decreasing, stable
                "steps_change_percent": 5.2,
                "calories_trend": "stable",
                "calories_change_percent": 1.1
            },
            "sleep_trends": {
                "duration_trend": "improving",
                "duration_change_hours": 0.3,
                "quality_trend": "stable",
                "quality_change_percent": 2.1
            },
            "weight_trends": {
                "weight_trend": "decreasing",
                "avg_weekly_change": -0.2,
                "family_progress": "positive"
            },
            "overall_health_score": {
                "current_score": 82.5,
                "previous_score": 79.3,
                "improvement_percent": 4.0,
                "trend_direction": "improving"
            }
        }
    
    async def _generate_key_metrics_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成关键指标摘要"""
        return {
            "top_performers": {
                "most_active": "member_001",
                "best_sleeper": "member_002", 
                "most_consistent": "member_001"
            },
            "family_achievements": [
                "全家平均步数超过8000步",
                "睡眠质量提升3%",
                "2名成员成功减重"
            ],
            "key_insights": [
                "家庭整体活动水平较上周提升5.2%",
                "睡眠质量持续改善，深度睡眠时间增加",
                "建议增加蛋白质摄入以支持减重目标"
            ],
            "next_week_focus": [
                "保持当前运动强度",
                "关注营养均衡",
                "继续优化睡眠时间"
            ]
        }
    
    async def _check_health_alerts(self, data: Dict[str, Any], members: List[str]) -> List[Dict[str, Any]]:
        """检查健康异常提醒"""
        alerts = []
        
        # 检查活动水平异常
        for member_id in members:
            member_activity = data["activity"]["by_member"].get(member_id, {})
            if member_activity.get("steps", 0) < 5000:
                alerts.append({
                    "type": "low_activity",
                    "severity": "medium",
                    "member_id": member_id,
                    "message": f"成员 {member_id} 日均步数低于5000步，建议增加活动量",
                    "recommendation": "每天增加30分钟中等强度运动"
                })
        
        # 检查睡眠异常
        for member_id in members:
            member_sleep = data["sleep"]["by_member"].get(member_id, {})
            if member_sleep.get("avg_duration", 0) < 6.5:
                alerts.append({
                    "type": "insufficient_sleep",
                    "severity": "high", 
                    "member_id": member_id,
                    "message": f"成员 {member_id} 平均睡眠时间不足6.5小时",
                    "recommendation": "建立规律作息，确保每晚至少7小时睡眠"
                })
        
        # 检查体重变化异常
        for member_id in members:
            member_weight = data["weight"]["by_member"].get(member_id, {})
            weight_change = member_weight.get("weight_change", 0)
            if abs(weight_change) > 2.0:  # 体重变化超过2kg
                severity = "high" if abs(weight_change) > 3.0 else "medium"
                direction = "增加" if weight_change > 0 else "减少"
                alerts.append({
                    "type": "significant_weight_change",
                    "severity": severity,
                    "member_id": member_id,
                    "message": f"成员 {member_id} 体重{direction}{abs(weight_change):.1f}kg，变化较大",
                    "recommendation": "建议咨询医生或营养师调整饮食计划"
                })
        
        return alerts 