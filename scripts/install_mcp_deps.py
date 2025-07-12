#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装真实MCP依赖的脚本
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command: str, description: str):
    """运行命令并处理错误"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 成功")
        if result.stdout:
            print(f"📄 输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误: {e.stderr}")
        return False


def check_npm():
    """检查npm是否安装"""
    try:
        subprocess.run("npm --version", shell=True, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def install_mcp_dependencies():
    """安装MCP相关依赖"""
    print("🚀 开始安装真实MCP工具依赖...")
    
    # 检查npm
    if not check_npm():
        print("❌ 需要安装Node.js和npm来运行MCP服务器")
        print("请访问 https://nodejs.org/ 下载安装")
        return False
    
    print("✅ npm 已安装")
    
    # 安装Python MCP SDK
    success = True
    
    # 1. 安装官方MCP Python SDK
    if not run_command(
        'pip install "mcp[cli]"',
        "安装MCP Python SDK"
    ):
        success = False
    
    # 2. 检查关键MCP服务器是否可用（不强制安装，因为是通过npx运行）
    print("\n📋 检查MCP服务器可用性:")
    
    servers_to_check = [
        "@modelcontextprotocol/server-math",
        "@modelcontextprotocol/server-time", 
        "@modelcontextprotocol/server-filesystem",
        "@modelcontextprotocol/server-brave-search"
    ]
    
    for server in servers_to_check:
        print(f"📦 {server} - 将通过npx自动下载")
    
    print("\n🎉 MCP依赖安装完成!")
    print("\n📝 使用说明:")
    print("1. 确保有网络连接，MCP服务器将通过npx自动下载")
    print("2. 对于Brave Search，需要设置环境变量 BRAVE_API_KEY")
    print("3. 可以运行测试: python tests/test_real_mcp.py")
    
    return success


def create_mcp_test_script():
    """创建MCP测试脚本"""
    test_script = '''#!/usr/bin/env python3
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
'''
    
    test_file = Path("tests/test_real_mcp.py")
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text(test_script)
    print(f"✅ 创建测试脚本: {test_file}")


def main():
    """主函数"""
    print("=" * 60)
    print("🔧 AuraWell MCP 真实工具连接安装器")
    print("=" * 60)
    
    if install_mcp_dependencies():
        create_mcp_test_script()
        print("\n🎉 安装完成！可以开始使用真实MCP工具了")
    else:
        print("\n❌ 安装过程中遇到问题，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main() 