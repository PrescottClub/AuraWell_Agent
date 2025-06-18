#!/usr/bin/env python3
"""
服务状态检查脚本

检查前后端服务的运行状态和连接性
"""

import asyncio
import aiohttp
import sys
from datetime import datetime
from pathlib import Path


async def check_backend_api():
    """检查后端API服务"""
    print("🔍 检查后端API服务...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # 检查健康状态端点
            async with session.get('http://127.0.0.1:8001/api/v1/health') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 后端API服务正常 - 状态: {response.status}")
                    print(f"   响应: {data}")
                    return True
                else:
                    print(f"⚠️  后端API响应异常 - 状态码: {response.status}")
                    return False
    except aiohttp.ClientConnectorError:
        print("❌ 无法连接到后端API服务 (http://127.0.0.1:8001)")
        return False
    except Exception as e:
        print(f"❌ 后端API检查失败: {e}")
        return False


async def check_frontend():
    """检查前端服务"""
    print("\n🔍 检查前端服务...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:5173/') as response:
                if response.status == 200:
                    print(f"✅ 前端服务正常 - 状态: {response.status}")
                    return True
                else:
                    print(f"⚠️  前端服务响应异常 - 状态码: {response.status}")
                    return False
    except aiohttp.ClientConnectorError:
        print("❌ 无法连接到前端服务 (http://localhost:5173)")
        return False
    except Exception as e:
        print(f"❌ 前端服务检查失败: {e}")
        return False


async def check_database():
    """检查数据库连接"""
    print("\n🔍 检查数据库连接...")
    
    try:
        # 导入数据库管理器
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))
        from aurawell.database.connection import DatabaseManager
        
        db_manager = DatabaseManager()
        await db_manager.initialize()
        
        # 测试连接
        is_healthy = await db_manager.health_check()
        
        if is_healthy:
            print("✅ 数据库连接正常")
            
            # 获取表信息
            from aurawell.database.migrations import DatabaseMigrator
            migrator = DatabaseMigrator(db_manager)
            table_info = await migrator.get_table_info()
            print(f"   数据表数量: {len(table_info)}")
            
            await db_manager.close()
            return True
        else:
            print("❌ 数据库连接失败")
            await db_manager.close()
            return False
            
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return False


async def test_api_endpoints():
    """测试关键API端点"""
    print("\n🔍 测试关键API端点...")
    
    endpoints = [
        ("GET", "/api/v1/health", "系统健康检查"),
        ("GET", "/", "根端点"),
        ("GET", "/docs", "API文档"),
        ("GET", "/openapi.json", "OpenAPI规范")
    ]
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for method, endpoint, description in endpoints:
            try:
                url = f"http://127.0.0.1:8001{endpoint}"
                async with session.request(method, url) as response:
                    status = "✅" if response.status == 200 else "⚠️"
                    print(f"   {status} {description}: {response.status}")
                    results.append((endpoint, response.status == 200))
            except Exception as e:
                print(f"   ❌ {description}: 连接失败 - {e}")
                results.append((endpoint, False))
    
    return results


def print_summary(backend_ok, frontend_ok, database_ok, api_results):
    """打印检查结果摘要"""
    print("\n" + "="*60)
    print("📊 AuraWell 服务状态摘要")
    print("="*60)
    
    print(f"🖥️  后端API服务:  {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"🌐 前端服务:     {'✅ 正常' if frontend_ok else '❌ 异常'}")
    print(f"🗄️  数据库:       {'✅ 正常' if database_ok else '❌ 异常'}")
    
    print(f"\n📡 API端点测试:")
    for endpoint, success in api_results:
        status = "✅" if success else "❌"
        print(f"   {status} {endpoint}")
    
    # 服务地址
    print(f"\n🔗 服务地址:")
    print(f"   前端: http://localhost:5173/")
    print(f"   后端API: http://127.0.0.1:8001/")
    print(f"   API文档: http://127.0.0.1:8001/docs")
    
    # 总体状态
    all_ok = backend_ok and frontend_ok and database_ok
    overall_status = "✅ 所有服务正常运行" if all_ok else "⚠️  部分服务存在问题"
    print(f"\n🎯 总体状态: {overall_status}")
    
    if not all_ok:
        print("\n💡 故障排除建议:")
        if not backend_ok:
            print("   - 检查后端服务是否在8001端口运行")
            print("   - 检查.env文件配置")
        if not frontend_ok:
            print("   - 检查前端服务是否在5173端口运行")
            print("   - 检查npm依赖是否安装完整")
        if not database_ok:
            print("   - 检查数据库文件是否存在")
            print("   - 运行 python scripts/init_database.py 初始化数据库")


async def main():
    """主函数"""
    print("🚀 AuraWell 服务状态检查")
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 并行检查服务
    backend_task = check_backend_api()
    frontend_task = check_frontend()
    database_task = check_database()
    
    backend_ok, frontend_ok, database_ok = await asyncio.gather(
        backend_task, frontend_task, database_task,
        return_exceptions=True
    )
    
    # 处理异常结果
    backend_ok = backend_ok if isinstance(backend_ok, bool) else False
    frontend_ok = frontend_ok if isinstance(frontend_ok, bool) else False
    database_ok = database_ok if isinstance(database_ok, bool) else False
    
    # 测试API端点
    api_results = []
    if backend_ok:
        api_results = await test_api_endpoints()
    
    # 打印摘要
    print_summary(backend_ok, frontend_ok, database_ok, api_results)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  检查被用户中断")
    except Exception as e:
        print(f"\n\n❌ 检查过程中发生错误: {e}")
