#!/usr/bin/env python3
"""
AuraWell 后端服务启动文件
"""

import sys
import os
from pathlib import Path
import uvicorn

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    uvicorn.run(
        "src.aurawell.interfaces.api_interface:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
