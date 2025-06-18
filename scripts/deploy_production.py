#!/usr/bin/env python3
"""
生产环境部署脚本

提供完整的生产环境部署流程
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def run_command(command, cwd=None, check=True):
    """运行命令"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd or project_root,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if check and result.returncode != 0:
            print(f"❌ 命令失败: {command}")
            print(f"错误输出: {result.stderr}")
            return False
        return True, result.stdout, result.stderr
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        return False


def check_prerequisites():
    """检查部署前提条件"""
    print("🔍 检查部署前提条件...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python版本过低: {python_version}，需要3.8+")
        return False
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}")
    
    # 检查必需文件
    required_files = [
        "src/aurawell/__init__.py",
        "requirements.txt",
        "alembic.ini",
        "migrations/env.py"
    ]
    
    for file_path in required_files:
        if not (project_root / file_path).exists():
            print(f"❌ 缺少必需文件: {file_path}")
            return False
    print("✅ 必需文件检查通过")
    
    return True


def install_dependencies():
    """安装生产依赖"""
    print("📦 安装生产依赖...")
    
    # 安装基础依赖
    success, _, _ = run_command("pip install -r requirements.txt")
    if not success:
        return False
    
    # 安装生产环境额外依赖
    production_deps = [
        "gunicorn>=20.1.0",
        "uvicorn[standard]>=0.20.0",
        "psutil>=5.9.0",
        "alembic>=1.8.0"
    ]
    
    for dep in production_deps:
        print(f"   安装 {dep}...")
        success, _, _ = run_command(f"pip install {dep}")
        if not success:
            return False
    
    print("✅ 依赖安装完成")
    return True


def setup_database():
    """设置数据库"""
    print("🗄️  设置数据库...")
    
    # 运行数据库迁移
    print("   运行数据库迁移...")
    success, _, _ = run_command("python scripts/manage_db.py upgrade")
    if not success:
        print("❌ 数据库迁移失败")
        return False
    
    print("✅ 数据库设置完成")
    return True


def run_tests():
    """运行测试"""
    print("🧪 运行生产前测试...")
    
    # 运行快速测试
    success, _, _ = run_command("python scripts/run_tests.py --quick")
    if not success:
        print("❌ 测试失败")
        return False
    
    print("✅ 测试通过")
    return True


def build_application():
    """构建应用"""
    print("🔨 构建应用...")
    
    # 编译Python文件
    success, _, _ = run_command("python -m compileall src/")
    if not success:
        print("❌ 编译失败")
        return False
    
    # 清理缓存文件
    success, _, _ = run_command("find . -name '__pycache__' -type d -exec rm -rf {} +", check=False)
    success, _, _ = run_command("find . -name '*.pyc' -delete", check=False)
    
    print("✅ 应用构建完成")
    return True


def setup_monitoring():
    """设置监控"""
    print("📊 设置监控...")
    
    # 创建日志目录
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 创建监控配置
    monitoring_config = {
        "log_level": "INFO",
        "log_file": str(log_dir / "aurawell.log"),
        "metrics_enabled": True,
        "health_check_interval": 60
    }
    
    import json
    config_file = project_root / "monitoring_config.json"
    with open(config_file, "w") as f:
        json.dump(monitoring_config, f, indent=2)
    
    print("✅ 监控设置完成")
    return True


def create_systemd_service():
    """创建systemd服务文件"""
    print("⚙️  创建systemd服务...")
    
    service_content = f"""[Unit]
Description=AuraWell Agent API Server
After=network.target

[Service]
Type=exec
User=aurawell
Group=aurawell
WorkingDirectory={project_root}
Environment=PATH={project_root}/venv/bin
Environment=PYTHONPATH={project_root}/src
ExecStart={project_root}/venv/bin/gunicorn -c gunicorn.conf.py aurawell.interfaces.api_interface:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = project_root / "aurawell-agent.service"
    with open(service_file, "w") as f:
        f.write(service_content)
    
    print(f"✅ 服务文件创建: {service_file}")
    print("   请手动复制到 /etc/systemd/system/ 并启用服务")
    return True


def create_gunicorn_config():
    """创建Gunicorn配置"""
    print("🚀 创建Gunicorn配置...")
    
    config_content = f"""# Gunicorn配置文件
import multiprocessing
import os

# 服务器套接字
bind = "0.0.0.0:8000"
backlog = 2048

# 工作进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 超时
timeout = 30
keepalive = 2

# 日志
accesslog = "{project_root}/logs/access.log"
errorlog = "{project_root}/logs/error.log"
loglevel = "info"
access_log_format = '%%(h)s %%(l)s %%(u)s %%(t)s "%%(r)s" %%(s)s %%(b)s "%%(f)s" "%%(a)s" %%(D)s'

# 进程命名
proc_name = "aurawell-agent"

# 安全
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 重启
max_requests = 1000
max_requests_jitter = 100

