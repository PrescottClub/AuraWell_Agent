#!/usr/bin/env python3
"""
数据库管理工具

提供数据库的常用管理功能，包括查看、备份、重置等操作。
"""

import asyncio
import logging
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent  # Go up one level from scripts to project root
sys.path.insert(0, str(project_root / "src"))

from aurawell.database.connection import DatabaseManager
from aurawell.database.migrations import DatabaseMigrator
from aurawell.config.settings import AuraWellSettings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class DatabaseManagerCLI:
    """数据库管理命令行工具"""
    
    def __init__(self):
        self.db_manager = None
        self.migrator = None
    
    async def initialize(self):
        """初始化数据库管理器"""
        db_url = AuraWellSettings.DATABASE_URL or "sqlite+aiosqlite:///./aurawell.db"
        self.db_manager = DatabaseManager(db_url)
        self.migrator = DatabaseMigrator(self.db_manager)
        await self.db_manager.initialize()
    
    async def close(self):
        """关闭数据库连接"""
        if self.db_manager:
            await self.db_manager.close()
    
    async def show_status(self):
        """显示数据库状态"""
        print("📊 数据库状态信息")
        print("=" * 50)
        
        # 基本信息
        print(f"数据库URL: {self.db_manager.database_url}")
        
        # 连接测试
        is_healthy = await self.db_manager.health_check()
        status = "✅ 正常" if is_healthy else "❌ 异常"
        print(f"连接状态: {status}")
        
        # 表信息
        table_info = await self.migrator.get_table_info()
        print(f"数据表数量: {len(table_info)}")
        
        print("\n📋 数据表详情:")
        for table_name, info in table_info.items():
            print(f"  - {table_name}: {info['column_count']} 列")
        
        # 验证结构
        is_valid = await self.migrator.validate_schema()
        schema_status = "✅ 有效" if is_valid else "❌ 无效"
        print(f"\n数据库结构: {schema_status}")
    
    async def backup_database(self, backup_path: Optional[str] = None):
        """备份数据库"""
        print("💾 创建数据库备份...")
        
        success = await self.migrator.backup_database(backup_path)
        if success:
            print("✅ 数据库备份创建成功")
        else:
            print("❌ 数据库备份失败")
        
        return success
    
    async def reset_database(self):
        """重置数据库"""
        print("⚠️  警告: 这将删除所有数据!")
        response = input("确认要重置数据库吗? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("操作已取消")
            return False
        
        print("🗑️  重置数据库...")
        success = await self.migrator.reset_database()
        
        if success:
            print("✅ 数据库重置成功")
        else:
            print("❌ 数据库重置失败")
        
        return success
    
    async def export_schema(self, output_file: str = "database_schema.json"):
        """导出数据库结构"""
        print(f"📤 导出数据库结构到 {output_file}...")
        
        try:
            table_info = await self.migrator.get_table_info()
            
            schema_data = {
                "database_url": self.db_manager.database_url,
                "export_time": datetime.now().isoformat(),
                "table_count": len(table_info),
                "tables": table_info
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(schema_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 数据库结构已导出到 {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False
    
    async def show_table_data(self, table_name: str, limit: int = 10):
        """显示表数据"""
        print(f"📋 表 '{table_name}' 的数据 (前 {limit} 条):")
        print("=" * 50)
        
        try:
            async with self.db_manager.get_session() as session:
                from sqlalchemy import text
                
                # 获取表结构
                result = await session.execute(text(f"PRAGMA table_info({table_name})"))
                columns = [row[1] for row in result.fetchall()]
                
                # 获取数据
                result = await session.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
                rows = result.fetchall()
                
                if not rows:
                    print("表中没有数据")
                    return
                
                # 显示列名
                print(" | ".join(columns))
                print("-" * (len(" | ".join(columns))))
                
                # 显示数据
                for row in rows:
                    print(" | ".join(str(value) for value in row))
                
                print(f"\n显示了 {len(rows)} 条记录")
                
        except Exception as e:
            print(f"❌ 查询失败: {e}")


def print_help():
    """打印帮助信息"""
    print("""
🛠️  AuraWell 数据库管理工具

用法:
    python database_manager.py <命令> [参数]

命令:
    status              显示数据库状态信息
    backup [路径]       备份数据库 (可选指定备份路径)
    reset               重置数据库 (删除所有数据)
    export [文件]       导出数据库结构 (默认: database_schema.json)
    show <表名> [数量]  显示表数据 (默认显示10条)
    help                显示此帮助信息

示例:
    python database_manager.py status
    python database_manager.py backup ./backups/db_backup.db
    python database_manager.py show user_profiles 5
    python database_manager.py export schema.json
    """)


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'help':
        print_help()
        return
    
    # 初始化数据库管理器
    cli = DatabaseManagerCLI()
    
    try:
        await cli.initialize()
        
        if command == 'status':
            await cli.show_status()
            
        elif command == 'backup':
            backup_path = sys.argv[2] if len(sys.argv) > 2 else None
            await cli.backup_database(backup_path)
            
        elif command == 'reset':
            await cli.reset_database()
            
        elif command == 'export':
            output_file = sys.argv[2] if len(sys.argv) > 2 else "database_schema.json"
            await cli.export_schema(output_file)
            
        elif command == 'show':
            if len(sys.argv) < 3:
                print("❌ 请指定表名")
                return
            
            table_name = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            await cli.show_table_data(table_name, limit)
            
        else:
            print(f"❌ 未知命令: {command}")
            print_help()
    
    except Exception as e:
        logger.error(f"执行失败: {e}")
    
    finally:
        await cli.close()


if __name__ == "__main__":
    asyncio.run(main())
