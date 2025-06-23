# AuraWell Nginx 部署指南

## 概述

本文档描述如何为AuraWell项目配置Nginx反向代理服务，实现通过80端口访问整个应用。

## 服务器信息

- **公网IP**: 166.108.224.73
- **系统**: Ubuntu 22.04
- **后端端口**: 8001 (内部)
- **前端端口**: 5173 (内部)
- **Nginx端口**: 80 (外部访问)

## 快速部署

### 1. 部署Nginx配置

```bash
# 在AuraWell项目根目录执行
sudo ./nginx/deploy_nginx.sh
```

### 2. 启动AuraWell服务

```bash
# 启动后端和前端服务
./start_aurawell.sh
```

### 3. 验证部署

访问以下地址验证部署是否成功：

- **主应用**: http://166.108.224.73
- **API文档**: http://166.108.224.73/docs
- **健康检查**: http://166.108.224.73/nginx-health

## 配置文件说明

### 文件结构

```
nginx/
├── aurawell.conf          # HTTP配置文件
├── aurawell-ssl.conf      # HTTPS配置文件
├── deploy_nginx.sh        # 自动部署脚本
├── manage_nginx.sh        # 管理脚本
└── README.md             # 详细说明文档
```

### 路由配置

Nginx配置了以下路由规则：

| 路径 | 目标服务 | 说明 |
|------|----------|------|
| `/api/*` | 127.0.0.1:8001 | 后端API接口 |
| `/docs` | 127.0.0.1:8001 | API文档 |
| `/openapi.json` | 127.0.0.1:8001 | OpenAPI规范 |
| `/ws` | 127.0.0.1:5173 | WebSocket连接 |
| `/*` | 127.0.0.1:5173 | 前端应用 |

## 管理命令

### 使用管理脚本

```bash
# 查看服务状态
./nginx/manage_nginx.sh status

# 部署配置
sudo ./nginx/manage_nginx.sh deploy

# 重载配置
sudo ./nginx/manage_nginx.sh reload

# 查看日志
./nginx/manage_nginx.sh logs

# 显示帮助
./nginx/manage_nginx.sh help
```

### 直接使用systemctl

```bash
# 查看Nginx状态
sudo systemctl status nginx

# 重启Nginx
sudo systemctl restart nginx

# 重载配置
sudo systemctl reload nginx

# 测试配置
sudo nginx -t
```

## 日志管理

### 日志文件位置

- **Nginx访问日志**: `/var/log/nginx/access.log`
- **Nginx错误日志**: `/var/log/nginx/error.log`
- **AuraWell访问日志**: `/var/log/nginx/aurawell_access.log`
- **AuraWell错误日志**: `/var/log/nginx/aurawell_error.log`

### 查看日志

```bash
# 实时查看访问日志
sudo tail -f /var/log/nginx/aurawell_access.log

# 实时查看错误日志
sudo tail -f /var/log/nginx/aurawell_error.log

# 查看最近的错误
sudo tail -n 100 /var/log/nginx/aurawell_error.log
```

## 与启动脚本的集成

### 兼容性

Nginx配置与现有的`start_aurawell.sh`脚本完全兼容：

1. **启动脚本会自动检测Nginx状态**
2. **显示正确的访问地址**
3. **提供Nginx相关的管理提示**

### 推荐启动顺序

```bash
# 1. 首次部署时配置Nginx
sudo ./nginx/deploy_nginx.sh

# 2. 启动AuraWell服务
./start_aurawell.sh

# 3. 验证服务
curl http://166.108.224.73/nginx-health
```

### 重启服务

```bash
# 重启所有服务
./restart_aurawell.sh

# 或者分别重启
sudo systemctl reload nginx
./restart_aurawell.sh
```

## 故障排除

### 常见问题

#### 1. 502 Bad Gateway

**原因**: 后端服务未运行或端口不正确

**解决方案**:
```bash
# 检查后端服务
curl http://localhost:8001/api/v1/health

# 检查前端服务
curl http://localhost:5173

# 重启AuraWell服务
./restart_aurawell.sh
```

#### 2. 配置测试失败

**原因**: Nginx配置文件语法错误

**解决方案**:
```bash
# 测试配置
sudo nginx -t

# 查看详细错误
sudo nginx -T
```

#### 3. 无法访问

**原因**: 防火墙阻止或端口未开放

**解决方案**:
```bash
# 检查防火墙状态
sudo ufw status

# 开放HTTP端口
sudo ufw allow 80/tcp

# 检查端口占用
sudo netstat -tlnp | grep :80
```

### 调试命令

```bash
# 检查所有相关端口
sudo netstat -tlnp | grep -E ':(80|443|8001|5173)'

# 检查Nginx进程
ps aux | grep nginx

# 检查配置文件
sudo nginx -T | grep -A 10 -B 10 "server_name"

# 测试代理转发
curl -H "Host: 166.108.224.73" http://localhost/api/v1/health
```

## HTTPS配置

### 使用Let's Encrypt

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d 166.108.224.73

# 部署SSL配置
sudo ./nginx/deploy_nginx.sh ssl
```

### 使用自签名证书

```bash
# 生成自签名证书
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/aurawell.key \
  -out /etc/ssl/certs/aurawell.crt

# 部署SSL配置
sudo ./nginx/deploy_nginx.sh ssl
```

## 性能优化

### 建议配置

1. **启用Gzip压缩** (已配置)
2. **设置静态资源缓存** (已配置)
3. **调整worker进程数**
4. **配置连接池**

### 监控建议

1. **设置日志轮转** (已配置)
2. **监控响应时间**
3. **设置告警机制**
4. **定期检查磁盘空间**

## 安全建议

1. **定期更新Nginx**
2. **配置SSL/TLS**
3. **限制请求频率**
4. **隐藏服务器信息**
5. **配置安全头** (已配置)

## 备份和恢复

### 备份配置

```bash
# 使用管理脚本备份
sudo ./nginx/manage_nginx.sh backup

# 手动备份
sudo cp -r /etc/nginx/sites-available /backup/nginx-$(date +%Y%m%d)
```

### 恢复配置

```bash
# 恢复配置文件
sudo cp /backup/nginx-20240623/sites-available/aurawell /etc/nginx/sites-available/

# 启用配置
sudo ln -sf /etc/nginx/sites-available/aurawell /etc/nginx/sites-enabled/

# 测试并重载
sudo nginx -t && sudo systemctl reload nginx
```

## 总结

通过本配置，AuraWell项目实现了：

1. ✅ **统一入口**: 通过80端口访问整个应用
2. ✅ **反向代理**: 自动转发请求到后端和前端服务
3. ✅ **负载均衡**: 支持多实例部署
4. ✅ **静态资源优化**: 缓存和压缩
5. ✅ **安全增强**: 安全头和访问控制
6. ✅ **易于管理**: 提供管理脚本和详细文档

配置完成后，用户可以直接通过 http://166.108.224.73 访问AuraWell应用，无需记住具体的端口号。
