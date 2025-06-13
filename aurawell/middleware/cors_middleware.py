"""
CORS Middleware Configuration

Configures Cross-Origin Resource Sharing (CORS) for frontend integration.
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os
from typing import List


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    # Get allowed origins from environment or use defaults
    allowed_origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "")

    if allowed_origins_env:
        allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]
    else:
        # Default allowed origins for development
        allowed_origins = [
            "http://localhost:3000",  # React dev server
            "http://localhost:8080",  # Vue dev server
            "http://localhost:5173",  # Vite dev server (default)
            "http://localhost:5174",  # Vite dev server (alternative port)
            "http://localhost:5175",  # Vite dev server (alternative port)
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
        ]
    
    # Add production origins if specified
    production_origin = os.getenv("PRODUCTION_ORIGIN")
    if production_origin:
        allowed_origins.append(production_origin)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "User-Agent",
            "DNT",
            "Cache-Control",
            "X-Mx-ReqToken",
            "Keep-Alive",
            "X-Requested-With",
            "If-Modified-Since",
        ],
        expose_headers=[
            "Content-Length",
            "Content-Range",
            "X-Total-Count",
        ],
        max_age=86400,  # 24 hours
    )


def get_cors_config() -> dict:
    """
    Get CORS configuration for documentation
    
    Returns:
        CORS configuration dictionary
    """
    return {
        "description": "CORS is configured to allow requests from frontend applications",
        "allowed_origins": [
            "http://localhost:3000",
            "http://localhost:8080", 
            "http://localhost:5173",
            "Production frontend domain (configurable)"
        ],
        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "credentials_supported": True
    }
