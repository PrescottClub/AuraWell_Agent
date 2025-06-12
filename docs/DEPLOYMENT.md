# AuraWell 部署指南

## 📋 概述

本文档提供AuraWell健康管理系统的完整部署指南，包括开发环境、测试环境和生产环境的部署方案。

## 🛠️ 环境要求

### 系统要求
- **操作系统**: Linux/macOS/Windows
- **Python**: 3.8+
- **Node.js**: 18+
- **内存**: 最低2GB，推荐4GB+
- **存储**: 最低10GB可用空间

### 依赖服务
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **Redis**: 缓存和会话存储 (可选)
- **Nginx**: 反向代理 (生产环境)

## 🚀 快速部署

### 1. 克隆项目

```bash
git clone https://github.com/PrescottClub/AuraWell_Agent.git
cd AuraWell_Agent
```

### 2. 后端部署

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
# 编辑 .env 文件，配置必要的环境变量

# 启动后端服务
python -m aurawell.main
```

### 3. 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 生产构建
npm run build
```

### 4. 验证部署

```bash
# 运行API测试
python test_api_endpoints.py

# 访问应用
# 前端: http://localhost:5175
# API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

## 🔧 环境配置

### 环境变量配置

创建 `.env` 文件并配置以下变量：

```bash
# 应用配置
APP_NAME=AuraWell
APP_VERSION=1.0.0
DEBUG=true

# 数据库配置
DATABASE_URL=sqlite:///./aurawell.db
# 生产环境使用PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/aurawell

# JWT配置
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI模型配置
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 健康平台API密钥
XIAOMI_HEALTH_API_KEY=your-xiaomi-api-key
APPLE_HEALTH_API_KEY=your-apple-api-key
BOHE_HEALTH_API_KEY=your-bohe-api-key

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=structured

# CORS配置
CORS_ORIGINS=["http://localhost:5175", "http://localhost:3000"]
```

### 数据库初始化

```bash
# 创建数据库表
python -c "
from aurawell.database.connection import init_database
import asyncio
asyncio.run(init_database())
"
```

## 🐳 Docker 部署

### 1. 创建 Dockerfile

**后端 Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "aurawell.main"]
```

**前端 Dockerfile**:
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
```

### 2. Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/aurawell
      - JWT_SECRET_KEY=your-secret-key
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=aurawell
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

## 🌐 生产环境部署

### 1. Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/aurawell/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 2. SSL配置 (Let's Encrypt)

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. 系统服务配置

创建 `/etc/systemd/system/aurawell.service`:

```ini
[Unit]
Description=AuraWell Health Management System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/aurawell
Environment=PATH=/var/www/aurawell/venv/bin
ExecStart=/var/www/aurawell/venv/bin/python -m aurawell.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aurawell
sudo systemctl start aurawell
sudo systemctl status aurawell
```

## 📊 监控和日志

### 1. 日志配置

```python
# 在 .env 中配置
LOG_LEVEL=INFO
LOG_FORMAT=structured
LOG_FILE=/var/log/aurawell/app.log
```

### 2. 健康检查

```bash
# API健康检查
curl http://localhost:8000/api/v1/health

# 系统资源监控
htop
df -h
free -m
```

### 3. 性能监控

```bash
# API响应时间监控
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/health

# 数据库性能
EXPLAIN ANALYZE SELECT * FROM users;
```

## 🔒 安全配置

### 1. 防火墙设置

```bash
# Ubuntu/Debian
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# 禁止直接访问后端端口
sudo ufw deny 8000
```

### 2. 数据库安全

```bash
# PostgreSQL安全配置
sudo -u postgres psql
ALTER USER postgres PASSWORD 'strong-password';
CREATE USER aurawell WITH PASSWORD 'app-password';
GRANT ALL PRIVILEGES ON DATABASE aurawell TO aurawell;
```

### 3. 应用安全

- 使用强JWT密钥
- 启用HTTPS
- 配置CORS白名单
- 定期更新依赖
- 实施API限流

## 🧪 测试部署

### 1. 功能测试

```bash
# 运行完整测试套件
python test_api_endpoints.py

# 前端功能测试
npm run test

# 端到端测试
npm run e2e
```

### 2. 性能测试

```bash
# API压力测试
ab -n 1000 -c 10 http://localhost:8000/api/v1/health

# 前端性能测试
npm run lighthouse
```

### 3. 安全测试

```bash
# 依赖安全扫描
pip audit
npm audit

# 代码安全扫描
bandit -r aurawell/
```

## 🔄 更新部署

### 1. 滚动更新

```bash
# 拉取最新代码
git pull origin main

# 更新后端
pip install -r requirements.txt
sudo systemctl restart aurawell

# 更新前端
cd frontend
npm install
npm run build
sudo cp -r dist/* /var/www/aurawell/frontend/
```

### 2. 数据库迁移

```bash
# 备份数据库
pg_dump aurawell > backup_$(date +%Y%m%d).sql

# 运行迁移
python -c "
from aurawell.database.migrations import run_migrations
import asyncio
asyncio.run(run_migrations())
"
```

## 📞 故障排除

### 常见问题

1. **端口占用**: `lsof -i :8000`
2. **权限问题**: 检查文件权限和用户组
3. **依赖冲突**: 重新创建虚拟环境
4. **数据库连接**: 检查数据库服务状态
5. **内存不足**: 监控系统资源使用

### 日志查看

```bash
# 应用日志
tail -f /var/log/aurawell/app.log

# 系统日志
sudo journalctl -u aurawell -f

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 📚 更多资源

- [API文档](./API.md)
- [开发指南](./DEVELOPMENT.md)
- [故障排除](./TROUBLESHOOTING.md)
- [性能优化](./PERFORMANCE.md)
