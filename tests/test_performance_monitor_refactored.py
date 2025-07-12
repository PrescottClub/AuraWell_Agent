"""
重构后性能监控器测试套件
专门测试策略模式和组合模式的新架构
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

# 项目导入
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from aurawell.monitoring.performance_monitor_refactored import (
    PerformanceMonitorRefactored,
    PerformanceMetric,
    AlertThreshold,
    SystemMetricCollector,
    NetworkMetricCollector,
    ApplicationMetricCollector,
    AlertManager,
    CPUAlertStrategy,
    MemoryAlertStrategy,
    DiskAlertStrategy
)


class TestPerformanceMonitorRefactored:
    """重构后性能监控器测试类"""
    
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
        """创建重构后的性能监控器实例"""
        monitor = PerformanceMonitorRefactored(
            collection_interval=1,
            retention_hours=1,
            alert_threshold=alert_threshold
        )
        yield monitor
        monitor.stop_monitoring()
    
    @pytest.fixture
    def sample_metric(self):
        """创建样本性能指标"""
        return PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            cpu_percent=45.5,
            memory_percent=65.2,
            disk_usage_percent=72.8,
            response_time_ms=150.0,
            error_rate=0.02,
            active_connections=5
        )
    
    # ============================================================================
    # 策略模式测试：指标收集器
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_system_metric_collector_success(self):
        """测试系统指标收集器成功场景"""
        with patch('aurawell.monitoring.performance_monitor_refactored.psutil') as mock_psutil:
            # 模拟psutil返回值
            mock_psutil.cpu_percent.return_value = 55.5
            
            mock_memory = Mock()
            mock_memory.percent = 70.2
            mock_psutil.virtual_memory.return_value = mock_memory
            
            mock_disk = Mock()
            mock_disk.percent = 80.8
            mock_psutil.disk_usage.return_value = mock_disk
            
            # 执行测试
            collector = SystemMetricCollector()
            result = await collector.collect()
            
            # 验证结果
            assert result['cpu_percent'] == 55.5
            assert result['memory_percent'] == 70.2
            assert result['disk_usage_percent'] == 80.8
            
            # 验证psutil被正确调用
            mock_psutil.cpu_percent.assert_called_once_with(interval=1)
            mock_psutil.virtual_memory.assert_called_once()
            mock_psutil.disk_usage.assert_called_once_with('/')
    
    @pytest.mark.asyncio
    async def test_system_metric_collector_failure(self):
        """测试系统指标收集器异常处理"""
        with patch('aurawell.monitoring.performance_monitor_refactored.psutil') as mock_psutil:
            # 模拟psutil抛出异常
            mock_psutil.cpu_percent.side_effect = Exception("CPU监控失败")
            
            collector = SystemMetricCollector()
            result = await collector.collect()
            
            # 验证错误处理
            assert result['cpu_percent'] == 0.0
            assert result['memory_percent'] == 0.0
            assert result['disk_usage_percent'] == 0.0
    
    @pytest.mark.asyncio
    async def test_network_metric_collector(self):
        """测试网络指标收集器"""
        with patch('aurawell.monitoring.performance_monitor_refactored.psutil') as mock_psutil:
            # 模拟网络连接
            mock_connections = [
                Mock(status='ESTABLISHED'),
                Mock(status='ESTABLISHED'),
                Mock(status='LISTEN'),
                Mock(status='ESTABLISHED')
            ]
            mock_psutil.net_connections.return_value = mock_connections
            
            collector = NetworkMetricCollector()
            result = await collector.collect()
            
            # 验证结果（3个ESTABLISHED连接）
            assert result['active_connections'] == 3
            mock_psutil.net_connections.assert_called_once_with(kind='inet')
    
    @pytest.mark.asyncio
    async def test_application_metric_collector(self):
        """测试应用指标收集器"""
        from collections import deque
        
        # 准备测试数据
        response_times = deque([100, 200, 150, 300, 250])
        request_count = 10
        error_count = 1
        
        collector = ApplicationMetricCollector(response_times, request_count, error_count)
        result = await collector.collect()
        
        # 验证计算结果
        expected_avg_response_time = sum(response_times) / len(response_times)
        expected_error_rate = error_count / request_count
        
        assert result['response_time_ms'] == expected_avg_response_time
        assert result['error_rate'] == expected_error_rate
    
    @pytest.mark.asyncio
    async def test_performance_monitor_with_injected_collectors(self, performance_monitor):
        """测试通过依赖注入模拟收集器的策略模式"""
        # 创建模拟收集器
        mock_system_collector = AsyncMock()
        mock_system_collector.collect.return_value = {
            'cpu_percent': 88.8,
            'memory_percent': 77.7,
            'disk_usage_percent': 66.6
        }
        
        mock_network_collector = AsyncMock()
        mock_network_collector.collect.return_value = {'active_connections': 10}
        
        mock_app_collector = AsyncMock()
        mock_app_collector.collect.return_value = {
            'response_time_ms': 500.0,
            'error_rate': 0.05
        }
        
        # 注入模拟收集器
        performance_monitor.collectors = [
            mock_system_collector,
            mock_network_collector,
            mock_app_collector
        ]
        
        # 执行指标收集
        await performance_monitor._collect_and_analyze_metrics()
        
        # 验证所有收集器都被调用
        mock_system_collector.collect.assert_called_once()
        mock_network_collector.collect.assert_called_once()
        mock_app_collector.collect.assert_called_once()
        
        # 验证指标被正确存储
        assert len(performance_monitor.metrics_history) == 1
        latest_metric = performance_monitor.metrics_history[0]
        
        assert latest_metric.cpu_percent == 88.8
        assert latest_metric.memory_percent == 77.7
        assert latest_metric.active_connections == 10
        assert latest_metric.response_time_ms == 500.0
        assert latest_metric.error_rate == 0.05
    
    # ============================================================================
    # 组合模式测试：告警管理器
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_alert_manager_composition_pattern(self, sample_metric, alert_threshold):
        """测试告警管理器的组合模式"""
        # 创建模拟告警策略
        mock_cpu_strategy = Mock(spec=CPUAlertStrategy)
        mock_memory_strategy = Mock(spec=MemoryAlertStrategy)
        mock_disk_strategy = Mock(spec=DiskAlertStrategy)
        
        # 配置模拟策略的返回值
        mock_cpu_strategy.check_alert.return_value = None  # 无告警
        mock_memory_strategy.check_alert.return_value = {
            "type": "memory_high",
            "message": "内存使用率过高",
            "severity": "warning"
        }
        mock_disk_strategy.check_alert.return_value = None  # 无告警
        
        # 创建告警管理器并注入模拟策略
        alert_manager = AlertManager()
        alert_manager.strategies = [mock_cpu_strategy, mock_memory_strategy, mock_disk_strategy]
        
        # 执行告警检查
        await alert_manager.check_all_alerts(sample_metric, alert_threshold)
        
        # 验证所有策略都被调用
        mock_cpu_strategy.check_alert.assert_called_once_with(sample_metric, alert_threshold)
        mock_memory_strategy.check_alert.assert_called_once_with(sample_metric, alert_threshold)
        mock_disk_strategy.check_alert.assert_called_once_with(sample_metric, alert_threshold)
        
        # 验证告警结果
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0]["type"] == "memory_high"
        assert active_alerts[0]["severity"] == "warning"
    
    @pytest.mark.asyncio
    async def test_alert_manager_multiple_alerts(self, sample_metric, alert_threshold):
        """测试告警管理器处理多个告警"""
        # 创建模拟策略，都返回告警
        mock_strategies = []
        expected_alerts = []
        
        for i, alert_type in enumerate(["cpu_high", "memory_high", "disk_high"]):
            mock_strategy = Mock()
            alert = {
                "type": alert_type,
                "message": f"告警{i+1}",
                "severity": "warning"
            }
            mock_strategy.check_alert.return_value = alert
            mock_strategies.append(mock_strategy)
            expected_alerts.append(alert)
        
        # 创建告警管理器
        alert_manager = AlertManager()
        alert_manager.strategies = mock_strategies
        
        # 执行告警检查
        await alert_manager.check_all_alerts(sample_metric, alert_threshold)
        
        # 验证所有告警都被收集
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) == 3
        
        for i, alert in enumerate(active_alerts):
            assert alert["type"] == expected_alerts[i]["type"]
            assert alert["message"] == expected_alerts[i]["message"]
    
    @pytest.mark.asyncio
    async def test_alert_manager_add_strategy_dynamically(self, sample_metric, alert_threshold):
        """测试动态添加告警策略"""
        alert_manager = AlertManager()
        
        # 初始状态：没有策略
        initial_strategy_count = len(alert_manager.strategies)
        
        # 动态添加策略
        custom_strategy = Mock()
        custom_strategy.check_alert.return_value = {
            "type": "custom_alert",
            "message": "自定义告警",
            "severity": "critical"
        }
        
        alert_manager.add_strategy(custom_strategy)
        
        # 验证策略被添加
        assert len(alert_manager.strategies) == initial_strategy_count + 1
        
        # 执行告警检查
        await alert_manager.check_all_alerts(sample_metric, alert_threshold)
        
        # 验证新策略被调用
        custom_strategy.check_alert.assert_called_once()
        
        # 验证自定义告警被触发
        active_alerts = alert_manager.get_active_alerts()
        custom_alerts = [alert for alert in active_alerts if alert["type"] == "custom_alert"]
        assert len(custom_alerts) == 1
    
    # ============================================================================
    # 具体告警策略测试
    # ============================================================================
    
    @pytest.mark.parametrize("cpu_percent,threshold,should_alert", [
        (70.0, 75.0, False),  # 低于阈值
        (75.0, 75.0, False),  # 等于阈值
        (80.0, 75.0, True),   # 高于阈值
        (95.0, 75.0, True)    # 远高于阈值
    ])
    def test_cpu_alert_strategy(self, cpu_percent, threshold, should_alert):
        """参数化测试CPU告警策略"""
        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=50.0,
            disk_usage_percent=50.0,
            response_time_ms=100.0,
            error_rate=0.01,
            active_connections=5
        )
        
        alert_threshold = AlertThreshold(cpu_threshold=threshold)
        strategy = CPUAlertStrategy()
        
        result = strategy.check_alert(metric, alert_threshold)
        
        if should_alert:
            assert result is not None
            assert result["type"] == "cpu_high"
            assert result["severity"] == "warning"
            assert result["value"] == cpu_percent
            assert result["threshold"] == threshold
        else:
            assert result is None
    
    def test_memory_alert_strategy(self):
        """测试内存告警策略"""
        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            cpu_percent=50.0,
            memory_percent=90.0,  # 高内存使用率
            disk_usage_percent=50.0,
            response_time_ms=100.0,
            error_rate=0.01,
            active_connections=5
        )
        
        alert_threshold = AlertThreshold(memory_threshold=85.0)
        strategy = MemoryAlertStrategy()
        
        result = strategy.check_alert(metric, alert_threshold)
        
        assert result is not None
        assert result["type"] == "memory_high"
        assert result["severity"] == "warning"
        assert result["value"] == 90.0
    
    def test_disk_alert_strategy(self):
        """测试磁盘告警策略"""
        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            cpu_percent=50.0,
            memory_percent=50.0,
            disk_usage_percent=95.0,  # 高磁盘使用率
            response_time_ms=100.0,
            error_rate=0.01,
            active_connections=5
        )
        
        alert_threshold = AlertThreshold(disk_threshold=90.0)
        strategy = DiskAlertStrategy()
        
        result = strategy.check_alert(metric, alert_threshold)
        
        assert result is not None
        assert result["type"] == "disk_high"
        assert result["severity"] == "critical"  # 磁盘告警是critical级别
        assert result["value"] == 95.0
    
    # ============================================================================
    # 集成测试：完整的监控流程
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_complete_monitoring_workflow_with_mocked_dependencies(self, performance_monitor):
        """测试完整的监控工作流程（模拟所有依赖）"""
        # 模拟系统指标
        with patch('aurawell.monitoring.performance_monitor_refactored.psutil') as mock_psutil:
            mock_psutil.cpu_percent.return_value = 85.0  # 触发CPU告警
            
            mock_memory = Mock()
            mock_memory.percent = 90.0  # 触发内存告警
            mock_psutil.virtual_memory.return_value = mock_memory
            
            mock_disk = Mock()
            mock_disk.percent = 70.0  # 不触发磁盘告警
            mock_psutil.disk_usage.return_value = mock_disk
            
            mock_psutil.net_connections.return_value = [Mock(status='ESTABLISHED')] * 8
            
            # 添加一些应用指标
            performance_monitor.record_request(200.0, False)
            performance_monitor.record_request(300.0, True)
            
            # 执行完整的指标收集和分析
            await performance_monitor._collect_and_analyze_metrics()
            
            # 验证指标被收集
            assert len(performance_monitor.metrics_history) == 1
            latest_metric = performance_monitor.metrics_history[0]
            
            assert latest_metric.cpu_percent == 85.0
            assert latest_metric.memory_percent == 90.0
            assert latest_metric.disk_usage_percent == 70.0
            assert latest_metric.active_connections == 8
            
            # 验证告警被触发
            active_alerts = performance_monitor.alert_manager.get_active_alerts()
            alert_types = [alert["type"] for alert in active_alerts]
            
            assert "cpu_high" in alert_types
            assert "memory_high" in alert_types
            assert "disk_high" not in alert_types  # 磁盘使用率未超过阈值
    
    @pytest.mark.asyncio
    async def test_performance_summary_with_strategy_pattern(self, performance_monitor):
        """测试性能摘要生成（验证策略模式的数据流）"""
        # 模拟收集多个指标点
        with patch.object(performance_monitor, 'collectors') as mock_collectors:
            # 模拟收集器返回不同的指标
            mock_collector = AsyncMock()
            mock_collector.collect.side_effect = [
                {'cpu_percent': 60.0, 'memory_percent': 70.0, 'disk_usage_percent': 50.0, 
                 'response_time_ms': 100.0, 'error_rate': 0.01, 'active_connections': 5},
                {'cpu_percent': 70.0, 'memory_percent': 75.0, 'disk_usage_percent': 55.0,
                 'response_time_ms': 150.0, 'error_rate': 0.02, 'active_connections': 6},
                {'cpu_percent': 65.0, 'memory_percent': 72.0, 'disk_usage_percent': 52.0,
                 'response_time_ms': 120.0, 'error_rate': 0.015, 'active_connections': 7}
            ]
            mock_collectors.__iter__.return_value = [mock_collector]
            
            # 收集多个指标点
            for _ in range(3):
                await performance_monitor._collect_and_analyze_metrics()
                await asyncio.sleep(0.01)  # 小延迟确保时间戳不同
            
            # 获取性能摘要
            summary = await performance_monitor.get_performance_summary()
            
            # 验证摘要数据
            assert summary['summary']['total_data_points'] == 3
            assert 'avg_cpu_1h' in summary['summary']
            assert 'avg_memory_1h' in summary['summary']
            
            # 验证平均值计算
            expected_avg_cpu = (60.0 + 70.0 + 65.0) / 3
            assert abs(summary['summary']['avg_cpu_1h'] - expected_avg_cpu) < 0.01


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
    pytest.main([__file__, "-v", "--tb=short", "--cov=aurawell.monitoring.performance_monitor_refactored"])
