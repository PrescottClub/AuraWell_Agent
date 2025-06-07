#!/usr/bin/env python3
"""
AuraWell数据库初始化脚本

用于初始化SQLAlchemy数据库，创建所有必要的表结构。
支持SQLite和PostgreSQL数据库。

Usage:
    python init_database.py [--database-url DATABASE_URL] [--reset]
    
Examples:
    # 使用默认SQLite数据库
    python init_database.py
    
    # 使用自定义数据库URL
    python init_database.py --database-url "postgresql+asyncpg://user:pass@localhost/aurawell"
    
    # 重置数据库（删除所有数据）
    python init_database.py --reset
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def init_database(database_url: str = None, reset: bool = False):
    """
    初始化数据库
    
    Args:
        database_url: 数据库连接URL
        reset: 是否重置数据库
    """
    try:
        from aurawell.database.migrations import DatabaseMigrator
        from aurawell.database.connection import DatabaseManager
        
        # 创建数据库管理器
        if database_url:
            db_manager = DatabaseManager(database_url)
            logger.info(f"使用自定义数据库URL: {database_url}")
        else:
            db_manager = DatabaseManager()
            logger.info(f"使用默认数据库URL: {db_manager.database_url}")
        
        # 创建迁移器
        migrator = DatabaseMigrator(db_manager)
        
        if reset:
            logger.warning("重置数据库 - 所有数据将被删除！")
            success = await migrator.reset_database()
            if success:
                logger.info("✅ 数据库重置成功")
            else:
                logger.error("❌ 数据库重置失败")
                return False
        else:
            # 初始化数据库
            logger.info("初始化数据库...")
            success = await migrator.initialize_database()
            if success:
                logger.info("✅ 数据库初始化成功")
            else:
                logger.error("❌ 数据库初始化失败")
                return False
        
        # 验证数据库模式
        logger.info("验证数据库模式...")
        valid = await migrator.validate_schema()
        if valid:
            logger.info("✅ 数据库模式验证通过")
        else:
            logger.warning("⚠️ 数据库模式验证失败")
        
        # 获取表信息
        table_info = await migrator.get_table_info()
        logger.info(f"📊 数据库统计: {len(table_info)} 个表")
        for table_name, info in table_info.items():
            logger.info(f"   - {table_name}: {info['column_count']} 列")
        
        # 关闭数据库连接
        await db_manager.close()
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ 导入错误: {e}")
        logger.error("请确保已安装所有依赖: pip install -r requirements.txt")
        return False
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_database_connection(database_url: str = None):
    """
    测试数据库连接
    
    Args:
        database_url: 数据库连接URL
    """
    try:
        from aurawell.database.connection import DatabaseManager
        
        # 创建数据库管理器
        if database_url:
            db_manager = DatabaseManager(database_url)
        else:
            db_manager = DatabaseManager()
        
        logger.info("测试数据库连接...")
        
        # 健康检查
        is_healthy = await db_manager.health_check()
        
        if is_healthy:
            logger.info("✅ 数据库连接正常")
        else:
            logger.error("❌ 数据库连接失败")
            return False
        
        # 关闭连接
        await db_manager.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库连接测试失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AuraWell数据库初始化脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                                    # 使用默认SQLite数据库
  %(prog)s --database-url "sqlite:///test.db" # 使用自定义SQLite数据库
  %(prog)s --reset                            # 重置数据库
  %(prog)s --test-only                        # 仅测试连接
        """
    )
    
    parser.add_argument(
        "--database-url",
        help="数据库连接URL (例如: sqlite:///aurawell.db 或 postgresql+asyncpg://user:pass@localhost/aurawell)"
    )
    
    parser.add_argument(
        "--reset",
        action="store_true",
        help="重置数据库（删除所有表和数据）"
    )
    
    parser.add_argument(
        "--test-only",
        action="store_true",
        help="仅测试数据库连接，不进行初始化"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 显示欢迎信息
    print("🚀 AuraWell数据库初始化工具")
    print("=" * 40)
    
    async def run():
        if args.test_only:
            # 仅测试连接
            success = await test_database_connection(args.database_url)
        else:
            # 初始化数据库
            success = await init_database(args.database_url, args.reset)
        
        if success:
            print("\n🎉 操作完成！")
            return 0
        else:
            print("\n❌ 操作失败！")
            return 1
    
    # 运行异步函数
    try:
        exit_code = asyncio.run(run())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ 操作被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 未预期的错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
