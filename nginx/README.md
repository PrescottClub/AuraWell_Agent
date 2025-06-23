# AuraWell Nginx 配置指南

## 概述

本目录包含AuraWell项目的Nginx反向代理配置，用于在Ubuntu 22.04云服务器上部署。

## 文件说明

- `aurawell.conf` - HTTP版本的Nginx配置文件
- `aurawell-ssl.conf` - HTTPS版本的Nginx配置文件（需要SSL证书）
- `deploy_nginx.sh` - 自动部署脚本
- `README.md` - 本说明文档

## 服务器信息

- **公网IP**: 166.108.224.73
- **后端端口**: 8001 (内部)
- **前端端口**: 5173 (内部)
- **Nginx端口**: 80 (HTTP) / 443 (HTTPS)

## 快速部署

### 1. HTTP部署（推荐开始使用）

```bash
# 在AuraWell项目根目录执行
sudo ./nginx/deploy_nginx.sh
```

### 2. HTTPS部署（需要SSL证书）

```bash
# 首先配置SSL证书，然后执行
sudo ./nginx/deploy_nginx.sh ssl
```

## 详细部署步骤

### 前置条件

1. Ubuntu 22.04 系统
2. 具有sudo权限的用户
3. AuraWell应用已正确配置

### 手动部署步骤

1. **安装Nginx**
   ```bash
   sudo apt update
   sudo apt install -y nginx
   ```

2. **复制配置文件**
   ```bash
   sudo cp nginx/aurawell.conf /etc/nginx/sites-available/aurawell
   ```

3. **启用站点**
   ```bash
   sudo ln -s /etc/nginx/sites-available/aurawell /etc/nginx/sites-enabled/
   sudo rm -f /etc/nginx/sites-enabled/default
   ```

4. **测试配置**
   ```bash
   sudo nginx -t
   ```

5. **重载Nginx**
   ```bash
   sudo systemctl reload nginx
   ```

## 配置说明

### 路由规则

- `/api/*` → 后端服务 (127.0.0.1:8001)
- `/docs` → API文档 (127.0.0.1:8001)
- `/openapi.json` → OpenAPI规范 (127.0.0.1:8001)
- `/ws` → WebSocket连接 (127.0.0.1:5173)
- `/*` → 前端服务 (127.0.0.1:5173)

### 特性

- **反向代理**: 将外部请求转发到内部服务
- **负载均衡**: 支持多实例部署
- **静态资源缓存**: 优化前端资源加载
- **Gzip压缩**: 减少传输数据量
- **安全头**: 增强安全性
- **WebSocket支持**: 支持Vite热重载
- **SPA支持**: 处理前端路由

## 访问地址

部署完成后，可通过以下地址访问：

- **主应用**: http://166.108.224.73
- **API文档**: http://166.108.224.73/docs
- **健康检查**: http://166.108.224.73/nginx-health

## 日志文件

- **访问日志**: `/var/log/nginx/aurawell_access.log`
- **错误日志**: `/var/log/nginx/aurawell_error.log`

## 管理命令

```bash
# 查看Nginx状态
sudo systemctl status nginx

# 重载配置
sudo systemctl reload nginx

# 重启Nginx
sudo systemctl restart nginx

# 测试配置
sudo nginx -t

# 查看访问日志
sudo tail -f /var/log/nginx/aurawell_access.log

# 查看错误日志
sudo tail -f /var/log/nginx/aurawell_error.log
```

## SSL/HTTPS配置

### 获取SSL证书

1. **使用Let's Encrypt（推荐）**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d 166.108.224.73
   ```

2. **使用自签名证书（测试用）**
   ```bash
   sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout /etc/ssl/private/aurawell.key \
     -out /etc/ssl/certs/aurawell.crt
   ```

### 部署HTTPS配置

```bash
sudo ./nginx/deploy_nginx.sh ssl
```

## 故障排除

### 常见问题

1. **502 Bad Gateway**
   - 检查后端服务是否运行在8001端口
   - 检查前端服务是否运行在5173端口
   - 查看错误日志: `sudo tail -f /var/log/nginx/aurawell_error.log`

2. **配置测试失败**
   - 检查配置文件语法: `sudo nginx -t`
   - 查看详细错误信息

3. **无法访问**
   - 检查防火墙设置: `sudo ufw status`
   - 确保端口80/443已开放

### 调试命令

```bash
# 检查端口占用
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :8001
sudo netstat -tlnp | grep :5173

# 检查服务状态
sudo systemctl status nginx
curl -I http://localhost:8001/api/v1/health
curl -I http://localhost:5173

# 测试代理
curl -H "Host: 166.108.224.73" http://localhost/nginx-health
```

## 与启动脚本的集成

Nginx配置与现有的`start_aurawell.sh`脚本完全兼容：

1. 先运行Nginx部署: `sudo ./nginx/deploy_nginx.sh`
2. 再启动应用服务: `./start_aurawell.sh`

Nginx会自动将外部请求转发到内部服务，无需修改应用配置。

## 性能优化

### 建议配置

1. **增加worker进程数**
   ```nginx
   worker_processes auto;
   ```

2. **调整连接数**
   ```nginx
   worker_connections 1024;
   ```

3. **启用缓存**
   ```nginx
   proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;
   ```

### 监控

- 使用`nginx-prometheus-exporter`监控性能
- 配置日志分析工具如ELK Stack
- 设置健康检查和告警

## 安全建议

1. **定期更新Nginx**
2. **配置SSL/TLS**
3. **限制请求频率**
4. **隐藏Nginx版本信息**
5. **配置Web应用防火墙(WAF)**

## 支持

如有问题，请检查：
1. 日志文件
2. 服务状态
3. 网络连接
4. 防火墙设置

更多信息请参考AuraWell项目的主要文档。
