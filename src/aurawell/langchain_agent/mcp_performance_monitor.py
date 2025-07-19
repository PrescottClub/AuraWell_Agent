#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具性能监控系统
提供详细的性能指标收集、存储和告警功能
"""

import asyncio
import logging
import json
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """性能指标数据结构"""
    tool_name: str
    action: str
    execution_time: float
    success: bool
    timestamp: datetime
    mode_used: str
    error_message: Optional[str] = None
    parameters_hash: Optional[str] = None


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    condition: str  # 条件表达式
    threshold: float
    level: AlertLevel
    enabled: bool = True


class MCPPerformanceMonitor:
    """
    MCP工具性能监控器
    
    功能：
    - 实时性能指标收集
    - 历史数据存储
    - 告警规则管理
    - 性能报告生成
    """
    
    def __init__(self, db_path: str = "mcp_performance.db"):
        self.db_path = db_path
        self.metrics_buffer: List[PerformanceMetric] = []
        self.alert_rules: List[AlertRule] = []
        self.is_monitoring = False
        self.buffer_lock = threading.Lock()
        self._memory_conn = None  # 用于内存数据库连接

        # 初始化数据库
        self._init_database()

        # 设置默认告警规则
        self._setup_default_alert_rules()

        logger.info("🔍 MCP性能监控器初始化完成")
    
    def _init_database(self):
        """初始化性能数据库"""
        try:
            # 如果是内存数据库，确保连接保持活跃
            if self.db_path == ":memory:":
                self._memory_conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn = self._memory_conn
            else:
                conn = sqlite3.connect(self.db_path)

            cursor = conn.cursor()

            # 创建性能指标表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    timestamp DATETIME NOT NULL,
                    mode_used TEXT NOT NULL,
                    error_message TEXT,
                    parameters_hash TEXT
                )
            """)

            # 创建告警记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_name TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE
                )
            """)

            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tool_timestamp ON performance_metrics(tool_name, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON performance_metrics(timestamp)")

            conn.commit()

            # 只有非内存数据库才关闭连接
            if self.db_path != ":memory:":
                conn.close()

            logger.info("📊 性能监控数据库初始化完成")

        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            raise
    
    def _setup_default_alert_rules(self):
        """设置默认告警规则"""
        self.alert_rules = [
            AlertRule(
                name="高响应时间",
                condition="avg_execution_time > threshold",
                threshold=5.0,
                level=AlertLevel.WARNING
            ),
            AlertRule(
                name="低成功率",
                condition="success_rate < threshold",
                threshold=80.0,
                level=AlertLevel.ERROR
            ),
            AlertRule(
                name="工具不可用",
                condition="success_rate < threshold",
                threshold=10.0,
                level=AlertLevel.CRITICAL
            ),
            AlertRule(
                name="频繁错误",
                condition="error_rate > threshold",
                threshold=20.0,
                level=AlertLevel.WARNING
            )
        ]
    
    def record_metric(self, tool_name: str, action: str, execution_time: float, 
                     success: bool, mode_used: str, error_message: Optional[str] = None):
        """记录性能指标"""
        metric = PerformanceMetric(
            tool_name=tool_name,
            action=action,
            execution_time=execution_time,
            success=success,
            timestamp=datetime.now(),
            mode_used=mode_used,
            error_message=error_message
        )
        
        with self.buffer_lock:
            self.metrics_buffer.append(metric)
        
        # 如果缓冲区满了，触发批量写入
        if len(self.metrics_buffer) >= 100:
            asyncio.create_task(self._flush_metrics())
    
    async def _flush_metrics(self):
        """批量写入性能指标到数据库"""
        if not self.metrics_buffer:
            return
        
        with self.buffer_lock:
            metrics_to_write = self.metrics_buffer.copy()
            self.metrics_buffer.clear()
        
        try:
            # 使用正确的数据库连接
            if self.db_path == ":memory:" and self._memory_conn:
                conn = self._memory_conn
                should_close = False
            else:
                conn = sqlite3.connect(self.db_path)
                should_close = True

            cursor = conn.cursor()

            for metric in metrics_to_write:
                cursor.execute("""
                    INSERT INTO performance_metrics
                    (tool_name, action, execution_time, success, timestamp, mode_used, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric.tool_name,
                    metric.action,
                    metric.execution_time,
                    metric.success,
                    metric.timestamp,
                    metric.mode_used,
                    metric.error_message
                ))

            conn.commit()

            if should_close:
                conn.close()

            logger.debug(f"📝 写入 {len(metrics_to_write)} 条性能指标")

        except Exception as e:
            logger.error(f"❌ 性能指标写入失败: {e}")
    
    async def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取性能摘要"""
        try:
            # 使用正确的数据库连接
            if self.db_path == ":memory:" and self._memory_conn:
                conn = self._memory_conn
                should_close = False
            else:
                conn = sqlite3.connect(self.db_path)
                should_close = True

            cursor = conn.cursor()
            
            # 计算时间范围
            since_time = datetime.now() - timedelta(hours=hours)
            
            # 总体统计
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_calls,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_calls,
                    AVG(execution_time) as avg_execution_time,
                    MAX(execution_time) as max_execution_time,
                    MIN(execution_time) as min_execution_time
                FROM performance_metrics 
                WHERE timestamp > ?
            """, (since_time,))
            
            overall_stats = cursor.fetchone()
            
            # 按工具统计
            cursor.execute("""
                SELECT 
                    tool_name,
                    COUNT(*) as calls,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                    AVG(execution_time) as avg_time,
                    COUNT(CASE WHEN success = 0 THEN 1 END) as failures
                FROM performance_metrics 
                WHERE timestamp > ?
                GROUP BY tool_name
                ORDER BY calls DESC
            """, (since_time,))
            
            tool_stats = cursor.fetchall()

            if should_close:
                conn.close()
            
            # 构建摘要
            summary = {
                "time_range_hours": hours,
                "overall": {
                    "total_calls": overall_stats[0] or 0,
                    "successful_calls": overall_stats[1] or 0,
                    "success_rate": (overall_stats[1] / max(overall_stats[0], 1)) * 100 if overall_stats[0] else 0,
                    "avg_execution_time": round(overall_stats[2] or 0, 3),
                    "max_execution_time": round(overall_stats[3] or 0, 3),
                    "min_execution_time": round(overall_stats[4] or 0, 3)
                },
                "by_tool": []
            }
            
            for tool_stat in tool_stats:
                tool_name, calls, successes, avg_time, failures = tool_stat
                summary["by_tool"].append({
                    "tool_name": tool_name,
                    "calls": calls,
                    "successes": successes,
                    "success_rate": round((successes / calls) * 100, 2),
                    "avg_execution_time": round(avg_time, 3),
                    "failures": failures
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ 获取性能摘要失败: {e}")
            return {"error": str(e)}
    
    async def check_alerts(self) -> List[Dict[str, Any]]:
        """检查告警条件"""
        alerts = []
        
        try:
            summary = await self.get_performance_summary(hours=1)  # 检查最近1小时
            overall = summary.get("overall", {})
            
            for rule in self.alert_rules:
                if not rule.enabled:
                    continue
                
                triggered = False
                message = ""
                
                if rule.name == "高响应时间":
                    avg_time = overall.get("avg_execution_time", 0)
                    if avg_time > rule.threshold:
                        triggered = True
                        message = f"平均响应时间 {avg_time:.2f}s 超过阈值 {rule.threshold}s"
                
                elif rule.name == "低成功率":
                    success_rate = overall.get("success_rate", 100)
                    if success_rate < rule.threshold:
                        triggered = True
                        message = f"成功率 {success_rate:.1f}% 低于阈值 {rule.threshold}%"
                
                elif rule.name == "工具不可用":
                    success_rate = overall.get("success_rate", 100)
                    if success_rate < rule.threshold:
                        triggered = True
                        message = f"工具几乎不可用，成功率仅 {success_rate:.1f}%"
                
                if triggered:
                    alert = {
                        "rule_name": rule.name,
                        "level": rule.level.value,
                        "message": message,
                        "timestamp": datetime.now().isoformat(),
                        "threshold": rule.threshold
                    }
                    alerts.append(alert)
                    
                    # 记录告警历史
                    await self._record_alert(alert)
            
        except Exception as e:
            logger.error(f"❌ 告警检查失败: {e}")
        
        return alerts
    
    async def _record_alert(self, alert: Dict[str, Any]):
        """记录告警历史"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO alert_history (rule_name, level, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                alert["rule_name"],
                alert["level"],
                alert["message"],
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ 告警记录失败: {e}")
    
    async def start_monitoring(self, check_interval: int = 300):
        """启动监控（每5分钟检查一次）"""
        self.is_monitoring = True
        logger.info("🚀 启动MCP性能监控")
        
        while self.is_monitoring:
            try:
                # 刷新缓冲区
                await self._flush_metrics()
                
                # 检查告警
                alerts = await self.check_alerts()
                if alerts:
                    logger.warning(f"⚠️ 检测到 {len(alerts)} 个告警")
                    for alert in alerts:
                        logger.warning(f"🚨 {alert['level'].upper()}: {alert['message']}")
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"❌ 监控循环错误: {e}")
                await asyncio.sleep(60)  # 错误时等待1分钟
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        logger.info("🛑 停止MCP性能监控")
    
    async def cleanup(self):
        """清理资源"""
        self.stop_monitoring()
        await self._flush_metrics()  # 最后一次刷新
        logger.info("🧹 MCP性能监控清理完成")


# 全局监控器实例
_performance_monitor = None


def get_performance_monitor() -> MCPPerformanceMonitor:
    """获取全局性能监控器实例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = MCPPerformanceMonitor()
    return _performance_monitor
