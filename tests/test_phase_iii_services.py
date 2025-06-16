"""
Phase III 服务测试
测试健康报告服务和家庭仪表盘服务
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, date, timedelta
import sys
import os

# Add the src directory to Python path for new structure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aurawell.services.report_service import HealthReportService
from aurawell.services.dashboard_service import FamilyDashboardService
from aurawell.core.exceptions import ValidationError


class TestHealthReportService:
    """健康报告服务测试"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = HealthReportService()
    
    @pytest.mark.asyncio
    async def test_generate_report_success(self):
        """测试成功生成健康报告"""
        members = ["user_001", "user_002"]
        start_date = "2024-01-01"
        end_date = "2024-01-07"
        
        result = await self.service.generate_report(members, start_date, end_date)
        
        assert result is not None
        assert "report_id" in result
        assert "generation_time" in result
        assert "members" in result
        assert result["members"] == members
        assert result["member_count"] == len(members)
        assert "summary" in result
        assert "trends" in result
        assert "alerts" in result
        assert "aggregated_data" in result
    
    @pytest.mark.asyncio
    async def test_generate_report_invalid_dates(self):
        """测试无效日期参数"""
        members = ["user_001"]
        start_date = "2024-01-07"  # 开始日期晚于结束日期
        end_date = "2024-01-01"
        
        with pytest.raises(ValidationError) as excinfo:
            await self.service.generate_report(members, start_date, end_date)

        assert "Invalid date range" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_generate_report_empty_members(self):
        """测试空成员列表"""
        members = []
        start_date = "2024-01-01"
        end_date = "2024-01-07"
        
        with pytest.raises(ValidationError) as excinfo:
            await self.service.generate_report(members, start_date, end_date)

        assert "At least one member required" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_generate_report_too_many_members(self):
        """测试成员数量过多"""
        members = [f"user_{i:03d}" for i in range(15)]  # 15个成员，超过限制
        start_date = "2024-01-01"
        end_date = "2024-01-07"
        
        with pytest.raises(ValidationError) as excinfo:
            await self.service.generate_report(members, start_date, end_date)

        assert "Maximum 10 members allowed" in str(excinfo.value)


class TestFamilyDashboardService:
    """家庭仪表盘服务测试"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = FamilyDashboardService()
    
    @pytest.mark.asyncio
    async def test_get_leaderboard_success(self):
        """测试成功获取排行榜"""
        metric = "steps"
        period = "weekly"
        family_id = "family_001"
        
        result = await self.service.get_leaderboard(metric, period, family_id)
        
        assert result is not None
        assert result["metric"] == metric
        assert result["period"] == period
        assert result["family_id"] == family_id
        assert "rankings" in result
        assert "statistics" in result
        assert "metadata" in result
        
        # 检查排行榜结构
        rankings = result["rankings"]
        assert len(rankings) > 0
        
        for ranking in rankings:
            assert "rank" in ranking
            assert "user_id" in ranking
            assert "name" in ranking
            assert "value" in ranking
            assert "percentage" in ranking
    
    @pytest.mark.asyncio
    async def test_get_leaderboard_different_metrics(self):
        """测试不同指标的排行榜"""
        metrics = ["steps", "calories", "sleep_quality", "weight_loss"]
        period = "daily"
        family_id = "family_001"
        
        for metric in metrics:
            result = await self.service.get_leaderboard(metric, period, family_id)
            assert result["metric"] == metric
            assert len(result["rankings"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_challenges_success(self):
        """测试成功获取挑战赛"""
        family_id = "family_001"
        
        result = await self.service.get_challenges(family_id)
        
        assert result is not None
        assert result["family_id"] == family_id
        assert "active_challenges" in result
        assert "completed_challenges" in result
        assert "upcoming_challenges" in result
        assert "challenge_summary" in result
        
        # 检查挑战赛摘要
        summary = result["challenge_summary"]
        assert "total_active" in summary
        assert "total_completed" in summary
        assert "total_upcoming" in summary
        assert "family_points" in summary
        assert "family_rank" in summary
    
    @pytest.mark.asyncio
    async def test_create_challenge_success(self):
        """测试成功创建挑战赛"""
        family_id = "family_001"
        challenge_data = {
            "title": "测试挑战",
            "description": "这是一个测试挑战",
            "challenge_type": "activity",
            "target_metric": "steps",
            "target_value": 10000,
            "duration_days": 7,
            "participants": ["user_001", "user_002"],
            "rewards": ["健康徽章"],
            "created_by": "user_001"
        }
        
        result = await self.service.create_challenge(family_id, challenge_data)
        
        assert result is not None
        assert result["family_id"] == family_id
        assert result["title"] == challenge_data["title"]
        assert result["description"] == challenge_data["description"]
        assert result["challenge_type"] == challenge_data["challenge_type"]
        assert result["target_metric"] == challenge_data["target_metric"]
        assert result["target_value"] == challenge_data["target_value"]
        assert result["duration_days"] == challenge_data["duration_days"]
        assert result["participants"] == challenge_data["participants"]
        assert result["rewards"] == challenge_data["rewards"]
        assert result["created_by"] == challenge_data["created_by"]
        assert result["status"] == "active"
        assert "challenge_id" in result
        assert "start_date" in result
        assert "end_date" in result
        assert "created_at" in result
    
    @pytest.mark.asyncio
    async def test_create_challenge_default_values(self):
        """测试使用默认值创建挑战赛"""
        family_id = "family_001"
        challenge_data = {
            "title": "简单挑战",
            "description": "简单测试",
            "challenge_type": "activity",
            "target_metric": "steps",
            "target_value": 5000
        }
        
        result = await self.service.create_challenge(family_id, challenge_data)
        
        # 检查默认值是否被正确应用
        assert result["duration_days"] == 7  # 默认7天
        assert result["participants"] == []  # 默认空列表
        assert result["rewards"] == []  # 默认空列表
        assert result["status"] == "active"
    
    def test_generate_metric_values(self):
        """测试指标值生成"""
        metric = "steps"
        count = 4
        
        values = self.service._generate_metric_values(metric, count)
        
        assert len(values) == count
        assert all(isinstance(v, (int, float)) for v in values)
        assert all(v > 0 for v in values)  # 所有值都应该是正数
    
    def test_get_metric_unit(self):
        """测试指标单位获取"""
        assert self.service._get_metric_unit("steps") == "步"
        assert self.service._get_metric_unit("calories") == "卡路里"
        assert self.service._get_metric_unit("sleep_quality") == "分"
        assert self.service._get_metric_unit("weight_loss") == "公斤"
        assert self.service._get_metric_unit("unknown_metric") == "单位"
    
    def test_get_period_start(self):
        """测试周期开始日期计算"""
        # 测试每日周期
        daily_start = self.service._get_period_start("daily")
        expected_daily = datetime.now().date().isoformat()
        assert daily_start == expected_daily
        
        # 测试每周周期
        weekly_start = self.service._get_period_start("weekly")
        today = datetime.now().date()
        expected_weekly = (today - timedelta(days=today.weekday())).isoformat()
        assert weekly_start == expected_weekly
        
        # 测试每月周期
        monthly_start = self.service._get_period_start("monthly")
        today = datetime.now().date()
        expected_monthly = today.replace(day=1).isoformat()
        assert monthly_start == expected_monthly
    
    def test_calculate_end_date(self):
        """测试结束日期计算"""
        start_date = "2024-01-15"
        duration_days = 7
        
        end_date = self.service._calculate_end_date(start_date, duration_days)
        
        assert end_date == "2024-01-22"


if __name__ == "__main__":
    pytest.main([__file__]) 