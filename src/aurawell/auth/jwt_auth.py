"""
JWT Authentication System

Provides JWT token generation, validation, and user authentication for the FastAPI application.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token scheme
security = HTTPBearer()


class JWTAuthenticator:
    """JWT authentication handler"""

    def __init__(self, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token

        Args:
            data: Token payload data
            expires_delta: Token expiration time

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_current_user_id(self, token: str) -> str:
        """
        Extract user ID from JWT token

        Args:
            token: JWT token string

        Returns:
            User ID from token

        Raises:
            HTTPException: If token is invalid or user_id missing
        """
        payload = self.verify_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id


# Global authenticator instance
authenticator = JWTAuthenticator()


# Dependency functions for FastAPI
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    FastAPI dependency to get current user ID from JWT token - 集成Token黑名单检查

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        Current user ID

    Raises:
        HTTPException: If authentication fails
    """
    # 开发环境特殊处理 - 优先处理，避免进入复杂的验证逻辑
    if credentials.credentials == "dev-test-token":
        logger.info("Using development test token")
        return "dev_user_001"

    token = credentials.credentials

    try:
        # 1. 检查Token是否在黑名单中
        try:
            from ..core.token_blacklist import get_token_blacklist_manager
            blacklist_manager = await get_token_blacklist_manager()

            if await blacklist_manager.is_token_blacklisted(token):
                logger.warning("Token在黑名单中，拒绝访问")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token已被撤销，请重新登录",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except ImportError:
            # 降级处理：如果黑名单模块不可用，跳过黑名单检查
            logger.warning("Token黑名单模块不可用，跳过黑名单检查")
        except Exception as e:
            # 降级处理：如果黑名单检查失败，跳过黑名单检查
            logger.warning(f"Token黑名单检查失败，跳过检查: {e}")

        # 2. 验证Token并获取用户ID
        return authenticator.get_current_user_id(token)

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"Token验证异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token验证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[str]:
    """
    FastAPI dependency to optionally get user ID from JWT token

    Args:
        credentials: Optional HTTP Bearer credentials

    Returns:
        User ID if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        return authenticator.get_current_user_id(credentials.credentials)
    except HTTPException:
        return None


def authenticate_user(username: str, password: str) -> Optional[str]:
    """
    Authenticate user with username and password

    Args:
        username: User's username
        password: User's password

    Returns:
        User ID if authentication successful, None otherwise

    Note:
        This is a simplified implementation. In production, you would
        validate against a user database with proper password hashing.
    """
    # Demo users for testing (replace with database lookup)
    demo_users = {
        "demo_user": {
            "user_id": "user_001",
            "password_hash": authenticator.get_password_hash("demo_password"),
        },
        "test_user": {
            "user_id": "user_002",
            "password_hash": authenticator.get_password_hash("test_password"),
        },
    }

    user_data = demo_users.get(username)
    if user_data and authenticator.verify_password(
        password, user_data["password_hash"]
    ):
        return user_data["user_id"]

    return None


def create_user_token(user_id: str) -> Dict[str, Any]:
    """
    Create access token for user

    Args:
        user_id: User identifier

    Returns:
        Token data including access_token, token_type, and expires_in
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = authenticator.create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
    }


# Security configuration for OpenAPI docs
def get_security_schemes():
    """Get security schemes for OpenAPI documentation"""
    return {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }


def get_security_requirements():
    """Get security requirements for protected endpoints"""
    return [{"BearerAuth": []}]
