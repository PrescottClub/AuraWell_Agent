"""
Health Plan Repository

Provides data access operations for health plans, modules, progress, and feedback.
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, asc, update, delete
from sqlalchemy.orm import selectinload
import uuid

from .base import BaseRepository
from ..database.models import (
    HealthPlanDB, HealthPlanModuleDB, HealthPlanProgressDB, 
    HealthPlanFeedbackDB, HealthPlanTemplateDB
)


class HealthPlanRepository(BaseRepository[HealthPlanDB]):
    """Repository for health plan operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, HealthPlanDB)
        self.plan_repo = BaseRepository[HealthPlanDB](session, HealthPlanDB)
        self.module_repo = BaseRepository[HealthPlanModuleDB](session, HealthPlanModuleDB)
        self.progress_repo = BaseRepository[HealthPlanProgressDB](session, HealthPlanProgressDB)
        self.feedback_repo = BaseRepository[HealthPlanFeedbackDB](session, HealthPlanFeedbackDB)
        self.template_repo = BaseRepository[HealthPlanTemplateDB](session, HealthPlanTemplateDB)
    
    # Health Plan CRUD Operations
    async def create_health_plan(self, user_id: str, plan_data: Dict[str, Any]) -> HealthPlanDB:
        """Create a new health plan"""
        # Generate unique ID if not provided
        if "id" not in plan_data:
            plan_data["id"] = f"plan_{user_id}_{uuid.uuid4().hex[:8]}"

        plan_data["user_id"] = user_id
        plan_data["created_at"] = datetime.utcnow()
        plan_data["updated_at"] = datetime.utcnow()
        return await self.plan_repo.create(**plan_data)
    
    async def get_health_plan_by_id(self, plan_id: str, user_id: str) -> Optional[HealthPlanDB]:
        """Get health plan by ID with user verification"""
        stmt = select(HealthPlanDB).where(
            and_(
                HealthPlanDB.id == plan_id,
                HealthPlanDB.user_id == user_id
            )
        ).options(
            selectinload(HealthPlanDB.modules),
            selectinload(HealthPlanDB.progress_records),
            selectinload(HealthPlanDB.feedback_records)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_health_plans(
        self, 
        user_id: str, 
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[HealthPlanDB]:
        """Get user's health plans with optional filtering"""
        stmt = select(HealthPlanDB).where(HealthPlanDB.user_id == user_id)
        
        if status:
            stmt = stmt.where(HealthPlanDB.status == status)
        
        stmt = stmt.options(selectinload(HealthPlanDB.modules))
        stmt = stmt.order_by(desc(HealthPlanDB.created_at))
        
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_health_plan(self, plan_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[HealthPlanDB]:
        """Update health plan"""
        update_data["updated_at"] = datetime.utcnow()
        
        stmt = update(HealthPlanDB).where(
            and_(
                HealthPlanDB.id == plan_id,
                HealthPlanDB.user_id == user_id
            )
        ).values(**update_data).returning(HealthPlanDB)
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()
    
    async def delete_health_plan(self, plan_id: str, user_id: str) -> bool:
        """Delete health plan"""
        stmt = delete(HealthPlanDB).where(
            and_(
                HealthPlanDB.id == plan_id,
                HealthPlanDB.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    # Health Plan Module Operations
    async def create_plan_module(self, plan_id: str, module_data: Dict[str, Any]) -> HealthPlanModuleDB:
        """Create a plan module"""
        # Generate unique ID if not provided
        if "id" not in module_data:
            module_data["id"] = f"module_{plan_id}_{uuid.uuid4().hex[:8]}"

        module_data["plan_id"] = plan_id
        module_data["created_at"] = datetime.utcnow()
        module_data["updated_at"] = datetime.utcnow()
        return await self.module_repo.create(**module_data)
    
    async def get_plan_modules(self, plan_id: str) -> List[HealthPlanModuleDB]:
        """Get all modules for a plan"""
        stmt = select(HealthPlanModuleDB).where(
            HealthPlanModuleDB.plan_id == plan_id
        ).order_by(HealthPlanModuleDB.order_index)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_plan_module(self, module_id: str, update_data: Dict[str, Any]) -> Optional[HealthPlanModuleDB]:
        """Update plan module"""
        update_data["updated_at"] = datetime.utcnow()
        
        stmt = update(HealthPlanModuleDB).where(
            HealthPlanModuleDB.id == module_id
        ).values(**update_data).returning(HealthPlanModuleDB)
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()
    
    # Progress Tracking Operations
    async def create_progress_record(self, plan_id: str, progress_data: Dict[str, Any]) -> HealthPlanProgressDB:
        """Create a progress record"""
        # Generate unique ID if not provided
        if "id" not in progress_data:
            progress_data["id"] = f"progress_{plan_id}_{uuid.uuid4().hex[:8]}"

        progress_data["plan_id"] = plan_id
        progress_data["created_at"] = datetime.utcnow()
        return await self.progress_repo.create(**progress_data)
    
    async def get_plan_progress(
        self, 
        plan_id: str, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        module_type: Optional[str] = None
    ) -> List[HealthPlanProgressDB]:
        """Get progress records for a plan"""
        stmt = select(HealthPlanProgressDB).where(HealthPlanProgressDB.plan_id == plan_id)
        
        if start_date:
            stmt = stmt.where(HealthPlanProgressDB.date >= start_date)
        if end_date:
            stmt = stmt.where(HealthPlanProgressDB.date <= end_date)
        if module_type:
            stmt = stmt.where(HealthPlanProgressDB.module_type == module_type)
        
        stmt = stmt.order_by(desc(HealthPlanProgressDB.date))
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_latest_progress(self, plan_id: str, module_type: Optional[str] = None) -> Optional[HealthPlanProgressDB]:
        """Get latest progress record"""
        stmt = select(HealthPlanProgressDB).where(HealthPlanProgressDB.plan_id == plan_id)
        
        if module_type:
            stmt = stmt.where(HealthPlanProgressDB.module_type == module_type)
        
        stmt = stmt.order_by(desc(HealthPlanProgressDB.date)).limit(1)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    # Feedback Operations
    async def create_feedback(self, plan_id: str, feedback_data: Dict[str, Any]) -> HealthPlanFeedbackDB:
        """Create feedback record"""
        # Generate unique ID if not provided
        if "id" not in feedback_data:
            feedback_data["id"] = f"feedback_{plan_id}_{uuid.uuid4().hex[:8]}"

        feedback_data["plan_id"] = plan_id
        feedback_data["created_at"] = datetime.utcnow()
        feedback_data["updated_at"] = datetime.utcnow()
        return await self.feedback_repo.create(**feedback_data)
    
    async def get_plan_feedback(
        self, 
        plan_id: str,
        feedback_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[HealthPlanFeedbackDB]:
        """Get feedback records for a plan"""
        stmt = select(HealthPlanFeedbackDB).where(HealthPlanFeedbackDB.plan_id == plan_id)
        
        if feedback_type:
            stmt = stmt.where(HealthPlanFeedbackDB.feedback_type == feedback_type)
        if status:
            stmt = stmt.where(HealthPlanFeedbackDB.status == status)
        
        stmt = stmt.order_by(desc(HealthPlanFeedbackDB.created_at))
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    # Template Operations
    async def get_plan_templates(
        self, 
        category: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        is_active: bool = True
    ) -> List[HealthPlanTemplateDB]:
        """Get plan templates"""
        stmt = select(HealthPlanTemplateDB).where(HealthPlanTemplateDB.is_active == is_active)
        
        if category:
            stmt = stmt.where(HealthPlanTemplateDB.category == category)
        if difficulty_level:
            stmt = stmt.where(HealthPlanTemplateDB.difficulty_level == difficulty_level)
        
        stmt = stmt.order_by(desc(HealthPlanTemplateDB.usage_count))
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_template_by_id(self, template_id: str) -> Optional[HealthPlanTemplateDB]:
        """Get template by ID"""
        return await self.template_repo.get_by_id(template_id)
    
    async def increment_template_usage(self, template_id: str) -> None:
        """Increment template usage count"""
        stmt = update(HealthPlanTemplateDB).where(
            HealthPlanTemplateDB.id == template_id
        ).values(
            usage_count=HealthPlanTemplateDB.usage_count + 1,
            updated_at=datetime.utcnow()
        )
        await self.session.execute(stmt)
        await self.session.commit()
    
    # Statistics and Analytics
    async def get_plan_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user's plan statistics"""
        # Total plans
        total_plans_stmt = select(func.count(HealthPlanDB.id)).where(HealthPlanDB.user_id == user_id)
        total_plans_result = await self.session.execute(total_plans_stmt)
        total_plans = total_plans_result.scalar() or 0
        
        # Active plans
        active_plans_stmt = select(func.count(HealthPlanDB.id)).where(
            and_(HealthPlanDB.user_id == user_id, HealthPlanDB.status == "active")
        )
        active_plans_result = await self.session.execute(active_plans_stmt)
        active_plans = active_plans_result.scalar() or 0
        
        # Completed plans
        completed_plans_stmt = select(func.count(HealthPlanDB.id)).where(
            and_(HealthPlanDB.user_id == user_id, HealthPlanDB.status == "completed")
        )
        completed_plans_result = await self.session.execute(completed_plans_stmt)
        completed_plans = completed_plans_result.scalar() or 0
        
        # Average progress
        avg_progress_stmt = select(func.avg(HealthPlanDB.progress)).where(
            and_(HealthPlanDB.user_id == user_id, HealthPlanDB.status == "active")
        )
        avg_progress_result = await self.session.execute(avg_progress_stmt)
        avg_progress = avg_progress_result.scalar() or 0.0
        
        return {
            "total_plans": total_plans,
            "active_plans": active_plans,
            "completed_plans": completed_plans,
            "average_progress": round(float(avg_progress), 2)
        }
