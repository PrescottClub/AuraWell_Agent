"""
重构后的性能监控器
采用组合模式和策略模式，提升代码可维护性和可扩展性
"""

import asyncio
import logging
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Protocol
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import deque
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """性能指标数据类"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    response_time_ms: float
    error_rate: float
    active_connections: int


@dataclass
class AlertThreshold:
    """告警阈值配置"""
    cpu_threshold: float = 80.0
    memory_threshold: float = 85.0
    disk_threshold: float = 90.0
    response_time_threshold: float = 5000.0
    error_rate_threshold: float = 0.05


# ============================================================================
# 策略模式：不同的指标收集策略
# ============================================================================

class MetricCollector(Protocol):
    """指标收集器接口"""
    async def collect(self) -> Dict[str, Any]:
        """收集指标数据"""
        ...


class SystemMetricCollector:
    """系统指标收集器"""
    
    async def collect(self) -> Dict[str, Any]:
        """收集系统资源指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_usage_percent': disk.percent
            }
        except Exception as e:
            logger.error(f"系统指标收集失败: {e}")
            return {
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'disk_usage_percent': 0.0
            }


class NetworkMetricCollector:
    """网络指标收集器"""
    
    async def collect(self) -> Dict[str, Any]:
        """收集网络连接指标"""
        try:
            connections = psutil.net_connections(kind='inet')
            active_count = len([conn for conn in connections if conn.status == 'ESTABLISHED'])
            return {'active_connections': active_count}
        except Exception as e:
            logger.warning(f"网络指标收集失败: {e}")
            return {'active_connections': 0}


