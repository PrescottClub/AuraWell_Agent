"""
任务调度器

负责管理和调度各种定时任务，支持：
- 每日Prompt性能分析
- 定时数据清理
- 健康检查
- 报告生成
"""

import logging
import asyncio
from datetime import datetime, time, timedelta
from typing import Dict, Any, List, Callable, Optional
import traceback

from .prompt_monitoring_task import schedule_daily_analysis

logger = logging.getLogger(__name__)


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.logger = logger
        self.is_running = False
        self.tasks = {}
        self.task_history = []
        
        # 注册默认任务
        self._register_default_tasks()
    
    def _register_default_tasks(self):
        """注册默认任务"""
        
        # 每日Prompt性能分析 - 每天凌晨2点执行
        self.register_daily_task(
            name="prompt_performance_analysis",
            func=schedule_daily_analysis,
            hour=2,
            minute=0,
            description="每日Prompt性能分析和优化建议生成"
        )
        
        # 每周数据清理 - 每周日凌晨3点执行
        self.register_weekly_task(
            name="data_cleanup",
            func=self._weekly_data_cleanup,
            weekday=6,  # Sunday
            hour=3,
            minute=0,
            description="清理过期的性能日志和临时数据"
        )
        
        # 每小时健康检查
        self.register_hourly_task(
            name="health_check",
            func=self._health_check,
            minute=0,
            description="系统健康状态检查"
        )
    
    def register_daily_task(
        self, 
        name: str, 
        func: Callable, 
        hour: int = 0, 
        minute: int = 0,
        description: str = ""
    ):
        """注册每日任务"""
        self.tasks[name] = {
            "type": "daily",
            "func": func,
            "schedule": {"hour": hour, "minute": minute},
            "description": description,
            "last_run": None,
            "next_run": None,
            "enabled": True
        }
        self._calculate_next_run(name)
        self.logger.info(f"Registered daily task: {name} at {hour:02d}:{minute:02d}")
    
    def register_weekly_task(
        self, 
        name: str, 
        func: Callable, 
        weekday: int, 
        hour: int = 0, 
        minute: int = 0,
        description: str = ""
    ):
        """注册每周任务"""
        self.tasks[name] = {
            "type": "weekly",
            "func": func,
            "schedule": {"weekday": weekday, "hour": hour, "minute": minute},
            "description": description,
            "last_run": None,
            "next_run": None,
            "enabled": True
        }
        self._calculate_next_run(name)
        self.logger.info(f"Registered weekly task: {name} on weekday {weekday} at {hour:02d}:{minute:02d}")
    
    def register_hourly_task(
        self, 
        name: str, 
        func: Callable, 
        minute: int = 0,
        description: str = ""
    ):
        """注册每小时任务"""
        self.tasks[name] = {
            "type": "hourly",
            "func": func,
            "schedule": {"minute": minute},
            "description": description,
            "last_run": None,
            "next_run": None,
            "enabled": True
        }
        self._calculate_next_run(name)
        self.logger.info(f"Registered hourly task: {name} at minute {minute}")
    
    def _calculate_next_run(self, task_name: str):
        """计算任务下次执行时间"""
        task = self.tasks[task_name]
        now = datetime.now()
        schedule = task["schedule"]
        
        if task["type"] == "daily":
            next_run = now.replace(
                hour=schedule["hour"], 
                minute=schedule["minute"], 
                second=0, 
                microsecond=0
            )
            if next_run <= now:
                next_run += timedelta(days=1)
                
        elif task["type"] == "weekly":
            days_ahead = schedule["weekday"] - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(
                hour=schedule["hour"], 
                minute=schedule["minute"], 
                second=0, 
                microsecond=0
            )
            
        elif task["type"] == "hourly":
            next_run = now.replace(
                minute=schedule["minute"], 
                second=0, 
                microsecond=0
            )
            if next_run <= now:
                next_run += timedelta(hours=1)
        
        task["next_run"] = next_run
        self.logger.debug(f"Next run for {task_name}: {next_run}")
    
    async def start(self):
        """启动调度器"""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.logger.info("Task scheduler started")
        
        try:
            while self.is_running:
                await self._check_and_run_tasks()
                await asyncio.sleep(60)  # 每分钟检查一次
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}")
            self.logger.error(traceback.format_exc())
        finally:
            self.is_running = False
            self.logger.info("Task scheduler stopped")
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        self.logger.info("Task scheduler stop requested")
    
    async def _check_and_run_tasks(self):
        """检查并运行到期的任务"""
        now = datetime.now()
        
        for task_name, task in self.tasks.items():
            if not task["enabled"]:
                continue
                
            if task["next_run"] and now >= task["next_run"]:
                await self._run_task(task_name)
    
    async def _run_task(self, task_name: str):
        """运行指定任务"""
        task = self.tasks[task_name]
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Running task: {task_name}")
            
            # 执行任务
            if asyncio.iscoroutinefunction(task["func"]):
                result = await task["func"]()
            else:
                result = task["func"]()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 记录任务执行历史
            task_record = {
                "task_name": task_name,
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": duration,
                "status": "success",
                "result": result
            }
            
            task["last_run"] = start_time
            self._calculate_next_run(task_name)
            
            self.logger.info(f"Task {task_name} completed successfully in {duration:.2f}s")
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            task_record = {
                "task_name": task_name,
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": duration,
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
            self.logger.error(f"Task {task_name} failed after {duration:.2f}s: {e}")
            self.logger.error(traceback.format_exc())
            
            # 重新计算下次执行时间
            self._calculate_next_run(task_name)
        
        # 保存任务历史（最多保留100条）
        self.task_history.append(task_record)
        if len(self.task_history) > 100:
            self.task_history = self.task_history[-100:]
    
    async def run_task_now(self, task_name: str) -> Dict[str, Any]:
        """立即运行指定任务"""
        if task_name not in self.tasks:
            raise ValueError(f"Task {task_name} not found")
        
        await self._run_task(task_name)
        
        # 返回最新的执行记录
        for record in reversed(self.task_history):
            if record["task_name"] == task_name:
                return record
        
        return {"status": "not_found"}
    
    def get_task_status(self) -> Dict[str, Any]:
        """获取所有任务状态"""
        status = {
            "scheduler_running": self.is_running,
            "total_tasks": len(self.tasks),
            "enabled_tasks": len([t for t in self.tasks.values() if t["enabled"]]),
            "tasks": {}
        }
        
        for name, task in self.tasks.items():
            status["tasks"][name] = {
                "type": task["type"],
                "description": task["description"],
                "enabled": task["enabled"],
                "last_run": task["last_run"].isoformat() if task["last_run"] else None,
                "next_run": task["next_run"].isoformat() if task["next_run"] else None,
                "schedule": task["schedule"]
            }
        
        return status
    
    def enable_task(self, task_name: str):
        """启用任务"""
        if task_name in self.tasks:
            self.tasks[task_name]["enabled"] = True
            self._calculate_next_run(task_name)
            self.logger.info(f"Task {task_name} enabled")
    
    def disable_task(self, task_name: str):
        """禁用任务"""
        if task_name in self.tasks:
            self.tasks[task_name]["enabled"] = False
            self.logger.info(f"Task {task_name} disabled")
    
    async def _weekly_data_cleanup(self) -> Dict[str, Any]:
        """每周数据清理任务"""
        try:
            self.logger.info("Starting weekly data cleanup")
            
            # 这里可以实现具体的数据清理逻辑
            # 例如：删除30天前的性能日志、清理临时文件等
            
            cleanup_summary = {
                "status": "completed",
                "cleaned_items": {
                    "old_performance_logs": 0,
                    "temp_files": 0,
                    "expired_cache": 0
                },
                "cleanup_date": datetime.now().isoformat()
            }
            
            self.logger.info("Weekly data cleanup completed")
            return cleanup_summary
            
        except Exception as e:
            self.logger.error(f"Weekly data cleanup failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _health_check(self) -> Dict[str, Any]:
        """系统健康检查任务"""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "scheduler_running": self.is_running,
                    "tasks_enabled": len([t for t in self.tasks.values() if t["enabled"]]),
                    "recent_failures": len([
                        r for r in self.task_history[-10:] 
                        if r.get("status") == "error"
                    ])
                }
            }
            
            # 如果最近有太多失败，标记为不健康
            if health_status["checks"]["recent_failures"] > 3:
                health_status["status"] = "unhealthy"
                health_status["reason"] = "Too many recent task failures"
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}


# 全局调度器实例
task_scheduler = TaskScheduler()
