"""
服务状态API接口

提供服务状态查询功能，显示哪些服务使用Mock客户端，哪些使用真实API。
用于开发调试和服务监控。
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..core.service_factory import ServiceClientFactory

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/services", tags=["services"])


class ServiceStatus(BaseModel):
    """服务状态响应模型"""
    name: str
    status: str  # 'live', 'mock', 'error'
    type: str    # 'real', 'mock', 'fallback'
    api_key_configured: bool
    last_updated: str
    error: str = None


class ServiceStatusResponse(BaseModel):
    """服务状态响应"""
    services: Dict[str, ServiceStatus]
    summary: Dict[str, Any]
    recommendations: list


@router.get("/status", response_model=ServiceStatusResponse)
async def get_services_status():
    """
    获取所有服务的状态信息
    
    Returns:
        ServiceStatusResponse: 包含所有服务状态的详细信息
    """
    try:
        # 获取服务状态
        raw_status = ServiceClientFactory.get_service_status()
        
        # 转换为响应模型
        services = {}
        live_count = 0
        mock_count = 0
        error_count = 0
        
        for service_name, status_data in raw_status.items():
            service_status = ServiceStatus(
                name=status_data['name'],
                status=status_data['status'],
                type=status_data['type'],
                api_key_configured=status_data.get('api_key_configured', False),
                last_updated=status_data['last_updated'],
                error=status_data.get('error')
            )
            services[service_name] = service_status
            
            # 统计计数
            if status_data['status'] == 'live':
                live_count += 1
            elif status_data['status'] == 'mock':
                mock_count += 1
            else:
                error_count += 1
        
        # 生成摘要
        total_services = len(services)
        summary = {
            'total_services': total_services,
            'live_services': live_count,
            'mock_services': mock_count,
            'error_services': error_count,
            'zero_config_mode': mock_count == total_services,
            'fully_configured': live_count == total_services
        }
        
        # 生成建议
        recommendations = _generate_recommendations(services, summary)
        
        return ServiceStatusResponse(
            services=services,
            summary=summary,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"获取服务状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取服务状态失败: {str(e)}")


@router.get("/status/{service_name}")
async def get_service_status(service_name: str):
    """
    获取特定服务的状态信息
    
    Args:
        service_name: 服务名称 (deepseek, mcp_tools)
        
    Returns:
        Dict: 服务状态详情
    """
    try:
        status = ServiceClientFactory.get_service_status()
        
        if service_name not in status:
            raise HTTPException(status_code=404, detail=f"服务 '{service_name}' 不存在")
        
        return {
            'service_name': service_name,
            'status': status[service_name],
            'timestamp': status[service_name]['last_updated']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取服务 {service_name} 状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取服务状态失败: {str(e)}")


@router.post("/reset")
async def reset_services():
    """
    重置所有服务客户端（主要用于开发调试）
    
    Returns:
        Dict: 重置结果
    """
    try:
        ServiceClientFactory.reset_clients()
        logger.info("所有服务客户端已重置")
        
        return {
            'success': True,
            'message': '所有服务客户端已重置',
            'timestamp': ServiceClientFactory._get_current_time()
        }
        
    except Exception as e:
        logger.error(f"重置服务失败: {e}")
        raise HTTPException(status_code=500, detail=f"重置服务失败: {str(e)}")


def _generate_recommendations(services: Dict[str, ServiceStatus], summary: Dict[str, Any]) -> list:
    """生成配置建议"""
    recommendations = []
    
    # 零配置模式建议
    if summary['zero_config_mode']:
        recommendations.append({
            'type': 'info',
            'title': '🚀 零配置模式运行中',
            'message': '所有服务都在使用Mock客户端。这是正常的开发模式，无需任何API Key配置。',
            'action': '如需使用真实服务，请在.env文件中添加相应的API Key。'
        })
    
    # DeepSeek AI 建议
    if 'deepseek' in services and services['deepseek'].status == 'mock':
        recommendations.append({
            'type': 'suggestion',
            'title': '🤖 启用真实AI服务',
            'message': '当前使用Mock AI响应。添加DASHSCOPE_API_KEY可获得真实的DeepSeek AI建议。',
            'action': '在.env文件中设置: DASHSCOPE_API_KEY=your-api-key'
        })
    
    # MCP工具建议
    if 'mcp_tools' in services and services['mcp_tools'].status == 'mock':
        recommendations.append({
            'type': 'suggestion',
            'title': '🛠️ 启用真实MCP工具',
            'message': '当前使用Mock MCP工具。添加API Key可启用真实的搜索、GitHub等功能。',
            'action': '在.env文件中设置: BRAVE_API_KEY, GITHUB_TOKEN 等'
        })
    
    # 错误服务建议
    error_services = [name for name, service in services.items() if service.status == 'error']
    if error_services:
        recommendations.append({
            'type': 'warning',
            'title': '⚠️ 服务配置错误',
            'message': f'以下服务配置有误: {", ".join(error_services)}',
            'action': '请检查API Key配置或网络连接。'
        })
    
    # 完全配置建议
    if summary['fully_configured']:
        recommendations.append({
            'type': 'success',
            'title': '✅ 所有服务已配置',
            'message': '所有服务都在使用真实API。系统运行在生产模式。',
            'action': '监控服务状态，确保API配额充足。'
        })
    
    return recommendations


# 便捷函数，用于其他模块调用
def get_current_service_status() -> Dict[str, Any]:
    """获取当前服务状态的便捷函数"""
    return ServiceClientFactory.get_service_status()


def is_zero_config_mode() -> bool:
    """检查是否在零配置模式下运行"""
    status = ServiceClientFactory.get_service_status()
    return all(service['status'] == 'mock' for service in status.values())


def get_live_services() -> list:
    """获取使用真实API的服务列表"""
    status = ServiceClientFactory.get_service_status()
    return [name for name, service in status.items() if service['status'] == 'live']


def get_mock_services() -> list:
    """获取使用Mock的服务列表"""
    status = ServiceClientFactory.get_service_status()
    return [name for name, service in status.items() if service['status'] == 'mock']
