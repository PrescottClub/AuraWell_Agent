"""
家庭交互功能服务层

处理成员点赞、健康告警等家庭互动功能的业务逻辑
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from ..repositories.family_interaction_repository import FamilyInteractionRepository
from ..repositories.family_repository import FamilyRepository
from ..repositories.user_repository import UserRepository
from ..models.api_models import HealthAlert
from ..config.health_constants import ALERT_CONSTANTS

logger = logging.getLogger(__name__)


class FamilyInteractionService:
    """家庭交互功能服务"""

    def __init__(
        self,
        interaction_repo: FamilyInteractionRepository,
        family_repo: FamilyRepository,
        user_repo: UserRepository,
    ):
        self.interaction_repo = interaction_repo
        self.family_repo = family_repo
        self.user_repo = user_repo

    # ============================================================================
    # 成员点赞功能
    # ============================================================================

    async def like_family_member(
        self,
        family_id: str,
        member_id: str,
        liker_id: str,
        like_type: str = "general",
        like_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        为家庭成员点赞
        
        Args:
            family_id: 家庭ID
            member_id: 被点赞成员ID
            liker_id: 点赞者ID
            like_type: 点赞类型
            like_reason: 点赞原因
        
        Returns:
            点赞结果
        """
        try:
            # 验证家庭成员身份
            await self._validate_family_membership(family_id, liker_id)
            await self._validate_family_membership(family_id, member_id)
            
            # 不能给自己点赞
            if liker_id == member_id:
                raise ValueError("不能给自己点赞")
            
            # 执行点赞操作
            result = await self.interaction_repo.like_member(
                family_id=family_id,
                liker_id=liker_id,
                liked_member_id=member_id,
                like_type=like_type,
                like_reason=like_reason,
            )
            
            # 记录家庭活动日志
            await self._log_family_activity(
                family_id=family_id,
                user_id=liker_id,
                action="member_liked" if result["action"] == "liked" else "member_unliked",
                details={
                    "liked_member_id": member_id,
                    "like_type": like_type,
                    "like_reason": like_reason,
                    "total_likes": result["total_likes"],
                }
            )
            
            logger.info(f"用户 {liker_id} 对成员 {member_id} 执行{result['action']}操作")
            return result
            
        except Exception as e:
            logger.error(f"成员点赞操作失败: {e}")
            raise

    async def get_member_likes(
        self,
        family_id: str,
        member_id: str,
        requester_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        获取成员收到的点赞列表
        
        Args:
            family_id: 家庭ID
            member_id: 成员ID
            requester_id: 请求者ID
            limit: 限制数量
            offset: 偏移量
        
        Returns:
            点赞列表和统计信息
        """
        try:
            # 验证权限
            await self._validate_family_membership(family_id, requester_id)
            
            # 获取点赞列表
            likes = await self.interaction_repo.get_member_likes(
                member_id=member_id,
                family_id=family_id,
                limit=limit,
                offset=offset,
            )
            
            # 获取总点赞数
            total_likes = await self.interaction_repo._count_member_likes(member_id, family_id)
            
            return {
                "likes": likes,
                "total_count": total_likes,
                "member_id": member_id,
                "family_id": family_id,
            }
            
        except Exception as e:
            logger.error(f"获取成员点赞列表失败: {e}")
            raise

    # ============================================================================
    # 健康告警功能
    # ============================================================================

    async def get_family_health_alerts(
        self,
        family_id: str,
        requester_id: str,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        获取家庭健康告警列表
        
        Args:
            family_id: 家庭ID
            requester_id: 请求者ID
            status: 状态过滤
            severity: 严重程度过滤
            limit: 限制数量
            offset: 偏移量
        
        Returns:
            健康告警列表
        """
        try:
            # 验证家庭成员身份
            await self._validate_family_membership(family_id, requester_id)
            
            # 获取告警列表
            alerts = await self.interaction_repo.get_family_health_alerts(
                family_id=family_id,
                status=status,
                severity=severity,
                limit=limit,
                offset=offset,
            )
            
            # 按严重程度分类统计
            alert_stats = self._calculate_alert_statistics(alerts)
            
            return {
                "alerts": alerts,
                "total_count": len(alerts),
                "statistics": alert_stats,
                "family_id": family_id,
            }
            
        except Exception as e:
            logger.error(f"获取家庭健康告警失败: {e}")
            raise

    async def create_health_alert(
        self,
        family_id: str,
        member_id: str,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        recommendation: Optional[str] = None,
        trigger_value: Optional[float] = None,
        threshold_value: Optional[float] = None,
        metric_unit: Optional[str] = None,
    ) -> str:
        """
        创建健康告警
        
        Args:
            family_id: 家庭ID
            member_id: 成员ID
            alert_type: 告警类型
            severity: 严重程度
            title: 告警标题
            message: 告警消息
            recommendation: 建议
            trigger_value: 触发值
            threshold_value: 阈值
            metric_unit: 指标单位
        
        Returns:
            告警ID
        """
        try:
            # 验证告警类型
            if alert_type not in ALERT_CONSTANTS["ALERT_TYPES"]:
                raise ValueError(f"无效的告警类型: {alert_type}")
            
            # 验证严重程度
            valid_severities = ["low", "medium", "high", "critical"]
            if severity not in valid_severities:
                raise ValueError(f"无效的严重程度: {severity}")
            
            # 创建告警
            alert_id = await self.interaction_repo.create_health_alert(
                family_id=family_id,
                member_id=member_id,
                alert_type=alert_type,
                severity=severity,
                title=title,
                message=message,
                recommendation=recommendation,
                trigger_value=trigger_value,
                threshold_value=threshold_value,
                metric_unit=metric_unit,
            )
            
            # 记录家庭活动日志
            await self._log_family_activity(
                family_id=family_id,
                user_id=member_id,
                action="health_alert_created",
                details={
                    "alert_id": alert_id,
                    "alert_type": alert_type,
                    "severity": severity,
                    "title": title,
                }
            )
            
            logger.info(f"为成员 {member_id} 创建健康告警: {alert_type} ({severity})")
            return alert_id
            
        except Exception as e:
            logger.error(f"创建健康告警失败: {e}")
            raise

    async def acknowledge_health_alert(
        self,
        alert_id: str,
        acknowledger_id: str,
        family_id: str,
    ) -> bool:
        """
        确认健康告警
        
        Args:
            alert_id: 告警ID
            acknowledger_id: 确认者ID
            family_id: 家庭ID
        
        Returns:
            是否成功
        """
        try:
            # 验证家庭成员身份
            await self._validate_family_membership(family_id, acknowledger_id)
            
            # 确认告警
            success = await self.interaction_repo.acknowledge_alert(
                alert_id=alert_id,
                acknowledger_id=acknowledger_id,
            )
            
            if success:
                # 记录家庭活动日志
                await self._log_family_activity(
                    family_id=family_id,
                    user_id=acknowledger_id,
                    action="health_alert_acknowledged",
                    details={
                        "alert_id": alert_id,
                        "acknowledged_by": acknowledger_id,
                    }
                )
                
                logger.info(f"用户 {acknowledger_id} 确认了告警 {alert_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"确认健康告警失败: {e}")
            raise

    # ============================================================================
    # 自动健康监控
    # ============================================================================

    async def check_and_create_health_alerts(
        self,
        family_id: str,
        member_id: str,
        health_data: Dict[str, Any],
    ) -> List[str]:
        """
        检查健康数据并自动创建告警
        
        Args:
            family_id: 家庭ID
            member_id: 成员ID
            health_data: 健康数据
        
        Returns:
            创建的告警ID列表
        """
        try:
            created_alerts = []
            
            # 检查活动量告警
            if "daily_steps" in health_data:
                steps = health_data["daily_steps"]
                if steps < ALERT_CONSTANTS["LOW_ACTIVITY_ALERT_THRESHOLD"]:
                    alert_id = await self.create_health_alert(
                        family_id=family_id,
                        member_id=member_id,
                        alert_type="low_activity",
                        severity="medium",
                        title="活动量不足提醒",
                        message=f"今日步数仅{steps}步，低于建议标准",
                        recommendation="建议增加日常活动，如散步、爬楼梯等",
                        trigger_value=steps,
                        threshold_value=ALERT_CONSTANTS["LOW_ACTIVITY_ALERT_THRESHOLD"],
                        metric_unit="步",
                    )
                    created_alerts.append(alert_id)
            
            # 检查睡眠告警
            if "sleep_hours" in health_data:
                sleep_hours = health_data["sleep_hours"]
                if sleep_hours < ALERT_CONSTANTS["INSUFFICIENT_SLEEP_THRESHOLD"]:
                    alert_id = await self.create_health_alert(
                        family_id=family_id,
                        member_id=member_id,
                        alert_type="insufficient_sleep",
                        severity="medium",
                        title="睡眠不足提醒",
                        message=f"昨夜睡眠时长仅{sleep_hours:.1f}小时，低于建议标准",
                        recommendation="建议保证充足睡眠，调整作息时间",
                        trigger_value=sleep_hours,
                        threshold_value=ALERT_CONSTANTS["INSUFFICIENT_SLEEP_THRESHOLD"],
                        metric_unit="小时",
                    )
                    created_alerts.append(alert_id)
            
            # 检查体重变化告警
            if "weight_change" in health_data:
                weight_change = abs(health_data["weight_change"])
                if weight_change >= ALERT_CONSTANTS["SIGNIFICANT_WEIGHT_CHANGE"]:
                    severity = "high" if weight_change >= 2.0 else "medium"
                    alert_id = await self.create_health_alert(
                        family_id=family_id,
                        member_id=member_id,
                        alert_type="significant_weight_change",
                        severity=severity,
                        title="体重变化提醒",
                        message=f"近期体重变化{weight_change:.1f}kg，变化较大",
                        recommendation="建议关注饮食和运动习惯，必要时咨询医生",
                        trigger_value=weight_change,
                        threshold_value=ALERT_CONSTANTS["SIGNIFICANT_WEIGHT_CHANGE"],
                        metric_unit="kg",
                    )
                    created_alerts.append(alert_id)
            
            return created_alerts
            
        except Exception as e:
            logger.error(f"自动健康监控失败: {e}")
            return []

    # ============================================================================
    # 辅助方法
    # ============================================================================

    async def _validate_family_membership(self, family_id: str, user_id: str) -> None:
        """验证用户是否为家庭成员"""
        is_member = await self.family_repo.is_family_member(family_id, user_id)
        if not is_member:
            raise ValueError(f"用户 {user_id} 不是家庭 {family_id} 的成员")

    async def _log_family_activity(
        self,
        family_id: str,
        user_id: str,
        action: str,
        details: Dict[str, Any],
    ) -> None:
        """记录家庭活动日志"""
        try:
            # 获取用户信息
            user = await self.user_repo.get_user_by_id(user_id)
            username = user.username if user else "未知用户"
            
            # 记录活动日志
            await self.family_repo.log_family_activity(
                family_id=family_id,
                user_id=user_id,
                username=username,
                action=action,
                details=details,
            )
        except Exception as e:
            # 日志记录失败不应该影响主要功能
            logger.warning(f"记录家庭活动日志失败: {e}")

    def _calculate_alert_statistics(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算告警统计信息"""
        stats = {
            "total": len(alerts),
            "by_severity": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "by_status": {"active": 0, "acknowledged": 0, "resolved": 0, "dismissed": 0},
            "by_type": {},
        }
        
        for alert in alerts:
            # 按严重程度统计
            severity = alert.get("severity", "medium")
            if severity in stats["by_severity"]:
                stats["by_severity"][severity] += 1
            
            # 按状态统计
            status = alert.get("status", "active")
            if status in stats["by_status"]:
                stats["by_status"][status] += 1
            
            # 按类型统计
            alert_type = alert.get("alert_type", "unknown")
            stats["by_type"][alert_type] = stats["by_type"].get(alert_type, 0) + 1
        
        return stats
