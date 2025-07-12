"""
Prompt性能监控服务

负责记录、分析和优化Prompt性能，支持：
- 性能数据收集
- 用户反馈处理
- A/B测试管理
- 自动化性能分析
"""

import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from ..database.models import PromptPerformanceLogDB, PromptVersionDB
from ..database.connection import get_async_session

logger = logging.getLogger(__name__)


class PromptPerformanceService:
    """Prompt性能监控和分析服务"""
    
    def __init__(self):
        self.logger = logger
    
    async def log_prompt_usage(
        self,
        session_id: str,
        user_id: str,
        prompt_scenario: str,
        prompt_version: str,
        user_message: str,
        ai_response: str,
        response_time_ms: Optional[int] = None,
        tools_called: Optional[List[str]] = None,
        tool_call_success: Optional[bool] = None,
        user_context: Optional[Dict[str, Any]] = None,
        intent_detected: Optional[str] = None,
        intent_confidence: Optional[float] = None,
        conversation_turn: int = 1,
        ab_test_group: Optional[str] = None,
        error_occurred: bool = False,
        error_message: Optional[str] = None
    ) -> int:
        """
        记录Prompt使用日志
        
        Returns:
            log_id: 创建的日志记录ID
        """
        try:
            # 计算prompt内容hash
            prompt_content = f"{prompt_scenario}_{prompt_version}_{user_message[:100]}"
            prompt_hash = hashlib.md5(prompt_content.encode()).hexdigest()
            
            async with get_async_session() as session:
                log_entry = PromptPerformanceLogDB(
                    session_id=session_id,
                    user_id=user_id,
                    prompt_scenario=prompt_scenario,
                    prompt_version=prompt_version,
                    prompt_hash=prompt_hash,
                    user_message=user_message,
                    ai_response=ai_response,
                    response_time_ms=response_time_ms,
                    tools_called=tools_called or [],
                    tool_call_success=tool_call_success,
                    tool_call_count=len(tools_called) if tools_called else 0,
                    user_context=user_context or {},
                    conversation_turn=conversation_turn,
                    intent_detected=intent_detected,
                    intent_confidence=intent_confidence,
                    ab_test_group=ab_test_group,
                    error_occurred=error_occurred,
                    error_message=error_message,
                    created_at=datetime.utcnow()
                )
                
                session.add(log_entry)
                await session.commit()
                await session.refresh(log_entry)
                
                self.logger.info(f"Prompt usage logged: {log_entry.id} for scenario {prompt_scenario}_{prompt_version}")
                return log_entry.id
                
        except Exception as e:
            self.logger.error(f"Error logging prompt usage: {e}")
            raise
    
    async def update_user_feedback(
        self,
        log_id: int,
        user_rating: int,
        response_relevance: Optional[float] = None,
        response_helpfulness: Optional[float] = None,
        response_accuracy: Optional[float] = None
    ) -> bool:
        """
        更新用户反馈
        
        Args:
            log_id: 日志记录ID
            user_rating: 用户评分 (1-5)
            response_relevance: 响应相关性评分 (0-1)
            response_helpfulness: 响应有用性评分 (0-1)
            response_accuracy: 响应准确性评分 (0-1)
        """
        try:
            async with get_async_session() as session:
                # 查找日志记录
                stmt = select(PromptPerformanceLogDB).where(PromptPerformanceLogDB.id == log_id)
                result = await session.execute(stmt)
                log_entry = result.scalar_one_or_none()
                
                if not log_entry:
                    self.logger.warning(f"Prompt log not found: {log_id}")
                    return False
                
                # 更新反馈数据
                log_entry.user_rating = user_rating
                log_entry.response_relevance = response_relevance
                log_entry.response_helpfulness = response_helpfulness
                log_entry.response_accuracy = response_accuracy
                log_entry.feedback_updated_at = datetime.utcnow()
                
                await session.commit()
                
                self.logger.info(f"User feedback updated for log {log_id}: rating={user_rating}")
                
                # 异步更新版本统计
                await self._update_version_stats(log_entry.prompt_scenario, log_entry.prompt_version)
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating user feedback: {e}")
            return False
    
    async def get_performance_stats(
        self,
        scenario: str,
        version: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取性能统计数据
        
        Args:
            scenario: 场景名称
            version: 版本号（可选）
            days: 统计天数
        """
        try:
            async with get_async_session() as session:
                # 构建查询条件
                since_date = datetime.utcnow() - timedelta(days=days)
                conditions = [
                    PromptPerformanceLogDB.prompt_scenario == scenario,
                    PromptPerformanceLogDB.created_at >= since_date
                ]
                
                if version:
                    conditions.append(PromptPerformanceLogDB.prompt_version == version)
                
                # 基础统计查询
                stmt = select(
                    func.count(PromptPerformanceLogDB.id).label('total_uses'),
                    func.avg(PromptPerformanceLogDB.user_rating).label('avg_rating'),
                    func.avg(PromptPerformanceLogDB.response_relevance).label('avg_relevance'),
                    func.avg(PromptPerformanceLogDB.response_time_ms).label('avg_response_time'),
                    func.avg(PromptPerformanceLogDB.tool_call_success.cast(Float)).label('tool_success_rate'),
                    func.sum(PromptPerformanceLogDB.error_occurred.cast(Integer)).label('error_count')
                ).where(and_(*conditions))
                
                result = await session.execute(stmt)
                stats = result.first()
                
                # 计算错误率
                error_rate = (stats.error_count / stats.total_uses * 100) if stats.total_uses > 0 else 0
                
                return {
                    'scenario': scenario,
                    'version': version,
                    'period_days': days,
                    'total_uses': stats.total_uses or 0,
                    'average_rating': round(stats.avg_rating, 2) if stats.avg_rating else None,
                    'average_relevance': round(stats.avg_relevance, 3) if stats.avg_relevance else None,
                    'average_response_time_ms': round(stats.avg_response_time, 1) if stats.avg_response_time else None,
                    'tool_success_rate': round(stats.tool_success_rate, 3) if stats.tool_success_rate else None,
                    'error_rate_percent': round(error_rate, 2),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting performance stats: {e}")
            return {}
    
    async def compare_versions(
        self,
        scenario: str,
        version_a: str,
        version_b: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        比较两个版本的性能
        
        Args:
            scenario: 场景名称
            version_a: 版本A
            version_b: 版本B
            days: 比较天数
        """
        try:
            stats_a = await self.get_performance_stats(scenario, version_a, days)
            stats_b = await self.get_performance_stats(scenario, version_b, days)
            
            # 计算性能差异
            comparison = {
                'scenario': scenario,
                'version_a': version_a,
                'version_b': version_b,
                'period_days': days,
                'stats_a': stats_a,
                'stats_b': stats_b,
                'comparison': {}
            }
            
            # 比较关键指标
            metrics = ['average_rating', 'average_relevance', 'average_response_time_ms', 'tool_success_rate', 'error_rate_percent']
            
            for metric in metrics:
                val_a = stats_a.get(metric)
                val_b = stats_b.get(metric)
                
                if val_a is not None and val_b is not None:
                    diff = val_b - val_a
                    diff_percent = (diff / val_a * 100) if val_a != 0 else 0
                    
                    comparison['comparison'][metric] = {
                        'difference': round(diff, 3),
                        'difference_percent': round(diff_percent, 2),
                        'better_version': version_b if diff > 0 else version_a if diff < 0 else 'equal'
                    }
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Error comparing versions: {e}")
            return {}
    
    async def _update_version_stats(self, scenario: str, version: str):
        """更新版本统计数据（异步后台任务）"""
        try:
            stats = await self.get_performance_stats(scenario, version, days=30)
            
            async with get_async_session() as session:
                # 查找或创建版本记录
                stmt = select(PromptVersionDB).where(
                    and_(
                        PromptVersionDB.scenario == scenario,
                        PromptVersionDB.version == version
                    )
                )
                result = await session.execute(stmt)
                version_record = result.scalar_one_or_none()
                
                if version_record:
                    # 更新统计数据
                    version_record.total_uses = stats.get('total_uses', 0)
                    version_record.average_rating = stats.get('average_rating')
                    version_record.average_relevance = stats.get('average_relevance')
                    version_record.average_response_time = stats.get('average_response_time_ms')
                    version_record.tool_success_rate = stats.get('tool_success_rate')
                    version_record.error_rate = stats.get('error_rate_percent')
                    version_record.stats_updated_at = datetime.utcnow()
                    version_record.last_used_at = datetime.utcnow()
                    
                    await session.commit()
                    self.logger.debug(f"Updated stats for version {scenario}_{version}")
                
        except Exception as e:
            self.logger.error(f"Error updating version stats: {e}")


# 全局实例
prompt_performance_service = PromptPerformanceService()
