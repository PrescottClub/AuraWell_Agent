"""
数据库初始化检查工具
验证数据库配置是否正确，修复常见的配置问题
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class DatabaseConfigChecker:
    """数据库配置检查器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.default_db_path = self.project_root / "aurawell.db"
    
    def check_database_config(self) -> Dict[str, Any]:
        """
        检查数据库配置
        
        Returns:
            配置检查结果
        """
        results = {
            "status": "success",
            "issues": [],
            "recommendations": [],
            "current_config": {},
            "suggested_config": {}
        }
        
        # 检查环境变量
        database_url = os.getenv("DATABASE_URL")
        results["current_config"]["DATABASE_URL"] = database_url
        
        if not database_url:
            # 没有配置 DATABASE_URL
            results["issues"].append("DATABASE_URL environment variable not set")
            suggested_url = f"sqlite+aiosqlite:///{self.default_db_path}"
            results["suggested_config"]["DATABASE_URL"] = suggested_url
            results["recommendations"].append(f"Set DATABASE_URL={suggested_url}")
        else:
            # 验证 DATABASE_URL 格式
            validation_result = self._validate_database_url(database_url)
            if not validation_result["valid"]:
                results["status"] = "error"
                results["issues"].extend(validation_result["errors"])
                results["recommendations"].extend(validation_result["recommendations"])
        
        # 检查数据库文件路径
        if database_url and "sqlite" in database_url:
            db_file_check = self._check_sqlite_file_path(database_url)
            if db_file_check["issues"]:
                results["issues"].extend(db_file_check["issues"])
                results["recommendations"].extend(db_file_check["recommendations"])
        
        return results
    
    def _validate_database_url(self, database_url: str) -> Dict[str, Any]:
        """验证数据库 URL 格式"""
        result = {
            "valid": True,
            "errors": [],
            "recommendations": []
        }
        
        try:
            parsed = urlparse(database_url)
            
            # 检查协议
            if not parsed.scheme:
                result["valid"] = False
                result["errors"].append("Database URL missing scheme (e.g., sqlite+aiosqlite://)")
                result["recommendations"].append("Use format: sqlite+aiosqlite:///path/to/db.db")
            
            # SQLite 特定检查
            if "sqlite" in parsed.scheme:
                if not parsed.path:
                    result["valid"] = False
                    result["errors"].append("SQLite URL missing database file path")
                    result["recommendations"].append("Include database file path: sqlite+aiosqlite:///path/to/db.db")
                
                # 检查是否使用了 aiosqlite 驱动
                if "aiosqlite" not in parsed.scheme:
                    result["valid"] = False
                    result["errors"].append("SQLite URL should use aiosqlite driver for async support")
                    result["recommendations"].append("Use sqlite+aiosqlite:// instead of sqlite://")
            
            # PostgreSQL 特定检查
            elif "postgresql" in parsed.scheme:
                if not parsed.hostname:
                    result["valid"] = False
                    result["errors"].append("PostgreSQL URL missing hostname")
                if not parsed.path or parsed.path == "/":
                    result["valid"] = False
                    result["errors"].append("PostgreSQL URL missing database name")
                    
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Invalid URL format: {str(e)}")
            result["recommendations"].append("Check URL syntax and encoding")
        
        return result
    
    def _check_sqlite_file_path(self, database_url: str) -> Dict[str, Any]:
        """检查 SQLite 文件路径"""
        result = {
            "issues": [],
            "recommendations": []
        }
        
        try:
            parsed = urlparse(database_url)
            if parsed.path:
                # 处理 SQLite 路径
                db_path = parsed.path
                if db_path.startswith("/"):
                    db_path = db_path[1:]  # 移除开头的斜杠
                
                db_file = Path(db_path)
                
                # 检查父目录是否存在
                if not db_file.parent.exists():
                    result["issues"].append(f"Database directory does not exist: {db_file.parent}")
                    result["recommendations"].append(f"Create directory: mkdir -p {db_file.parent}")
                
                # 检查文件权限
                if db_file.exists() and not os.access(db_file, os.R_OK | os.W_OK):
                    result["issues"].append(f"Database file permissions issue: {db_file}")
                    result["recommendations"].append(f"Fix permissions: chmod 666 {db_file}")
                
        except Exception as e:
            result["issues"].append(f"Error checking SQLite path: {str(e)}")
        
        return result
    
    def fix_database_config(self, auto_fix: bool = False) -> Dict[str, Any]:
        """
        修复数据库配置问题
        
        Args:
            auto_fix: 是否自动修复
            
        Returns:
            修复结果
        """
        check_result = self.check_database_config()
        
        if check_result["status"] == "success":
            return {"status": "no_issues", "message": "Database configuration is valid"}
        
        if not auto_fix:
            return {
                "status": "manual_action_required",
                "issues": check_result["issues"],
                "recommendations": check_result["recommendations"]
            }
        
        # 自动修复逻辑
        fix_result = {
            "status": "success",
            "actions_taken": [],
            "remaining_issues": []
        }
        
        # 自动创建默认 SQLite 配置
        if "DATABASE_URL environment variable not set" in check_result["issues"]:
            suggested_url = check_result["suggested_config"]["DATABASE_URL"]
            os.environ["DATABASE_URL"] = suggested_url
            fix_result["actions_taken"].append(f"Set DATABASE_URL to {suggested_url}")
        
        # 创建 SQLite 数据库文件目录
        database_url = os.getenv("DATABASE_URL")
        if database_url and "sqlite" in database_url:
            try:
                parsed = urlparse(database_url)
                if parsed.path:
                    db_path = parsed.path[1:] if parsed.path.startswith("/") else parsed.path
                    db_file = Path(db_path)
                    
                    # 创建父目录
                    db_file.parent.mkdir(parents=True, exist_ok=True)
                    fix_result["actions_taken"].append(f"Created database directory: {db_file.parent}")
                    
                    # 创建空数据库文件（如果不存在）
                    if not db_file.exists():
                        db_file.touch()
                        fix_result["actions_taken"].append(f"Created database file: {db_file}")
                        
            except Exception as e:
                fix_result["remaining_issues"].append(f"Failed to create database file: {str(e)}")
        
        return fix_result
    
    def generate_env_template(self) -> str:
        """生成环境变量模板"""
        template = f"""# Database Configuration
# Choose one of the following options:

# Option 1: SQLite (recommended for development)
DATABASE_URL=sqlite+aiosqlite:///{self.default_db_path}

# Option 2: PostgreSQL (recommended for production)
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/aurawell

# Option 3: In-memory SQLite (for testing only)
# DATABASE_URL=sqlite+aiosqlite:///:memory:
"""
        return template


