"""
AuraWell Authentication Module

Provides JWT-based authentication and authorization for the FastAPI application.
"""

from .jwt_auth import (
    JWTAuthenticator,
    authenticator,
    get_current_user_id,
    get_optional_user_id,
    authenticate_user,
    create_user_token,
    get_security_schemes,
    get_security_requirements,
)

__all__ = [
    "JWTAuthenticator",
    "authenticator",
    "get_current_user_id",
    "get_optional_user_id",
    "authenticate_user",
    "create_user_token",
    "get_security_schemes",
    "get_security_requirements",
]