# SSL (如果需要)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
"""
    
    config_file = project_root / "gunicorn.conf.py"
    with open(config_file, "w") as f:
        f.write(config_content)
    
    print("✅ Gunicorn配置创建完成")
    return True


def create_nginx_config():
    """创建Nginx配置"""
    print("🌐 创建Nginx配置...")
    
    nginx_config = f"""# AuraWell Agent Nginx配置
server {{
    listen 80;
    server_name your-domain.com;  # 替换为实际域名
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name your-domain.com;  # 替换为实际域名
    
    # SSL配置
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # 日志
    access_log {project_root}/logs/nginx_access.log;
    error_log {project_root}/logs/nginx_error.log;
    
    # 静态文件
    location /static/ {{
        alias {project_root}/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # API代理
    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }}
    
    # 健康检查
    location /health {{
        proxy_pass http://127.0.0.1:8000/api/v1/health;
        access_log off;
    }}
}}
"""
    
    nginx_file = project_root / "nginx.conf"
    with open(nginx_file, "w") as f:
        f.write(nginx_config)
    
    print(f"✅ Nginx配置创建: {nginx_file}")
    print("   请根据实际情况修改域名和SSL证书路径")
    return True


def create_deployment_summary():
    """创建部署摘要"""
    print("📋 创建部署摘要...")
    
    summary = f"""# AuraWell Agent 生产环境部署摘要

## 部署信息
- 部署时间: {os.popen('date').read().strip()}
- 项目路径: {project_root}
- Python版本: {sys.version}

## 已创建的文件
- gunicorn.conf.py - Gunicorn配置
- aurawell-agent.service - systemd服务文件
- nginx.conf - Nginx配置模板
- monitoring_config.json - 监控配置

## 下一步操作

### 1. 系统服务设置
```bash
# 复制服务文件
sudo cp aurawell-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aurawell-agent
sudo systemctl start aurawell-agent
```

### 2. Nginx设置
```bash
# 复制配置文件（根据实际情况修改）
sudo cp nginx.conf /etc/nginx/sites-available/aurawell-agent
sudo ln -s /etc/nginx/sites-available/aurawell-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. 防火墙设置
```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000  # 如果需要直接访问
```

### 4. SSL证书
- 使用Let's Encrypt或其他CA获取SSL证书
- 更新nginx.conf中的证书路径

### 5. 监控
- 检查日志: tail -f logs/aurawell.log
- 健康检查: curl http://localhost:8000/api/v1/health
- 系统状态: systemctl status aurawell-agent

## 环境变量
确保设置以下环境变量：
- DATABASE_URL: 数据库连接字符串
- SECRET_KEY: JWT密钥
- ENVIRONMENT: production

## 备份
定期备份以下内容：
- 数据库文件 (aurawell.db)
- 配置文件
- 日志文件

## 故障排除
- 检查服务状态: systemctl status aurawell-agent
- 查看日志: journalctl -u aurawell-agent -f
- 检查端口: netstat -tlnp | grep 8000
"""
    
    summary_file = project_root / "DEPLOYMENT_SUMMARY.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"✅ 部署摘要创建: {summary_file}")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AuraWell Agent 生产环境部署")
    
    parser.add_argument("--skip-tests", action="store_true", help="跳过测试")
    parser.add_argument("--skip-deps", action="store_true", help="跳过依赖安装")
    parser.add_argument("--config-only", action="store_true", help="只生成配置文件")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 AuraWell Agent 生产环境部署")
    print("=" * 60)
    
    steps = []
    
    if args.config_only:
        steps = [
            ("创建Gunicorn配置", create_gunicorn_config),
            ("创建systemd服务", create_systemd_service),
            ("创建Nginx配置", create_nginx_config),
            ("设置监控", setup_monitoring),
            ("创建部署摘要", create_deployment_summary),
        ]
    else:
        steps = [
            ("检查前提条件", check_prerequisites),
        ]
        
        if not args.skip_deps:
            steps.append(("安装依赖", install_dependencies))
        
        steps.extend([
            ("设置数据库", setup_database),
        ])
        
        if not args.skip_tests:
            steps.append(("运行测试", run_tests))
        
        steps.extend([
            ("构建应用", build_application),
            ("创建Gunicorn配置", create_gunicorn_config),
            ("创建systemd服务", create_systemd_service),
            ("创建Nginx配置", create_nginx_config),
            ("设置监控", setup_monitoring),
            ("创建部署摘要", create_deployment_summary),
        ])
    
    success_count = 0
    total_count = len(steps)
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        if step_func():
            success_count += 1
        else:
            print(f"❌ {step_name} 失败")
            break
    
    print("\n" + "=" * 60)
    print(f"📊 部署结果: {success_count}/{total_count} 步骤完成")
    
    if success_count == total_count:
        print("🎉 部署成功！")
        print("\n请查看 DEPLOYMENT_SUMMARY.md 了解后续操作")
        sys.exit(0)
    else:
        print(f"❌ 部署失败，{total_count - success_count} 个步骤未完成")
        sys.exit(1)


if __name__ == "__main__":
    main()
