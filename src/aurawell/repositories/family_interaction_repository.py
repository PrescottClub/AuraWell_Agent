"""
家庭交互功能仓库层

处理成员点赞、健康告警等家庭互动功能的数据库操作
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, and_, or_, desc, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database.family_interaction_models import (
    FamilyMemberLikeDB,
    FamilyHealthAlertDB,
    FamilyInteractionStatsDB,
)
from ..database.family_models import FamilyMemberDB
from ..database.models import UserProfileDB
from ..models.family_models import FamilyMember
from ..models.api_models import HealthAlert



class FamilyInteractionRepository:
    """家庭交互功能仓库"""

    def __init__(self, session: Session):
        self.session = session

    # ============================================================================
    # 成员点赞功能
    # ============================================================================

    async def like_member(
        self,
        family_id: str,
        liker_id: str,
        liked_member_id: str,
        like_type: str = "general",
        like_reason: Optional[str] = None,
        related_activity_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        为家庭成员点赞
        
        Args:
            family_id: 家庭ID
            liker_id: 点赞者ID
            liked_member_id: 被点赞成员ID
            like_type: 点赞类型
            like_reason: 点赞原因
            related_activity_id: 关联活动ID
        
        Returns:
            点赞结果信息
        """
        try:
            # 检查是否已经点赞过
            existing_like = await self._get_existing_like(
                family_id, liker_id, liked_member_id, like_type
            )
            
            if existing_like:
                if existing_like.is_active:
                    # 如果已经点赞，则取消点赞
                    existing_like.is_active = False
                    existing_like.updated_at = datetime.now(timezone.utc)
                    await self.session.commit()
                    
                    return {
                        "action": "unliked",
                        "like_id": existing_like.like_id,
                        "total_likes": await self._count_member_likes(liked_member_id, family_id),
                        "message": "取消点赞成功"
                    }
                else:
                    # 重新激活点赞
                    existing_like.is_active = True
                    existing_like.like_reason = like_reason
                    existing_like.related_activity_id = related_activity_id
                    existing_like.updated_at = datetime.now(timezone.utc)
                    await self.session.commit()
                    
                    return {
                        "action": "liked",
                        "like_id": existing_like.like_id,
                        "total_likes": await self._count_member_likes(liked_member_id, family_id),
                        "message": "点赞成功"
                    }
            else:
                # 创建新的点赞记录
                like_id = str(uuid.uuid4())
                new_like = FamilyMemberLikeDB(
                    like_id=like_id,
                    family_id=family_id,
                    liker_id=liker_id,
                    liked_member_id=liked_member_id,
                    like_type=like_type,
                    like_reason=like_reason,
                    related_activity_id=related_activity_id,
                    is_active=True,
                )
                
                self.session.add(new_like)
                await self.session.commit()
                
                # 更新互动统计
                await self._update_interaction_stats(liker_id, family_id, "like_given")
                await self._update_interaction_stats(liked_member_id, family_id, "like_received")
                
                return {
                    "action": "liked",
                    "like_id": like_id,
                    "total_likes": await self._count_member_likes(liked_member_id, family_id),
                    "message": "点赞成功"
                }
                
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"点赞操作失败: {str(e)}")

    async def get_member_likes(
        self,
        member_id: str,
        family_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取成员收到的点赞列表
        
        Args:
            member_id: 成员ID
            family_id: 家庭ID
            limit: 限制数量
            offset: 偏移量
        
        Returns:
            点赞列表
        """
        try:
            query = (
                select(FamilyMemberLikeDB, UserProfileDB.username)
                .join(UserProfileDB, FamilyMemberLikeDB.liker_id == UserProfileDB.user_id)
                .where(
                    and_(
                        FamilyMemberLikeDB.liked_member_id == member_id,
                        FamilyMemberLikeDB.family_id == family_id,
                        FamilyMemberLikeDB.is_active == True
                    )
                )
                .order_by(desc(FamilyMemberLikeDB.created_at))
                .limit(limit)
                .offset(offset)
            )
            
            result = await self.session.execute(query)
            likes_data = result.fetchall()
            
            likes = []
            for like_db, liker_username in likes_data:
                likes.append({
                    "like_id": like_db.like_id,
                    "liker_id": like_db.liker_id,
                    "liker_username": liker_username,
                    "like_type": like_db.like_type,
                    "like_reason": like_db.like_reason,
                    "related_activity_id": like_db.related_activity_id,
                    "created_at": like_db.created_at.isoformat(),
                })
            
            return likes
            
        except Exception as e:
            raise Exception(f"获取点赞列表失败: {str(e)}")

    async def _get_existing_like(
        self,
        family_id: str,
        liker_id: str,
        liked_member_id: str,
        like_type: str
    ) -> Optional[FamilyMemberLikeDB]:
        """获取已存在的点赞记录"""
        query = select(FamilyMemberLikeDB).where(
            and_(
                FamilyMemberLikeDB.family_id == family_id,
                FamilyMemberLikeDB.liker_id == liker_id,
                FamilyMemberLikeDB.liked_member_id == liked_member_id,
                FamilyMemberLikeDB.like_type == like_type
            )
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _count_member_likes(self, member_id: str, family_id: str) -> int:
        """统计成员收到的点赞总数"""
        query = select(func.count(FamilyMemberLikeDB.like_id)).where(
            and_(
                FamilyMemberLikeDB.liked_member_id == member_id,
                FamilyMemberLikeDB.family_id == family_id,
                FamilyMemberLikeDB.is_active == True
            )
        )
        
        result = await self.session.execute(query)
        return result.scalar() or 0

    # ============================================================================
    # 健康告警功能
    # ============================================================================

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
        alert_metadata: Optional[Dict[str, Any]] = None,
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
            alert_metadata: 告警元数据
        
        Returns:
            告警ID
        """
        try:
            alert_id = str(uuid.uuid4())
            
            new_alert = FamilyHealthAlertDB(
                alert_id=alert_id,
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
                alert_metadata=alert_metadata or {},
                status="active",
            )
            
            self.session.add(new_alert)
            await self.session.commit()
            
            # 更新互动统计
            await self._update_interaction_stats(member_id, family_id, "alert_triggered")
            
            return alert_id
            
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"创建健康告警失败: {str(e)}")

    async def get_family_health_alerts(
        self,
        family_id: str,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[HealthAlert]:
        """
        获取家庭健康告警列表
        
        Args:
            family_id: 家庭ID
            status: 告警状态过滤
            severity: 严重程度过滤
            limit: 限制数量
            offset: 偏移量
        
        Returns:
            健康告警列表
        """
        try:
            # 构建查询条件
            conditions = [FamilyHealthAlertDB.family_id == family_id]
            
            if status:
                conditions.append(FamilyHealthAlertDB.status == status)
            
            if severity:
                conditions.append(FamilyHealthAlertDB.severity == severity)
            
            # 执行查询
            query = (
                select(FamilyHealthAlertDB, UserProfileDB.username)
                .join(UserProfileDB, FamilyHealthAlertDB.member_id == UserProfileDB.user_id)
                .where(and_(*conditions))
                .order_by(desc(FamilyHealthAlertDB.created_at))
                .limit(limit)
                .offset(offset)
            )
            
            result = await self.session.execute(query)
            alerts_data = result.fetchall()
            
            alerts = []
            for alert_db, member_username in alerts_data:
                alert = HealthAlert(
                    alert_type=alert_db.alert_type,
                    severity=alert_db.severity,
                    member_id=alert_db.member_id,
                    message=alert_db.message,
                    recommendation=alert_db.recommendation or "请关注健康状况变化",
                )
                
                # 添加扩展信息
                alert_dict = alert.model_dump()
                alert_dict.update({
                    "alert_id": alert_db.alert_id,
                    "title": alert_db.title,
                    "member_username": member_username,
                    "trigger_value": alert_db.trigger_value,
                    "threshold_value": alert_db.threshold_value,
                    "metric_unit": alert_db.metric_unit,
                    "status": alert_db.status,
                    "created_at": alert_db.created_at.isoformat(),
                    "acknowledged_at": alert_db.acknowledged_at.isoformat() if alert_db.acknowledged_at else None,
                })
                
                alerts.append(alert_dict)
            
            return alerts
            
        except Exception as e:
            raise Exception(f"获取健康告警列表失败: {str(e)}")

    async def acknowledge_alert(
        self,
        alert_id: str,
        acknowledger_id: str
    ) -> bool:
        """
        确认健康告警
        
        Args:
            alert_id: 告警ID
            acknowledger_id: 确认者ID
        
        Returns:
            是否成功
        """
        try:
            query = (
                update(FamilyHealthAlertDB)
                .where(FamilyHealthAlertDB.alert_id == alert_id)
                .values(
                    status="acknowledged",
                    acknowledged_by=acknowledger_id,
                    acknowledged_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
            )
            
            result = await self.session.execute(query)
            await self.session.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"确认告警失败: {str(e)}")

    # ============================================================================
    # 互动统计功能
    # ============================================================================

    async def _update_interaction_stats(
        self,
        member_id: str,
        family_id: str,
        stat_type: str
    ) -> None:
        """更新互动统计"""
        try:
            today = datetime.now(timezone.utc).date()
            
            # 查找今日统计记录
            query = select(FamilyInteractionStatsDB).where(
                and_(
                    FamilyInteractionStatsDB.family_id == family_id,
                    FamilyInteractionStatsDB.member_id == member_id,
                    func.date(FamilyInteractionStatsDB.stats_date) == today,
                    FamilyInteractionStatsDB.stats_period == "daily"
                )
            )
            
            result = await self.session.execute(query)
            stats_record = result.scalar_one_or_none()
            
            if stats_record:
                # 更新现有记录
                if stat_type == "like_given":
                    stats_record.likes_given += 1
                elif stat_type == "like_received":
                    stats_record.likes_received += 1
                elif stat_type == "alert_triggered":
                    stats_record.alerts_triggered += 1
                elif stat_type == "alert_acknowledged":
                    stats_record.alerts_acknowledged += 1
                
                stats_record.family_interactions += 1
                stats_record.updated_at = datetime.now(timezone.utc)
            else:
                # 创建新记录
                stats_id = str(uuid.uuid4())
                stats_data = {
                    "likes_given": 1 if stat_type == "like_given" else 0,
                    "likes_received": 1 if stat_type == "like_received" else 0,
                    "alerts_triggered": 1 if stat_type == "alert_triggered" else 0,
                    "alerts_acknowledged": 1 if stat_type == "alert_acknowledged" else 0,
                    "family_interactions": 1,
                }
                
                new_stats = FamilyInteractionStatsDB(
                    stats_id=stats_id,
                    family_id=family_id,
                    member_id=member_id,
                    stats_date=datetime.now(timezone.utc),
                    stats_period="daily",
                    **stats_data
                )
                
                self.session.add(new_stats)
            
            await self.session.commit()
            
        except Exception as e:
            # 统计更新失败不应该影响主要功能
            pass
