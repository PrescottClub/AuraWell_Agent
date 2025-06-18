"""
监控系统单元测试

测试指标收集、性能监控等功能
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock

from aurawell.monitoring.metrics import (
    MetricsCollector,
    PerformanceMetrics,
    MetricPoint,
    get_metrics_collector,
    track_request_performance,
    record_business_metric,
    record_database_operation
)
from aurawell.monitoring.structured_logging import (
    StructuredLogger,
    LogContext,
    get_structured_logger,
    log_request,
    log_database_operation,
    log_business_event
)


class TestMetricsCollector:
    """指标收集器测试"""

    def test_record_metric(self):
        """测试记录指标"""
        collector = MetricsCollector()
        
        # 记录指标
        collector.record_metric("test.metric", 100.0, {"tag": "value"}, "ms")
        
        # 验证指标被记录
        metrics = collector.get_recent_metrics("test.metric")
        assert len(metrics) == 1
        assert metrics[0].name == "test.metric"
        assert metrics[0].value == 100.0
        assert metrics[0].tags == {"tag": "value"}
        assert metrics[0].unit == "ms"

    def test_record_request_performance(self):
        """测试记录请求性能"""
        collector = MetricsCollector()
        endpoint = "/api/v1/test"
        
        # 记录请求开始
        collector.record_request_start(endpoint)
        assert collector.performance_metrics[endpoint].active_requests == 1
        
        # 记录请求结束
        collector.record_request_end(endpoint, 150.0, success=True)
        
        # 验证性能指标
        metrics = collector.performance_metrics[endpoint]
        assert metrics.request_count == 1
        assert metrics.error_count == 0
        assert metrics.total_response_time == 150.0
        assert metrics.avg_response_time == 150.0
        assert metrics.min_response_time == 150.0
        assert metrics.max_response_time == 150.0
        assert metrics.active_requests == 0

    def test_record_request_error(self):
        """测试记录请求错误"""
        collector = MetricsCollector()
        endpoint = "/api/v1/test"
        
        # 记录失败的请求
        collector.record_request_start(endpoint)
        collector.record_request_end(endpoint, 200.0, success=False)
        
        # 验证错误统计
        metrics = collector.performance_metrics[endpoint]
        assert metrics.request_count == 1
        assert metrics.error_count == 1
        assert metrics.error_rate == 1.0

    def test_performance_summary(self):
        """测试性能摘要"""
        collector = MetricsCollector()
        
        # 记录多个请求
        endpoints = ["/api/v1/test1", "/api/v1/test2"]
        for endpoint in endpoints:
            collector.record_request_start(endpoint)
            collector.record_request_end(endpoint, 100.0, success=True)
        
        # 获取性能摘要
        summary = collector.get_performance_summary()
        
        # 验证摘要
        assert len(summary) == 2
        for endpoint in endpoints:
            assert endpoint in summary
            assert summary[endpoint]["request_count"] == 1
            assert summary[endpoint]["error_count"] == 0

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.net_io_counters')
    @patch('psutil.Process')
    def test_collect_system_metrics(self, mock_process, mock_net, mock_disk, mock_memory, mock_cpu):
        """测试收集系统指标"""
        # 设置模拟
        mock_cpu.return_value = 50.0
        
        mock_memory_info = MagicMock()
        mock_memory_info.percent = 60.0
        mock_memory_info.available = 1024 * 1024 * 1024  # 1GB
        mock_memory.return_value = mock_memory_info
        
        mock_disk_info = MagicMock()
        mock_disk_info.percent = 70.0
        mock_disk_info.free = 10 * 1024 * 1024 * 1024  # 10GB
        mock_disk.return_value = mock_disk_info
        
        mock_net_info = MagicMock()
        mock_net_info.bytes_sent = 1000
        mock_net_info.bytes_recv = 2000
        mock_net.return_value = mock_net_info
        
        mock_process_instance = MagicMock()
        mock_process_memory = MagicMock()
        mock_process_memory.rss = 100 * 1024 * 1024  # 100MB
        mock_process_instance.memory_info.return_value = mock_process_memory
        mock_process_instance.cpu_percent.return_value = 25.0
        mock_process.return_value = mock_process_instance
        
        # 收集系统指标
        collector = MetricsCollector()
        collector.collect_system_metrics()
        
        # 验证指标被记录
        cpu_metrics = collector.get_recent_metrics("system.cpu.usage")
        assert len(cpu_metrics) == 1
        assert cpu_metrics[0].value == 50.0

    def test_health_status_healthy(self):
        """测试健康状态 - 正常"""
        with patch('psutil.cpu_percent', return_value=30.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory_info = MagicMock()
            mock_memory_info.percent = 40.0
            mock_memory.return_value = mock_memory_info
            
            mock_disk_info = MagicMock()
            mock_disk_info.percent = 50.0
            mock_disk.return_value = mock_disk_info
            
            collector = MetricsCollector()
            health = collector.get_health_status()
            
            assert health["status"] == "healthy"
            assert len(health["issues"]) == 0

    def test_health_status_warning(self):
        """测试健康状态 - 警告"""
        with patch('psutil.cpu_percent', return_value=85.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory_info = MagicMock()
            mock_memory_info.percent = 40.0
            mock_memory.return_value = mock_memory_info
            
            mock_disk_info = MagicMock()
            mock_disk_info.percent = 50.0
            mock_disk.return_value = mock_disk_info
            
            collector = MetricsCollector()
            health = collector.get_health_status()
            
            assert health["status"] == "warning"
            assert len(health["issues"]) > 0
            assert any("High CPU usage" in issue for issue in health["issues"])

    @pytest.mark.asyncio
    async def test_monitoring_lifecycle(self):
        """测试监控生命周期"""
        collector = MetricsCollector()
        
        # 开始监控
        await collector.start_monitoring(interval=0.1)
        assert collector._monitoring_active is True
        
        # 等待一小段时间
        await asyncio.sleep(0.2)
        
        # 停止监控
        await collector.stop_monitoring()
        assert collector._monitoring_active is False


class TestTrackRequestPerformance:
    """请求性能跟踪测试"""

    @pytest.mark.asyncio
    async def test_track_request_success(self):
        """测试跟踪成功请求"""
        collector = get_metrics_collector()
        endpoint = "/api/v1/test"
        
        # 清除之前的数据
        collector.performance_metrics.clear()
        
        async with track_request_performance(endpoint):
            await asyncio.sleep(0.01)  # 模拟处理时间
        
        # 验证性能被记录
        metrics = collector.performance_metrics[endpoint]
        assert metrics.request_count == 1
        assert metrics.error_count == 0
        assert metrics.avg_response_time > 0

    @pytest.mark.asyncio
    async def test_track_request_error(self):
        """测试跟踪失败请求"""
        collector = get_metrics_collector()
        endpoint = "/api/v1/test"
        
        # 清除之前的数据
        collector.performance_metrics.clear()
        
        with pytest.raises(ValueError):
            async with track_request_performance(endpoint):
                raise ValueError("Test error")
        
        # 验证错误被记录
        metrics = collector.performance_metrics[endpoint]
        assert metrics.request_count == 1
        assert metrics.error_count == 1
        assert metrics.error_rate == 1.0


class TestStructuredLogger:
    """结构化日志测试"""

    def test_logger_creation(self):
        """测试日志记录器创建"""
        context = LogContext(request_id="req-123", user_id="user-456")
        logger = StructuredLogger("test.logger", context)
        
        assert logger.logger.name == "test.logger"
        assert logger.context.request_id == "req-123"
        assert logger.context.user_id == "user-456"

    def test_logger_with_context(self):
        """测试带上下文的日志记录器"""
        logger = StructuredLogger("test.logger")
        new_logger = logger.with_context(request_id="req-789", operation="test")
        
        assert new_logger.context.request_id == "req-789"
        assert new_logger.context.operation == "test"

    def test_get_structured_logger(self):
        """测试获取结构化日志记录器"""
        logger1 = get_structured_logger("test.logger")
        logger2 = get_structured_logger("test.logger")
        
        # 应该返回相同的实例
        assert logger1 is logger2

    @patch('aurawell.monitoring.structured_logging.logging.getLogger')
    def test_log_request(self, mock_get_logger):
        """测试记录请求日志"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_request(
            method="POST",
            path="/api/v1/test",
            status_code=200,
            response_time=150.0,
            request_id="req-123",
            user_id="user-456"
        )
        
        # 验证日志被调用
        mock_logger.log.assert_called_once()

    @patch('aurawell.monitoring.structured_logging.logging.getLogger')
    def test_log_database_operation(self, mock_get_logger):
        """测试记录数据库操作日志"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_database_operation(
            operation="INSERT",
            table="families",
            duration=50.0,
            success=True
        )
        
        # 验证日志被调用
        mock_logger.log.assert_called_once()

    @patch('aurawell.monitoring.structured_logging.logging.getLogger')
    def test_log_business_event(self, mock_get_logger):
        """测试记录业务事件日志"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_business_event(
            event_type="family_created",
            event_data={"family_id": "fam-123", "member_count": 1},
            user_id="user-456"
        )
        
        # 验证日志被调用
        mock_logger.log.assert_called_once()


class TestBusinessMetrics:
    """业务指标测试"""

    def test_record_business_metric(self):
        """测试记录业务指标"""
        collector = get_metrics_collector()
        
        record_business_metric("family.created", 1, {"user_type": "premium"})
        
        # 验证指标被记录
        metrics = collector.get_recent_metrics("business.family.created")
        assert len(metrics) > 0
        assert metrics[-1].value == 1
        assert metrics[-1].tags == {"user_type": "premium"}

    def test_record_database_operation_metric(self):
        """测试记录数据库操作指标"""
        collector = get_metrics_collector()
        
        record_database_operation("SELECT", 25.0, success=True)
        
        # 验证指标被记录
        duration_metrics = collector.get_recent_metrics("database.operation.duration")
        count_metrics = collector.get_recent_metrics("database.operation.count")
        
        assert len(duration_metrics) > 0
        assert len(count_metrics) > 0
        assert duration_metrics[-1].value == 25.0
        assert count_metrics[-1].value == 1
