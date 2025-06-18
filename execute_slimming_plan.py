#!/usr/bin/env python3
"""
AuraWell Agent 瘦身计划执行脚本

安全地移除冗余依赖项，为Agent卸下不必要的负重。
基于详细的依赖项分析报告，分阶段执行瘦身计划。

版本: 1.0.0
"""

import subprocess
import sys
import time
from typing import List, Dict, Tuple

class SlimmingExecutor:
    def __init__(self):
        self.removed_packages = []
        self.failed_removals = []
        self.execution_log = []
    
    def log_action(self, action: str, status: str, details: str = ""):
        """记录执行动作"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {action}: {status}"
        if details:
            log_entry += f" - {details}"
        
        self.execution_log.append(log_entry)
        print(log_entry)
    
    def execute_command(self, command: str) -> Tuple[bool, str, str]:
        """执行命令并返回结果"""
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "命令执行超时"
        except Exception as e:
            return False, "", str(e)
    
    def uninstall_packages(self, packages: List[str], phase_name: str) -> bool:
        """卸载一组包"""
        print(f"\n🗑️  {phase_name}")
        print("=" * 50)
        
        all_success = True
        
        for package in packages:
            print(f"📦 正在移除: {package}")
            
            success, stdout, stderr = self.execute_command(f"pip uninstall {package} -y")
            
            if success:
                self.log_action(f"移除 {package}", "✅ 成功")
                self.removed_packages.append(package)
            else:
                self.log_action(f"移除 {package}", "❌ 失败", stderr)
                self.failed_removals.append((package, stderr))
                all_success = False
        
        return all_success
    
    def install_missing_packages(self, packages: List[str]) -> bool:
        """安装缺失的包"""
        print(f"\n📦 安装缺失的依赖包")
        print("=" * 50)
        
        all_success = True
        
        for package in packages:
            print(f"📦 正在安装: {package}")
            
            success, stdout, stderr = self.execute_command(f"pip install {package}")
            
            if success:
                self.log_action(f"安装 {package}", "✅ 成功")
            else:
                self.log_action(f"安装 {package}", "❌ 失败", stderr)
                all_success = False
        
        return all_success
    
    def backup_requirements(self):
        """备份当前的requirements.txt"""
        print("💾 备份当前requirements.txt...")
        
        try:
            with open("requirements.txt", "r", encoding="utf-8") as f:
                content = f.read()
            
            backup_filename = f"requirements_backup_{int(time.time())}.txt"
            with open(backup_filename, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.log_action("备份requirements.txt", "✅ 成功", backup_filename)
            return backup_filename
        except Exception as e:
            self.log_action("备份requirements.txt", "❌ 失败", str(e))
            return None
    
    def update_requirements(self):
        """更新requirements.txt文件"""
        print("\n📝 更新requirements.txt...")
        
        new_requirements = """# Core AI and API dependencies
openai>=1.50.0
pydantic>=2.8.0
python-dotenv>=1.0.0

# HTTP requests and API handling
urllib3>=2.0.0
requests>=2.28.0

# Database and ORM
sqlalchemy>=2.0.0
aiosqlite>=0.20.0  # SQLite async driver

# Health data and time handling
pytz>=2024.1

# FastAPI web interface and authentication
fastapi>=0.110.0
uvicorn>=0.28.0
python-jose[cryptography]>=3.3.0  # JWT handling
passlib[bcrypt]>=1.7.4  # Password hashing
python-multipart>=0.0.6  # Form data handling

# Security
cryptography>=42.0.0

# LangChain Framework
langchain>=0.1.0
langchain-openai>=0.0.5