def check_and_fix_database_config(auto_fix: bool = False) -> Dict[str, Any]:
    """
    便捷函数：检查并修复数据库配置
    
    Args:
        auto_fix: 是否自动修复问题
        
    Returns:
        检查和修复结果
    """
    checker = DatabaseConfigChecker()
    
    # 先检查配置
    check_result = checker.check_database_config()
    
    if check_result["status"] != "success":
        logger.warning(f"Database configuration issues found: {check_result['issues']}")
        
        # 尝试修复
        fix_result = checker.fix_database_config(auto_fix=auto_fix)
        
        return {
            "check_result": check_result,
            "fix_result": fix_result,
            "status": fix_result["status"]
        }
    
    return {
        "check_result": check_result,
        "status": "success",
        "message": "Database configuration is valid"
    }


if __name__ == "__main__":
    # 命令行使用示例
    import sys
    
    auto_fix = "--auto-fix" in sys.argv
    result = check_and_fix_database_config(auto_fix=auto_fix)
    
    print(f"Database Configuration Check Result: {result['status']}")
    
    if result["status"] != "success":
        print("\nIssues found:")
        for issue in result.get("check_result", {}).get("issues", []):
            print(f"  - {issue}")
        
        print("\nRecommendations:")
        for rec in result.get("check_result", {}).get("recommendations", []):
            print(f"  - {rec}")
        
        if auto_fix and "fix_result" in result:
            print("\nActions taken:")
            for action in result["fix_result"].get("actions_taken", []):
                print(f"  - {action}")
    else:
        print("✅ Database configuration is valid!") 