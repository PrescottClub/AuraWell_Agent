"""
Base Repository Pattern Implementation

Provides abstract base class for all repositories with common CRUD operations.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

from ..database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType], ABC):
    """
    Abstract base repository providing common database operations
    
    Implements Repository pattern with async SQLAlchemy operations.
    """
    
    def __init__(self, session: AsyncSession, model_class: Type[ModelType]):
        """
        Initialize repository
        
        Args:
            session: Database session
            model_class: SQLAlchemy model class
        """
        self.session = session
        self.model_class = model_class
    
    async def create(self, **kwargs) -> ModelType:
        """
        Create new record
        
        Args:
            **kwargs: Field values for the new record
            
        Returns:
            Created model instance
        """
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
    
    async def get_by_id(self, id_value: Any) -> Optional[ModelType]:
        """
        Get record by primary key
        
        Args:
            id_value: Primary key value
            
        Returns:
            Model instance or None if not found
        """
        return await self.session.get(self.model_class, id_value)
    
    async def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """
        Get single record by field value
        
        Args:
            field_name: Field name to filter by
            value: Field value to match
            
        Returns:
            Model instance or None if not found
        """
        stmt = select(self.model_class).where(
            getattr(self.model_class, field_name) == value
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[ModelType]:
        """
        Get all records with optional pagination
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of model instances
        """
        stmt = select(self.model_class).offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_filters(self, filters: Dict[str, Any], 
                           limit: Optional[int] = None, 
                           offset: int = 0) -> List[ModelType]:
        """
        Get records by multiple field filters
        
        Args:
            filters: Dictionary of field_name: value pairs
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of model instances
        """
        stmt = select(self.model_class)
        
        for field_name, value in filters.items():
            if hasattr(self.model_class, field_name):
                stmt = stmt.where(getattr(self.model_class, field_name) == value)
        
        stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_first_by_filters(self, filters: Dict[str, Any]) -> Optional[ModelType]:
        """
        Get first record by multiple field filters

        Args:
            filters: Dictionary of field_name: value pairs

        Returns:
            First matching model instance or None
        """
        stmt = select(self.model_class)

        for field_name, value in filters.items():
            if hasattr(self.model_class, field_name):
                stmt = stmt.where(getattr(self.model_class, field_name) == value)

        stmt = stmt.limit(1)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_by_id(self, id_value: Any, **kwargs) -> Optional[ModelType]:
        """
        Update record by primary key
        
        Args:
            id_value: Primary key value
            **kwargs: Field values to update
            
        Returns:
            Updated model instance or None if not found
        """
        instance = await self.get_by_id(id_value)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            await self.session.flush()
            await self.session.refresh(instance)
        return instance
    
    async def update_by_filters(self, filters: Dict[str, Any], **kwargs) -> int:
        """
        Update multiple records by filters
        
        Args:
            filters: Dictionary of field_name: value pairs for filtering
            **kwargs: Field values to update
            
        Returns:
            Number of updated records
        """
        stmt = update(self.model_class)
        
        for field_name, value in filters.items():
            if hasattr(self.model_class, field_name):
                stmt = stmt.where(getattr(self.model_class, field_name) == value)
        
        stmt = stmt.values(**kwargs)
        result = await self.session.execute(stmt)
        return result.rowcount
    
    async def delete_by_id(self, id_value: Any) -> bool:
        """
        Delete record by primary key
        
        Args:
            id_value: Primary key value
            
        Returns:
            True if record was deleted, False if not found
        """
        instance = await self.get_by_id(id_value)
        if instance:
            await self.session.delete(instance)
            return True
        return False
    
    async def delete_by_filters(self, filters: Dict[str, Any]) -> int:
        """
        Delete multiple records by filters
        
        Args:
            filters: Dictionary of field_name: value pairs for filtering
            
        Returns:
            Number of deleted records
        """
        stmt = delete(self.model_class)
        
        for field_name, value in filters.items():
            if hasattr(self.model_class, field_name):
                stmt = stmt.where(getattr(self.model_class, field_name) == value)
        
        result = await self.session.execute(stmt)
        return result.rowcount
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters
        
        Args:
            filters: Optional dictionary of field_name: value pairs
            
        Returns:
            Number of matching records
        """
        stmt = select(func.count()).select_from(self.model_class)
        
        if filters:
            for field_name, value in filters.items():
                if hasattr(self.model_class, field_name):
                    stmt = stmt.where(getattr(self.model_class, field_name) == value)
        
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def exists(self, filters: Dict[str, Any]) -> bool:
        """
        Check if record exists with given filters

        Args:
            filters: Dictionary of field_name: value pairs

        Returns:
            True if record exists, False otherwise
        """
        count = await self.count(filters)
        return count > 0

    async def upsert(self, unique_fields: Dict[str, Any], **kwargs) -> ModelType:
        """
        Insert or update record based on unique fields

        Args:
            unique_fields: Dictionary of field_name: value pairs for uniqueness check
            **kwargs: Field values to insert or update

        Returns:
            Model instance (created or updated)
        """
        instance = await self.get_first_by_filters(unique_fields)
        if instance:
            # Update existing record
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            await self.session.flush()
            await self.session.refresh(instance)
            return instance

        # Create new record
        all_fields = {**unique_fields, **kwargs}
        return await self.create(**all_fields)
