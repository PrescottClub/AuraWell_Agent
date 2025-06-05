"""
Health Monitoring for AuraWell

Provides system health monitoring, performance tracking, and alerting.
"""

import asyncio
import logging
import psutil
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass


class HealthStatus(str, Enum):
    """System health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class SystemHealthCheck:
    """System health check result"""
    component: str
    status: HealthStatus
    message: str
    metrics: Dict[str, Any]
    timestamp: datetime
    response_time_ms: Optional[float] = None


@dataclass
class PerformanceMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    uptime_seconds: float
    timestamp: datetime


class HealthMonitor:
    """
    System health monitoring service
    
    Monitors system resources, service health, and performance metrics.
    Provides alerting and automated recovery capabilities.
    """
    
    def __init__(self, check_interval: int = 30):
        """
        Initialize health monitor
        
        Args:
            check_interval: Health check interval in seconds
        """
        self.logger = logging.getLogger(__name__)
        self.check_interval = check_interval
        self._health_checks: Dict[str, Callable] = {}
        self._health_history: List[SystemHealthCheck] = []
        self._performance_history: List[PerformanceMetrics] = []
        self._max_history_size = 1000
        self._is_monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._start_time = time.time()
        
        # Register default health checks
        self._register_default_health_checks()
    
    def register_health_check(self, name: str, check_func: Callable) -> None:
        """
        Register a health check function
        
        Args:
            name: Name of the health check
            check_func: Async function that returns SystemHealthCheck
        """
        self._health_checks[name] = check_func
        self.logger.info(f"Registered health check: {name}")
    
    async def start_monitoring(self) -> None:
        """Start continuous health monitoring"""
        if self._is_monitoring:
            self.logger.warning("Health monitoring is already running")
            return
        
        self._is_monitoring = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Health monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop health monitoring"""
        if not self._is_monitoring:
            return
        
        self._is_monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Health monitoring stopped")
    
    async def perform_health_check(self) -> Dict[str, SystemHealthCheck]:
        """
        Perform all registered health checks
        
        Returns:
            Dictionary of health check results
        """
        results = {}
        
        for name, check_func in self._health_checks.items():
            try:
                start_time = time.time()
                result = await check_func()
                end_time = time.time()
                
                # Add response time
                result.response_time_ms = (end_time - start_time) * 1000
                
                results[name] = result
                
                # Add to history
                self._add_health_check_to_history(result)
                
            except Exception as e:
                self.logger.error(f"Health check {name} failed: {e}")
                error_result = SystemHealthCheck(
                    component=name,
                    status=HealthStatus.CRITICAL,
                    message=f"Health check failed: {str(e)}",
                    metrics={},
                    timestamp=datetime.now(timezone.utc)
                )
                results[name] = error_result
                self._add_health_check_to_history(error_result)
        
        return results
    
    async def get_system_metrics(self) -> PerformanceMetrics:
        """
        Get current system performance metrics
        
        Returns:
            Performance metrics
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # Process count
            process_count = len(psutil.pids())
            
            # Uptime
            uptime_seconds = time.time() - self._start_time
            
            metrics = PerformanceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_io=network_io,
                process_count=process_count,
                uptime_seconds=uptime_seconds,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Add to history
            self._add_performance_metrics_to_history(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            raise
    
    def get_overall_health_status(self) -> HealthStatus:
        """
        Get overall system health status
        
        Returns:
            Overall health status
        """
        if not self._health_history:
            return HealthStatus.UNHEALTHY
        
        # Get recent health checks (last 5 minutes)
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        recent_checks = [
            check for check in self._health_history
            if check.timestamp > cutoff_time
        ]
        
        if not recent_checks:
            return HealthStatus.UNHEALTHY
        
        # Count status occurrences
        status_counts = {}
        for check in recent_checks:
            status_counts[check.status] = status_counts.get(check.status, 0) + 1
        
        # Determine overall status
        if status_counts.get(HealthStatus.CRITICAL, 0) > 0:
            return HealthStatus.CRITICAL
        elif status_counts.get(HealthStatus.UNHEALTHY, 0) > 0:
            return HealthStatus.UNHEALTHY
        elif status_counts.get(HealthStatus.DEGRADED, 0) > 0:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get health monitoring summary
        
        Returns:
            Health summary
        """
        overall_status = self.get_overall_health_status()
        
        # Get latest metrics
        latest_metrics = self._performance_history[-1] if self._performance_history else None
        
        # Get component status summary
        component_status = {}
        if self._health_history:
            # Group by component and get latest status
            for check in reversed(self._health_history):
                if check.component not in component_status:
                    component_status[check.component] = check.status.value
        
        return {
            "overall_status": overall_status.value,
            "component_status": component_status,
            "latest_metrics": {
                "cpu_percent": latest_metrics.cpu_percent if latest_metrics else None,
                "memory_percent": latest_metrics.memory_percent if latest_metrics else None,
                "disk_percent": latest_metrics.disk_percent if latest_metrics else None,
                "uptime_seconds": latest_metrics.uptime_seconds if latest_metrics else None
            } if latest_metrics else None,
            "monitoring_active": self._is_monitoring,
            "registered_checks": list(self._health_checks.keys()),
            "history_size": len(self._health_history)
        }
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, List[float]]:
        """
        Get performance trends over specified time period
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Performance trends
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_metrics = [
            metrics for metrics in self._performance_history
            if metrics.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        return {
            "timestamps": [m.timestamp.isoformat() for m in recent_metrics],
            "cpu_percent": [m.cpu_percent for m in recent_metrics],
            "memory_percent": [m.memory_percent for m in recent_metrics],
            "disk_percent": [m.disk_percent for m in recent_metrics],
            "process_count": [m.process_count for m in recent_metrics]
        }
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self._is_monitoring:
            try:
                # Perform health checks
                await self.perform_health_check()
                
                # Collect system metrics
                await self.get_system_metrics()
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    def _register_default_health_checks(self) -> None:
        """Register default system health checks"""
        self.register_health_check("system_resources", self._check_system_resources)
        self.register_health_check("disk_space", self._check_disk_space)
        self.register_health_check("memory_usage", self._check_memory_usage)
    
    async def _check_system_resources(self) -> SystemHealthCheck:
        """Check overall system resources"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            # Determine status based on resource usage
            if cpu_percent > 90 or memory_percent > 90:
                status = HealthStatus.CRITICAL
                message = f"High resource usage: CPU {cpu_percent}%, Memory {memory_percent}%"
            elif cpu_percent > 75 or memory_percent > 75:
                status = HealthStatus.DEGRADED
                message = f"Elevated resource usage: CPU {cpu_percent}%, Memory {memory_percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Normal resource usage: CPU {cpu_percent}%, Memory {memory_percent}%"
            
            return SystemHealthCheck(
                component="system_resources",
                status=status,
                message=message,
                metrics={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent
                },
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return SystemHealthCheck(
                component="system_resources",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check system resources: {str(e)}",
                metrics={},
                timestamp=datetime.now(timezone.utc)
            )
    
    async def _check_disk_space(self) -> SystemHealthCheck:
        """Check disk space"""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            if disk_percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical disk space: {disk_percent:.1f}% used"
            elif disk_percent > 85:
                status = HealthStatus.DEGRADED
                message = f"Low disk space: {disk_percent:.1f}% used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Sufficient disk space: {disk_percent:.1f}% used"
            
            return SystemHealthCheck(
                component="disk_space",
                status=status,
                message=message,
                metrics={
                    "disk_percent": disk_percent,
                    "total_gb": disk.total / (1024**3),
                    "used_gb": disk.used / (1024**3),
                    "free_gb": disk.free / (1024**3)
                },
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return SystemHealthCheck(
                component="disk_space",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check disk space: {str(e)}",
                metrics={},
                timestamp=datetime.now(timezone.utc)
            )
    
    async def _check_memory_usage(self) -> SystemHealthCheck:
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            if memory_percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical memory usage: {memory_percent:.1f}%"
            elif memory_percent > 85:
                status = HealthStatus.DEGRADED
                message = f"High memory usage: {memory_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Normal memory usage: {memory_percent:.1f}%"
            
            return SystemHealthCheck(
                component="memory_usage",
                status=status,
                message=message,
                metrics={
                    "memory_percent": memory_percent,
                    "total_gb": memory.total / (1024**3),
                    "used_gb": memory.used / (1024**3),
                    "available_gb": memory.available / (1024**3)
                },
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return SystemHealthCheck(
                component="memory_usage",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check memory usage: {str(e)}",
                metrics={},
                timestamp=datetime.now(timezone.utc)
            )
    
    def _add_health_check_to_history(self, check: SystemHealthCheck) -> None:
        """Add health check to history"""
        self._health_history.append(check)
        
        # Trim history if too large
        if len(self._health_history) > self._max_history_size:
            self._health_history = self._health_history[-self._max_history_size:]
    
    def _add_performance_metrics_to_history(self, metrics: PerformanceMetrics) -> None:
        """Add performance metrics to history"""
        self._performance_history.append(metrics)
        
        # Trim history if too large
        if len(self._performance_history) > self._max_history_size:
            self._performance_history = self._performance_history[-self._max_history_size:]
