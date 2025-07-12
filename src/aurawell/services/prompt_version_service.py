"""
Prompt版本管理服务

负责管理Prompt版本、A/B测试和自动版本选择，支持：
- 版本注册和管理
- A/B测试配置
- 性能驱动的版本选择
- 版本统计更新
"""

import logging
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update
from sqlalchemy.orm import selectinload

from ..database.models import PromptVersionDB, PromptPerformanceLogDB
from ..database.connection import get_async_session
from ..core.prompt_manager import prompt_manager

logger = logging.getLogger(__name__)


class PromptVersionService:
    """Prompt版本管理和A/B测试服务"""
    
    def __init__(self):
        self.logger = logger
        self._version_cache = {}  # 版本性能缓存
    
    async def register_prompt_version(
        self,
        scenario: str,
        version: str,
        name: str,
        description: Optional[str] = None,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_default: bool = False,
        is_experimental: bool = False
    ) -> int:
        """
        注册新的Prompt版本
        
        Args:
            scenario: 场景名称
            version: 版本号
            name: 版本名称
            description: 版本描述
            author: 作者
            tags: 标签列表
            is_default: 是否为默认版本
            is_experimental: 是否为实验版本
            
        Returns:
            version_id: 版本记录ID
        """
        try:
            # 计算版本内容hash
            version_content = f"{scenario}_{version}_{name}"
            version_hash = hashlib.md5(version_content.encode()).hexdigest()
            
            async with get_async_session() as session:
                # 检查版本是否已存在
                stmt = select(PromptVersionDB).where(
                    and_(
                        PromptVersionDB.scenario == scenario,
                        PromptVersionDB.version == version
                    )
                )
                existing = await session.execute(stmt)
                if existing.scalar_one_or_none():
                    self.logger.warning(f"Version {scenario}_{version} already exists")
                    return existing.scalar_one().id
                
                # 如果设置为默认版本，先取消其他默认版本
                if is_default:
                    await session.execute(
                        update(PromptVersionDB)
                        .where(
                            and_(
                                PromptVersionDB.scenario == scenario,
                                PromptVersionDB.is_default == True
                            )
                        )
                        .values(is_default=False)
                    )
                
                # 创建新版本记录
                version_record = PromptVersionDB(
                    scenario=scenario,
                    version=version,
                    version_hash=version_hash,
                    name=name,
                    description=description,
                    author=author,
                    tags=tags or [],
                    is_default=is_default,
                    is_experimental=is_experimental,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                session.add(version_record)
                await session.commit()
                await session.refresh(version_record)
                
                self.logger.info(f"Registered prompt version: {scenario}_{version}")
                return version_record.id
                
        except Exception as e:
            self.logger.error(f"Error registering prompt version: {e}")
            raise
    
    async def get_best_version(
        self,
        scenario: str,
        user_id: Optional[str] = None,
        enable_ab_testing: bool = True
    ) -> str:
        """
        获取最佳版本（支持A/B测试）
        
        Args:
            scenario: 场景名称
            user_id: 用户ID（用于A/B测试分组）
            enable_ab_testing: 是否启用A/B测试
            
        Returns:
            最佳版本号
        """
        try:
            async with get_async_session() as session:
                # 查询活跃版本
                stmt = select(PromptVersionDB).where(
                    and_(
                        PromptVersionDB.scenario == scenario,
                        PromptVersionDB.is_active == True
                    )
                ).order_by(PromptVersionDB.performance_score.desc().nulls_last())
                
                result = await session.execute(stmt)
                versions = result.scalars().all()
                
                if not versions:
                    self.logger.warning(f"No active versions found for scenario: {scenario}")
                    return "v3_1"  # 默认版本
                
                # 如果只有一个版本，直接返回
                if len(versions) == 1:
                    return versions[0].version
                
                # A/B测试逻辑
                if enable_ab_testing and user_id:
                    # 查找启用A/B测试的版本
                    ab_versions = [v for v in versions if v.ab_test_enabled]
                    
                    if ab_versions:
                        # 基于用户ID进行一致性分组
                        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
                        total_traffic = sum(v.ab_test_traffic_percentage for v in ab_versions)
                        
                        if total_traffic > 0:
                            # 计算用户应该分配到哪个版本
                            user_bucket = (user_hash % 100) + 1  # 1-100
                            cumulative_traffic = 0
                            
                            for version in ab_versions:
                                cumulative_traffic += version.ab_test_traffic_percentage
                                if user_bucket <= cumulative_traffic:
                                    self.logger.debug(f"A/B test: user {user_id} assigned to {version.version}")
                                    return version.version
                
                # 返回性能最佳的版本
                best_version = versions[0]
                return best_version.version
                
        except Exception as e:
            self.logger.error(f"Error getting best version: {e}")
            return "v3_1"  # 降级到默认版本
    
    async def setup_ab_test(
        self,
        scenario: str,
        version_a: str,
        version_b: str,
        traffic_split: Tuple[float, float] = (50.0, 50.0),
        duration_days: int = 7
    ) -> bool:
        """
        设置A/B测试
        
        Args:
            scenario: 场景名称
            version_a: 版本A
            version_b: 版本B
            traffic_split: 流量分配 (版本A%, 版本B%)
            duration_days: 测试持续天数
            
        Returns:
            是否设置成功
        """
        try:
            async with get_async_session() as session:
                start_date = datetime.utcnow()
                end_date = start_date + timedelta(days=duration_days)
                
                # 更新版本A
                await session.execute(
                    update(PromptVersionDB)
                    .where(
                        and_(
                            PromptVersionDB.scenario == scenario,
                            PromptVersionDB.version == version_a
                        )
                    )
                    .values(
                        ab_test_enabled=True,
                        ab_test_traffic_percentage=traffic_split[0],
                        ab_test_start_date=start_date,
                        ab_test_end_date=end_date,
                        updated_at=datetime.utcnow()
                    )
                )
                
                # 更新版本B
                await session.execute(
                    update(PromptVersionDB)
                    .where(
                        and_(
                            PromptVersionDB.scenario == scenario,
                            PromptVersionDB.version == version_b
                        )
                    )
                    .values(
                        ab_test_enabled=True,
                        ab_test_traffic_percentage=traffic_split[1],
                        ab_test_start_date=start_date,
                        ab_test_end_date=end_date,
                        updated_at=datetime.utcnow()
                    )
                )
                
                await session.commit()
                
                self.logger.info(f"A/B test setup: {scenario} {version_a}({traffic_split[0]}%) vs {version_b}({traffic_split[1]}%)")
                return True
                
        except Exception as e:
            self.logger.error(f"Error setting up A/B test: {e}")
            return False
    
    async def update_version_performance(
        self,
        scenario: str,
        version: str,
        performance_data: Dict[str, float]
    ) -> bool:
        """
        更新版本性能数据
        
        Args:
            scenario: 场景名称
            version: 版本号
            performance_data: 性能数据字典
            
        Returns:
            是否更新成功
        """
        try:
            async with get_async_session() as session:
                # 计算综合性能分数
                performance_score = self._calculate_performance_score(performance_data)
                
                await session.execute(
                    update(PromptVersionDB)
                    .where(
                        and_(
                            PromptVersionDB.scenario == scenario,
                            PromptVersionDB.version == version
                        )
                    )
                    .values(
                        total_uses=performance_data.get('total_uses', 0),
                        average_rating=performance_data.get('average_rating'),
                        average_relevance=performance_data.get('average_relevance'),
                        average_response_time=performance_data.get('average_response_time_ms'),
                        tool_success_rate=performance_data.get('tool_success_rate'),
                        error_rate=performance_data.get('error_rate_percent'),
                        performance_score=performance_score,
                        stats_updated_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                )
                
                await session.commit()
                
                # 更新缓存
                cache_key = f"{scenario}_{version}"
                self._version_cache[cache_key] = performance_data
                
                self.logger.debug(f"Updated performance for {scenario}_{version}: score={performance_score}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating version performance: {e}")
            return False
    
    def _calculate_performance_score(self, data: Dict[str, float]) -> float:
        """
        计算综合性能分数
        
        权重分配：
        - 用户评分: 40%
        - 响应相关性: 25%
        - 工具成功率: 20%
        - 响应时间: 10%
        - 错误率: 5%
        """
        try:
            score = 0.0
            
            # 用户评分 (1-5 -> 0-1)
            if data.get('average_rating'):
                score += (data['average_rating'] / 5.0) * 0.4
            
            # 响应相关性 (0-1)
            if data.get('average_relevance'):
                score += data['average_relevance'] * 0.25
            
            # 工具成功率 (0-1)
            if data.get('tool_success_rate'):
                score += data['tool_success_rate'] * 0.2
            
            # 响应时间 (越低越好，2秒为基准)
            if data.get('average_response_time_ms'):
                time_score = max(0, 1 - (data['average_response_time_ms'] / 2000))
                score += time_score * 0.1
            
            # 错误率 (越低越好)
            if data.get('error_rate_percent') is not None:
                error_score = max(0, 1 - (data['error_rate_percent'] / 100))
                score += error_score * 0.05
            
            return round(score, 3)
            
        except Exception as e:
            self.logger.error(f"Error calculating performance score: {e}")
            return 0.0


# 全局实例
prompt_version_service = PromptVersionService()
