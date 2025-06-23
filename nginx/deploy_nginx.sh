#!/bin/bash

# AuraWell Nginx 部署脚本
# 适用于 Ubuntu 22.04 系统
# 公网IP: 166.108.224.73

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查权限
check_permissions() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        log_info "请使用: sudo $0"
        exit 1
    fi
}

# 检查系统
check_system() {
    log_step "检查系统环境..."
    
    if [[ ! -f /etc/os-release ]]; then
        log_error "无法检测系统版本"
        exit 1
    fi
    
    source /etc/os-release
    
    if [[ "$ID" != "ubuntu" ]]; then
        log_warn "检测到非Ubuntu系统: $ID"
        log_warn "脚本针对Ubuntu优化，可能需要手动调整"
    else
        log_info "系统检查通过: $PRETTY_NAME"
    fi
}

# 安装Nginx
install_nginx() {
    log_step "检查并安装Nginx..."
    
    if ! command -v nginx &> /dev/null; then
        log_info "Nginx未安装，开始安装..."
        apt update
        apt install -y nginx
        log_info "Nginx安装完成"
    else
        log_info "Nginx已安装: $(nginx -v 2>&1)"
    fi
    
    # 启用并启动Nginx
    systemctl enable nginx
    if ! systemctl is-active --quiet nginx; then
        systemctl start nginx
        log_info "Nginx服务已启动"
    else
        log_info "Nginx服务正在运行"
    fi
}

# 备份现有配置
backup_config() {
    log_step "备份现有Nginx配置..."
    
    BACKUP_DIR="/etc/nginx/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    if [[ -f "/etc/nginx/sites-available/default" ]]; then
        cp "/etc/nginx/sites-available/default" "$BACKUP_DIR/"
        log_info "已备份默认配置到: $BACKUP_DIR"
    fi
    
    if [[ -f "/etc/nginx/sites-available/aurawell" ]]; then
        cp "/etc/nginx/sites-available/aurawell" "$BACKUP_DIR/"
        log_info "已备份AuraWell配置到: $BACKUP_DIR"
    fi
}

# 部署配置文件
deploy_config() {
    log_step "部署Nginx配置文件..."
    
    # 检查配置文件是否存在
    if [[ ! -f "nginx/aurawell.conf" ]]; then
        log_error "找不到nginx/aurawell.conf配置文件"
        exit 1
    fi
    
    # 复制配置文件
    cp "nginx/aurawell.conf" "/etc/nginx/sites-available/aurawell"
    log_info "已复制配置文件到 /etc/nginx/sites-available/aurawell"
    
    # 创建符号链接
    if [[ -L "/etc/nginx/sites-enabled/aurawell" ]]; then
        rm "/etc/nginx/sites-enabled/aurawell"
    fi
    ln -s "/etc/nginx/sites-available/aurawell" "/etc/nginx/sites-enabled/aurawell"
    log_info "已创建配置文件符号链接"
    
    # 禁用默认站点
    if [[ -L "/etc/nginx/sites-enabled/default" ]]; then
        rm "/etc/nginx/sites-enabled/default"
        log_info "已禁用默认站点配置"
    fi
}

# 测试配置
test_config() {
    log_step "测试Nginx配置..."
    
    if nginx -t; then
        log_info "✅ Nginx配置测试通过"
    else
        log_error "❌ Nginx配置测试失败"
        log_error "请检查配置文件语法"
        exit 1
    fi
}

# 重载Nginx
reload_nginx() {
    log_step "重载Nginx配置..."
    
    systemctl reload nginx
    
    if systemctl is-active --quiet nginx; then
        log_info "✅ Nginx配置重载成功"
    else
        log_error "❌ Nginx重载失败"
        systemctl status nginx
        exit 1
    fi
}

# 创建日志目录
setup_logs() {
    log_step "设置日志目录..."
    
    # 确保日志目录存在
    mkdir -p /var/log/nginx
    
    # 设置日志轮转
    if [[ ! -f "/etc/logrotate.d/aurawell-nginx" ]]; then
        cat > /etc/logrotate.d/aurawell-nginx << 'EOF'
/var/log/nginx/aurawell_*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 `cat /var/run/nginx.pid`
        fi
    endscript
}
EOF
        log_info "已配置日志轮转"
    fi
}

