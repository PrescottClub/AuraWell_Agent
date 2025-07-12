"""
AuraWell性能监控器
后台运行的性能监控服务，定期收集和分析系统性能指标
"""

import asyncio
import logging
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import deque

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
    response_time_threshold: float = 5000.0  # 5秒
    error_rate_threshold: float = 0.05  # 5%


class PerformanceMonitor:
    """性能监控器主类"""
    
    def __init__(self, 
                 collection_interval: int = 60,  # 收集间隔（秒）
                 retention_hours: int = 24,      # 数据保留时间（小时）
                 alert_threshold: Optional[AlertThreshold] = None):
        
        self.collection_interval = collection_interval
        self.retention_hours = retention_hours
        self.alert_threshold = alert_threshold or AlertThreshold()
        
        # 性能数据存储（内存中的时间序列数据）
        self.metrics_history: deque = deque(maxlen=int(retention_hours * 3600 / collection_interval))
        
        # 统计计数器
        self.request_count = 0
        self.error_count = 0
        self.response_times = deque(maxlen=1000)  # 最近1000个请求的响应时间
        
        # 监控状态
        self.is_running = False
        self.last_collection_time = None
        
        # 告警状态
        self.active_alerts = []
        
        logger.info("性能监控器初始化完成")
    
    async def start_monitoring(self):
        """启动性能监控"""
        if self.is_running:
            logger.warning("性能监控已在运行中")
            return
        
        self.is_running = True
        logger.info(f"🚀 启动性能监控，收集间隔: {self.collection_interval}秒")
        
        try:
            while self.is_running:
                await self._collect_metrics()
                await self._check_alerts()
                await asyncio.sleep(self.collection_interval)
                
        except Exception as e:
            logger.error(f"性能监控运行异常: {e}")
        finally:
            self.is_running = False
            logger.info("性能监控已停止")
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.is_running = False
        logger.info("正在停止性能监控...")
    
    async def _collect_metrics(self):
        """收集性能指标"""
        try:
            start_time = time.time()
            
            # 系统资源指标
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 应用性能指标
            avg_response_time = self._calculate_avg_response_time()
            error_rate = self._calculate_error_rate()
            active_connections = self._get_active_connections()
            
            # 创建性能指标对象
            metric = PerformanceMetric(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                response_time_ms=avg_response_time,
                error_rate=error_rate,
                active_connections=active_connections
            )
            
            # 存储指标
            self.metrics_history.append(metric)
            self.last_collection_time = datetime.now()
            
            # 记录收集耗时
            collection_time = (time.time() - start_time) * 1000
            logger.debug(f"性能指标收集完成，耗时: {collection_time:.2f}ms")
            
            # 定期清理过期数据
            await self._cleanup_old_data()
            
        except Exception as e:
            logger.error(f"性能指标收集失败: {e}")
    
    def _calculate_avg_response_time(self) -> float:
        """计算平均响应时间"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def _calculate_error_rate(self) -> float:
        """计算错误率"""
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count
    
    def _get_active_connections(self) -> int:
        """获取活跃连接数"""
        try:
            # 获取网络连接信息
            connections = psutil.net_connections(kind='inet')
            active_count = len([conn for conn in connections if conn.status == 'ESTABLISHED'])
            return active_count
        except Exception as e:
            logger.warning(f"获取连接数失败: {e}")
            return 0
    
    async def _check_alerts(self):
        """检查告警条件"""
        if not self.metrics_history:
            return
        
        latest_metric = self.metrics_history[-1]
        new_alerts = []
        
        # CPU使用率告警
        if latest_metric.cpu_percent > self.alert_threshold.cpu_threshold:
            new_alerts.append({
                "type": "cpu_high",
                "message": f"CPU使用率过高: {latest_metric.cpu_percent:.1f}%",
                "severity": "warning",
                "timestamp": latest_metric.timestamp,
                "value": latest_metric.cpu_percent,
                "threshold": self.alert_threshold.cpu_threshold
            })
        
        # 内存使用率告警
        if latest_metric.memory_percent > self.alert_threshold.memory_threshold:
            new_alerts.append({
                "type": "memory_high",
                "message": f"内存使用率过高: {latest_metric.memory_percent:.1f}%",
                "severity": "warning",
                "timestamp": latest_metric.timestamp,
                "value": latest_metric.memory_percent,
                "threshold": self.alert_threshold.memory_threshold
            })
        
        # 磁盘使用率告警
        if latest_metric.disk_usage_percent > self.alert_threshold.disk_threshold:
            new_alerts.append({
                "type": "disk_high",
                "message": f"磁盘使用率过高: {latest_metric.disk_usage_percent:.1f}%",
                "severity": "critical",
                "timestamp": latest_metric.timestamp,
                "value": latest_metric.disk_usage_percent,
                "threshold": self.alert_threshold.disk_threshold
            })
        
        # 响应时间告警
        if latest_metric.response_time_ms > self.alert_threshold.response_time_threshold:
            new_alerts.append({
                "type": "response_time_high",
                "message": f"响应时间过长: {latest_metric.response_time_ms:.1f}ms",
                "severity": "warning",
                "timestamp": latest_metric.timestamp,
                "value": latest_metric.response_time_ms,
                "threshold": self.alert_threshold.response_time_threshold
            })
        
        # 错误率告警
        if latest_metric.error_rate > self.alert_threshold.error_rate_threshold:
            new_alerts.append({
                "type": "error_rate_high",
                "message": f"错误率过高: {latest_metric.error_rate:.2%}",
                "severity": "critical",
                "timestamp": latest_metric.timestamp,
                "value": latest_metric.error_rate,
                "threshold": self.alert_threshold.error_rate_threshold
            })
        
        # 更新活跃告警
        self.active_alerts = new_alerts
        
        # 记录告警
        if new_alerts:
            for alert in new_alerts:
                logger.warning(f"⚠️ 性能告警: {alert['message']}")
    
    async def _cleanup_old_data(self):
        """清理过期数据"""
        # deque会自动限制长度，这里主要是清理其他可能的过期数据
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        
        # 清理过期的响应时间记录（这里简化处理）
        if len(self.response_times) > 1000:
            # 保留最近的1000个记录
            while len(self.response_times) > 1000:
                self.response_times.popleft()
    
    def record_request(self, response_time_ms: float, is_error: bool = False):
        """记录请求性能数据"""
        self.request_count += 1
        self.response_times.append(response_time_ms)
        
        if is_error:
            self.error_count += 1
        
        logger.debug(f"记录请求: 响应时间={response_time_ms:.2f}ms, 错误={is_error}")
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """获取当前性能指标"""
        if not self.metrics_history:
            return {"error": "暂无性能数据"}
        
        latest_metric = self.metrics_history[-1]
        
        return {
            "current": asdict(latest_metric),
            "alerts": self.active_alerts,
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
        
        # 计算统计指标
        metrics_data = [asdict(m) for m in self.metrics_history]
        
        # 最近1小时的数据
        recent_metrics = [m for m in self.metrics_history 
                         if datetime.fromisoformat(m.timestamp) > datetime.now() - timedelta(hours=1)]
        
        if recent_metrics:
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            avg_response_time = sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics)
            max_cpu = max(m.cpu_percent for m in recent_metrics)
            max_memory = max(m.memory_percent for m in recent_metrics)
        else:
            avg_cpu = avg_memory = avg_response_time = max_cpu = max_memory = 0
        
        return {
            "summary": {
                "total_data_points": len(self.metrics_history),
                "recent_hour_points": len(recent_metrics),
                "avg_cpu_1h": round(avg_cpu, 2),
                "avg_memory_1h": round(avg_memory, 2),
                "avg_response_time_1h": round(avg_response_time, 2),
                "max_cpu_1h": round(max_cpu, 2),
                "max_memory_1h": round(max_memory, 2)
            },
            "current_alerts": self.active_alerts,
            "request_stats": {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "current_error_rate": self._calculate_error_rate()
            },
            "thresholds": asdict(self.alert_threshold),
            "last_updated": datetime.now().isoformat()
        }
    
    async def get_metrics_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """获取指定时间范围的历史指标"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_metrics = [
            asdict(m) for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
        
        return filtered_metrics
    
    def export_metrics_to_file(self, file_path: str):
        """导出性能指标到文件"""
        try:
            metrics_data = [asdict(m) for m in self.metrics_history]
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_metrics": len(metrics_data),
                "collection_interval": self.collection_interval,
                "retention_hours": self.retention_hours,
                "metrics": metrics_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"性能指标已导出到: {file_path}")
            
        except Exception as e:
            logger.error(f"性能指标导出失败: {e}")


# 全局性能监控器实例
_global_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


async def start_background_monitoring():
    """启动后台性能监控"""
    monitor = get_performance_monitor()
    await monitor.start_monitoring()


if __name__ == "__main__":
    # 直接运行性能监控器
    async def main():
        monitor = PerformanceMonitor(collection_interval=10)  # 10秒收集一次
        
        # 启动监控
        monitoring_task = asyncio.create_task(monitor.start_monitoring())
        
        # 模拟一些请求数据
        async def simulate_requests():
            import random
            for i in range(100):
                response_time = random.uniform(100, 2000)  # 100ms到2s
                is_error = random.random() < 0.02  # 2%错误率
                monitor.record_request(response_time, is_error)
                await asyncio.sleep(1)
        
        # 启动模拟请求
        simulation_task = asyncio.create_task(simulate_requests())
        
        # 等待一段时间后停止
        await asyncio.sleep(60)  # 运行1分钟
        monitor.stop_monitoring()
        
        # 等待任务完成
        await asyncio.gather(monitoring_task, simulation_task, return_exceptions=True)
        
        # 输出性能摘要
        summary = await monitor.get_performance_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    asyncio.run(main())
