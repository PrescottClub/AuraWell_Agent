#!/usr/bin/env python3
"""
AuraWell 版本发布脚本

用法:
    python scripts/release.py --version v1.0.0-M1 --message "M1阶段完成"
    python scripts/release.py --version v1.0.0 --message "正式版本发布"
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd, check=True):
    """执行命令并返回结果"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"错误: {result.stderr}")
        sys.exit(1)
    return result

def validate_version(version):
    """验证版本号格式"""
    if not version.startswith('v'):
        return False
    
    # 支持的格式: v1.0.0, v1.0.0-M1, v1.0.0-alpha.1
    import re
    pattern = r'^v\d+\.\d+\.\d+(-[a-zA-Z0-9]+(\.\d+)?)?$'
    return bool(re.match(pattern, version))

def check_git_status():
    """检查Git状态"""
    result = run_command("git status --porcelain")
    if result.stdout.strip():
        print("警告: 工作目录有未提交的更改")
        print(result.stdout)
        response = input("是否继续? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)

def update_version_file(version):
    """更新版本文件"""
    version_file = Path("aurawell/__init__.py")
    if version_file.exists():
        content = version_file.read_text(encoding='utf-8')
        # 更新版本号
        import re
        new_content = re.sub(
            r'__version__ = ["\'][^"\']*["\']',
            f'__version__ = "{version[1:]}"',  # 去掉v前缀
            content
        )
        version_file.write_text(new_content, encoding='utf-8')
        print(f"已更新版本文件: {version}")

def create_tag(version, message):
    """创建Git tag"""
    tag_message = f"{version}: {message}"
    run_command(f'git tag -a {version} -m "{tag_message}"')
    print(f"已创建tag: {version}")

def push_tag(version):
    """推送tag到远程仓库"""
    run_command(f"git push origin {version}")
    print(f"已推送tag到远程: {version}")

def generate_release_notes(version):
    """生成发布说明"""
    changelog_file = Path("CHANGELOG.md")
    if not changelog_file.exists():
        return f"发布版本 {version}"
    
    content = changelog_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # 查找当前版本的变更内容
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if f"[{version}]" in line:
            start_idx = i
        elif start_idx is not None and line.startswith("## [") and i > start_idx:
            end_idx = i
            break
    
    if start_idx is not None:
        end_idx = end_idx or len(lines)
        release_notes = '\n'.join(lines[start_idx:end_idx]).strip()
        return release_notes
    
    return f"发布版本 {version}"

def main():
    parser = argparse.ArgumentParser(description='AuraWell 版本发布脚本')
    parser.add_argument('--version', required=True, help='版本号 (例如: v1.0.0-M1)')
    parser.add_argument('--message', required=True, help='发布说明')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际执行')
    parser.add_argument('--no-push', action='store_true', help='不推送到远程仓库')
    
    args = parser.parse_args()
    
    # 验证版本号
    if not validate_version(args.version):
        print(f"错误: 无效的版本号格式: {args.version}")
        print("支持的格式: v1.0.0, v1.0.0-M1, v1.0.0-alpha.1")
        sys.exit(1)
    
    print(f"准备发布版本: {args.version}")
    print(f"发布说明: {args.message}")
    
    if args.dry_run:
        print("预览模式 - 不会实际执行操作")
        return
    
    # 检查Git状态
    check_git_status()
    
    # 更新版本文件
    update_version_file(args.version)
    
    # 提交版本文件更改
    run_command("git add .")
    run_command(f'git commit -m "chore: bump version to {args.version}"')
    
    # 创建tag
    create_tag(args.version, args.message)
    
    # 推送到远程
    if not args.no_push:
        run_command("git push origin HEAD")
        push_tag(args.version)
    
    # 生成发布说明
    release_notes = generate_release_notes(args.version)
    print("\n发布说明:")
    print("=" * 50)
    print(release_notes)
    print("=" * 50)
    
    print(f"\n✅ 版本 {args.version} 发布完成!")
    print(f"🔗 GitHub Release: https://github.com/PrescottClub/AuraWell_Agent/releases/tag/{args.version}")

if __name__ == "__main__":
    main()
