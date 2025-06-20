#!/usr/bin/env python3
"""
AuraWell 后端服务启动文件
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "aurawell.interfaces.api_interface:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
