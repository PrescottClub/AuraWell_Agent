#!/usr/bin/env python3
"""
API服务器测试启动脚本
用于验证API契约修复是否正常工作
"""

import uvicorn
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """启动API服务器进行测试"""
    print("🚀 启动AuraWell API服务器...")
    print("📋 API契约修复验证模式")
    print("="*50)
    
    try:
        # 导入API应用
        from src.aurawell.interfaces.api_interface import app
        
        print("✅ API应用导入成功")
        print("🌐 服务器将在 http://localhost:8000 启动")
        print("📖 API文档: http://localhost:8000/docs")
        print("🔍 ReDoc文档: http://localhost:8000/redoc")
        print("\n🎯 测试端点:")
        print("  • GET  /api/v1/chat/conversations/{id}/messages")
        print("  • PUT  /api/v1/user/health-goals/{id}")
        print("  • DELETE /api/v1/user/health-goals/{id}")
        print("  • GET  /api/v1/user/profile/frontend")
        print("  • GET  /api/v1/health/summary/frontend")
        print("\n按 Ctrl+C 停止服务器")
        print("="*50)
        
        # 启动服务器
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # 测试模式不需要热重载
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ 导入API应用失败: {e}")
        print("请确保所有依赖已安装:")
        print("  pip install fastapi uvicorn")
        return 1
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