# Redis for caching
redis>=4.0.0
"""
        
        try:
            with open("requirements.txt", "w", encoding="utf-8") as f:
                f.write(new_requirements)
            
            self.log_action("更新requirements.txt", "✅ 成功")
            return True
        except Exception as e:
            self.log_action("更新requirements.txt", "❌ 失败", str(e))
            return False
    
    def execute_slimming_plan(self):
        """执行完整的瘦身计划"""
        print("🎯 AuraWell Agent 瘦身计划执行")
        print("=" * 60)
        print("⚠️  警告: 此操作将移除多个Python包")
        print("📋 详细分析报告: DEPENDENCY_SLIMMING_REPORT.md")
        print()
        
        # 确认执行
        response = input("是否继续执行瘦身计划? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ 瘦身计划已取消")
            return False
        
        # 备份requirements.txt
        backup_file = self.backup_requirements()
        if not backup_file:
            print("❌ 备份失败，瘦身计划终止")
            return False
        
        # 定义瘦身阶段
        slimming_phases = [
            {
                "name": "第一阶段: 移除开发工具",
                "packages": ["black", "flake8", "mypy", "pytest", "pytest-asyncio"],
                "safe": True
            },
            {
                "name": "第二阶段: 移除未使用的数据处理库",
                "packages": ["pandas", "numpy", "python-dateutil"],
                "safe": True
            },
            {
                "name": "第三阶段: 移除重复的HTTP客户端",
                "packages": ["httpx"],
                "safe": True
            },
            {
                "name": "第四阶段: 移除未来功能的包",
                "packages": ["chromadb", "sentence-transformers", "faiss-cpu", "websockets", "asyncio-mqtt"],
                "safe": True
            },
            {
                "name": "第五阶段: 移除替代日志库",
                "packages": ["loguru", "structlog"],
                "safe": True
            },
            {
                "name": "第六阶段: 移除其他工具",
                "packages": ["configparser", "iso8601", "deepseek"],
                "safe": True
            },
            {
                "name": "第七阶段: 移除数据库相关 (谨慎)",
                "packages": ["asyncpg", "alembic"],
                "safe": False
            }
        ]
        
        # 执行各个阶段
        total_success = True
        
        for phase in slimming_phases:
            if not phase["safe"]:
                response = input(f"\n⚠️  {phase['name']} - 需要谨慎执行，是否继续? (y/N): ").strip().lower()
                if response != 'y':
                    print(f"⏭️  跳过 {phase['name']}")
                    continue
            
            success = self.uninstall_packages(phase["packages"], phase["name"])
            if not success:
                total_success = False
                print(f"⚠️  {phase['name']} 部分失败")
        
        # 安装缺失的包
        missing_packages = ["python-dotenv", "python-jose[cryptography]", "python-multipart"]
        self.install_missing_packages(missing_packages)
        
        # 更新requirements.txt
        self.update_requirements()
        
        # 生成执行报告
        self.generate_execution_report(backup_file)
        
        return total_success
    
    def generate_execution_report(self, backup_file: str):
        """生成执行报告"""
        print(f"\n📄 生成执行报告...")
        
        report = []
        report.append("# AuraWell Agent 瘦身计划执行报告")
        report.append(f"执行时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"备份文件: {backup_file}")
        report.append("")
        
        report.append("## 执行日志")
        for log_entry in self.execution_log:
            report.append(f"- {log_entry}")
        report.append("")
        
        report.append(f"## 成功移除的包 ({len(self.removed_packages)}个)")
        for package in self.removed_packages:
            report.append(f"- ✅ {package}")
        report.append("")
        
        if self.failed_removals:
            report.append(f"## 移除失败的包 ({len(self.failed_removals)}个)")
            for package, error in self.failed_removals:
                report.append(f"- ❌ {package}: {error}")
            report.append("")
        
        report.append("## 瘦身效果")
        original_count = 38  # 原始包数量
        removed_count = len(self.removed_packages)
        remaining_count = original_count - removed_count
        reduction_percentage = (removed_count / original_count) * 100
        
        report.append(f"- 原始包数量: {original_count}")
        report.append(f"- 移除包数量: {removed_count}")
        report.append(f"- 剩余包数量: {remaining_count}")
        report.append(f"- 减重比例: {reduction_percentage:.1f}%")
        
        # 保存报告
        report_content = "\n".join(report)
        report_filename = f"slimming_execution_report_{int(time.time())}.md"
        
        try:
            with open(report_filename, "w", encoding="utf-8") as f:
                f.write(report_content)
            
            print(f"✅ 执行报告已保存: {report_filename}")
        except Exception as e:
            print(f"❌ 保存执行报告失败: {e}")


def main():
    """主函数"""
    executor = SlimmingExecutor()
    
    try:
        success = executor.execute_slimming_plan()
        
        if success:
            print("\n🎉 瘦身计划执行完成！")
            print("💡 建议执行功能测试确保系统正常运行")
        else:
            print("\n⚠️  瘦身计划部分失败，请检查执行报告")
        
        print(f"\n📊 瘦身统计:")
        print(f"   • 成功移除: {len(executor.removed_packages)} 个包")
        print(f"   • 移除失败: {len(executor.failed_removals)} 个包")
        
    except KeyboardInterrupt:
        print("\n⚠️  瘦身计划被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 瘦身计划执行异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
