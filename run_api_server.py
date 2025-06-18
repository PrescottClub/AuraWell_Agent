#!/usr/bin/env python3
"""
AuraWell FastAPI Server Startup Script

Starts the FastAPI server with proper configuration for development and production.
"""

import os
import sys
import uvicorn
import logging
from pathlib import Path

# Add the src directory to Python path for new structure
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Start the FastAPI server"""
    
    # Environment configuration
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    workers = int(os.getenv("API_WORKERS", "1"))
    
    # Log configuration
    logger.info("Starting AuraWell FastAPI Server")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Reload: {reload}")
    logger.info(f"Workers: {workers}")
    
    # Check for required environment variables
    required_env_vars = ["DEEPSEEK_API_KEY"]
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Some features may not work properly. Please check your .env file.")
    
    try:
        # Start the server
        uvicorn.run(
            "aurawell.interfaces.api_interface:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,  # Workers > 1 not compatible with reload
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
