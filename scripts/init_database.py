#!/usr/bin/env python3
"""
数据库初始化脚本

用于初始化AuraWell项目的数据库，创建所有必要的表结构。
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent  # Go up one level from scripts to project root
sys.path.insert(0, str(project_root / "src"))

from aurawell.database.connection import DatabaseManager, init_database
from aurawell.database.migrations import DatabaseMigrator, init_database_schema
from aurawell.config.settings import AuraWellSettings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """主函数：初始化数据库"""
    
    logger.info("🚀 开始初始化AuraWell数据库...")
    
    try:
        # 1. 检查配置
        logger.info("📋 检查数据库配置...")
        
        # 获取数据库URL，如果没有配置则使用默认SQLite
        db_url = AuraWellSettings.DATABASE_URL
        if not db_url:
            db_url = "sqlite+aiosqlite:///aurawell.db"
            logger.info(f"使用默认SQLite数据库: {db_url}")
        else:
            logger.info(f"使用配置的数据库: {db_url}")
        
        # 2. 初始化数据库管理器
        logger.info("🔧 初始化数据库管理器...")
        db_manager = DatabaseManager(db_url)
        migrator = DatabaseMigrator(db_manager)
        
        # 3. 检查数据库是否已存在
        logger.info("🔍 检查现有数据库状态...")
        await db_manager.initialize()
        
        table_info = await migrator.get_table_info()
        if table_info:
            logger.info(f"发现现有表: {list(table_info.keys())}")
            
            # 询问是否重置数据库
            response = input("数据库已存在，是否要重置？(y/N): ").strip().lower()
            if response in ['y', 'yes']:
                logger.warning("🗑️  重置数据库...")
                success = await migrator.reset_database()
                if not success:
                    logger.error("❌ 数据库重置失败")
                    return False
                logger.info("✅ 数据库重置成功")
            else:
                logger.info("保持现有数据库不变")
        else:
            # 4. 创建数据库表
            logger.info("📊 创建数据库表...")
            success = await migrator.create_tables()
            if not success:
                logger.error("❌ 数据库表创建失败")
                return False
            logger.info("✅ 数据库表创建成功")
        
        # 5. 验证数据库结构
        logger.info("🔍 验证数据库结构...")
        is_valid = await migrator.validate_schema()
        if not is_valid:
            logger.error("❌ 数据库结构验证失败")
            return False
        logger.info("✅ 数据库结构验证通过")
        
        # 6. 显示数据库信息
        logger.info("📈 数据库信息:")
        table_info = await migrator.get_table_info()
        for table_name, info in table_info.items():
            logger.info(f"  - {table_name}: {info['column_count']} 列")
        
        # 7. 测试数据库连接
        logger.info("🔗 测试数据库连接...")
        is_healthy = await db_manager.health_check()
        if not is_healthy:
            logger.error("❌ 数据库连接测试失败")
            return False
        logger.info("✅ 数据库连接正常")
        
        # 8. 创建备份（如果是SQLite）
        if db_url.startswith("sqlite"):
            logger.info("💾 创建数据库备份...")
            backup_success = await migrator.backup_database()
            if backup_success:
                logger.info("✅ 数据库备份创建成功")
        
        logger.info("🎉 数据库初始化完成！")
        logger.info(f"数据库位置: {db_url}")
        logger.info(f"总表数: {len(table_info)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        return False
    
    finally:
        # 关闭数据库连接
        if 'db_manager' in locals():
            await db_manager.close()


def print_usage():
    """打印使用说明"""
    print("""
🏥 AuraWell 数据库初始化工具

用法:
    python init_database.py

功能:
    - 自动检测数据库配置
    - 创建所有必要的数据表
    - 验证数据库结构
    - 测试数据库连接
    - 创建数据库备份

数据库表包括:
    📊 用户管理: user_profiles, user_health_profiles
    🏃 健康数据: activity_summaries, sleep_sessions, heart_rate_samples, nutrition_entries
    📋 健康计划: health_plans, health_plan_modules, health_plan_progress, health_plan_feedback
    💬 对话系统: conversations, messages
    🏆 成就系统: achievement_progress
    🔗 平台连接: platform_connections

注意: 请确保已正确配置 .env 文件中的数据库设置
    """)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print_usage()
    else:
        try:
            success = asyncio.run(main())
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            logger.info("用户中断操作")
            sys.exit(1)
        except Exception as e:
            logger.error(f"程序异常: {e}")
            sys.exit(1)
