"""
家庭仪表盘服务
管理家庭排行榜和挑战赛功能
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import logging

from ..core.exceptions import AurawellException, ValidationError, BusinessLogicError

logger = logging.getLogger(__name__)


class FamilyDashboardService:
    """家庭仪表盘服务类"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def get_leaderboard(
        self, metric: str, period: str, family_id: str = None
    ) -> Dict[str, Any]:
        """
        获取家庭排行榜

        Args:
            metric: 排行榜指标 (steps, calories, sleep_quality, weight_loss)
            period: 时间周期 (daily, weekly, monthly)
            family_id: 家庭ID（可选）

        Returns:
            排行榜数据字典

        Raises:
            ValidationError: If invalid metric or period
            BusinessLogicError: If leaderboard generation fails
        """
        try:
            # Validate inputs
            valid_metrics = ["steps", "calories", "sleep_quality", "weight_loss"]
            valid_periods = ["daily", "weekly", "monthly"]

            if metric not in valid_metrics:
                raise ValidationError(
                    f"Invalid metric: {metric}. Valid options: {valid_metrics}",
                    field="metric",
                )

            if period not in valid_periods:
                raise ValidationError(
                    f"Invalid period: {period}. Valid options: {valid_periods}",
                    field="period",
                )

            self.logger.info(
                f"Getting leaderboard for metric: {metric}, period: {period}"
            )

            # 模拟获取排行榜数据
            leaderboard_data = await self._calculate_leaderboard(
                metric, period, family_id
            )

            return {
                "leaderboard_id": f"lb_{metric}_{period}_{datetime.now().strftime('%Y%m%d')}",
                "metric": metric,
                "period": period,
                "family_id": family_id,
                "generated_at": datetime.now().isoformat(),
                "rankings": leaderboard_data["rankings"],
                "statistics": leaderboard_data["statistics"],
                "metadata": {
                    "total_participants": len(leaderboard_data["rankings"]),
                    "metric_unit": self._get_metric_unit(metric),
                    "update_frequency": "real-time",
                },
            }

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to get leaderboard: {e}")
            raise BusinessLogicError(f"Failed to generate leaderboard: {str(e)}")

    async def get_challenges(self, family_id: str) -> Dict[str, Any]:
        """
        获取家庭挑战赛

        Args:
            family_id: 家庭ID

        Returns:
            挑战赛数据字典
        """
        try:
            self.logger.info(f"Getting challenges for family: {family_id}")

            # 模拟获取挑战赛数据
            challenges_data = await self._get_family_challenges(family_id)

            return {
                "family_id": family_id,
                "retrieved_at": datetime.now().isoformat(),
                "active_challenges": challenges_data["active"],
                "completed_challenges": challenges_data["completed"],
                "upcoming_challenges": challenges_data["upcoming"],
                "challenge_summary": {
                    "total_active": len(challenges_data["active"]),
                    "total_completed": len(challenges_data["completed"]),
                    "total_upcoming": len(challenges_data["upcoming"]),
                    "family_points": challenges_data["family_points"],
                    "family_rank": challenges_data["family_rank"],
                },
            }

        except Exception as e:
            self.logger.error(f"Failed to get challenges: {e}")
            raise

    async def create_challenge(
        self, family_id: str, challenge_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建新的家庭挑战赛

        Args:
            family_id: 家庭ID
            challenge_data: 挑战赛数据

        Returns:
            创建的挑战赛信息
        """
        try:
            self.logger.info(f"Creating challenge for family: {family_id}")

            # 生成挑战赛ID
            challenge_id = (
                f"challenge_{family_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # 处理挑战赛数据
            challenge = {
                "challenge_id": challenge_id,
                "family_id": family_id,
                "title": challenge_data.get("title", "新的家庭挑战"),
                "description": challenge_data.get("description", ""),
                "challenge_type": challenge_data.get("challenge_type", "activity"),
                "target_metric": challenge_data.get("target_metric", "steps"),
                "target_value": challenge_data.get("target_value", 10000),
                "duration_days": challenge_data.get("duration_days", 7),
                "start_date": challenge_data.get(
                    "start_date", datetime.now().date().isoformat()
                ),
                "end_date": self._calculate_end_date(
                    challenge_data.get("start_date", datetime.now().date().isoformat()),
                    challenge_data.get("duration_days", 7),
                ),
                "participants": challenge_data.get("participants", []),
                "rewards": challenge_data.get("rewards", []),
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "created_by": challenge_data.get("created_by", "system"),
                "progress": {
                    "completion_percentage": 0.0,
                    "participants_joined": len(challenge_data.get("participants", [])),
                    "current_leader": None,
                },
            }

            self.logger.info(f"Challenge created successfully: {challenge_id}")
            return challenge

        except Exception as e:
            self.logger.error(f"Failed to create challenge: {e}")
            raise

    async def _calculate_leaderboard(
        self, metric: str, period: str, family_id: str = None
    ) -> Dict[str, Any]:
        """计算排行榜数据"""

        # 模拟成员数据
        mock_members = [
            {"user_id": "user_001", "name": "张小明", "avatar": "avatar1.jpg"},
            {"user_id": "user_002", "name": "李小红", "avatar": "avatar2.jpg"},
            {"user_id": "user_003", "name": "王小刚", "avatar": "avatar3.jpg"},
            {"user_id": "user_004", "name": "刘小美", "avatar": "avatar4.jpg"},
        ]

        # 根据指标类型生成排行榜数据
        rankings = []
        metric_values = self._generate_metric_values(metric, len(mock_members))

        for i, member in enumerate(mock_members):
            ranking = {
                "rank": i + 1,
                "user_id": member["user_id"],
                "name": member["name"],
                "avatar": member["avatar"],
                "value": metric_values[i],
                "percentage": round((metric_values[i] / max(metric_values)) * 100, 1),
                "change_from_last_period": self._calculate_change(i),
                "streak_days": 5 + i,
                "badges": self._get_member_badges(i, metric),
            }
            rankings.append(ranking)

        # 按值排序
        rankings.sort(key=lambda x: x["value"], reverse=True)

        # 更新排名
        for i, ranking in enumerate(rankings):
            ranking["rank"] = i + 1

        statistics = {
            "average_value": sum(metric_values) / len(metric_values),
            "highest_value": max(metric_values),
            "lowest_value": min(metric_values),
            "total_participants": len(mock_members),
            "period_start": self._get_period_start(period),
            "period_end": datetime.now().date().isoformat(),
        }

        return {"rankings": rankings, "statistics": statistics}

    async def _get_family_challenges(self, family_id: str) -> Dict[str, Any]:
        """获取家庭挑战赛数据"""
        # 模拟挑战赛数据
        active_challenges = [
            {
                "challenge_id": "challenge_001",
                "title": "每日万步挑战",
                "description": "连续7天每天走10000步",
                "challenge_type": "activity",
                "target_metric": "steps",
                "target_value": 10000,
                "start_date": "2024-01-15",
                "end_date": "2024-01-21",
                "progress": {
                    "completion_percentage": 65.5,
                    "participants_completed": 2,
                    "total_participants": 4,
                    "current_leader": "user_001",
                    "days_remaining": 3,
                },
                "participants": [
                    {"user_id": "user_001", "progress": 85.0, "completed": False},
                    {"user_id": "user_002", "progress": 72.5, "completed": False},
                    {"user_id": "user_003", "progress": 45.0, "completed": False},
                    {"user_id": "user_004", "progress": 58.0, "completed": False},
                ],
                "status": "active",
            }
        ]

        completed_challenges = [
            {
                "challenge_id": "challenge_002",
                "title": "睡眠质量提升挑战",
                "description": "连续14天保证8小时睡眠",
                "challenge_type": "sleep",
                "target_metric": "sleep_hours",
                "target_value": 8.0,
                "completed_date": "2024-01-10",
                "results": {
                    "winner": "user_002",
                    "completion_rate": 75,
                    "total_participants": 4,
                },
            }
        ]

        upcoming_challenges = [
            {
                "challenge_id": "challenge_003",
                "title": "健康饮食挑战",
                "description": "连续30天健康饮食计划",
                "challenge_type": "nutrition",
                "target_metric": "healthy_meals",
                "target_value": 90,
                "start_date": "2024-02-01",
                "end_date": "2024-03-02",
                "participants_registered": 3,
            }
        ]

        return {
            "active": active_challenges,
            "completed": completed_challenges,
            "upcoming": upcoming_challenges,
            "family_points": 1250,
            "family_rank": 3,
        }

    def _generate_metric_values(self, metric: str, count: int) -> List[float]:
        """根据指标类型生成模拟数值"""
        base_values = {
            "steps": [9500, 8200, 7800, 6500],
            "calories": [2200, 1950, 1800, 1650],
            "sleep_quality": [88.5, 82.3, 79.1, 75.8],
            "weight_loss": [2.1, 1.8, 1.2, 0.9],
        }

        return base_values.get(metric, [100, 90, 80, 70])[:count]

    def _calculate_change(self, index: int) -> float:
        """计算相比上一周期的变化"""
        changes = [5.2, -2.1, 8.7, -0.5]
        return changes[index % len(changes)]

    def _get_member_badges(self, index: int, metric: str) -> List[str]:
        """获取成员徽章"""
        all_badges = [
            ["streak_master", "top_performer"],
            ["consistent_improver"],
            ["rising_star", "newcomer"],
            ["effort_champion"],
        ]
        return all_badges[index % len(all_badges)]

    def _get_metric_unit(self, metric: str) -> str:
        """获取指标单位"""
        units = {
            "steps": "步",
            "calories": "卡路里",
            "sleep_quality": "分",
            "weight_loss": "公斤",
        }
        return units.get(metric, "单位")

    def _get_period_start(self, period: str) -> str:
        """获取周期开始日期"""
        today = datetime.now().date()
        if period == "daily":
            return today.isoformat()
        elif period == "weekly":
            return (today - timedelta(days=today.weekday())).isoformat()
        elif period == "monthly":
            return today.replace(day=1).isoformat()
        else:
            return today.isoformat()

    def _calculate_end_date(self, start_date: str, duration_days: int) -> str:
        """计算结束日期"""
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = start + timedelta(days=duration_days)
        return end.isoformat()
