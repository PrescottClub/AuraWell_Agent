"""
MCP工具智能管理器
实现智能工具选择、并行调用、结果整合
"""

import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ToolExecutionMode(Enum):
    """工具执行模式"""
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    CONDITIONAL = "conditional"


@dataclass
class ToolCallConfig:
    """工具调用配置"""
    name: str
    action: str
    parameters: Dict[str, Any]
    priority: int = 1
    timeout: float = 10.0
    required: bool = True


@dataclass
class WorkflowResult:
    """工作流执行结果"""
    success: bool
    results: Dict[str, Any]
    tool_calls: List[str]
    execution_time: float
    errors: List[str]


class IntentAnalyzer:
    """用户意图分析器 - 智能识别触发词并选择工具组合"""
    
    # 基于.cursorrules定义的智能触发规则
    TRIGGER_PATTERNS = {
        'health_analysis': {
            'keywords': ['分析', '数据', '统计', '趋势', 'BMI', '体重', 'statistics', 'analyze', 'trend'],
            'tools': ['database-sqlite', 'calculator', 'quickchart', 'sequential-thinking'],
            'mode': ToolExecutionMode.PARALLEL,
            'description': '健康数据分析和可视化'
        },
        
        'nutrition_planning': {
            'keywords': ['饮食', '营养', 'meal', 'diet', '卡路里', 'nutrition', 'food', 'calories'],
            'tools': ['brave-search', 'calculator', 'database-sqlite', 'memory', 'quickchart'],
            'mode': ToolExecutionMode.SEQUENTIAL,
            'description': '营养规划和饮食建议'
        },
        
        'fitness_planning': {
            'keywords': ['运动', '健身', 'workout', 'fitness', '锻炼', 'exercise', 'training'],
            'tools': ['memory', 'weather', 'calculator', 'quickchart'],
            'mode': ToolExecutionMode.PARALLEL,
            'description': '运动健身计划制定'
        },
        
        'comprehensive_assessment': {
            'keywords': ['健康评估', '全面分析', '制定计划', 'assessment', 'comprehensive', 'plan'],
            'tools': ['memory', 'database-sqlite', 'calculator', 'sequential-thinking', 'quickchart'],
            'mode': ToolExecutionMode.SEQUENTIAL,
            'description': '综合健康评估和规划'
        },
        
        'research_query': {
            'keywords': ['搜索', 'research', '最新', '科学', 'study', '研究', '文献'],
            'tools': ['brave-search', 'fetch', 'memory'],
            'mode': ToolExecutionMode.SEQUENTIAL,
            'description': '健康信息搜索和研究'
        },
        
        'user_profile': {
            'keywords': ['画像', 'profile', '个性化', 'preferences', '偏好', '档案'],
            'tools': ['memory', 'database-sqlite', 'sequential-thinking'],
            'mode': ToolExecutionMode.PARALLEL,
            'description': '用户健康画像管理'
        }
    }
    
    def analyze_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析用户意图并返回工具调用配置
        
        Args:
            message: 用户输入消息
            context: 上下文信息
            
        Returns:
            Dict包含意图分析结果和工具配置
        """
        message_lower = message.lower()
        detected_intents = []
        
        # 检测匹配的意图类型
        for intent_type, config in self.TRIGGER_PATTERNS.items():
            keyword_matches = [kw for kw in config['keywords'] if kw.lower() in message_lower]
            if keyword_matches:
                confidence = len(keyword_matches) / len(config['keywords'])
                detected_intents.append({
                    'type': intent_type,
                    'confidence': confidence,
                    'matched_keywords': keyword_matches,
                    'config': config
                })
        
        # 按置信度排序
        detected_intents.sort(key=lambda x: x['confidence'], reverse=True)
        
        if detected_intents:
            primary_intent = detected_intents[0]
            
            return {
                'needs_tools': True,
                'primary_intent': primary_intent['type'],
                'confidence': primary_intent['confidence'],
                'matched_keywords': primary_intent['matched_keywords'],
                'tools_config': self._build_tools_config(primary_intent, message, context),
                'execution_mode': primary_intent['config']['mode'],
                'all_intents': detected_intents
            }
        else:
            # 没有特定意图，使用默认响应
            return {
                'needs_tools': False,
                'primary_intent': 'general_chat',
                'confidence': 0.0,
                'matched_keywords': [],
                'tools_config': [],
                'execution_mode': ToolExecutionMode.PARALLEL,
                'all_intents': []
            }
    
    def _build_tools_config(self, intent: Dict[str, Any], message: str, context: Optional[Dict[str, Any]]) -> List[ToolCallConfig]:
        """根据意图构建具体的工具调用配置"""
        tools_config = []
        intent_type = intent['type']
        tools = intent['config']['tools']
        
        # 根据不同意图类型构建特定的工具配置
        if intent_type == 'health_analysis':
            tools_config = [
                ToolCallConfig(
                    name='database-sqlite',
                    action='query_health_data',
                    parameters={'user_query': message, 'table_focus': 'health_metrics'},
                    priority=1
                ),
                ToolCallConfig(
                    name='calculator',
                    action='calculate_health_metrics',
                    parameters={'calculation_type': 'comprehensive'},
                    priority=1
                ),
                ToolCallConfig(
                    name='quickchart',
                    action='generate_health_dashboard',
                    parameters={'chart_type': 'comprehensive'},
                    priority=2
                ),
                ToolCallConfig(
                    name='sequential-thinking',
                    action='analyze_health_trends',
                    parameters={'analysis_focus': 'trends_and_recommendations'},
                    priority=2
                )
            ]
            
        elif intent_type == 'nutrition_planning':
            tools_config = [
                ToolCallConfig(
                    name='brave-search',
                    action='search_nutrition_research',
                    parameters={'query': f'nutrition research {" ".join(intent["matched_keywords"])}'},
                    priority=1
                ),
                ToolCallConfig(
                    name='calculator',
                    action='calculate_nutrition_needs',
                    parameters={'calculation_type': 'nutrition'},
                    priority=2
                ),
                ToolCallConfig(
                    name='database-sqlite',
                    action='query_diet_history',
                    parameters={'table_focus': 'diet_records'},
                    priority=2
                ),
                ToolCallConfig(
                    name='memory',
                    action='store_nutrition_preferences',
                    parameters={'preference_type': 'nutrition'},
                    priority=3
                ),
                ToolCallConfig(
                    name='quickchart',
                    action='visualize_nutrition',
                    parameters={'chart_type': 'nutrition_breakdown'},
                    priority=4
                )
            ]
            
        elif intent_type == 'fitness_planning':
            tools_config = [
                ToolCallConfig(
                    name='memory',
                    action='get_fitness_profile',
                    parameters={'profile_type': 'fitness'},
                    priority=1
                ),
                ToolCallConfig(
                    name='weather',
                    action='get_exercise_conditions',
                    parameters={'forecast_days': 7},
                    priority=1
                ),
                ToolCallConfig(
                    name='calculator',
                    action='calculate_exercise_metrics',
                    parameters={'calculation_type': 'exercise'},
                    priority=2
                ),
                ToolCallConfig(
                    name='quickchart',
                    action='generate_fitness_chart',
                    parameters={'chart_type': 'fitness_progress'},
                    priority=3
                )
            ]
        
        # 可以根据context进一步定制参数
        if context:
            for config in tools_config:
                config.parameters.update(context.get('tool_context', {}))
        
        return tools_config


class MCPToolsManager:
    """
    MCP工具智能管理器
    负责工具调用、并行执行、结果整合
    """
    
    def __init__(self):
        self.intent_analyzer = IntentAnalyzer()
        self.tool_interface = None
        self.execution_stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'avg_execution_time': 0.0
        }
        
        # 初始化MCP工具接口
        self._initialize_mcp_interface()
    
    def _initialize_mcp_interface(self):
        """初始化MCP工具接口"""
        try:
            from .mcp_interface import MCPToolInterface
            self.tool_interface = MCPToolInterface()
            logger.info("MCP工具接口初始化成功")
        except ImportError as e:
            logger.warning(f"MCP工具接口导入失败: {e}，使用占位符接口")
            self.tool_interface = None
        except Exception as e:
            logger.error(f"MCP工具接口初始化失败: {e}")
            self.tool_interface = None
    
    def _register_mcp_tools(self):
        """注册所有MCP工具接口"""
        # 这里先定义工具列表，实际调用逻辑将在后续实现
        self.available_tools = {
            'database-sqlite': self._call_database_sqlite,
            'calculator': self._call_calculator,
            'quickchart': self._call_quickchart,
            'brave-search': self._call_brave_search,
            'fetch': self._call_fetch,
            'sequential-thinking': self._call_sequential_thinking,
            'memory': self._call_memory,
            'weather': self._call_weather,
            'time': self._call_time,
            'run-python': self._call_run_python,
            'github': self._call_github,
            'filesystem': self._call_filesystem,
            'figma': self._call_figma
        }
        
        logger.info(f"注册了 {len(self.available_tools)} 个MCP工具")
    
    async def analyze_and_execute(self, message: str, context: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """
        分析用户意图并执行相应的工具工作流
        
        Args:
            message: 用户输入消息
            context: 上下文信息
            
        Returns:
            WorkflowResult: 工作流执行结果
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 1. 分析用户意图
            intent_result = self.intent_analyzer.analyze_intent(message, context)
            
            if not intent_result['needs_tools']:
                return WorkflowResult(
                    success=True,
                    results={'message': '未检测到需要工具处理的意图'},
                    tool_calls=[],
                    execution_time=0.0,
                    errors=[]
                )
            
            # 2. 执行工具工作流
            execution_result = await self._execute_workflow(
                intent_result['tools_config'],
                intent_result['execution_mode']
            )
            
            # 3. 计算执行时间
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # 4. 更新统计信息
            self._update_stats(execution_result['success'], execution_time)
            
            return WorkflowResult(
                success=execution_result['success'],
                results={
                    **execution_result['results'],
                    'intent_analysis': intent_result
                },
                tool_calls=execution_result['tool_calls'],
                execution_time=execution_time,
                errors=execution_result['errors']
            )
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(False, execution_time)
            
            return WorkflowResult(
                success=False,
                results={},
                tool_calls=[],
                execution_time=execution_time,
                errors=[str(e)]
            )
    
    async def _execute_workflow(self, tools_config: List[ToolCallConfig], mode: ToolExecutionMode) -> Dict[str, Any]:
        """执行工具工作流"""
        if mode == ToolExecutionMode.PARALLEL:
            return await self._execute_parallel(tools_config)
        elif mode == ToolExecutionMode.SEQUENTIAL:
            return await self._execute_sequential(tools_config)
        else:
            return await self._execute_conditional(tools_config)
    
    async def _execute_parallel(self, tools_config: List[ToolCallConfig]) -> Dict[str, Any]:
        """并行执行工具"""
        tasks = []
        tool_calls = []
        
        for config in tools_config:
            if config.name in self.available_tools:
                task = asyncio.create_task(
                    self._execute_single_tool(config),
                    name=f"tool_{config.name}"
                )
                tasks.append((config.name, task))
                tool_calls.append(f"{config.name}:{config.action}")
        
        # 等待所有任务完成
        results = {}
        errors = []
        
        for tool_name, task in tasks:
            try:
                result = await asyncio.wait_for(task, timeout=10.0)
                results[tool_name] = result
            except asyncio.TimeoutError:
                error_msg = f"工具 {tool_name} 执行超时"
                errors.append(error_msg)
                logger.warning(error_msg)
            except Exception as e:
                error_msg = f"工具 {tool_name} 执行失败: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return {
            'success': len(results) > 0,
            'results': results,
            'tool_calls': tool_calls,
            'errors': errors
        }
    
    async def _execute_sequential(self, tools_config: List[ToolCallConfig]) -> Dict[str, Any]:
        """顺序执行工具"""
        results = {}
        errors = []
        tool_calls = []
        
        # 按优先级排序
        sorted_configs = sorted(tools_config, key=lambda x: x.priority)
        
        for config in sorted_configs:
            if config.name in self.available_tools:
                try:
                    result = await asyncio.wait_for(
                        self._execute_single_tool(config),
                        timeout=config.timeout
                    )
                    results[config.name] = result
                    tool_calls.append(f"{config.name}:{config.action}")
                    
                    # 如果是必需工具且失败，则停止执行
                    if config.required and not result.get('success', True):
                        break
                        
                except Exception as e:
                    error_msg = f"工具 {config.name} 执行失败: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    
                    if config.required:
                        break
        
        return {
            'success': len(results) > 0,
            'results': results,
            'tool_calls': tool_calls,
            'errors': errors
        }
    
    async def _execute_conditional(self, tools_config: List[ToolCallConfig]) -> Dict[str, Any]:
        """条件执行工具（暂时实现为顺序执行）"""
        return await self._execute_sequential(tools_config)
    
    async def _execute_single_tool(self, config: ToolCallConfig) -> Dict[str, Any]:
        """执行单个工具"""
        try:
            if self.tool_interface:
                # 使用MCP工具接口
                result = await self.tool_interface.call_tool(
                    config.name,
                    config.action,
                    config.parameters,
                    config.timeout
                )
                
                return {
                    'success': result.success,
                    'data': result.data,
                    'error': result.error,
                    'tool': result.tool_name,
                    'action': result.action,
                    'execution_time': result.execution_time
                }
            else:
                # fallback到占位符实现
                tool_func = self.available_tools.get(config.name)
                if not tool_func:
                    raise ValueError(f"工具 {config.name} 不可用")
                
                result = await tool_func(config.action, config.parameters)
                return {
                    'success': True,
                    'data': result,
                    'tool': config.name,
                    'action': config.action
                }
                
        except Exception as e:
            logger.error(f"工具 {config.name} 调用失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool': config.name,
                'action': config.action
            }
    
    def _update_stats(self, success: bool, execution_time: float):
        """更新执行统计信息"""
        self.execution_stats['total_calls'] += 1
        if success:
            self.execution_stats['successful_calls'] += 1
        else:
            self.execution_stats['failed_calls'] += 1
        
        # 更新平均执行时间
        total_time = self.execution_stats['avg_execution_time'] * (self.execution_stats['total_calls'] - 1)
        self.execution_stats['avg_execution_time'] = (total_time + execution_time) / self.execution_stats['total_calls']
    
    def get_stats(self) -> Dict[str, Any]:
        """获取执行统计信息"""
        return self.execution_stats.copy()
    
    # MCP工具调用方法（占位符，后续实现具体逻辑）
    async def _call_database_sqlite(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用database-sqlite工具"""
        # TODO: 实现实际的MCP工具调用
        logger.info(f"调用database-sqlite: {action} with {parameters}")
        return {'status': 'placeholder', 'action': action, 'tool': 'database-sqlite'}
    
    async def _call_calculator(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用calculator工具"""
        # TODO: 实现实际的MCP工具调用
        logger.info(f"调用calculator: {action} with {parameters}")
        return {'status': 'placeholder', 'action': action, 'tool': 'calculator'}
    
    async def _call_quickchart(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用quickchart工具"""
        # TODO: 实现实际的MCP工具调用
        logger.info(f"调用quickchart: {action} with {parameters}")
        return {'status': 'placeholder', 'action': action, 'tool': 'quickchart'}
    
    async def _call_brave_search(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用brave-search工具"""
        # TODO: 实现实际的MCP工具调用
        logger.info(f"调用brave-search: {action} with {parameters}")
        return {'status': 'placeholder', 'action': action, 'tool': 'brave-search'}
    
    async def _call_fetch(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用fetch工具"""
        # TODO: 实现实际的MCP工具调用
        logger.info(f"调用fetch: {action} with {parameters}")
        return {'status': 'placeholder', 'action': action, 'tool': 'fetch'}
    
    async def _call_sequential_thinking(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用sequential-thinking工具"""
        # TODO: 实现实际的MCP工具调用
        logger.info(f"调用sequential-thinking: {action} with {parameters}")
        return {'status': 'placeholder', 'action': action, 'tool': 'sequential-thinking'}
    
    async def _call_memory(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用memory工具"""
        # TODO: 实现实际的MCP工具调用
        logger.info(f"调用memory: {action} with {parameters}")
        return {'status': 'placeholder', 'action': action, 'tool': 'memory'}
    
    async def _call_weather(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用weather工具"""
        # TODO: 实现实际的MCP工具调用
        logger.info(f"调用weather: {action} with {parameters}")
        return {'status': 'placeholder', 'action': action, 'tool': 'weather'}
    
    async def _call_time(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用time工具"""
        # TODO: 实现实际的MCP工具调用
        logger.info(f"调用time: {action} with {parameters}")
        return {'status': 'placeholder', 'action': action, 'tool': 'time'}
    
    async def _call_run_python(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用run-python工具"""
        # TODO: 实现实际的MCP工具调用
        logger.info(f"调用run-python: {action} with {parameters}")
        return {'status': 'placeholder', 'action': action, 'tool': 'run-python'}
    
    async def _call_github(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用github工具"""
        # TODO: 实现实际的MCP工具调用
        logger.info(f"调用github: {action} with {parameters}")
        return {'status': 'placeholder', 'action': action, 'tool': 'github'}
    
    async def _call_filesystem(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用filesystem工具"""
        # TODO: 实现实际的MCP工具调用
        logger.info(f"调用filesystem: {action} with {parameters}")
        return {'status': 'placeholder', 'action': action, 'tool': 'filesystem'}
    
    async def _call_figma(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用figma工具"""
        # TODO: 实现实际的MCP工具调用
        logger.info(f"调用figma: {action} with {parameters}")
        return {'status': 'placeholder', 'action': action, 'tool': 'figma'} 