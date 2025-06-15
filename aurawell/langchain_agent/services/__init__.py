"""
LangChain Agent Services Module

Contains specialized services for health advice generation and AI-powered analysis.
"""

try:
    from .health_advice_service import HealthAdviceService
    from .parsers import FiveSectionParser, HealthAdviceResponse, HealthAdviceSection
    
    __all__ = [
        "HealthAdviceService", 
        "FiveSectionParser",
        "HealthAdviceResponse",
        "HealthAdviceSection"
    ]
    
except ImportError as e:
    # 如果导入失败，提供基本的错误处理
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"导入健康建议服务模块时出现问题: {e}")
    
    __all__ = [] 