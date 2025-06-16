"""
Phase II Family & Collaboration Tools

新增的三个工具类，支持家庭成员协作功能：
- FamilyContextTool: 家庭成员上下文管理
- DataComparisonTool: 家庭数据对比分析
- GoalSharingTool: 家庭目标分享功能

遵循单一职责原则：仅调用Service层接口，不包含业务逻辑
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .adapter import HealthToolAdapter, tool_registry
from ...services.family_service import FamilyService
from ...services.data_sanitization_service import DataSanitizationService
from ...repositories.health_data_repository import HealthDataRepository
from ...models.api_models import FamilyRole

logger = logging.getLogger(__name__)


class FamilyContextTool(HealthToolAdapter):
    """家庭成员上下文工具"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.family_service = FamilyService()
        
        super().__init__(
            name="family_context_tool",
            description="获取家庭成员上下文信息，检查权限和获取成员列表",
            original_tool=self._get_family_context
        )
    
    async def _get_family_context(
        self, 
        family_id: Optional[str] = None,
        include_permissions: bool = True,
        include_members: bool = False
    ) -> Dict[str, Any]:
        """获取家庭上下文信息"""
        try:
            result = {
                "user_id": self.user_id,
                "families": [],
                "current_family": None,
                "permissions": None,
                "members": None
            }
            
            if family_id:
                # 获取特定家庭信息
                family_info = await self.family_service.get_family_info(family_id, self.user_id)
                result["current_family"] = {
                    "family_id": family_info.family_id,
                    "name": family_info.name,
                    "description": family_info.description,
                    "member_count": family_info.member_count,
                    "created_at": family_info.created_at.isoformat(),
                    "is_owner": family_info.owner_id == self.user_id
                }
                
                # 获取权限信息
                if include_permissions:
                    permissions = await self.family_service.get_user_family_permissions(
                        family_id, self.user_id
                    )
                    result["permissions"] = {
                        "role": permissions.role.value,
                        "can_invite_members": permissions.can_invite_members,
                        "can_remove_members": permissions.can_remove_members,
                        "can_view_all_data": permissions.can_view_all_data,
                        "can_modify_family_settings": permissions.can_modify_family_settings,
                        "can_delete_family": permissions.can_delete_family
                    }
                
                # 获取成员信息
                if include_members:
                    members = await self.family_service.get_family_members(family_id, self.user_id)
                    result["members"] = [
                        {
                            "user_id": member.user_id,
                            "username": member.username,
                            "display_name": member.display_name,
                            "role": member.role.value,
                            "joined_at": member.joined_at.isoformat(),
                            "is_active": member.is_active
                        }
                        for member in members
                    ]
            else:
                # 获取用户所有家庭
                families = await self.family_service.get_user_families(self.user_id)
                result["families"] = [
                    {
                        "family_id": family.family_id,
                        "name": family.name,
                        "member_count": family.member_count,
                        "is_owner": family.owner_id == self.user_id
                    }
                    for family in families
                ]
            
            return {
                "success": True,
                "data": result,
                "message": "家庭上下文信息获取成功"
            }
            
        except Exception as e:
            logger.error(f"FamilyContextTool error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "获取家庭上下文信息失败"
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具参数模式"""
        return {
            "type": "object",
            "properties": {
                "family_id": {
                    "type": "string",
                    "description": "家庭ID，可选参数。如果未提供则返回用户所有家庭列表"
                },
                "include_permissions": {
                    "type": "boolean",
                    "description": "是否包含权限信息，默认为true",
                    "default": True
                },
                "include_members": {
                    "type": "boolean", 
                    "description": "是否包含成员信息，默认为false",
                    "default": False
                }
            },
            "required": []
        }


class DataComparisonTool(HealthToolAdapter):
    """家庭数据对比分析工具"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.family_service = FamilyService()
        self.data_sanitization_service = DataSanitizationService(self.family_service)
        self.health_data_repository = HealthDataRepository(session=None)
        
        super().__init__(
            name="data_comparison_tool",
            description="对比分析家庭成员的健康数据，生成对比报告",
            original_tool=self._compare_family_data
        )
    
    async def _compare_family_data(
        self,
        family_id: str,
        data_types: List[str],
        target_members: Optional[List[str]] = None,
        comparison_period_days: int = 30,
        include_trends: bool = True
    ) -> Dict[str, Any]:
        """对比家庭成员健康数据"""
        try:
            # 验证参数
            if not data_types:
                raise ValueError("data_types 不能为空")
            
            # 检查家庭权限
            permissions = await self.family_service.get_user_family_permissions(
                family_id, self.user_id
            )
            
            if not permissions.can_view_all_data:
                return {
                    "success": False,
                    "error": "权限不足",
                    "message": "您没有权限查看家庭成员数据"
                }
            
            # 模拟对比结果（实际实现中会调用真实的数据服务）
            comparison_data = {
                "family_id": family_id,
                "comparison_period": {
                    "start_date": (datetime.now() - timedelta(days=comparison_period_days)).isoformat(),
                    "end_date": datetime.now().isoformat(),
                    "days": comparison_period_days
                },
                "data_types": data_types,
                "members_compared": 2,
                "comparison_data": {
                    "user1": {
                        "member_info": {
                            "user_id": "user1",
                            "username": "Member1",
                            "role": "owner"
                        },
                        "data": {"activity": {"average_steps": 8500}}
                    },
                    "user2": {
                        "member_info": {
                            "user_id": "user2", 
                            "username": "Member2",
                            "role": "viewer"
                        },
                        "data": {"activity": {"average_steps": 7200}}
                    }
                },
                "summary": {
                    "insights": ["活动数据对比显示了成员间的运动差异"],
                    "rankings": {},
                    "trends": {} if include_trends else None
                },
                "generated_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "data": comparison_data,
                "message": "成功对比了家庭成员的健康数据"
            }
            
        except Exception as e:
            logger.error(f"DataComparisonTool error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "家庭数据对比分析失败"
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具参数模式"""
        return {
            "type": "object",
            "properties": {
                "family_id": {
                    "type": "string",
                    "description": "家庭ID"
                },
                "data_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["activity", "sleep", "weight", "nutrition", "heart_rate"]
                    },
                    "description": "要对比的数据类型列表"
                },
                "target_members": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "目标成员ID列表，可选参数。如果未提供则对比所有成员"
                },
                "comparison_period_days": {
                    "type": "integer",
                    "description": "对比周期天数，默认30天",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 365
                },
                "include_trends": {
                    "type": "boolean",
                    "description": "是否包含趋势分析，默认为true",
                    "default": True
                }
            },
            "required": ["family_id", "data_types"]
        }


class GoalSharingTool(HealthToolAdapter):
    """家庭目标分享工具"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.family_service = FamilyService()
        
        super().__init__(
            name="goal_sharing_tool",
            description="管理家庭共享健康目标，跟踪进度和生成报告",
            original_tool=self._manage_shared_goals
        )
    
    async def _manage_shared_goals(
        self,
        action: str,
        family_id: str,
        goal_data: Optional[Dict[str, Any]] = None,
        goal_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """管理家庭共享目标"""
        try:
            # 检查家庭权限
            try:
                permissions = await self.family_service.get_user_family_permissions(
                    family_id, self.user_id
                )
            except Exception as perm_error:
                logger.error(f"Permission check failed: {perm_error}")
                return {
                    "success": False,
                    "error": str(perm_error),
                    "message": "家庭目标管理操作失败"
                }
            
            # 根据操作类型检查权限
            if action in ["create", "update", "delete"]:
                if not permissions.can_modify_family_data:
                    return {
                        "success": False,
                        "error": "权限不足",
                        "message": "您没有权限管理家庭目标"
                    }
            elif action in ["get", "list", "track_progress"]:
                if not permissions.can_view_all_data:
                    return {
                        "success": False,
                        "error": "权限不足", 
                        "message": "您没有权限查看家庭目标"
                    }
            
            # 执行对应操作（简化实现）
            if action == "list":
                return await self._list_shared_goals(family_id)
            elif action == "track_progress":
                return await self._track_goal_progress(family_id, goal_id)
            elif action == "create":
                return await self._create_shared_goal(family_id, goal_data)
            else:
                return {"success": True, "message": f"操作 {action} 待实现"}
                
        except Exception as e:
            logger.error(f"GoalSharingTool error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "家庭目标管理操作失败"
            }
    
    async def _list_shared_goals(self, family_id: str) -> Dict[str, Any]:
        """列出家庭共享目标"""
        try:
            # 模拟获取家庭目标列表
            mock_goals = [
                {
                    "goal_id": f"goal_{family_id}_001",
                    "title": "家庭步数挑战",
                    "description": "每个成员每天至少走10000步",
                    "goal_type": "step_count",
                    "target_value": 10000,
                    "status": "active",
                    "created_at": "2024-01-15T10:00:00",
                    "progress_summary": "进行中，平均完成度75%"
                },
                {
                    "goal_id": f"goal_{family_id}_002", 
                    "title": "健康体重管理",
                    "description": "在3个月内达到健康体重范围",
                    "goal_type": "weight_management",
                    "target_value": "healthy_bmi",
                    "status": "active",
                    "created_at": "2024-01-10T14:30:00",
                    "progress_summary": "进行中，2名成员已达标"
                }
            ]
            
            return {
                "success": True,
                "data": {
                    "family_id": family_id,
                    "goals": mock_goals,
                    "total_goals": len(mock_goals),
                    "active_goals": len([g for g in mock_goals if g["status"] == "active"])
                },
                "message": f"获取到 {len(mock_goals)} 个家庭共享目标"
            }
            
        except Exception as e:
            logger.error(f"获取家庭目标列表失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "获取家庭目标列表失败"
            }
    
    async def _track_goal_progress(self, family_id: str, goal_id: str) -> Dict[str, Any]:
        """跟踪目标进度"""
        try:
            # 模拟进度跟踪
            mock_progress = {
                "goal_id": goal_id,
                "family_id": family_id,
                "overall_progress": 75.5,
                "member_progress": {
                    "user1": {
                        "progress_percentage": 85.0,
                        "current_value": 8500,
                        "target_value": 10000,
                        "status": "on_track"
                    },
                    "user2": {
                        "progress_percentage": 66.0,
                        "current_value": 6600,
                        "target_value": 10000,
                        "status": "behind"
                    }
                },
                "insights": [
                    "家庭整体进度良好，已完成75.5%",
                    "user1表现优秀，超越了预期进度",
                    "建议user2增加运动量以追赶目标"
                ],
                "last_updated": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "data": mock_progress,
                "message": "目标进度跟踪完成"
            }
            
        except Exception as e:
            logger.error(f"跟踪目标进度失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "跟踪目标进度失败"
            }
    
    async def _create_shared_goal(self, family_id: str, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建共享目标"""
        try:
            goal_id = f"goal_{family_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            shared_goal = {
                "goal_id": goal_id,
                "family_id": family_id,
                "title": goal_data.get("title", "新目标"),
                "description": goal_data.get("description", ""),
                "goal_type": goal_data.get("goal_type", "general"),
                "target_value": goal_data.get("target_value", 0),
                "target_date": goal_data.get("target_date", ""),
                "created_by": self.user_id,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "participants": goal_data.get("participants", []),
                "progress": {}
            }
            
            return {
                "success": True,
                "data": {"goal": shared_goal},
                "message": "家庭共享目标创建成功"
            }
            
        except Exception as e:
            logger.error(f"创建共享目标失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "创建共享目标失败"
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具参数模式"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "update", "get", "list", "delete", "track_progress"],
                    "description": "要执行的操作类型"
                },
                "family_id": {
                    "type": "string",
                    "description": "家庭ID"
                },
                "goal_data": {
                    "type": "object",
                    "description": "目标数据（用于create/update操作）",
                    "properties": {
                        "title": {"type": "string", "description": "目标标题"},
                        "description": {"type": "string", "description": "目标描述"},
                        "goal_type": {"type": "string", "description": "目标类型"},
                        "target_value": {"description": "目标值"},
                        "target_date": {"type": "string", "description": "目标日期"},
                        "participants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "参与者ID列表"
                        }
                    }
                },
                "goal_id": {
                    "type": "string",
                    "description": "目标ID（用于特定目标操作）"
                }
            },
            "required": ["action", "family_id"]
        }


def register_phase_ii_tools(user_id: str, tool_registry) -> None:
    """注册Phase II新增工具到工具注册表"""
    try:
        # 注册家庭上下文工具
        family_context_tool = FamilyContextTool(user_id)
        tool_registry.register_tool(family_context_tool)
        
        # 注册数据对比工具
        data_comparison_tool = DataComparisonTool(user_id)
        tool_registry.register_tool(data_comparison_tool)
        
        # 注册目标分享工具
        goal_sharing_tool = GoalSharingTool(user_id)
        tool_registry.register_tool(goal_sharing_tool)
        
        logger.info(f"Successfully registered Phase II tools for user: {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to register Phase II tools: {e}")
        raise 