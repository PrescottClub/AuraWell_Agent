"""
性能监控器测试套件
测试性能指标收集、告警系统和监控功能
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from collections import deque

# 项目导入
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from aurawell.monitoring.performance_monitor import (
    PerformanceMonitor, 
    PerformanceMetric, 
    AlertThreshold,
    get_performance_monitor
)


class TestPerformanceMonitor:
    """性能监控器测试类"""
    
    @pytest.fixture
    def alert_threshold(self):
        """创建测试用的告警阈值"""
        return AlertThreshold(
            cpu_threshold=75.0,
            memory_threshold=80.0,
            disk_threshold=85.0,
            response_time_threshold=3000.0,
            error_rate_threshold=0.03
        )
    
    @pytest.fixture
    def performance_monitor(self, alert_threshold):
        """创建性能监控器实例"""
        monitor = PerformanceMonitor(
            collection_interval=1,  # 1秒收集间隔，便于测试
            retention_hours=1,      # 1小时保留时间
            alert_threshold=alert_threshold
        )
        yield monitor
        # 清理
        monitor.stop_monitoring()
    
    @pytest.fixture
    def mock_psutil(self):
        """模拟psutil系统监控库"""
        with patch('aurawell.monitoring.performance_monitor.psutil') as mock:
            # 模拟CPU使用率
            mock.cpu_percent.return_value = 45.5
            
            # 模拟内存信息
            mock_memory = Mock()
            mock_memory.percent = 65.2
            mock.virtual_memory.return_value = mock_memory
            
            # 模拟磁盘信息
            mock_disk = Mock()
            mock_disk.percent = 72.8
            mock.disk_usage.return_value = mock_disk
            
            # 模拟网络连接
            mock_conn = Mock()
            mock_conn.status = 'ESTABLISHED'
            mock.net_connections.return_value = [mock_conn] * 5  # 5个活跃连接
            
            yield mock
    
    # ============================================================================
    # 性能指标收集测试
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_collect_metrics_success(self, performance_monitor, mock_psutil):
        """测试性能指标收集成功场景"""
        # 添加一些模拟的响应时间数据
        performance_monitor.response_times.extend([100, 200, 150, 300, 250])
        performance_monitor.request_count = 10
        performance_monitor.error_count = 1
        
        # 执行指标收集
        await performance_monitor._collect_metrics()
        
        # 验证指标被收集
        assert len(performance_monitor.metrics_history) == 1
        
        metric = performance_monitor.metrics_history[0]
        assert isinstance(metric, PerformanceMetric)
        assert metric.cpu_percent == 45.5
        assert metric.memory_percent == 65.2
        assert metric.disk_usage_percent == 72.8
        assert metric.active_connections == 5
        
        # 验证计算的指标
        expected_avg_response_time = sum([100, 200, 150, 300, 250]) / 5
        assert metric.response_time_ms == expected_avg_response_time
        assert metric.error_rate == 0.1  # 1/10
    
    @pytest.mark.asyncio
    async def test_collect_metrics_with_empty_data(self, performance_monitor, mock_psutil):
        """测试没有请求数据时的指标收集"""
        # 不添加任何请求数据
        await performance_monitor._collect_metrics()
        
        metric = performance_monitor.metrics_history[0]
        assert metric.response_time_ms == 0.0
        assert metric.error_rate == 0.0
        assert metric.active_connections == 5
    
    @pytest.mark.asyncio
    async def test_collect_metrics_psutil_error(self, performance_monitor):
        """测试psutil调用失败的错误处理"""
        with patch('aurawell.monitoring.performance_monitor.psutil') as mock_psutil:
            mock_psutil.cpu_percent.side_effect = Exception("CPU监控失败")
            
            # 应该不抛出异常，而是记录错误日志
            await performance_monitor._collect_metrics()
            
            # 验证没有添加指标数据
            assert len(performance_monitor.metrics_history) == 0
    
    # ============================================================================
    # 告警系统测试
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_check_alerts_cpu_high(self, performance_monitor, mock_psutil):
        """测试CPU使用率过高告警"""
        # 设置高CPU使用率
        mock_psutil.cpu_percent.return_value = 85.0  # 超过75%阈值
        
        await performance_monitor._collect_metrics()
        await performance_monitor._check_alerts()
        
        # 验证告警被触发
        assert len(performance_monitor.active_alerts) > 0
        
        cpu_alert = next((alert for alert in performance_monitor.active_alerts 
                         if alert['type'] == 'cpu_high'), None)
        assert cpu_alert is not None
        assert cpu_alert['severity'] == 'warning'
        assert cpu_alert['value'] == 85.0
        assert cpu_alert['threshold'] == 75.0
    
    @pytest.mark.asyncio
    async def test_check_alerts_memory_high(self, performance_monitor, mock_psutil):
        """测试内存使用率过高告警"""
        # 设置高内存使用率
        mock_memory = Mock()
        mock_memory.percent = 90.0  # 超过80%阈值
        mock_psutil.virtual_memory.return_value = mock_memory
        
        await performance_monitor._collect_metrics()
        await performance_monitor._check_alerts()
        
        memory_alert = next((alert for alert in performance_monitor.active_alerts 
                           if alert['type'] == 'memory_high'), None)
        assert memory_alert is not None
        assert memory_alert['severity'] == 'warning'
        assert memory_alert['value'] == 90.0
    
    @pytest.mark.asyncio
    async def test_check_alerts_disk_critical(self, performance_monitor, mock_psutil):
        """测试磁盘使用率严重告警"""
        # 设置极高磁盘使用率
        mock_disk = Mock()
        mock_disk.percent = 95.0  # 超过85%阈值
        mock_psutil.disk_usage.return_value = mock_disk
        
        await performance_monitor._collect_metrics()
        await performance_monitor._check_alerts()
        
        disk_alert = next((alert for alert in performance_monitor.active_alerts 
                          if alert['type'] == 'disk_high'), None)
        assert disk_alert is not None
        assert disk_alert['severity'] == 'critical'
        assert disk_alert['value'] == 95.0
    
    @pytest.mark.asyncio
    async def test_check_alerts_response_time_high(self, performance_monitor, mock_psutil):
        """测试响应时间过长告警"""
        # 添加高响应时间数据
        performance_monitor.response_times.extend([5000, 6000, 4500])  # 超过3000ms阈值
        
        await performance_monitor._collect_metrics()
        await performance_monitor._check_alerts()
        
        response_alert = next((alert for alert in performance_monitor.active_alerts 
                             if alert['type'] == 'response_time_high'), None)
        assert response_alert is not None
        assert response_alert['severity'] == 'warning'
        assert response_alert['value'] > 3000.0
    
    @pytest.mark.asyncio
    async def test_check_alerts_error_rate_high(self, performance_monitor, mock_psutil):
        """测试错误率过高告警"""
        # 设置高错误率
        performance_monitor.request_count = 100
        performance_monitor.error_count = 5  # 5%错误率，超过3%阈值
        
        await performance_monitor._collect_metrics()
        await performance_monitor._check_alerts()
        
        error_alert = next((alert for alert in performance_monitor.active_alerts 
                          if alert['type'] == 'error_rate_high'), None)
        assert error_alert is not None
        assert error_alert['severity'] == 'critical'
        assert error_alert['value'] == 0.05
    
    @pytest.mark.asyncio
    async def test_no_alerts_when_metrics_normal(self, performance_monitor, mock_psutil):
        """测试正常指标时不触发告警"""
        # 所有指标都在正常范围内（使用默认的mock值）
        await performance_monitor._collect_metrics()
        await performance_monitor._check_alerts()
        
        # 验证没有告警
        assert len(performance_monitor.active_alerts) == 0
    
    # ============================================================================
    # 请求记录测试
    # ============================================================================
    
    def test_record_request_success(self, performance_monitor):
        """测试成功请求记录"""
        initial_count = performance_monitor.request_count
        
        performance_monitor.record_request(150.5, is_error=False)
        
        assert performance_monitor.request_count == initial_count + 1
        assert performance_monitor.error_count == 0
        assert 150.5 in performance_monitor.response_times
    
    def test_record_request_error(self, performance_monitor):
        """测试错误请求记录"""
        initial_error_count = performance_monitor.error_count
        
        performance_monitor.record_request(2000.0, is_error=True)
        
        assert performance_monitor.error_count == initial_error_count + 1
        assert 2000.0 in performance_monitor.response_times
    
    def test_record_multiple_requests(self, performance_monitor):
        """测试多个请求记录"""
        response_times = [100, 200, 300, 150, 250]
        errors = [False, True, False, False, True]
        
        for rt, is_error in zip(response_times, errors):
            performance_monitor.record_request(rt, is_error)
        
        assert performance_monitor.request_count == 5
        assert performance_monitor.error_count == 2
        assert len(performance_monitor.response_times) == 5
    
    # ============================================================================
    # 数据获取和摘要测试
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_get_current_metrics(self, performance_monitor, mock_psutil):
        """测试获取当前指标"""
        # 先收集一些指标
        await performance_monitor._collect_metrics()
        
        metrics = await performance_monitor.get_current_metrics()
        
        assert 'current' in metrics
        assert 'alerts' in metrics
        assert 'monitoring_status' in metrics
        
        current = metrics['current']
        assert 'cpu_percent' in current
        assert 'memory_percent' in current
        assert current['cpu_percent'] == 45.5
    
    @pytest.mark.asyncio
    async def test_get_current_metrics_no_data(self, performance_monitor):
        """测试没有数据时获取当前指标"""
        metrics = await performance_monitor.get_current_metrics()
        
        assert 'error' in metrics
        assert metrics['error'] == "暂无性能数据"
    
    @pytest.mark.asyncio
    async def test_get_performance_summary(self, performance_monitor, mock_psutil):
        """测试获取性能摘要"""
        # 添加一些测试数据
        performance_monitor.request_count = 50
        performance_monitor.error_count = 2
        
        # 收集多个指标点
        for _ in range(3):
            await performance_monitor._collect_metrics()
            await asyncio.sleep(0.1)  # 小延迟确保时间戳不同
        
        summary = await performance_monitor.get_performance_summary()
        
        assert 'summary' in summary
        assert 'current_alerts' in summary
        assert 'request_stats' in summary
        assert 'thresholds' in summary
        
        # 验证摘要数据
        summary_data = summary['summary']
        assert summary_data['total_data_points'] == 3
        assert 'avg_cpu_1h' in summary_data
        assert 'avg_memory_1h' in summary_data
        
        # 验证请求统计
        request_stats = summary['request_stats']
        assert request_stats['total_requests'] == 50
        assert request_stats['total_errors'] == 2
        assert request_stats['current_error_rate'] == 0.04
    
    @pytest.mark.asyncio
    async def test_get_metrics_history(self, performance_monitor, mock_psutil):
        """测试获取历史指标"""
        # 收集一些历史数据
        for _ in range(5):
            await performance_monitor._collect_metrics()
            await asyncio.sleep(0.1)
        
        history = await performance_monitor.get_metrics_history(hours=1)
        
        assert len(history) == 5
        for metric in history:
            assert 'timestamp' in metric
            assert 'cpu_percent' in metric
            assert 'memory_percent' in metric
    
    # ============================================================================
    # 监控生命周期测试
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, performance_monitor, mock_psutil):
        """测试监控启动和停止"""
        assert not performance_monitor.is_running
        
        # 启动监控（短时间运行）
        monitoring_task = asyncio.create_task(performance_monitor.start_monitoring())
        
        # 等待监控启动
        await asyncio.sleep(0.1)
        assert performance_monitor.is_running
        
        # 停止监控
        performance_monitor.stop_monitoring()
        
        # 等待任务完成
        await asyncio.sleep(0.2)
        assert not performance_monitor.is_running
        
        # 清理任务
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
    
    @pytest.mark.asyncio
    async def test_monitoring_data_collection_over_time(self, performance_monitor, mock_psutil):
        """测试监控数据随时间收集"""
        # 启动短期监控
        monitoring_task = asyncio.create_task(performance_monitor.start_monitoring())
        
        # 运行一段时间
        await asyncio.sleep(2.5)  # 运行2.5秒，应该收集2-3个数据点
        
        performance_monitor.stop_monitoring()
        
        # 验证收集了数据
        assert len(performance_monitor.metrics_history) >= 2
        assert performance_monitor.last_collection_time is not None
        
        # 清理
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
    
    # ============================================================================
    # 全局监控器测试
    # ============================================================================
    
    def test_get_performance_monitor_singleton(self):
        """测试全局性能监控器单例"""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()
        
        # 应该返回同一个实例
        assert monitor1 is monitor2
        assert isinstance(monitor1, PerformanceMonitor)
    
    # ============================================================================
    # 边界条件和错误处理测试
    # ============================================================================
    
    def test_alert_threshold_validation(self):
        """测试告警阈值验证"""
        # 测试默认阈值
        threshold = AlertThreshold()
        assert threshold.cpu_threshold == 80.0
        assert threshold.memory_threshold == 85.0
        
        # 测试自定义阈值
        custom_threshold = AlertThreshold(
            cpu_threshold=90.0,
            memory_threshold=95.0
        )
        assert custom_threshold.cpu_threshold == 90.0
        assert custom_threshold.memory_threshold == 95.0
    
    def test_performance_metric_creation(self):
        """测试性能指标数据类创建"""
        timestamp = datetime.now().isoformat()
        metric = PerformanceMetric(
            timestamp=timestamp,
            cpu_percent=50.0,
            memory_percent=60.0,
            disk_usage_percent=70.0,
            response_time_ms=200.0,
            error_rate=0.02,
            active_connections=10
        )
        
        assert metric.timestamp == timestamp
        assert metric.cpu_percent == 50.0
        assert metric.error_rate == 0.02
    
    def test_response_times_deque_limit(self, performance_monitor):
        """测试响应时间队列长度限制"""
        # 添加超过限制的响应时间数据
        for i in range(1500):  # 超过1000的限制
            performance_monitor.record_request(float(i), False)
        
        # 验证队列长度被限制
        assert len(performance_monitor.response_times) <= 1000


# ============================================================================
# 测试配置和辅助函数
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
