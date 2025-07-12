"""
AuraWell Prompt Manager - 动态智能Prompt组装系统

这个模块实现了世界级的Prompt工程管理，支持：
- 模块化Prompt组装
- 版本控制和A/B测试
- 动态上下文注入
- 性能监控和优化
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class PromptManager:
    """
    智能Prompt管理器
    
    核心功能：
    1. 动态组装模块化Prompt
    2. 版本管理和最优版本选择
    3. 上下文数据注入
    4. 性能监控和反馈收集
    """
    
    def __init__(self, prompts_base_path: str = "src/aurawell/prompts"):
        """
        初始化Prompt管理器
        
        Args:
            prompts_base_path: Prompt文件基础路径
        """
        self.base_path = Path(prompts_base_path)
        self.cache = {}  # 组件缓存
        self.performance_data = {}  # 性能数据缓存
        
        # 确保目录存在
        if not self.base_path.exists():
            logger.warning(f"Prompts directory not found: {self.base_path}")
            
        logger.info(f"PromptManager initialized with base path: {self.base_path}")
    
    def _load_prompt_component(self, path: str) -> Dict[str, Any]:
        """
        加载Prompt组件文件
        
        Args:
            path: 相对于base_path的文件路径（不含.json扩展名）
            
        Returns:
            组件数据字典
        """
        # 检查缓存
        if path in self.cache:
            return self.cache[path]
            
        file_path = self.base_path / f"{path}.json"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                component = json.load(f)
                
            # 缓存组件
            self.cache[path] = component
            logger.debug(f"Loaded prompt component: {path}")
            return component
            
        except FileNotFoundError:
            logger.error(f"Prompt component not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in prompt component {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading prompt component {file_path}: {e}")
            raise
    
    async def get_best_version(self, scenario: str, user_id: Optional[str] = None) -> str:
        """
        获取指定场景的最佳版本（集成版本管理服务）

        Args:
            scenario: 场景名称
            user_id: 用户ID（用于A/B测试）

        Returns:
            最佳版本号
        """
        try:
            # 尝试使用版本管理服务
            from ..services.prompt_version_service import prompt_version_service
            return await prompt_version_service.get_best_version(scenario, user_id)
        except Exception as e:
            logger.warning(f"Failed to get best version from service: {e}")
            # 降级到默认版本
            if scenario == "health_advice":
                return "v3_1"
            return "v1_0"
    
    async def construct_prompt(
        self,
        scenario: str,
        context: Dict[str, Any],
        version: Optional[str] = None,
        user_id: Optional[str] = None,
        include_reasoning: bool = True
    ) -> List[Dict[str, str]]:
        """
        动态组装Prompt

        Args:
            scenario: 场景名称
            context: 上下文数据
            version: 指定版本（可选，默认使用最佳版本）
            user_id: 用户ID（用于A/B测试）
            include_reasoning: 是否包含推理组件

        Returns:
            消息列表，格式为 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        """
        try:
            # 确定版本
            if version is None:
                version = await self.get_best_version(scenario, user_id)
            
            logger.info(f"Constructing prompt for scenario: {scenario}, version: {version}")
            
            # 1. 加载系统级组件
            identity = self._load_prompt_component("system/identity_v1")
            safety = self._load_prompt_component("system/safety_v1")
            
            # 2. 加载推理组件（可选）
            reasoning_content = ""
            if include_reasoning:
                cot_reasoning = self._load_prompt_component("components/reasoning/chain_of_thought")
                react_pattern = self._load_prompt_component("components/reasoning/react_pattern")
                reasoning_content = f"\n\n{cot_reasoning['content']}\n\n{react_pattern['content']}"
            
            # 3. 加载核心场景模板
            scenario_template = self._load_prompt_component(f"scenarios/{scenario}_{version}")
            
            # 4. 加载输出格式
            output_format = self._load_prompt_component("formats/five_section_report")
            
            # 5. 组装系统Prompt
            system_prompt_content = f"""
{identity['content']}

{reasoning_content}

{safety['content']}

{output_format['content']}
"""
            
            # 6. 处理用户Prompt并注入上下文
            user_prompt_content = scenario_template['content'].format(**context)
            
            # 7. 构建消息列表
            messages = [
                {"role": "system", "content": system_prompt_content.strip()},
                {"role": "user", "content": user_prompt_content}
            ]
            
            logger.info(f"Prompt constructed successfully. System prompt length: {len(system_prompt_content)}, User prompt length: {len(user_prompt_content)}")
            
            return messages
            
        except Exception as e:
            logger.error(f"Error constructing prompt for scenario {scenario}: {e}")
            raise
    
    def get_prompt_metadata(self, scenario: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        获取Prompt元数据
        
        Args:
            scenario: 场景名称
            version: 版本号
            
        Returns:
            元数据字典
        """
        if version is None:
            version = self.get_best_version(scenario)
            
        try:
            component = self._load_prompt_component(f"scenarios/{scenario}_{version}")
            return {
                "name": component.get("name", "Unknown"),
                "version": component.get("version", version),
                "description": component.get("description", ""),
                "tags": component.get("tags", []),
                "created_at": component.get("created_at", ""),
                "author": component.get("author", "")
            }
        except Exception as e:
            logger.error(f"Error getting metadata for {scenario}_{version}: {e}")
            return {}
    
    def list_available_scenarios(self) -> List[Dict[str, Any]]:
        """
        列出所有可用的场景
        
        Returns:
            场景列表
        """
        scenarios = []
        scenarios_dir = self.base_path / "scenarios"
        
        if not scenarios_dir.exists():
            return scenarios
            
        for file_path in scenarios_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    component = json.load(f)
                    
                scenarios.append({
                    "file": file_path.stem,
                    "name": component.get("name", file_path.stem),
                    "version": component.get("version", "unknown"),
                    "description": component.get("description", "")
                })
            except Exception as e:
                logger.warning(f"Error reading scenario file {file_path}: {e}")
                
        return sorted(scenarios, key=lambda x: x["name"])
    
    def clear_cache(self):
        """清空组件缓存"""
        self.cache.clear()
        logger.info("Prompt component cache cleared")


# 全局实例
prompt_manager = PromptManager()
