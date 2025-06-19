"""
认证中间件

实现JWT Token验证和黑名单检查的FastAPI中间件
"""

import logging
from typing import Optional, Tuple
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from .token_blacklist import get_token_blacklist_manager
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class JWTAuthMiddleware:
    """JWT认证中间件"""

    def __init__(self):
        self.settings = get_settings()
        self.security = HTTPBearer(auto_error=False)

    async def verify_token(self, token: str) -> Tuple[bool, Optional[dict], Optional[str]]:
        """
        验证JWT Token

        Args:
            token: JWT Token字符串

        Returns:
            (is_valid, payload, error_message)
        """
        try:
            # 1. 检查Token是否在黑名单中
            blacklist_manager = await get_token_blacklist_manager()
            if await blacklist_manager.is_token_blacklisted(token):
                return False, None, "Token已被撤销"

            # 2. 验证Token签名和有效性
            payload = jwt.decode(
                token,
                self.settings.JWT_SECRET,
                algorithms=[self.settings.JWT_ALGORITHM]
            )

            # 3. 检查必要的声明
            if "sub" not in payload:
                return False, None, "Token缺少用户标识"

            if "exp" not in payload:
                return False, None, "Token缺少过期时间"

            return True, payload, None

        except jwt.ExpiredSignatureError:
            return False, None, "Token已过期"
        except jwt.InvalidTokenError:
            return False, None, "Token无效"
        except JWTError as e:
            logger.warning(f"JWT验证失败: {e}")
            return False, None, "Token验证失败"
        except Exception as e:
            logger.error(f"Token验证异常: {e}")
            return False, None, "Token验证异常"

    async def extract_token_from_request(self, request: Request) -> Optional[str]:
        """
        从请求中提取Token

        Args:
            request: FastAPI请求对象

        Returns:
            Token字符串或None
        """
        try:
            # 1. 从Authorization头提取
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                return authorization[7:]  # 移除"Bearer "前缀

            # 2. 从查询参数提取（可选）
            token = request.query_params.get("token")
            if token:
                return token

            # 3. 从Cookie提取（可选）
            token = request.cookies.get("access_token")
            if token:
                return token

            return None

        except Exception as e:
            logger.warning(f"提取Token失败: {e}")
            return None

    async def get_current_user_from_token(self, token: str) -> Optional[str]:
        """
        从Token中获取当前用户ID

        Args:
            token: JWT Token

        Returns:
            用户ID或None
        """
        is_valid, payload, _ = await self.verify_token(token)
        if is_valid and payload:
            return payload.get("sub")
        return None


# 全局认证中间件实例
_auth_middleware: Optional[JWTAuthMiddleware] = None


def get_auth_middleware() -> JWTAuthMiddleware:
    """获取认证中间件实例"""
    global _auth_middleware
    if _auth_middleware is None:
        _auth_middleware = JWTAuthMiddleware()
    return _auth_middleware


# 🔧 统一FastAPI认证依赖项
async def get_current_user_id(request: Request) -> str:
    """
    统一的FastAPI认证依赖项：获取当前认证用户ID

    这是系统中唯一的用户ID获取方法，整合了Token验证和黑名单检查

    Args:
        request: FastAPI请求对象

    Returns:
        用户ID

    Raises:
        HTTPException: 认证失败时抛出
    """
    auth_middleware = get_auth_middleware()

    # 开发环境特殊处理
    from ..config.settings import get_settings
    settings = get_settings()

    # 提取Token
    token = await auth_middleware.extract_token_from_request(request)

    # 开发环境允许测试token
    if not token and settings.ENVIRONMENT == "development":
        # 检查是否有开发测试token
        auth_header = request.headers.get("Authorization", "")
        if auth_header == "Bearer dev-test-token":
            logger.info("🔧 开发环境：使用测试token")
            return "dev_user_001"

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 返回用户ID
    # 验证Token（包含黑名单检查）
    is_valid, payload, error_message = await auth_middleware.verify_token(token)
    if not is_valid:
        logger.warning(f"Token验证失败: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message or "认证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token中缺少用户标识",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"✅ 用户认证成功: {user_id}")
    return user_id


async def get_optional_current_user_id(request: Request) -> Optional[str]:
    """
    FastAPI依赖项：获取当前认证用户ID（可选）

    Args:
        request: FastAPI请求对象

    Returns:
        用户ID或None（如果未认证）
    """
    try:
        return await get_current_user_id(request)
    except HTTPException:
        return None


# Token提取器（用于需要手动处理的场景）
class TokenExtractor:
    """Token提取器"""

    def __init__(self):
        self.auth_middleware = get_auth_middleware()

    async def extract_and_verify_token(self, request: Request) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        提取并验证Token

        Args:
            request: FastAPI请求对象

        Returns:
            (is_authenticated, user_id, payload)
        """
        try:
            # 提取Token
            token = await self.auth_middleware.extract_token_from_request(request)
            if not token:
                return False, None, None

            # 验证Token
            is_valid, payload, _ = await self.auth_middleware.verify_token(token)
            if not is_valid or not payload:
                return False, None, None

            user_id = payload.get("sub")
            return True, user_id, payload

        except Exception as e:
            logger.warning(f"Token提取和验证失败: {e}")
            return False, None, None


# 认证装饰器（用于函数级别的认证）
def require_auth(func):
    """
    认证装饰器

    用于需要认证的函数，自动验证Token并注入用户ID
    """
    import functools

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # 查找Request对象
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        if not request:
            raise ValueError("require_auth装饰器需要Request参数")

        # 验证认证
        user_id = await get_current_user_id(request)

        # 将用户ID注入到kwargs中
        kwargs["current_user_id"] = user_id

        return await func(*args, **kwargs)

    return wrapper


# 权限检查器
class PermissionChecker:
    """权限检查器"""

    @staticmethod
    async def check_user_permission(
        user_id: str,
        required_permission: str,
        resource_id: Optional[str] = None
    ) -> bool:
        """
        检查用户权限

        Args:
            user_id: 用户ID
            required_permission: 所需权限
            resource_id: 资源ID（可选）

        Returns:
            是否有权限
        """
        # TODO: 实现具体的权限检查逻辑
        # 这里可以查询数据库或缓存来验证用户权限

        # 临时实现：所有认证用户都有基本权限
        basic_permissions = ["read", "write", "update"]
        if required_permission in basic_permissions:
            return True

        # 管理员权限需要特殊检查
        admin_permissions = ["admin", "delete", "manage_users"]
        if required_permission in admin_permissions:
            # TODO: 查询用户是否为管理员
            return False

        return False

    @staticmethod
    async def require_permission(
        user_id: str,
        required_permission: str,
        resource_id: Optional[str] = None
    ) -> None:
        """
        要求特定权限，如果没有权限则抛出异常

        Args:
            user_id: 用户ID
            required_permission: 所需权限
            resource_id: 资源ID（可选）

        Raises:
            HTTPException: 权限不足时抛出
        """
        has_permission = await PermissionChecker.check_user_permission(
            user_id, required_permission, resource_id
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {required_permission} 权限",
            )


# 创建全局实例
token_extractor = TokenExtractor()
permission_checker = PermissionChecker()
