"""
ServiceClientFactory - 统一服务客户端工厂

这个模块提供了一个统一的工厂类，用于管理所有外部服务客户端的创建和配置。
支持根据环境变量自动选择真实API客户端或Mock客户端，实现零配置启动。

核心特性:
1. 自动检测API Key，无Key时使用Mock客户端
2. 单例模式管理客户端实例，避免重复创建
3. 统一的接口规范，便于切换和测试
4. 支持运行时状态查询和调试
"""

import os
import logging
from typing import Dict, Any, Optional, Protocol, runtime_checkable, List
from abc import ABC, abstractmethod
import asyncio

# 导入现有的真实客户端
from .deepseek_client import DeepSeekClient, DeepSeekResponse

logger = logging.getLogger(__name__)


@runtime_checkable
class AIClientProtocol(Protocol):
    """AI客户端协议，定义统一接口"""
    
    def get_deepseek_response(
        self,
        messages: list,
        model_name: Optional[str] = None,
        tools: Optional[list] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> DeepSeekResponse:
        """获取AI响应"""
        ...
    
    async def get_streaming_response(
        self,
        messages: list,
        model_name: Optional[str] = None,
        tools: Optional[list] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        """获取流式响应"""
        ...


class MockDeepSeekClient:
    """DeepSeek Mock客户端，提供合理的测试数据"""
    
    def __init__(self):
        self.is_mock = True
        logger.info("MockDeepSeekClient initialized - 使用Mock模式")
    
    def get_deepseek_response(
        self,
        messages: list,
        model_name: Optional[str] = None,
        tools: Optional[list] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> DeepSeekResponse:
        """返回Mock响应数据"""
        
        # 根据消息内容生成合理的Mock响应
        user_message = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # 生成基于上下文的Mock响应
        mock_content = self._generate_mock_content(user_message, tools)
        
        # 模拟工具调用
        mock_tool_calls = None
        if tools and len(tools) > 0:
            mock_tool_calls = self._generate_mock_tool_calls(tools, user_message)
        
        return DeepSeekResponse(
            content=mock_content,
            tool_calls=mock_tool_calls,
            usage=None,  # Mock模式不计算token使用
            model=model_name or "deepseek-v3-mock",
            finish_reason="stop"
        )
    
    async def get_streaming_response(
        self,
        messages: list,
        model_name: Optional[str] = None,
        tools: Optional[list] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        """返回Mock流式响应"""
        mock_content = self._generate_mock_content(
            messages[-1].get("content", "") if messages else "", 
            tools
        )
        
        # 模拟流式输出
        for char in mock_content:
            yield char
    
    def _generate_mock_content(self, user_message: str, tools: Optional[list] = None) -> str:
        """根据用户消息生成合理的Mock内容"""
        
        # 健康相关关键词映射
        health_keywords = {
            "健康": "根据您的健康数据分析，建议您保持规律作息，均衡饮食。",
            "运动": "建议您每天进行30分钟中等强度运动，如快走、游泳等。",
            "饮食": "建议采用地中海饮食模式，多吃蔬菜水果，适量蛋白质。",
            "睡眠": "建议保持7-8小时优质睡眠，晚上11点前入睡。",
            "体重": "根据您的BMI指数，当前体重在正常范围内，继续保持。",
            "心理": "建议通过冥想、深呼吸等方式缓解压力，保持心理健康。"
        }
        
        # 检查用户消息中的关键词
        for keyword, response in health_keywords.items():
            if keyword in user_message:
                return f"[Mock响应] {response}\n\n这是一个模拟响应，用于开发测试。要获得真实AI建议，请在.env文件中配置DASHSCOPE_API_KEY。"
        
        # 默认响应
        return "[Mock响应] 感谢您使用AuraWell健康助手！这是一个模拟响应，用于开发测试。要获得真实AI建议，请在.env文件中配置DASHSCOPE_API_KEY。"
    
    def _generate_mock_tool_calls(self, tools: list, user_message: str) -> list:
        """生成Mock工具调用"""
        if not tools:
            return None
        
        # 简单的工具调用模拟
        tool_calls = []
        for i, tool in enumerate(tools[:2]):  # 最多模拟2个工具调用
            tool_name = tool.get("function", {}).get("name", f"tool_{i}")
            tool_calls.append({
                "id": f"mock_call_{i}",
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": '{"mock": true, "message": "这是Mock工具调用结果"}'
                }
            })
        
        return tool_calls if tool_calls else None


# MCP工具相关协议定义
@runtime_checkable
class MCPToolProtocol(Protocol):
    """MCP工具协议，定义统一接口"""

    async def call_tool(
        self,
        tool_name: str,
        action: str,
        parameters: Dict[str, Any],
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """调用MCP工具"""
        ...

    def get_tool_status(self) -> Dict[str, Any]:
        """获取工具状态"""
        ...


class ServiceClientFactory:
    """
    统一服务客户端工厂
    
    负责管理所有外部服务客户端的创建、配置和生命周期。
    根据环境变量自动选择真实API或Mock客户端。
    """
    
    _clients: Dict[str, Any] = {}
    _service_status: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def get_deepseek_client(cls) -> AIClientProtocol:
        """
        获取DeepSeek客户端实例
        
        Returns:
            AIClientProtocol: DeepSeek客户端实例（真实或Mock）
        """
        if 'deepseek' not in cls._clients:
            # 检查API Key配置
            api_key = (
                os.getenv('DASHSCOPE_API_KEY') or 
                os.getenv('QWEN_API') or 
                os.getenv('DEEP_SEEK_API') or 
                os.getenv('DEEPSEEK_API_KEY')
            )
            
            if api_key:
                try:
                    # 尝试创建真实客户端
                    cls._clients['deepseek'] = DeepSeekClient(api_key=api_key)
                    cls._service_status['deepseek'] = {
                        'name': 'DeepSeek AI',
                        'status': 'live',
                        'type': 'real',
                        'api_key_configured': True,
                        'last_updated': cls._get_current_time()
                    }
                    logger.info("DeepSeek真实客户端初始化成功")
                except Exception as e:
                    # 如果真实客户端初始化失败，回退到Mock
                    logger.warning(f"DeepSeek真实客户端初始化失败，使用Mock客户端: {e}")
                    cls._clients['deepseek'] = MockDeepSeekClient()
                    cls._service_status['deepseek'] = {
                        'name': 'DeepSeek AI',
                        'status': 'mock',
                        'type': 'fallback',
                        'api_key_configured': True,
                        'error': str(e),
                        'last_updated': cls._get_current_time()
                    }
            else:
                # 没有API Key，使用Mock客户端
                cls._clients['deepseek'] = MockDeepSeekClient()
                cls._service_status['deepseek'] = {
                    'name': 'DeepSeek AI',
                    'status': 'mock',
                    'type': 'mock',
                    'api_key_configured': False,
                    'last_updated': cls._get_current_time()
                }
                logger.info("未配置DeepSeek API Key，使用Mock客户端")
        
        return cls._clients['deepseek']
    
    @classmethod
    def get_mcp_tools_interface(cls) -> MCPToolProtocol:
        """
        获取MCP工具接口实例

        Returns:
            MCPToolProtocol: MCP工具接口实例（真实或Mock）
        """
        if 'mcp_tools' not in cls._clients:
            # 检查是否有MCP相关的API Key配置
            mcp_api_keys = {
                'brave_search': os.getenv('BRAVE_API_KEY'),
                'github': os.getenv('GITHUB_TOKEN'),
                'weather': os.getenv('WEATHER_API_KEY'),
                'figma': os.getenv('FIGMA_TOKEN')
            }

            # 检查是否有任何真实API Key配置
            has_real_api_keys = any(key for key in mcp_api_keys.values() if key)

            if has_real_api_keys:
                try:
                    # 尝试创建真实MCP工具接口
                    from ..langchain_agent.mcp_interface import MCPToolInterface
                    cls._clients['mcp_tools'] = MCPToolInterface()
                    cls._service_status['mcp_tools'] = {
                        'name': 'MCP Tools',
                        'status': 'live',
                        'type': 'real',
                        'api_keys_configured': mcp_api_keys,
                        'last_updated': cls._get_current_time()
                    }
                    logger.info("MCP工具真实接口初始化成功")
                except Exception as e:
                    # 如果真实接口初始化失败，回退到Mock
                    logger.warning(f"MCP工具真实接口初始化失败，使用Mock接口: {e}")
                    cls._clients['mcp_tools'] = MockMCPToolInterface()
                    cls._service_status['mcp_tools'] = {
                        'name': 'MCP Tools',
                        'status': 'mock',
                        'type': 'fallback',
                        'api_keys_configured': mcp_api_keys,
                        'error': str(e),
                        'last_updated': cls._get_current_time()
                    }
            else:
                # 没有API Key，使用Mock接口
                cls._clients['mcp_tools'] = MockMCPToolInterface()
                cls._service_status['mcp_tools'] = {
                    'name': 'MCP Tools',
                    'status': 'mock',
                    'type': 'mock',
                    'api_keys_configured': mcp_api_keys,
                    'last_updated': cls._get_current_time()
                }
                logger.info("未配置MCP工具API Key，使用Mock接口")

        return cls._clients['mcp_tools']

    @classmethod
    def get_service_status(cls) -> Dict[str, Dict[str, Any]]:
        """
        获取所有服务的状态信息

        Returns:
            Dict: 服务状态信息
        """
        # 确保至少初始化了DeepSeek客户端
        if 'deepseek' not in cls._service_status:
            cls.get_deepseek_client()

        # 确保初始化了MCP工具接口
        if 'mcp_tools' not in cls._service_status:
            cls.get_mcp_tools_interface()

        return cls._service_status.copy()

    @classmethod
    def reset_clients(cls):
        """重置所有客户端实例（主要用于测试）"""
        cls._clients.clear()
        cls._service_status.clear()
        logger.info("所有服务客户端已重置")

    @classmethod
    def _get_current_time(cls) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# MCP工具Mock实现

class MockMCPToolInterface:
    """MCP工具Mock接口，提供13个工具的模拟实现"""

    def __init__(self):
        self.is_mock = True
        self.available_tools = [
            'database-sqlite', 'calculator', 'quickchart', 'brave-search',
            'fetch', 'sequential-thinking', 'memory', 'weather', 'time',
            'run-python', 'github', 'filesystem', 'figma'
        ]
        logger.info("MockMCPToolInterface initialized - 使用Mock模式")

    async def call_tool(
        self,
        tool_name: str,
        action: str,
        parameters: Dict[str, Any],
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """调用Mock MCP工具"""

        # 模拟工具调用延迟
        await asyncio.sleep(0.1)

        # 根据工具类型生成不同的Mock响应
        mock_responses = {
            'database-sqlite': self._mock_database_response(action, parameters),
            'calculator': self._mock_calculator_response(action, parameters),
            'quickchart': self._mock_quickchart_response(action, parameters),
            'brave-search': self._mock_search_response(action, parameters),
            'fetch': self._mock_fetch_response(action, parameters),
            'sequential-thinking': self._mock_thinking_response(action, parameters),
            'memory': self._mock_memory_response(action, parameters),
            'weather': self._mock_weather_response(action, parameters),
            'time': self._mock_time_response(action, parameters),
            'run-python': self._mock_python_response(action, parameters),
            'github': self._mock_github_response(action, parameters),
            'filesystem': self._mock_filesystem_response(action, parameters),
            'figma': self._mock_figma_response(action, parameters)
        }

        if tool_name in mock_responses:
            response = mock_responses[tool_name]
        else:
            response = {
                'success': False,
                'error': f'未知工具: {tool_name}',
                'data': None
            }

        # 添加通用Mock标识
        response.update({
            'tool_name': tool_name,
            'action': action,
            'is_mock': True,
            'execution_time': 0.1
        })

        return response

    def _mock_database_response(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """模拟数据库工具响应"""
        if action == 'query':
            return {
                'success': True,
                'data': [
                    {'id': 1, 'name': 'Mock用户', 'age': 25, 'weight': 70.0},
                    {'id': 2, 'name': 'Test用户', 'age': 30, 'weight': 65.0}
                ],
                'rows_affected': 2
            }
        elif action == 'insert':
            return {
                'success': True,
                'data': {'inserted_id': 123},
                'rows_affected': 1
            }
        else:
            return {
                'success': True,
                'data': f'Mock数据库操作: {action}',
                'rows_affected': 0
            }

    def _mock_calculator_response(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """模拟计算器工具响应"""
        expression = parameters.get('expression', '2+2')
        return {
            'success': True,
            'data': {
                'expression': expression,
                'result': 4.0,  # Mock结果
                'type': 'number'
            }
        }

    def _mock_search_response(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """模拟搜索工具响应"""
        query = parameters.get('query', 'health tips')
        return {
            'success': True,
            'data': {
                'query': query,
                'results': [
                    {
                        'title': 'Mock健康建议 - 均衡饮食的重要性',
                        'url': 'https://example.com/health-tips-1',
                        'snippet': '均衡饮食是维持健康的基础...'
                    },
                    {
                        'title': 'Mock运动指南 - 每日30分钟运动',
                        'url': 'https://example.com/exercise-guide',
                        'snippet': '规律运动有助于提高身体素质...'
                    }
                ],
                'total_results': 2
            }
        }

    def _mock_weather_response(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """模拟天气工具响应"""
        location = parameters.get('location', '北京')
        return {
            'success': True,
            'data': {
                'location': location,
                'temperature': 22,
                'humidity': 65,
                'weather': '晴朗',
                'air_quality': '良好',
                'uv_index': 5
            }
        }

    def _mock_time_response(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """模拟时间工具响应"""
        from datetime import datetime
        now = datetime.now()
        return {
            'success': True,
            'data': {
                'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': now.timestamp(),
                'timezone': 'Asia/Shanghai'
            }
        }

    def _mock_quickchart_response(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """模拟图表工具响应"""
        return {
            'success': True,
            'data': {
                'chart_url': 'https://quickchart.io/chart?c={type:"bar",data:{labels:["Mock数据"],datasets:[{data:[100]}]}}',
                'chart_type': parameters.get('type', 'bar')
            }
        }

    def _mock_fetch_response(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """模拟网页抓取工具响应"""
        url = parameters.get('url', 'https://example.com')
        return {
            'success': True,
            'data': {
                'url': url,
                'content': '<html><body>Mock网页内容</body></html>',
                'status_code': 200
            }
        }

    def _mock_thinking_response(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """模拟思维链工具响应"""
        problem = parameters.get('problem', '健康问题分析')
        return {
            'success': True,
            'data': {
                'problem': problem,
                'thinking_steps': [
                    '1. 分析用户当前健康状况',
                    '2. 识别潜在健康风险',
                    '3. 制定个性化建议方案',
                    '4. 评估方案可行性'
                ],
                'conclusion': 'Mock思维链分析完成'
            }
        }

    def _mock_memory_response(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """模拟记忆工具响应"""
        if action == 'store':
            return {
                'success': True,
                'data': {'memory_id': 'mock_123', 'stored': True}
            }
        elif action == 'retrieve':
            return {
                'success': True,
                'data': {
                    'memories': [
                        {'id': 'mock_123', 'content': 'Mock记忆内容', 'timestamp': '2025-07-13'}
                    ]
                }
            }
        else:
            return {
                'success': True,
                'data': f'Mock记忆操作: {action}'
            }

    def _mock_python_response(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """模拟Python执行工具响应"""
        code = parameters.get('code', 'print("Hello Mock")')
        return {
            'success': True,
            'data': {
                'code': code,
                'output': 'Hello Mock\n',
                'execution_time': 0.05
            }
        }

    def _mock_github_response(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """模拟GitHub工具响应"""
        return {
            'success': True,
            'data': {
                'repository': 'mock/repo',
                'action': action,
                'result': 'Mock GitHub操作完成'
            }
        }

    def _mock_filesystem_response(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """模拟文件系统工具响应"""
        if action == 'read':
            return {
                'success': True,
                'data': {
                    'content': 'Mock文件内容',
                    'file_path': parameters.get('path', '/mock/file.txt')
                }
            }
        elif action == 'write':
            return {
                'success': True,
                'data': {
                    'bytes_written': 100,
                    'file_path': parameters.get('path', '/mock/file.txt')
                }
            }
        else:
            return {
                'success': True,
                'data': f'Mock文件系统操作: {action}'
            }

    def _mock_figma_response(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """模拟Figma工具响应"""
        return {
            'success': True,
            'data': {
                'design_url': 'https://figma.com/mock-design',
                'action': action,
                'result': 'Mock Figma操作完成'
            }
        }

    def get_tool_status(self) -> Dict[str, Any]:
        """获取Mock工具状态"""
        return {
            'total_tools': len(self.available_tools),
            'available_tools': self.available_tools,
            'status': 'mock',
            'all_tools_available': True,
            'is_mock': True
        }


# 便捷函数，用于向后兼容
def get_deepseek_client() -> AIClientProtocol:
    """获取DeepSeek客户端的便捷函数"""
    return ServiceClientFactory.get_deepseek_client()


def get_mcp_tools_interface() -> MCPToolProtocol:
    """获取MCP工具接口的便捷函数"""
    return ServiceClientFactory.get_mcp_tools_interface()