# 配置防火墙
setup_firewall() {
    log_step "配置防火墙规则..."
    
    if command -v ufw &> /dev/null; then
        # 允许HTTP和HTTPS
        ufw allow 80/tcp
        ufw allow 443/tcp
        
        # 确保SSH仍然可用
        ufw allow 22/tcp
        
        log_info "已配置UFW防火墙规则"
        log_warn "请确保UFW已启用: sudo ufw enable"
    else
        log_warn "UFW未安装，请手动配置防火墙规则"
        log_info "需要开放端口: 80 (HTTP), 443 (HTTPS)"
    fi
}

# 显示状态
show_status() {
    log_step "显示部署状态..."
    
    echo
    echo "=================================="
    echo "🚀 AuraWell Nginx 部署完成!"
    echo "=================================="
    echo
    echo "🌐 访问地址:"
    echo "  ┌─────────────────────────────────────────────┐"
    echo "  │  🎯 主要入口: http://166.108.224.73         │"
    echo "  │  📚 API文档: http://166.108.224.73/docs     │"
    echo "  │  🔍 健康检查: http://166.108.224.73/nginx-health │"
    echo "  └─────────────────────────────────────────────┘"
    echo
    echo "📋 服务信息:"
    echo "  • Nginx状态: $(systemctl is-active nginx)"
    echo "  • 配置文件: /etc/nginx/sites-available/aurawell"
    echo "  • 访问日志: /var/log/nginx/aurawell_access.log"
    echo "  • 错误日志: /var/log/nginx/aurawell_error.log"
    echo
    echo "🔧 管理命令:"
    echo "  • 重载配置: sudo systemctl reload nginx"
    echo "  • 重启服务: sudo systemctl restart nginx"
    echo "  • 查看状态: sudo systemctl status nginx"
    echo "  • 测试配置: sudo nginx -t"
    echo "  • 查看日志: sudo tail -f /var/log/nginx/aurawell_access.log"
    echo
    echo "⚠️  重要提醒:"
    echo "  • 确保AuraWell后端服务运行在端口8001"
    echo "  • 确保AuraWell前端服务运行在端口5173"
    echo "  • 使用 ./start_aurawell.sh 启动应用服务"
    echo
}

# SSL配置提示
show_ssl_info() {
    echo "🔒 SSL/HTTPS配置:"
    echo "  • 当前使用HTTP配置"
    echo "  • 如需HTTPS，请:"
    echo "    1. 获取SSL证书"
    echo "    2. 使用 nginx/aurawell-ssl.conf 配置"
    echo "    3. 运行: sudo $0 ssl"
    echo
}

# SSL部署
deploy_ssl() {
    log_step "部署SSL配置..."
    
    if [[ ! -f "nginx/aurawell-ssl.conf" ]]; then
        log_error "找不到nginx/aurawell-ssl.conf配置文件"
        exit 1
    fi
    
    # 检查证书文件
    if [[ ! -f "/etc/ssl/certs/aurawell.crt" ]] || [[ ! -f "/etc/ssl/private/aurawell.key" ]]; then
        log_error "SSL证书文件不存在"
        log_info "请先配置SSL证书:"
        log_info "  • 证书文件: /etc/ssl/certs/aurawell.crt"
        log_info "  • 私钥文件: /etc/ssl/private/aurawell.key"
        exit 1
    fi
    
    # 部署SSL配置
    cp "nginx/aurawell-ssl.conf" "/etc/nginx/sites-available/aurawell"
    log_info "已部署SSL配置"
    
    test_config
    reload_nginx
    
    log_info "✅ SSL配置部署完成"
    log_info "🌐 HTTPS访问: https://166.108.224.73"
}

# 主函数
main() {
    echo "🔧 AuraWell Nginx 部署脚本"
    echo "=================================="
    echo
    
    # 解析参数
    if [[ "$1" == "ssl" ]]; then
        log_info "SSL模式部署"
        check_permissions
        check_system
        install_nginx
        backup_config
        deploy_ssl
        setup_logs
        setup_firewall
        show_status
    else
        log_info "HTTP模式部署"
        check_permissions
        check_system
        install_nginx
        backup_config
        deploy_config
        test_config
        reload_nginx
        setup_logs
        setup_firewall
        show_status
        show_ssl_info
    fi
    
    log_info "🎉 Nginx部署完成！"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
