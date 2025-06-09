"""
Async task processing utilities for AuraWell API

Provides background task processing for time-consuming operations.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import uuid

logger = logging.getLogger(__name__)


class TaskStatus:
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AsyncTask:
    """Represents an async task"""
    
    def __init__(self, task_id: str, func: Callable, *args, **kwargs):
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.progress = 0.0
    
    async def execute(self):
        """Execute the task"""
        try:
            self.status = TaskStatus.RUNNING
            self.started_at = datetime.now()
            
            # Execute the function
            if asyncio.iscoroutinefunction(self.func):
                self.result = await self.func(*self.args, **self.kwargs)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    self.result = await loop.run_in_executor(
                        executor, self.func, *self.args, **self.kwargs
                    )
            
            self.status = TaskStatus.COMPLETED
            self.progress = 100.0
            self.completed_at = datetime.now()
            
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            self.completed_at = datetime.now()
            logger.error(f"Task {self.task_id} failed: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'task_id': self.task_id,
            'status': self.status,
            'progress': self.progress,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class TaskManager:
    """Manages async task execution"""
    
    def __init__(self, max_concurrent_tasks: int = 10):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.tasks: Dict[str, AsyncTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
    
    def create_task(self, func: Callable, *args, **kwargs) -> str:
        """Create a new async task"""
        task_id = str(uuid.uuid4())
        task = AsyncTask(task_id, func, *args, **kwargs)
        self.tasks[task_id] = task
        
        # Start task execution
        asyncio.create_task(self._execute_task(task))
        
        logger.info(f"Created task {task_id} for function {func.__name__}")
        return task_id
    
    async def _execute_task(self, task: AsyncTask):
        """Execute task with concurrency control"""
        async with self.semaphore:
            try:
                # Create asyncio task for execution
                execution_task = asyncio.create_task(task.execute())
                self.running_tasks[task.task_id] = execution_task
                
                # Wait for completion
                await execution_task
                
            except asyncio.CancelledError:
                task.status = TaskStatus.CANCELLED
                logger.info(f"Task {task.task_id} was cancelled")
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                logger.error(f"Task execution failed for {task.task_id}: {e}")
            finally:
                # Clean up
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            return True
        return False
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks"""
        return [task.to_dict() for task in self.tasks.values()]
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        tasks_to_remove = []
        
        for task_id, task in self.tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] 
                and task.completed_at and task.completed_at < cutoff_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
        
        logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")


# Global task manager
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """Get global task manager instance"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager


# Decorator for async task execution
def async_task(func: Callable) -> Callable:
    """Decorator to run function as async task"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        task_manager = get_task_manager()
        return task_manager.create_task(func, *args, **kwargs)
    
    return wrapper


# Common async tasks
@async_task
async def process_health_data_batch(user_id: str, data_batch: List[Dict[str, Any]]):
    """Process a batch of health data asynchronously"""
    logger.info(f"Processing health data batch for user {user_id}")
    
    # Simulate processing time
    await asyncio.sleep(2)
    
    processed_count = 0
    for data_item in data_batch:
        # Simulate processing each item
        await asyncio.sleep(0.1)
        processed_count += 1
    
    return {
        'user_id': user_id,
        'processed_count': processed_count,
        'total_count': len(data_batch),
        'status': 'completed'
    }


@async_task
async def generate_health_report(user_id: str, report_type: str, date_range: Dict[str, str]):
    """Generate comprehensive health report asynchronously"""
    logger.info(f"Generating {report_type} report for user {user_id}")
    
    # Simulate report generation
    await asyncio.sleep(5)
    
    return {
        'user_id': user_id,
        'report_type': report_type,
        'date_range': date_range,
        'report_url': f'/reports/{user_id}_{report_type}_{datetime.now().strftime("%Y%m%d")}.pdf',
        'generated_at': datetime.now().isoformat()
    }


@async_task
async def sync_external_health_data(user_id: str, platform: str):
    """Sync health data from external platform asynchronously"""
    logger.info(f"Syncing health data from {platform} for user {user_id}")
    
    # Simulate data sync
    await asyncio.sleep(3)
    
    return {
        'user_id': user_id,
        'platform': platform,
        'synced_records': 150,
        'sync_status': 'completed',
        'last_sync': datetime.now().isoformat()
    }


# Performance optimization utilities
class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def optimize_health_data_query(user_id: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize health data query parameters"""
        optimized_filters = filters.copy()
        
        # Add user_id index hint
        optimized_filters['_index_hint'] = 'user_id'
        
        # Optimize date range queries
        if 'date_from' in filters and 'date_to' in filters:
            optimized_filters['_use_date_index'] = True
        
        # Limit result set for performance
        if 'limit' not in optimized_filters:
            optimized_filters['limit'] = 1000
        
        return optimized_filters
    
    @staticmethod
    def batch_database_operations(operations: List[Dict[str, Any]], batch_size: int = 100) -> List[List[Dict[str, Any]]]:
        """Batch database operations for better performance"""
        batches = []
        for i in range(0, len(operations), batch_size):
            batch = operations[i:i + batch_size]
            batches.append(batch)
        return batches


# Connection pooling utilities
class ConnectionPool:
    """Database connection pool manager"""
    
    def __init__(self, min_connections: int = 5, max_connections: int = 20):
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.active_connections = 0
        self.pool_semaphore = asyncio.Semaphore(max_connections)
    
    async def acquire_connection(self):
        """Acquire database connection from pool"""
        await self.pool_semaphore.acquire()
        self.active_connections += 1
        logger.debug(f"Acquired connection, active: {self.active_connections}")
    
    async def release_connection(self):
        """Release database connection back to pool"""
        self.active_connections -= 1
        self.pool_semaphore.release()
        logger.debug(f"Released connection, active: {self.active_connections}")
    
    def get_pool_stats(self) -> Dict[str, int]:
        """Get connection pool statistics"""
        return {
            'active_connections': self.active_connections,
            'max_connections': self.max_connections,
            'available_connections': self.max_connections - self.active_connections
        }
