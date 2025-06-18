#!/usr/bin/env python3
"""
数据库迁移管理脚本

提供数据库迁移、升级、降级等操作
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

from aurawell.database.base import Base
from aurawell.database.manager import DatabaseManager


def get_alembic_config():
    """获取 Alembic 配置"""
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    
    # 设置脚本位置
    alembic_cfg.set_main_option("script_location", str(project_root / "migrations"))
    
    # 设置数据库URL
    database_url = os.getenv('DATABASE_URL', 'sqlite:///aurawell.db')
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    
    return alembic_cfg


def init_alembic():
    """初始化 Alembic"""
    print("🔧 初始化 Alembic...")
    
    try:
        alembic_cfg = get_alembic_config()
        
        # 检查是否已经初始化
        versions_dir = project_root / "migrations" / "versions"
        if not versions_dir.exists():
            versions_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ Alembic 初始化完成")
        return True
        
    except Exception as e:
        print(f"❌ Alembic 初始化失败: {e}")
        return False


def create_migration(message: str):
    """创建新的迁移"""
    print(f"📝 创建迁移: {message}")
    
    try:
        alembic_cfg = get_alembic_config()
        command.revision(alembic_cfg, message=message, autogenerate=True)
        print("✅ 迁移创建成功")
        return True
        
    except Exception as e:
        print(f"❌ 创建迁移失败: {e}")
        return False


def upgrade_database(revision: str = "head"):
    """升级数据库"""
    print(f"⬆️  升级数据库到: {revision}")
    
    try:
        alembic_cfg = get_alembic_config()
        command.upgrade(alembic_cfg, revision)
        print("✅ 数据库升级成功")
        return True
        
    except Exception as e:
        print(f"❌ 数据库升级失败: {e}")
        return False


def downgrade_database(revision: str):
    """降级数据库"""
    print(f"⬇️  降级数据库到: {revision}")
    
    try:
        alembic_cfg = get_alembic_config()
        command.downgrade(alembic_cfg, revision)
        print("✅ 数据库降级成功")
        return True
        
    except Exception as e:
        print(f"❌ 数据库降级失败: {e}")
        return False


def show_current_revision():
    """显示当前数据库版本"""
    print("📋 当前数据库版本:")
    
    try:
        alembic_cfg = get_alembic_config()
        command.current(alembic_cfg)
        return True
        
    except Exception as e:
        print(f"❌ 获取当前版本失败: {e}")
        return False


def show_migration_history():
    """显示迁移历史"""
    print("📚 迁移历史:")
    
    try:
        alembic_cfg = get_alembic_config()
        command.history(alembic_cfg)
        return True
        
    except Exception as e:
        print(f"❌ 获取迁移历史失败: {e}")
        return False


async def init_database():
    """初始化数据库"""
    print("🗄️  初始化数据库...")
    
    try:
        # 创建数据库管理器
        db_manager = DatabaseManager()
        await db_manager.initialize()
        
        print("✅ 数据库初始化成功")
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False


async def check_database_status():
    """检查数据库状态"""
    print("🔍 检查数据库状态...")
    
    try:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///aurawell.db')
        
        if database_url.startswith('sqlite'):
            # SQLite 数据库
            db_file = database_url.replace('sqlite:///', '')
            if os.path.exists(db_file):
                print(f"✅ SQLite 数据库文件存在: {db_file}")
                
                # 检查文件大小
                size = os.path.getsize(db_file)
                print(f"📊 数据库文件大小: {size} bytes")
                
                # 检查表
                engine = create_engine(database_url)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                    tables = [row[0] for row in result]
                    print(f"📋 数据库表: {len(tables)} 个")
                    for table in tables:
                        print(f"   - {table}")
                
                engine.dispose()
            else:
                print(f"❌ SQLite 数据库文件不存在: {db_file}")
                return False
        else:
            # 其他数据库
            engine = create_async_engine(database_url)
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                if result.scalar():
                    print("✅ 数据库连接正常")
            await engine.dispose()
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库状态检查失败: {e}")
        return False


def reset_database():
    """重置数据库"""
    print("🔄 重置数据库...")
    
    try:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///aurawell.db')
        
        if database_url.startswith('sqlite'):
            # 删除 SQLite 文件
            db_file = database_url.replace('sqlite:///', '')
            if os.path.exists(db_file):
                os.remove(db_file)
                print(f"🗑️  删除数据库文件: {db_file}")
            
            # 删除相关文件
            for ext in ['-shm', '-wal']:
                file_path = db_file + ext
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🗑️  删除文件: {file_path}")
        
        print("✅ 数据库重置成功")
        return True
        
    except Exception as e:
        print(f"❌ 数据库重置失败: {e}")
        return False


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AuraWell 数据库迁移管理")
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 初始化命令
    subparsers.add_parser('init', help='初始化数据库和 Alembic')
    
    # 迁移命令
    migration_parser = subparsers.add_parser('migrate', help='创建新迁移')
    migration_parser.add_argument('message', help='迁移描述')
    
    # 升级命令
    upgrade_parser = subparsers.add_parser('upgrade', help='升级数据库')
    upgrade_parser.add_argument('--revision', default='head', help='目标版本 (默认: head)')
    
    # 降级命令
    downgrade_parser = subparsers.add_parser('downgrade', help='降级数据库')
    downgrade_parser.add_argument('revision', help='目标版本')
    
    # 状态命令
    subparsers.add_parser('current', help='显示当前数据库版本')
    subparsers.add_parser('history', help='显示迁移历史')
    subparsers.add_parser('status', help='检查数据库状态')
    
    # 重置命令
    subparsers.add_parser('reset', help='重置数据库')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("=" * 60)
    print("🗄️  AuraWell 数据库迁移管理")
    print("=" * 60)
    
    success = False
    
    if args.command == 'init':
        success = init_alembic() and await init_database()
    elif args.command == 'migrate':
        success = create_migration(args.message)
    elif args.command == 'upgrade':
        success = upgrade_database(args.revision)
    elif args.command == 'downgrade':
        success = downgrade_database(args.revision)
    elif args.command == 'current':
        success = show_current_revision()
    elif args.command == 'history':
        success = show_migration_history()
    elif args.command == 'status':
        success = await check_database_status()
    elif args.command == 'reset':
        success = reset_database()
    
    print("=" * 60)
    if success:
        print("🎉 操作完成")
    else:
        print("❌ 操作失败")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
