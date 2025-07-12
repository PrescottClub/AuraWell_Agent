"""
AuraWell Prompt Manager - 动态智能Prompt组装系统

这个模块实现了世界级的Prompt工程管理，支持：
- 模块化Prompt组装
- 版本控制和A/B测试
- 动态上下文注入
- 性能监控和优化
- 生产级错误处理和缓存优化
"""

import json
import logging
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import aiofiles
from functools import lru_cache
import os

logger = logging.getLogger(__name__)


class PromptComponentCache:
    """
    高性能Prompt组件缓存系统

    特性：
    - LRU缓存策略
    - 文件修改时间检测
    - 自动缓存失效
    """

    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache = {}
        self._access_times = {}
        self._file_mtimes = {}

    def get(self, key: str, file_path: Path) -> Optional[Dict[str, Any]]:
        """获取缓存项，检查文件修改时间"""
        try:
            if not file_path.exists():
                return None

            current_mtime = file_path.stat().st_mtime
            cached_mtime = self._file_mtimes.get(key)

            # 检查文件是否被修改
            if cached_mtime and current_mtime > cached_mtime:
                self._invalidate(key)
                return None

            # 检查缓存是否存在且未过期
            if key in self._cache:
                cache_time = self._access_times.get(key, 0)
                if time.time() - cache_time < self.ttl_seconds:
                    self._access_times[key] = time.time()
                    return self._cache[key]
                else:
                    self._invalidate(key)

            return None
        except Exception as e:
            logger.warning(f"Cache get error for {key}: {e}")
            return None

    def set(self, key: str, value: Dict[str, Any], file_path: Path):
        """设置缓存项"""
        try:
            # 检查缓存大小，执行LRU清理
            if len(self._cache) >= self.max_size:
                self._evict_lru()

            self._cache[key] = value
            self._access_times[key] = time.time()
            self._file_mtimes[key] = file_path.stat().st_mtime
        except Exception as e:
            logger.warning(f"Cache set error for {key}: {e}")

    def _invalidate(self, key: str):
        """使缓存项失效"""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
        self._file_mtimes.pop(key, None)

    def _evict_lru(self):
        """清理最近最少使用的缓存项"""
        if not self._access_times:
            return

        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        self._invalidate(lru_key)

    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
        self._access_times.clear()
        self._file_mtimes.clear()


