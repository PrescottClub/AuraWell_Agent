"""
高级监控和指标收集系统

提供性能监控、错误跟踪、业务指标等功能
"""

import time
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, field
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import psutil
import threading

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """指标数据点"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""


@dataclass
class PerformanceMetrics:
    """性能指标"""
    request_count: int = 0
    error_count: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    active_requests: int = 0
    
    @property
    def avg_response_time(self) -> float:
        """平均响应时间"""
        if self.request_count == 0:
            return 0.0
        return self.total_response_time / self.request_count
    
    @property
    def error_rate(self) -> float:
        """错误率"""
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_points: int = 10000):
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.performance_metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self.system_metrics: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None, unit: str = ""):
        """记录指标"""
        with self._lock:
            point = MetricPoint(
                name=name,
                value=value,
                timestamp=datetime.now(timezone.utc),
                tags=tags or {},
                unit=unit
            )
            self.metrics[name].append(point)
            logger.debug(f"Recorded metric: {name}={value}{unit}")
    
    def record_request_start(self, endpoint: str):
        """记录请求开始"""
        with self._lock:
            self.performance_metrics[endpoint].active_requests += 1
    
    def record_request_end(self, endpoint: str, response_time: float, success: bool = True):
        """记录请求结束"""
        with self._lock:
            metrics = self.performance_metrics[endpoint]
            metrics.request_count += 1
            metrics.total_response_time += response_time
            metrics.min_response_time = min(metrics.min_response_time, response_time)
            metrics.max_response_time = max(metrics.max_response_time, response_time)
            metrics.active_requests = max(0, metrics.active_requests - 1)
            
            if not success:
                metrics.error_count += 1
            
            # 记录到时间序列
            self.record_metric(f"request.{endpoint}.response_time", response_time, unit="ms")
            self.record_metric(f"request.{endpoint}.count", 1)
            if not success:
                self.record_metric(f"request.{endpoint}.error", 1)
    
    def get_performance_summary(self) -> Dict[str, Dict[str, Any]]:
        """获取性能摘要"""
        with self._lock:
            summary = {}
            for endpoint, metrics in self.performance_metrics.items():
                summary[endpoint] = {
                    "request_count": metrics.request_count,
                    "error_count": metrics.error_count,
                    "error_rate": metrics.error_rate,
                    "avg_response_time": metrics.avg_response_time,
                    "min_response_time": metrics.min_response_time if metrics.min_response_time != float('inf') else 0,
                    "max_response_time": metrics.max_response_time,
                    "active_requests": metrics.active_requests
                }
            return summary
    
    def get_recent_metrics(self, name: str, limit: int = 100) -> List[MetricPoint]:
        """获取最近的指标"""
        with self._lock:
            if name in self.metrics:
                return list(self.metrics[name])[-limit:]
            return []
    
    def collect_system_metrics(self):
        """收集系统指标"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("system.cpu.usage", cpu_percent, unit="%")
            
            # 内存使用
            memory = psutil.virtual_memory()
            self.record_metric("system.memory.usage", memory.percent, unit="%")
            self.record_metric("system.memory.available", memory.available / 1024 / 1024, unit="MB")
            
            # 磁盘使用
            disk = psutil.disk_usage('/')
            self.record_metric("system.disk.usage", disk.percent, unit="%")
            self.record_metric("system.disk.free", disk.free / 1024 / 1024 / 1024, unit="GB")
            
            # 网络统计
            network = psutil.net_io_counters()
            self.record_metric("system.network.bytes_sent", network.bytes_sent, unit="bytes")
            self.record_metric("system.network.bytes_recv", network.bytes_recv, unit="bytes")
            
            # 进程信息
            process = psutil.Process()
            self.record_metric("process.memory.rss", process.memory_info().rss / 1024 / 1024, unit="MB")
            self.record_metric("process.cpu.percent", process.cpu_percent(), unit="%")
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def start_monitoring(self, interval: int = 60):
        """开始监控"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        logger.info(f"Starting metrics monitoring with {interval}s interval")
        
        async def monitor_loop():
            while self._monitoring_active:
                try:
                    self.collect_system_metrics()
                    await asyncio.sleep(interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(interval)
        
        self._monitoring_task = asyncio.create_task(monitor_loop())
    
    async def stop_monitoring(self):
        """停止监控"""
        if not self._monitoring_active:
            return
        
        self._monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped metrics monitoring")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        try:
            # 系统资源检查
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 性能检查
            total_requests = sum(m.request_count for m in self.performance_metrics.values())
            total_errors = sum(m.error_count for m in self.performance_metrics.values())
            overall_error_rate = total_errors / total_requests if total_requests > 0 else 0
            
            # 健康状态判断
            status = "healthy"
            issues = []
            
            if cpu_percent > 80:
                status = "warning"
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory.percent > 80:
                status = "warning"
                issues.append(f"High memory usage: {memory.percent:.1f}%")
            
            if disk.percent > 90:
                status = "critical"
                issues.append(f"Low disk space: {disk.percent:.1f}% used")
            
            if overall_error_rate > 0.05:  # 5% 错误率
                status = "warning"
                issues.append(f"High error rate: {overall_error_rate:.2%}")
            
            return {
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "issues": issues,
                "metrics": {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "disk_usage": disk.percent,
                    "total_requests": total_requests,
                    "error_rate": overall_error_rate,
                    "active_requests": sum(m.active_requests for m in self.performance_metrics.values())
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "issues": [f"Health check failed: {str(e)}"],
                "metrics": {}
            }


# 全局指标收集器实例
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


@asynccontextmanager
async def track_request_performance(endpoint: str):
    """跟踪请求性能的上下文管理器"""
    collector = get_metrics_collector()
    start_time = time.time()
    
    collector.record_request_start(endpoint)
    
    try:
        yield
        # 请求成功
        response_time = (time.time() - start_time) * 1000  # 转换为毫秒
        collector.record_request_end(endpoint, response_time, success=True)
    except Exception as e:
        # 请求失败
        response_time = (time.time() - start_time) * 1000
        collector.record_request_end(endpoint, response_time, success=False)
        raise


def record_business_metric(name: str, value: float, tags: Optional[Dict[str, str]] = None):
    """记录业务指标"""
    collector = get_metrics_collector()
    collector.record_metric(f"business.{name}", value, tags)


def record_database_operation(operation: str, duration: float, success: bool = True):
    """记录数据库操作指标"""
    collector = get_metrics_collector()
    tags = {"operation": operation, "success": str(success)}
    collector.record_metric("database.operation.duration", duration, tags, "ms")
    collector.record_metric("database.operation.count", 1, tags)


async def initialize_monitoring():
    """初始化监控系统"""
    collector = get_metrics_collector()
    await collector.start_monitoring()
    logger.info("Monitoring system initialized")


async def shutdown_monitoring():
    """关闭监控系统"""
    collector = get_metrics_collector()
    await collector.stop_monitoring()
    logger.info("Monitoring system shutdown")
