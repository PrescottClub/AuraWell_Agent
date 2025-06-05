"""
AuraWell 成就系统

追踪和奖励用户的健康活动里程碑，提供成就感和激励。

主要功能:
- 定义各类健康成就
- 追踪用户进度
- 自动解锁成就
- 成就历史记录
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import json

from ..utils.date_utils import get_current_utc
from ..config.logging_config import gamification_logger


class AchievementType(Enum):
    """成就类型"""
    DAILY_STEPS = "daily_steps"  # 每日步数
    WEEKLY_STEPS = "weekly_steps"  # 周步数
    MONTHLY_STEPS = "monthly_steps"  # 月步数
    CONSECUTIVE_DAYS = "consecutive_days"  # 连续天数
    SLEEP_QUALITY = "sleep_quality"  # 睡眠质量
    WORKOUT_FREQUENCY = "workout_frequency"  # 锻炼频率
    WEIGHT_LOSS = "weight_loss"  # 减重成就
    HEALTH_STREAK = "health_streak"  # 健康连击
    CALORIE_BURN = "calorie_burn"  # 卡路里消耗
    DISTANCE_COVERED = "distance_covered"  # 距离覆盖
    HEART_RATE_TARGET = "heart_rate_target"  # 心率目标
    SOCIAL_CHALLENGE = "social_challenge"  # 社交挑战


class AchievementDifficulty(Enum):
    """成就难度"""
    BRONZE = "bronze"
    SILVER = "silver" 
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


@dataclass
class Achievement:
    """成就数据模型"""
    achievement_id: str
    name: str
    description: str
    achievement_type: AchievementType
    difficulty: AchievementDifficulty
    target_value: float
    unit: str
    icon: str
    points: int
    unlocked: bool = False
    unlocked_date: Optional[datetime] = None
    progress: float = 0.0
    progress_description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "achievement_id": self.achievement_id,
            "name": self.name,
            "description": self.description,
            "achievement_type": self.achievement_type.value,
            "difficulty": self.difficulty.value,
            "target_value": self.target_value,
            "unit": self.unit,
            "icon": self.icon,
            "points": self.points,
            "unlocked": self.unlocked,
            "unlocked_date": self.unlocked_date.isoformat() if self.unlocked_date else None,
            "progress": self.progress,
            "progress_description": self.progress_description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Achievement":
        """从字典创建"""
        return cls(
            achievement_id=data["achievement_id"],
            name=data["name"],
            description=data["description"],
            achievement_type=AchievementType(data["achievement_type"]),
            difficulty=AchievementDifficulty(data["difficulty"]),
            target_value=data["target_value"],
            unit=data["unit"],
            icon=data["icon"],
            points=data["points"],
            unlocked=data.get("unlocked", False),
            unlocked_date=datetime.fromisoformat(data["unlocked_date"]) if data.get("unlocked_date") else None,
            progress=data.get("progress", 0.0),
            progress_description=data.get("progress_description", "")
        )


class AchievementManager:
    """成就管理器"""
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.user_achievements: Dict[str, Dict[str, Achievement]] = {}  # user_id -> achievements
        self._initialize_default_achievements()
        gamification_logger.info("AchievementManager初始化完成")
    
    def _initialize_default_achievements(self):
        """初始化默认成就"""
        default_achievements = [
            # 每日步数成就
            Achievement(
                "daily_steps_5k", "初级行者", "单日步数达到5,000步", 
                AchievementType.DAILY_STEPS, AchievementDifficulty.BRONZE, 5000, "步", "🚶", 10
            ),
            Achievement(
                "daily_steps_10k", "健步如飞", "单日步数达到10,000步",
                AchievementType.DAILY_STEPS, AchievementDifficulty.SILVER, 10000, "步", "🏃", 25
            ),
            Achievement(
                "daily_steps_15k", "超级行者", "单日步数达到15,000步",
                AchievementType.DAILY_STEPS, AchievementDifficulty.GOLD, 15000, "步", "🏃‍♂️", 50
            ),
            
            # 连续天数成就
            Achievement(
                "streak_7days", "坚持一周", "连续7天达到步数目标",
                AchievementType.CONSECUTIVE_DAYS, AchievementDifficulty.BRONZE, 7, "天", "📅", 20
            ),
            Achievement(
                "streak_30days", "月度冠军", "连续30天达到步数目标",
                AchievementType.CONSECUTIVE_DAYS, AchievementDifficulty.GOLD, 30, "天", "🏆", 100
            ),
            
            # 睡眠质量成就
            Achievement(
                "sleep_quality_80", "优质睡眠", "睡眠效率达到80%以上",
                AchievementType.SLEEP_QUALITY, AchievementDifficulty.SILVER, 80, "%", "😴", 30
            ),
            Achievement(
                "sleep_quality_90", "睡眠大师", "睡眠效率达到90%以上",
                AchievementType.SLEEP_QUALITY, AchievementDifficulty.GOLD, 90, "%", "🌙", 75
            ),
            
            # 锻炼频率成就
            Achievement(
                "workout_weekly_3", "运动新手", "一周内锻炼3次",
                AchievementType.WORKOUT_FREQUENCY, AchievementDifficulty.BRONZE, 3, "次/周", "💪", 15
            ),
            Achievement(
                "workout_weekly_5", "健身达人", "一周内锻炼5次",
                AchievementType.WORKOUT_FREQUENCY, AchievementDifficulty.SILVER, 5, "次/周", "🏋️", 40
            ),
            
            # 卡路里消耗成就
            Achievement(
                "calories_500", "燃脂小能手", "单日消耗500卡路里",
                AchievementType.CALORIE_BURN, AchievementDifficulty.BRONZE, 500, "千卡", "🔥", 20
            ),
            Achievement(
                "calories_1000", "燃脂大师", "单日消耗1000卡路里",
                AchievementType.CALORIE_BURN, AchievementDifficulty.GOLD, 1000, "千卡", "🌋", 60
            ),
            
            # 距离覆盖成就
            Achievement(
                "distance_5km", "五公里挑战", "单日行走/跑步5公里",
                AchievementType.DISTANCE_COVERED, AchievementDifficulty.SILVER, 5000, "米", "🗺️", 35
            ),
            Achievement(
                "distance_10km", "十公里英雄", "单日行走/跑步10公里",
                AchievementType.DISTANCE_COVERED, AchievementDifficulty.GOLD, 10000, "米", "🎯", 70
            )
        ]
        
        for achievement in default_achievements:
            self.achievements[achievement.achievement_id] = achievement
        
        gamification_logger.info(f"初始化了{len(default_achievements)}个默认成就")
    
    def get_user_achievements(self, user_id: str) -> Dict[str, Achievement]:
        """获取用户成就"""
        if user_id not in self.user_achievements:
            # 为新用户初始化成就副本
            self.user_achievements[user_id] = {}
            for achievement_id, achievement in self.achievements.items():
                user_achievement = Achievement(
                    achievement_id=achievement.achievement_id,
                    name=achievement.name,
                    description=achievement.description,
                    achievement_type=achievement.achievement_type,
                    difficulty=achievement.difficulty,
                    target_value=achievement.target_value,
                    unit=achievement.unit,
                    icon=achievement.icon,
                    points=achievement.points
                )
                self.user_achievements[user_id][achievement_id] = user_achievement
        
        return self.user_achievements[user_id]
    
    def update_progress(self, user_id: str, achievement_type: AchievementType, current_value: float) -> List[Achievement]:
        """更新成就进度，返回新解锁的成就"""
        user_achievements = self.get_user_achievements(user_id)
        newly_unlocked = []
        
        for achievement in user_achievements.values():
            if achievement.achievement_type == achievement_type and not achievement.unlocked:
                # 更新进度
                progress = min(current_value / achievement.target_value, 1.0)
                achievement.progress = progress
                achievement.progress_description = f"{current_value:.0f}/{achievement.target_value:.0f} {achievement.unit}"
                
                # 检查是否达到解锁条件
                if progress >= 1.0:
                    achievement.unlocked = True
                    achievement.unlocked_date = get_current_utc()
                    newly_unlocked.append(achievement)
                    
                    gamification_logger.info(
                        f"用户 {user_id} 解锁成就: {achievement.name}",
                        extra={
                            "user_id": user_id,
                            "achievement_id": achievement.achievement_id,
                            "achievement_type": achievement_type.value,
                            "points": achievement.points
                        }
                    )
        
        return newly_unlocked
    
    def get_unlocked_achievements(self, user_id: str) -> List[Achievement]:
        """获取已解锁的成就"""
        user_achievements = self.get_user_achievements(user_id)
        return [a for a in user_achievements.values() if a.unlocked]
    
    def get_locked_achievements(self, user_id: str) -> List[Achievement]:
        """获取未解锁的成就"""
        user_achievements = self.get_user_achievements(user_id)
        return [a for a in user_achievements.values() if not a.unlocked]
    
    def get_achievements_by_difficulty(self, user_id: str, difficulty: AchievementDifficulty) -> List[Achievement]:
        """按难度获取成就"""
        user_achievements = self.get_user_achievements(user_id)
        return [a for a in user_achievements.values() if a.difficulty == difficulty]
    
    def get_total_points(self, user_id: str) -> int:
        """获取用户总积分"""
        unlocked_achievements = self.get_unlocked_achievements(user_id)
        return sum(a.points for a in unlocked_achievements)
    
    def get_achievement_stats(self, user_id: str) -> Dict[str, Any]:
        """获取成就统计信息"""
        user_achievements = self.get_user_achievements(user_id)
        unlocked = self.get_unlocked_achievements(user_id)
        total_points = self.get_total_points(user_id)
        
        difficulty_counts = {}
        for difficulty in AchievementDifficulty:
            unlocked_count = len([a for a in unlocked if a.difficulty == difficulty])
            total_count = len([a for a in user_achievements.values() if a.difficulty == difficulty])
            difficulty_counts[difficulty.value] = {
                "unlocked": unlocked_count,
                "total": total_count
            }
        
        return {
            "total_achievements": len(user_achievements),
            "unlocked_achievements": len(unlocked),
            "unlock_percentage": len(unlocked) / len(user_achievements) * 100 if user_achievements else 0,
            "total_points": total_points,
            "difficulty_breakdown": difficulty_counts,
            "recent_achievements": [a.to_dict() for a in sorted(unlocked, key=lambda x: x.unlocked_date or datetime.min, reverse=True)[:5]]
        }
    
    def check_weekly_achievements(self, user_id: str, weekly_data: Dict[str, float]) -> List[Achievement]:
        """检查周度成就"""
        newly_unlocked = []
        
        # 检查周步数成就
        if "weekly_steps" in weekly_data:
            unlocked = self.update_progress(user_id, AchievementType.WEEKLY_STEPS, weekly_data["weekly_steps"])
            newly_unlocked.extend(unlocked)
        
        # 检查锻炼频率成就
        if "workout_count" in weekly_data:
            unlocked = self.update_progress(user_id, AchievementType.WORKOUT_FREQUENCY, weekly_data["workout_count"])
            newly_unlocked.extend(unlocked)
        
        return newly_unlocked
    
    def check_sleep_achievements(self, user_id: str, sleep_efficiency: float) -> List[Achievement]:
        """检查睡眠相关成就"""
        return self.update_progress(user_id, AchievementType.SLEEP_QUALITY, sleep_efficiency)
    
    def check_streak_achievements(self, user_id: str, current_streak: int) -> List[Achievement]:
        """检查连击成就"""
        return self.update_progress(user_id, AchievementType.CONSECUTIVE_DAYS, current_streak)
    
    def add_custom_achievement(self, achievement: Achievement):
        """添加自定义成就"""
        self.achievements[achievement.achievement_id] = achievement
        gamification_logger.info(f"添加自定义成就: {achievement.name} ({achievement.achievement_id})")
    
    def export_user_achievements(self, user_id: str) -> str:
        """导出用户成就数据为JSON"""
        user_achievements = self.get_user_achievements(user_id)
        data = {
            "user_id": user_id,
            "export_date": get_current_utc().isoformat(),
            "achievements": [a.to_dict() for a in user_achievements.values()]
        }
        return json.dumps(data, ensure_ascii=False, indent=2) 