class PromptManager:
    """
    生产级智能Prompt管理器

    核心功能：
    1. 动态组装模块化Prompt
    2. 版本管理和最优版本选择
    3. 上下文数据注入
    4. 性能监控和反馈收集
    5. 高性能缓存和错误处理
    """

    def __init__(self, prompts_base_path: Optional[str] = None):
        """
        初始化Prompt管理器

        Args:
            prompts_base_path: Prompt文件基础路径，支持环境变量配置
        """
        # 支持环境变量配置，避免硬编码
        if prompts_base_path is None:
            prompts_base_path = os.getenv('AURAWELL_PROMPTS_PATH', 'src/aurawell/prompts')

        self.base_path = Path(prompts_base_path)
        self.cache = PromptComponentCache()  # 高性能缓存系统
        self.performance_data = {}  # 性能数据缓存
        self._initialization_errors = []  # 初始化错误记录

        # 验证目录结构
        self._validate_directory_structure()

        logger.info(f"PromptManager initialized with base path: {self.base_path}")
        if self._initialization_errors:
            logger.warning(f"Initialization warnings: {len(self._initialization_errors)} issues found")

    def _validate_directory_structure(self):
        """
        验证Prompt目录结构的完整性

        检查必需的子目录是否存在，记录任何结构问题
        """
        required_dirs = ['system', 'scenarios', 'components', 'formats']
        required_subdirs = {
            'components': ['reasoning', 'context']
        }

        try:
            if not self.base_path.exists():
                error_msg = f"Prompts base directory not found: {self.base_path}"
                self._initialization_errors.append(error_msg)
                logger.error(error_msg)
                return

            # 检查必需目录
            for dir_name in required_dirs:
                dir_path = self.base_path / dir_name
                if not dir_path.exists():
                    error_msg = f"Required directory missing: {dir_path}"
                    self._initialization_errors.append(error_msg)
                    logger.warning(error_msg)

            # 检查子目录
            for parent_dir, subdirs in required_subdirs.items():
                parent_path = self.base_path / parent_dir
                if parent_path.exists():
                    for subdir in subdirs:
                        subdir_path = parent_path / subdir
                        if not subdir_path.exists():
                            error_msg = f"Required subdirectory missing: {subdir_path}"
                            self._initialization_errors.append(error_msg)
                            logger.warning(error_msg)

            logger.debug("Directory structure validation completed")

        except Exception as e:
            error_msg = f"Error validating directory structure: {e}"
            self._initialization_errors.append(error_msg)
            logger.error(error_msg)

    async def _load_prompt_component(self, path: str) -> Dict[str, Any]:
        """
        异步加载Prompt组件文件，支持高性能缓存和错误处理

        Args:
            path: 相对于base_path的文件路径（不含.json扩展名）

        Returns:
            组件数据字典

        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
            ValueError: 组件内容验证失败
        """
        file_path = self.base_path / f"{path}.json"

        # 检查缓存
        cached_component = self.cache.get(path, file_path)
        if cached_component is not None:
            logger.debug(f"Loaded prompt component from cache: {path}")
            return cached_component

        try:
            # 异步文件读取
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()

            # JSON解析
            component = json.loads(content)

            # 组件内容验证
            self._validate_component(component, path)

            # 更新缓存
            self.cache.set(path, component, file_path)

            logger.debug(f"Loaded prompt component: {path}")
            return component

        except FileNotFoundError:
            error_msg = f"Prompt component not found: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in prompt component {file_path}: {e}"
            logger.error(error_msg)
            raise json.JSONDecodeError(error_msg, e.doc, e.pos)

        except Exception as e:
            error_msg = f"Error loading prompt component {file_path}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _validate_component(self, component: Dict[str, Any], path: str):
        """
        验证Prompt组件的内容格式

        Args:
            component: 组件数据
            path: 组件路径（用于错误报告）

        Raises:
            ValueError: 组件格式不符合要求
        """
        required_fields = ['name', 'version', 'content']

        for field in required_fields:
            if field not in component:
                raise ValueError(f"Missing required field '{field}' in component {path}")

        # 验证内容不为空
        if not component['content'].strip():
            raise ValueError(f"Empty content in component {path}")

        # 验证版本格式
        version = component['version']
        if not isinstance(version, str) or not version:
            raise ValueError(f"Invalid version format in component {path}")

        logger.debug(f"Component validation passed: {path}")
    
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
            # 尝试使用版本管理服务进行智能版本选择
            from ..services.prompt_version_service import prompt_version_service
            best_version = await prompt_version_service.get_best_version(scenario, user_id)

            # 验证版本文件是否存在
            version_file = self.base_path / "scenarios" / f"{scenario}_{best_version}.json"
            if not version_file.exists():
                logger.warning(f"Best version file not found: {version_file}, falling back to default")
                return self._get_fallback_version(scenario)

            logger.debug(f"Selected best version for {scenario}: {best_version}")
            return best_version

        except ImportError:
            logger.warning("Version service not available, using fallback version selection")
            return self._get_fallback_version(scenario)
        except Exception as e:
            logger.warning(f"Failed to get best version from service: {e}")
            return self._get_fallback_version(scenario)

    def _get_fallback_version(self, scenario: str) -> str:
        """
        获取降级版本（当版本服务不可用时）

        Args:
            scenario: 场景名称

        Returns:
            降级版本号
        """
        fallback_versions = {
            "health_advice": "v3_1",
            "nutrition_planning": "v1_0",
            "exercise_guidance": "v1_0"
        }

        return fallback_versions.get(scenario, "v1_0")
    
    async def construct_prompt(
        self,
        scenario: str,
        context: Dict[str, Any],
        version: Optional[str] = None,
        user_id: Optional[str] = None,
        include_reasoning: bool = True
    ) -> List[Dict[str, str]]:
        """
        动态组装Prompt - 生产级实现，支持CoT/ReAct集成

        Args:
            scenario: 场景名称
            context: 上下文数据
            version: 指定版本（可选，默认使用最佳版本）
            user_id: 用户ID（用于A/B测试）
            include_reasoning: 是否包含推理组件

        Returns:
            消息列表，格式为 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]

        Raises:
            ValueError: 参数验证失败
            FileNotFoundError: 必需的组件文件不存在
            RuntimeError: Prompt组装失败
        """
        start_time = time.time()

        try:
            # 参数验证
            if not scenario or not isinstance(scenario, str):
                raise ValueError("Scenario must be a non-empty string")

            if not context or not isinstance(context, dict):
                raise ValueError("Context must be a non-empty dictionary")

            # 确定版本
            if version is None:
                version = await self.get_best_version(scenario, user_id)

            logger.info(f"Constructing prompt for scenario: {scenario}, version: {version}, user: {user_id}")

            # 并行加载系统级组件（性能优化）
            system_components = await asyncio.gather(
                self._load_prompt_component("system/identity_v1"),
                self._load_prompt_component("system/safety_v1"),
                return_exceptions=True
            )

            # 检查系统组件加载结果
            identity, safety = system_components
            if isinstance(identity, Exception):
                logger.error(f"Failed to load identity component: {identity}")
                raise RuntimeError("Critical system component (identity) failed to load")

            if isinstance(safety, Exception):
                logger.error(f"Failed to load safety component: {safety}")
                raise RuntimeError("Critical system component (safety) failed to load")

            # 加载推理组件（CoT和ReAct集成）
            reasoning_content = ""
            if include_reasoning:
                try:
                    reasoning_components = await asyncio.gather(
                        self._load_prompt_component("components/reasoning/chain_of_thought"),
                        self._load_prompt_component("components/reasoning/react_pattern"),
                        return_exceptions=True
                    )

                    cot_reasoning, react_pattern = reasoning_components

                    if not isinstance(cot_reasoning, Exception) and not isinstance(react_pattern, Exception):
                        reasoning_content = f"\n\n{cot_reasoning['content']}\n\n{react_pattern['content']}"
                        logger.debug("CoT and ReAct reasoning components integrated successfully")
                    else:
                        logger.warning("Some reasoning components failed to load, continuing without them")

                except Exception as e:
                    logger.warning(f"Failed to load reasoning components: {e}, continuing without them")

            # 加载核心场景模板和输出格式
            try:
                scenario_template, output_format = await asyncio.gather(
                    self._load_prompt_component(f"scenarios/{scenario}_{version}"),
                    self._load_prompt_component("formats/five_section_report"),
                    return_exceptions=True
                )

                if isinstance(scenario_template, Exception):
                    raise RuntimeError(f"Failed to load scenario template: {scenario_template}")

                if isinstance(output_format, Exception):
                    logger.warning(f"Failed to load output format: {output_format}, using default")
                    output_format = {"content": "请提供清晰、结构化的回答。"}

            except Exception as e:
                logger.error(f"Critical error loading scenario components: {e}")
                raise RuntimeError(f"Failed to load required scenario components: {e}")

            # 组装系统Prompt
            system_prompt_content = f"""
{identity['content']}

{reasoning_content}

{safety['content']}

{output_format['content']}
"""

            # 处理用户Prompt并注入上下文（安全的字符串格式化）
            try:
                user_prompt_content = self._safe_format_template(scenario_template['content'], context)
            except Exception as e:
                logger.error(f"Failed to format user prompt template: {e}")
                raise RuntimeError(f"Template formatting failed: {e}")

            # 构建最终消息列表
            messages = [
                {"role": "system", "content": system_prompt_content.strip()},
                {"role": "user", "content": user_prompt_content}
            ]

            # 性能监控
            construction_time = time.time() - start_time
            logger.info(f"Prompt constructed successfully in {construction_time:.3f}s. "
                       f"System: {len(system_prompt_content)} chars, User: {len(user_prompt_content)} chars")

            return messages

        except Exception as e:
            construction_time = time.time() - start_time
            logger.error(f"Error constructing prompt for scenario {scenario} after {construction_time:.3f}s: {e}")
            raise

    def _safe_format_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        安全的模板格式化，处理缺失的上下文变量

        Args:
            template: 模板字符串
            context: 上下文数据

        Returns:
            格式化后的字符串
        """
        try:
            # 创建安全的上下文，为缺失的变量提供默认值
            safe_context = {}

            # 提取模板中的变量
            import re
            variables = re.findall(r'\{([^}]+)\}', template)

            for var in variables:
                if var in context:
                    safe_context[var] = context[var]
                else:
                    safe_context[var] = f"[{var}_NOT_PROVIDED]"
                    logger.warning(f"Missing context variable: {var}")

            return template.format(**safe_context)

        except Exception as e:
            logger.error(f"Template formatting error: {e}")
            raise ValueError(f"Failed to format template: {e}")
    
    async def get_prompt_metadata(self, scenario: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        获取Prompt元数据

        Args:
            scenario: 场景名称
            version: 版本号

        Returns:
            元数据字典
        """
        try:
            if version is None:
                version = await self.get_best_version(scenario)

            component = await self._load_prompt_component(f"scenarios/{scenario}_{version}")
            return {
                "name": component.get("name", "Unknown"),
                "version": component.get("version", version),
                "description": component.get("description", ""),
                "tags": component.get("tags", []),
                "created_at": component.get("created_at", ""),
                "author": component.get("author", ""),
                "file_path": f"scenarios/{scenario}_{version}.json"
            }
        except Exception as e:
            logger.error(f"Error getting metadata for {scenario}_{version}: {e}")
            return {
                "error": str(e),
                "scenario": scenario,
                "version": version
            }

    async def list_available_scenarios(self) -> List[Dict[str, Any]]:
        """
        异步列出所有可用的场景

        Returns:
            场景列表
        """
        scenarios = []
        scenarios_dir = self.base_path / "scenarios"

        if not scenarios_dir.exists():
            logger.warning(f"Scenarios directory not found: {scenarios_dir}")
            return scenarios

        try:
            # 并行处理所有JSON文件
            json_files = list(scenarios_dir.glob("*.json"))

            if not json_files:
                logger.info("No scenario files found")
                return scenarios

            # 异步加载所有场景文件
            tasks = []
            for file_path in json_files:
                tasks.append(self._load_scenario_metadata(file_path))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 处理结果
            for result in results:
                if isinstance(result, Exception):
                    logger.warning(f"Failed to load scenario metadata: {result}")
                elif result:
                    scenarios.append(result)

            return sorted(scenarios, key=lambda x: x.get("name", ""))

        except Exception as e:
            logger.error(f"Error listing scenarios: {e}")
            return []

    async def _load_scenario_metadata(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        加载单个场景文件的元数据

        Args:
            file_path: 场景文件路径

        Returns:
            场景元数据或None
        """
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()

            component = json.loads(content)

            return {
                "file": file_path.stem,
                "name": component.get("name", file_path.stem),
                "version": component.get("version", "unknown"),
                "description": component.get("description", ""),
                "tags": component.get("tags", []),
                "created_at": component.get("created_at", ""),
                "author": component.get("author", ""),
                "file_path": str(file_path.relative_to(self.base_path))
            }

        except Exception as e:
            logger.warning(f"Error reading scenario file {file_path}: {e}")
            return None

    def clear_cache(self):
        """清空组件缓存"""
        self.cache.clear()
        logger.info("Prompt component cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            缓存统计数据
        """
        return {
            "cache_size": len(self.cache._cache),
            "max_size": self.cache.max_size,
            "ttl_seconds": self.cache.ttl_seconds,
            "cached_items": list(self.cache._cache.keys()),
            "initialization_errors": self._initialization_errors
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        系统健康检查

        Returns:
            健康状态报告
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }

        try:
            # 检查目录结构
            health_status["checks"]["directory_structure"] = len(self._initialization_errors) == 0

            # 检查核心组件
            try:
                await self._load_prompt_component("system/identity_v1")
                health_status["checks"]["core_components"] = True
            except Exception:
                health_status["checks"]["core_components"] = False

            # 检查场景文件
            scenarios = await self.list_available_scenarios()
            health_status["checks"]["scenarios_available"] = len(scenarios) > 0
            health_status["checks"]["scenario_count"] = len(scenarios)

            # 检查缓存状态
            cache_stats = self.get_cache_stats()
            health_status["checks"]["cache_functional"] = True
            health_status["cache_stats"] = cache_stats

            # 总体状态评估
            failed_checks = [k for k, v in health_status["checks"].items() if v is False]
            if failed_checks:
                health_status["status"] = "degraded" if len(failed_checks) < 2 else "unhealthy"
                health_status["failed_checks"] = failed_checks

        except Exception as e:
            health_status["status"] = "error"
            health_status["error"] = str(e)
            logger.error(f"Health check failed: {e}")

        return health_status


# 全局实例 - 支持环境变量配置
prompt_manager = PromptManager()
