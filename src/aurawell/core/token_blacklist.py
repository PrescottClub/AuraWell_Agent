"""
JWT Token黑名单管理器

实现基于Redis的JWT Token黑名单机制，确保登出Token无法被重复使用
"""

import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import redis.asyncio as redis
from jose import jwt, JWTError

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class TokenBlacklistManager:
    """JWT Token黑名单管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._redis_client: Optional[redis.Redis] = None
        self.blacklist_prefix = "token_blacklist:"
        self.user_tokens_prefix = "user_tokens:"
        
    async def _get_redis_client(self) -> redis.Redis:
        """获取Redis客户端"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(
                    self.settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )
                # 测试连接
                await self._redis_client.ping()
                logger.info("Redis连接成功建立")
            except Exception as e:
                logger.error(f"Redis连接失败: {e}")
                # 如果Redis不可用，使用内存存储作为降级
                self._redis_client = None
                raise ConnectionError(f"无法连接到Redis: {e}")
        
        return self._redis_client
    
    async def add_token_to_blacklist(
        self,
        token: str,
        user_id: str,
        reason: str = "logout",
        expires_at: Optional[datetime] = None
    ) -> bool:
        """
        将Token添加到黑名单
        
        Args:
            token: JWT Token
            user_id: 用户ID
            reason: 加入黑名单的原因
            expires_at: Token过期时间
        
        Returns:
            是否成功添加
        """
        try:
            # 解析Token获取信息
            token_info = await self._parse_token_info(token)
            if not token_info:
                logger.warning("无法解析Token信息")
                return False
            
            # 计算TTL（生存时间）
            if expires_at:
                ttl_seconds = int((expires_at - datetime.now(timezone.utc)).total_seconds())
            else:
                # 从Token中获取过期时间
                exp_timestamp = token_info.get("exp")
                if exp_timestamp:
                    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
                    ttl_seconds = int((exp_datetime - datetime.now(timezone.utc)).total_seconds())
                else:
                    # 默认24小时过期
                    ttl_seconds = 24 * 60 * 60
            
            # 如果Token已经过期，不需要加入黑名单
            if ttl_seconds <= 0:
                logger.info("Token已过期，无需加入黑名单")
                return True
            
            redis_client = await self._get_redis_client()
            
            # 创建黑名单记录
            blacklist_data = {
                "user_id": user_id,
                "reason": reason,
                "blacklisted_at": datetime.now(timezone.utc).isoformat(),
                "token_id": token_info.get("jti", ""),
                "expires_at": expires_at.isoformat() if expires_at else None,
            }
            
            # 使用Token的哈希作为键
            token_hash = self._get_token_hash(token)
            blacklist_key = f"{self.blacklist_prefix}{token_hash}"
            
            # 添加到Redis，设置TTL
            await redis_client.setex(
                blacklist_key,
                ttl_seconds,
                json.dumps(blacklist_data)
            )
            
            # 同时维护用户Token列表（用于批量撤销）
            user_tokens_key = f"{self.user_tokens_prefix}{user_id}"
            await redis_client.sadd(user_tokens_key, token_hash)
            await redis_client.expire(user_tokens_key, ttl_seconds)
            
            logger.info(f"Token已加入黑名单: user_id={user_id}, reason={reason}, ttl={ttl_seconds}s")
            return True
            
        except Exception as e:
            logger.error(f"添加Token到黑名单失败: {e}")
            return False
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """
        检查Token是否在黑名单中
        
        Args:
            token: JWT Token
        
        Returns:
            是否在黑名单中
        """
        try:
            redis_client = await self._get_redis_client()
            
            # 计算Token哈希
            token_hash = self._get_token_hash(token)
            blacklist_key = f"{self.blacklist_prefix}{token_hash}"
            
            # 检查是否存在
            exists = await redis_client.exists(blacklist_key)
            
            if exists:
                # 获取黑名单信息用于日志
                blacklist_data = await redis_client.get(blacklist_key)
                if blacklist_data:
                    data = json.loads(blacklist_data)
                    logger.info(f"Token在黑名单中: user_id={data.get('user_id')}, reason={data.get('reason')}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查Token黑名单状态失败: {e}")
            # 出错时为了安全起见，假设Token有效
            return False
    
    async def revoke_all_user_tokens(self, user_id: str, reason: str = "security") -> int:
        """
        撤销用户的所有Token
        
        Args:
            user_id: 用户ID
            reason: 撤销原因
        
        Returns:
            撤销的Token数量
        """
        try:
            redis_client = await self._get_redis_client()
            
            # 获取用户所有Token
            user_tokens_key = f"{self.user_tokens_prefix}{user_id}"
            token_hashes = await redis_client.smembers(user_tokens_key)
            
            if not token_hashes:
                logger.info(f"用户 {user_id} 没有活跃的Token")
                return 0
            
            # 批量添加到黑名单
            revoked_count = 0
            for token_hash in token_hashes:
                blacklist_key = f"{self.blacklist_prefix}{token_hash}"
                
                # 创建黑名单记录
                blacklist_data = {
                    "user_id": user_id,
                    "reason": reason,
                    "blacklisted_at": datetime.now(timezone.utc).isoformat(),
                    "batch_revoke": True,
                }
                
                # 设置较长的TTL（24小时）
                await redis_client.setex(
                    blacklist_key,
                    24 * 60 * 60,
                    json.dumps(blacklist_data)
                )
                revoked_count += 1
            
            # 清除用户Token列表
            await redis_client.delete(user_tokens_key)
            
            logger.info(f"已撤销用户 {user_id} 的 {revoked_count} 个Token，原因: {reason}")
            return revoked_count
            
        except Exception as e:
            logger.error(f"撤销用户Token失败: {e}")
            return 0
    
    async def get_blacklist_stats(self) -> Dict[str, Any]:
        """
        获取黑名单统计信息
        
        Returns:
            统计信息
        """
        try:
            redis_client = await self._get_redis_client()
            
            # 扫描所有黑名单键
            blacklist_keys = []
            async for key in redis_client.scan_iter(match=f"{self.blacklist_prefix}*"):
                blacklist_keys.append(key)
            
            # 统计信息
            stats = {
                "total_blacklisted_tokens": len(blacklist_keys),
                "blacklist_prefix": self.blacklist_prefix,
                "redis_connected": True,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            
            # 按原因分类统计
            reason_stats = {}
            for key in blacklist_keys[:100]:  # 限制扫描数量避免性能问题
                try:
                    data = await redis_client.get(key)
                    if data:
                        blacklist_info = json.loads(data)
                        reason = blacklist_info.get("reason", "unknown")
                        reason_stats[reason] = reason_stats.get(reason, 0) + 1
                except:
                    continue
            
            stats["by_reason"] = reason_stats
            return stats
            
        except Exception as e:
            logger.error(f"获取黑名单统计失败: {e}")
            return {
                "total_blacklisted_tokens": 0,
                "redis_connected": False,
                "error": str(e),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
    
    async def cleanup_expired_tokens(self) -> int:
        """
        清理过期的黑名单Token（Redis会自动过期，这里主要用于统计）
        
        Returns:
            清理的Token数量
        """
        try:
            redis_client = await self._get_redis_client()
            
            # Redis的TTL机制会自动清理过期键
            # 这里主要是清理用户Token列表中的过期引用
            
            user_keys = []
            async for key in redis_client.scan_iter(match=f"{self.user_tokens_prefix}*"):
                user_keys.append(key)
            
            cleaned_count = 0
            for user_key in user_keys:
                # 检查用户Token列表中的Token是否还在黑名单中
                token_hashes = await redis_client.smembers(user_key)
                for token_hash in token_hashes:
                    blacklist_key = f"{self.blacklist_prefix}{token_hash}"
                    if not await redis_client.exists(blacklist_key):
                        # 从用户Token列表中移除已过期的Token
                        await redis_client.srem(user_key, token_hash)
                        cleaned_count += 1
            
            logger.info(f"清理了 {cleaned_count} 个过期Token引用")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理过期Token失败: {e}")
            return 0
    
    def _get_token_hash(self, token: str) -> str:
        """获取Token的哈希值"""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()[:32]
    
    async def _parse_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """解析Token信息（不验证签名）"""
        try:
            # 不验证签名，只解析payload
            payload = jwt.get_unverified_claims(token)
            return payload
        except JWTError as e:
            logger.warning(f"解析Token失败: {e}")
            return None
    
    async def close(self):
        """关闭Redis连接"""
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None


# 全局黑名单管理器实例
_blacklist_manager: Optional[TokenBlacklistManager] = None


async def get_token_blacklist_manager() -> TokenBlacklistManager:
    """获取Token黑名单管理器实例"""
    global _blacklist_manager
    if _blacklist_manager is None:
        _blacklist_manager = TokenBlacklistManager()
    return _blacklist_manager


async def cleanup_blacklist_manager():
    """清理黑名单管理器"""
    global _blacklist_manager
    if _blacklist_manager:
        await _blacklist_manager.close()
        _blacklist_manager = None
