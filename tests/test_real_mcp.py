#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实MCP连接测试脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

async def test_real_mcp():
    """测试真实MCP连接"""
    try:
        from aurawell.langchain_agent.mcp_real_interface import test_real_mcp_connection
        await test_real_mcp_connection()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请先安装MCP依赖: python scripts/install_mcp_deps.py")
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_real_mcp())
