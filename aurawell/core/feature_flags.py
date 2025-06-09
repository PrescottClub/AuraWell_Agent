"""
功能开关管理器
用于控制新旧功能的切换，支持渐进式升级
"""
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class FeatureFlagManager:
    """功能开关管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化功能开关管理器
        
        Args:
            config_path: 配置文件路径，默认为项目根目录下的feature_flags.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "feature_flags.json"
        
        self.config_path = Path(config_path)
        self.flags = self._load_flags()
    
    def _load_flags(self) -> Dict[str, Any]:
        """加载功能开关配置"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 默认配置：所有新功能都关闭，保持现有系统稳定
                default_flags = {
                    "langchain_agent": {
                        "enabled": False,
                        "rollout_percentage": 0,
                        "user_whitelist": [],
                        "feature_whitelist": []
                    },
                    "rag_knowledge": {
                        "enabled": False,
                        "rollout_percentage": 0,
                        "user_whitelist": [],
                        "feature_whitelist": []
                    },
                    "mcp_protocol": {
                        "enabled": False,
                        "rollout_percentage": 0,
                        "user_whitelist": [],
                        "feature_whitelist": []
                    }
                }
                self._save_flags(default_flags)
                return default_flags
        except Exception as e:
            logger.error(f"加载功能开关配置失败: {e}")
            return {}
    
    def _save_flags(self, flags: Dict[str, Any]) -> None:
        """保存功能开关配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(flags, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存功能开关配置失败: {e}")
    
    def is_enabled(self, feature: str, user_id: str = None, context: str = None) -> bool:
        """
        检查功能是否启用
        
        Args:
            feature: 功能名称
            user_id: 用户ID
            context: 上下文信息
            
        Returns:
            bool: 功能是否启用
        """
        if feature not in self.flags:
            return False
        
        flag_config = self.flags[feature]
        
        # 检查全局开关
        if not flag_config.get("enabled", False):
            return False
        
        # 检查用户白名单
        user_whitelist = flag_config.get("user_whitelist", [])
        if user_id and user_id in user_whitelist:
            return True
        
        # 检查功能白名单
        feature_whitelist = flag_config.get("feature_whitelist", [])
        if context and context in feature_whitelist:
            return True
        
        # 检查灰度发布百分比
        rollout_percentage = flag_config.get("rollout_percentage", 0)
        if rollout_percentage > 0:
            # 简单的哈希算法决定是否启用
            if user_id:
                hash_value = hash(user_id) % 100
                return hash_value < rollout_percentage
        
        return False
    
    def enable_feature(self, feature: str, enabled: bool = True) -> None:
        """启用或禁用功能"""
        if feature not in self.flags:
            self.flags[feature] = {
                "enabled": enabled,
                "rollout_percentage": 0,
                "user_whitelist": [],
                "feature_whitelist": []
            }
        else:
            self.flags[feature]["enabled"] = enabled
        
        self._save_flags(self.flags)
        logger.info(f"功能 {feature} {'启用' if enabled else '禁用'}")
    
    def set_rollout_percentage(self, feature: str, percentage: int) -> None:
        """设置灰度发布百分比"""
        if feature not in self.flags:
            self.flags[feature] = {
                "enabled": True,
                "rollout_percentage": percentage,
                "user_whitelist": [],
                "feature_whitelist": []
            }
        else:
            self.flags[feature]["rollout_percentage"] = percentage
        
        self._save_flags(self.flags)
        logger.info(f"功能 {feature} 灰度发布百分比设置为 {percentage}%")
    
    def add_user_to_whitelist(self, feature: str, user_id: str) -> None:
        """将用户添加到白名单"""
        if feature not in self.flags:
            self.flags[feature] = {
                "enabled": True,
                "rollout_percentage": 0,
                "user_whitelist": [user_id],
                "feature_whitelist": []
            }
        else:
            if user_id not in self.flags[feature]["user_whitelist"]:
                self.flags[feature]["user_whitelist"].append(user_id)
        
        self._save_flags(self.flags)
        logger.info(f"用户 {user_id} 已添加到功能 {feature} 白名单")
    
    def remove_user_from_whitelist(self, feature: str, user_id: str) -> None:
        """从白名单中移除用户"""
        if feature in self.flags and user_id in self.flags[feature]["user_whitelist"]:
            self.flags[feature]["user_whitelist"].remove(user_id)
            self._save_flags(self.flags)
            logger.info(f"用户 {user_id} 已从功能 {feature} 白名单中移除")
    
    def get_feature_status(self, feature: str) -> Dict[str, Any]:
        """获取功能状态"""
        return self.flags.get(feature, {})
    
    def get_all_features(self) -> Dict[str, Any]:
        """获取所有功能状态"""
        return self.flags.copy()


# 全局功能开关管理器实例
feature_flags = FeatureFlagManager()
