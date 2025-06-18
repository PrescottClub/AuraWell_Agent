"""
结构化日志系统

提供统一的结构化日志记录功能
"""

import json
import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class LogContext:
    """日志上下文"""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation: Optional[str] = None
    component: Optional[str] = None


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        # 基础日志信息
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 添加自定义字段
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info']:
                log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self, name: str, context: Optional[LogContext] = None):
        self.logger = logging.getLogger(name)
        self.context = context or LogContext()
    
    def _log(self, level: int, message: str, **kwargs):
        """内部日志记录方法"""
        # 合并上下文和额外参数
        extra = asdict(self.context)
        extra.update(kwargs)
        
        # 过滤 None 值
        extra = {k: v for k, v in extra.items() if v is not None}
        
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """调试日志"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """信息日志"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告日志"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """错误日志"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def with_context(self, **context_updates) -> 'StructuredLogger':
        """创建带有更新上下文的新日志记录器"""
        new_context = LogContext(**{**asdict(self.context), **context_updates})
        return StructuredLogger(self.logger.name, new_context)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_structured: bool = True
):
    """设置日志系统"""
    
    # 设置根日志级别
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 选择格式化器
    if enable_structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # 控制台处理器
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('alembic').setLevel(logging.INFO)
    logging.getLogger('uvicorn').setLevel(logging.INFO)


# 全局结构化日志记录器
_structured_loggers: Dict[str, StructuredLogger] = {}


def get_structured_logger(name: str, context: Optional[LogContext] = None) -> StructuredLogger:
    """获取结构化日志记录器"""
    key = f"{name}:{id(context) if context else 'default'}"
    if key not in _structured_loggers:
        _structured_loggers[key] = StructuredLogger(name, context)
    return _structured_loggers[key]


def log_request(
    method: str,
    path: str,
    status_code: int,
    response_time: float,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    **kwargs
):
    """记录HTTP请求日志"""
    logger = get_structured_logger("aurawell.request")
    
    logger.info(
        f"{method} {path} - {status_code}",
        request_id=request_id,
        user_id=user_id,
        method=method,
        path=path,
        status_code=status_code,
        response_time=response_time,
        **kwargs
    )


def log_database_operation(
    operation: str,
    table: str,
    duration: float,
    success: bool = True,
    error: Optional[str] = None,
    **kwargs
):
    """记录数据库操作日志"""
    logger = get_structured_logger("aurawell.database")
    
    level = logging.INFO if success else logging.ERROR
    message = f"DB {operation} on {table} - {'SUCCESS' if success else 'FAILED'}"
    
    logger._log(
        level,
        message,
        operation=operation,
        table=table,
        duration=duration,
        success=success,
        error=error,
        **kwargs
    )


def log_business_event(
    event_type: str,
    event_data: Dict[str, Any],
    user_id: Optional[str] = None,
    **kwargs
):
    """记录业务事件日志"""
    logger = get_structured_logger("aurawell.business")
    
    logger.info(
        f"Business event: {event_type}",
        user_id=user_id,
        event_type=event_type,
        event_data=event_data,
        **kwargs
    )


def log_security_event(
    event_type: str,
    severity: str,
    details: Dict[str, Any],
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    **kwargs
):
    """记录安全事件日志"""
    logger = get_structured_logger("aurawell.security")
    
    # 根据严重程度选择日志级别
    level_map = {
        "low": logging.INFO,
        "medium": logging.WARNING,
        "high": logging.ERROR,
        "critical": logging.CRITICAL
    }
    level = level_map.get(severity.lower(), logging.WARNING)
    
    logger._log(
        level,
        f"Security event: {event_type}",
        user_id=user_id,
        ip_address=ip_address,
        event_type=event_type,
        severity=severity,
        details=details,
        **kwargs
    )


def log_performance_issue(
    component: str,
    issue_type: str,
    metrics: Dict[str, Any],
    threshold: Optional[float] = None,
    **kwargs
):
    """记录性能问题日志"""
    logger = get_structured_logger("aurawell.performance")
    
    logger.warning(
        f"Performance issue in {component}: {issue_type}",
        component=component,
        issue_type=issue_type,
        metrics=metrics,
        threshold=threshold,
        **kwargs
    )


def log_family_activity(
    family_id: str,
    user_id: str,
    action: str,
    details: Dict[str, Any],
    **kwargs
):
    """记录家庭活动日志"""
    logger = get_structured_logger("aurawell.family")
    
    logger.info(
        f"Family activity: {action}",
        family_id=family_id,
        user_id=user_id,
        action=action,
        details=details,
        **kwargs
    )