class ApplicationMetricCollector:
    """应用指标收集器"""
    
    def __init__(self, response_times: deque, request_count: int, error_count: int):
        self.response_times = response_times
        self.request_count = request_count
        self.error_count = error_count
    
    async def collect(self) -> Dict[str, Any]:
        """收集应用性能指标"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
        error_rate = self.error_count / self.request_count if self.request_count > 0 else 0.0
        
        return {
            'response_time_ms': avg_response_time,
            'error_rate': error_rate
        }


# ============================================================================
# 策略模式：不同的告警策略
# ============================================================================

class AlertStrategy(ABC):
    """告警策略抽象基类"""
    
    @abstractmethod
    def check_alert(self, metric: PerformanceMetric, threshold: AlertThreshold) -> Optional[Dict[str, Any]]:
        """检查是否需要告警"""
        pass


class CPUAlertStrategy(AlertStrategy):
    """CPU告警策略"""
    
    def check_alert(self, metric: PerformanceMetric, threshold: AlertThreshold) -> Optional[Dict[str, Any]]:
        if metric.cpu_percent > threshold.cpu_threshold:
            return {
                "type": "cpu_high",
                "message": f"CPU使用率过高: {metric.cpu_percent:.1f}%",
                "severity": "warning",
                "timestamp": metric.timestamp,
                "value": metric.cpu_percent,
                "threshold": threshold.cpu_threshold
            }
        return None


class MemoryAlertStrategy(AlertStrategy):
    """内存告警策略"""
    
    def check_alert(self, metric: PerformanceMetric, threshold: AlertThreshold) -> Optional[Dict[str, Any]]:
        if metric.memory_percent > threshold.memory_threshold:
            return {
                "type": "memory_high",
                "message": f"内存使用率过高: {metric.memory_percent:.1f}%",
                "severity": "warning",
                "timestamp": metric.timestamp,
                "value": metric.memory_percent,
                "threshold": threshold.memory_threshold
            }
        return None


class DiskAlertStrategy(AlertStrategy):
    """磁盘告警策略"""
    
    def check_alert(self, metric: PerformanceMetric, threshold: AlertThreshold) -> Optional[Dict[str, Any]]:
        if metric.disk_usage_percent > threshold.disk_threshold:
            return {
                "type": "disk_high",
                "message": f"磁盘使用率过高: {metric.disk_usage_percent:.1f}%",
                "severity": "critical",
                "timestamp": metric.timestamp,
                "value": metric.disk_usage_percent,
                "threshold": threshold.disk_threshold
            }
        return None


# ============================================================================
# 组合模式：告警管理器
# ============================================================================

class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.strategies: List[AlertStrategy] = [
            CPUAlertStrategy(),
            MemoryAlertStrategy(),
            DiskAlertStrategy()
        ]
        self.active_alerts: List[Dict[str, Any]] = []
    
    def add_strategy(self, strategy: AlertStrategy):
        """添加告警策略"""
        self.strategies.append(strategy)
    
    async def check_all_alerts(self, metric: PerformanceMetric, threshold: AlertThreshold):
        """检查所有告警策略"""
        new_alerts = []
        
        for strategy in self.strategies:
            alert = strategy.check_alert(metric, threshold)
            if alert:
                new_alerts.append(alert)
        
        self.active_alerts = new_alerts
        
        # 记录告警
        for alert in new_alerts:
            logger.warning(f"⚠️ 性能告警: {alert['message']}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """获取活跃告警"""
        return self.active_alerts.copy()


# ============================================================================
# 重构后的性能监控器主类
# ============================================================================

class PerformanceMonitorRefactored:
    """重构后的性能监控器"""
    
    def __init__(self, 
                 collection_interval: int = 60,
                 retention_hours: int = 24,
                 alert_threshold: Optional[AlertThreshold] = None):
        
        self.collection_interval = collection_interval
        self.retention_hours = retention_hours
        self.alert_threshold = alert_threshold or AlertThreshold()
        
        # 数据存储
        self.metrics_history: deque = deque(maxlen=int(retention_hours * 3600 / collection_interval))
        self.response_times = deque(maxlen=1000)
        self.request_count = 0
        self.error_count = 0
        
        # 组件初始化
        self._init_collectors()
        self.alert_manager = AlertManager()
        
        # 监控状态
        self.is_running = False
        self.last_collection_time = None
        
        logger.info("重构版性能监控器初始化完成")
    
    def _init_collectors(self):
        """初始化指标收集器"""
        self.collectors = [
            SystemMetricCollector(),
            NetworkMetricCollector(),
            ApplicationMetricCollector(self.response_times, self.request_count, self.error_count)
        ]
    
    async def start_monitoring(self):
        """启动性能监控"""
        if self.is_running:
            logger.warning("性能监控已在运行中")
            return
        
        self.is_running = True
        logger.info(f"🚀 启动重构版性能监控，收集间隔: {self.collection_interval}秒")
        
        try:
            while self.is_running:
                await self._collect_and_analyze_metrics()
                await asyncio.sleep(self.collection_interval)
        except Exception as e:
            logger.error(f"性能监控运行异常: {e}")
        finally:
            self.is_running = False
            logger.info("性能监控已停止")
    
    async def _collect_and_analyze_metrics(self):
        """收集并分析指标"""
        try:
            # 使用组合的收集器收集所有指标
            all_metrics = {}
            for collector in self.collectors:
                metrics = await collector.collect()
                all_metrics.update(metrics)
            
            # 创建性能指标对象
            metric = PerformanceMetric(
                timestamp=datetime.now().isoformat(),
                **all_metrics
            )
            
            # 存储指标
            self.metrics_history.append(metric)
            self.last_collection_time = datetime.now()
            
            # 检查告警
            await self.alert_manager.check_all_alerts(metric, self.alert_threshold)
            
            logger.debug(f"指标收集完成: CPU={metric.cpu_percent:.1f}%, 内存={metric.memory_percent:.1f}%")
            
        except Exception as e:
            logger.error(f"指标收集和分析失败: {e}")
    
    def record_request(self, response_time_ms: float, is_error: bool = False):
        """记录请求性能数据"""
        self.request_count += 1
        self.response_times.append(response_time_ms)
        
        if is_error:
            self.error_count += 1
        
        # 更新应用指标收集器的引用
        for collector in self.collectors:
            if isinstance(collector, ApplicationMetricCollector):
                collector.request_count = self.request_count
                collector.error_count = self.error_count
                break
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.is_running = False
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """获取当前性能指标"""
        if not self.metrics_history:
            return {"error": "暂无性能数据"}
        
        latest_metric = self.metrics_history[-1]
        
        return {
            "current": asdict(latest_metric),
            "alerts": self.alert_manager.get_active_alerts(),
            "monitoring_status": {
                "is_running": self.is_running,
                "last_collection": self.last_collection_time.isoformat() if self.last_collection_time else None,
                "data_points": len(self.metrics_history),
                "collection_interval": self.collection_interval
            }
        }
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要报告"""
        if not self.metrics_history:
            return {"error": "暂无性能数据"}
        
        # 计算最近1小时的统计数据
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m.timestamp) > datetime.now() - timedelta(hours=1)
        ]
        
        if recent_metrics:
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            avg_response_time = sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics)
        else:
            avg_cpu = avg_memory = avg_response_time = 0
        
        return {
            "summary": {
                "total_data_points": len(self.metrics_history),
                "recent_hour_points": len(recent_metrics),
                "avg_cpu_1h": round(avg_cpu, 2),
                "avg_memory_1h": round(avg_memory, 2),
                "avg_response_time_1h": round(avg_response_time, 2)
            },
            "current_alerts": self.alert_manager.get_active_alerts(),
            "request_stats": {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "current_error_rate": self.error_count / self.request_count if self.request_count > 0 else 0
            },
            "last_updated": datetime.now().isoformat()
        }


# 全局实例管理
_global_monitor = None

def get_performance_monitor_refactored() -> PerformanceMonitorRefactored:
    """获取重构版全局性能监控器实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitorRefactored()
    return _global_monitor
