#!/bin/bash

# AuraWell Nginx 管理脚本
# 用于管理Nginx服务和配置

set -e

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

# 显示帮助信息
show_help() {
    echo "AuraWell Nginx 管理脚本"
    echo
    echo "用法: $0 [命令]"
    echo
    echo "命令:"
    echo "  status    - 显示Nginx和AuraWell服务状态"
    echo "  deploy    - 部署Nginx配置"
    echo "  ssl       - 部署SSL配置"
    echo "  reload    - 重载Nginx配置"
    echo "  restart   - 重启Nginx服务"
    echo "  test      - 测试Nginx配置"
    echo "  logs      - 查看Nginx日志"
    echo "  enable    - 启用AuraWell站点"
    echo "  disable   - 禁用AuraWell站点"
    echo "  backup    - 备份当前配置"
    echo "  help      - 显示此帮助信息"
    echo
    echo "示例:"
    echo "  $0 status     # 查看状态"
    echo "  $0 deploy     # 部署HTTP配置"
    echo "  $0 ssl        # 部署HTTPS配置"
    echo "  $0 logs       # 查看日志"
}

# 检查权限
check_sudo() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此操作需要root权限"
        log_info "请使用: sudo $0 $1"
        exit 1
    fi
}

# 显示状态
show_status() {
    log_step "检查服务状态..."
    
    echo
    echo "=================================="
    echo "🔍 AuraWell 服务状态"
    echo "=================================="
    echo
    
    # Nginx状态
    echo "📦 Nginx 服务:"
    if command -v nginx &> /dev/null; then
        echo "  • 安装状态: ✅ 已安装 ($(nginx -v 2>&1 | cut -d' ' -f3))"
        if systemctl is-active --quiet nginx; then
            echo "  • 运行状态: ✅ 正在运行"
        else
            echo "  • 运行状态: ❌ 未运行"
        fi
        
        if nginx -t >/dev/null 2>&1; then
            echo "  • 配置状态: ✅ 配置正确"
        else
            echo "  • 配置状态: ❌ 配置错误"
        fi
    else
        echo "  • 安装状态: ❌ 未安装"
    fi
    
    echo
    
    # AuraWell配置状态
    echo "🌟 AuraWell 配置:"
    if [[ -f "/etc/nginx/sites-available/aurawell" ]]; then
        echo "  • 配置文件: ✅ 存在"
        if [[ -L "/etc/nginx/sites-enabled/aurawell" ]]; then
            echo "  • 启用状态: ✅ 已启用"
        else
            echo "  • 启用状态: ❌ 未启用"
        fi
    else
        echo "  • 配置文件: ❌ 不存在"
        echo "  • 启用状态: ❌ 未配置"
    fi
    
    echo
    
    # 端口状态
    echo "🔌 端口状态:"
    for port in 80 443 8001 5173; do
        if lsof -Pi :$port -sTCP:LISTEN >/dev/null 2>&1; then
            PID=$(lsof -Pi :$port -sTCP:LISTEN -t | head -1)
            PROCESS=$(ps -p $PID -o comm= 2>/dev/null || echo "unknown")
            echo "  • 端口 $port: ✅ 被占用 (PID: $PID, 进程: $PROCESS)"
        else
            echo "  • 端口 $port: ⭕ 空闲"
        fi
    done
    
    echo
    
    # 访问地址
    echo "🌐 访问地址:"
    if [[ -L "/etc/nginx/sites-enabled/aurawell" ]] && systemctl is-active --quiet nginx; then
        echo "  • 主要入口: http://166.108.224.73"
        echo "  • API文档: http://166.108.224.73/docs"
        echo "  • 健康检查: http://166.108.224.73/nginx-health"
    fi
    echo "  • 直接前端: http://166.108.224.73:5173"
    echo "  • 直接API: http://166.108.224.73:8001/docs"
    
    echo
}

# 部署配置
deploy_config() {
    check_sudo "deploy"
    log_step "部署Nginx配置..."
    
    if [[ ! -f "nginx/aurawell.conf" ]]; then
        log_error "找不到nginx/aurawell.conf配置文件"
        exit 1
    fi
    
    # 安装Nginx
    if ! command -v nginx &> /dev/null; then
        log_info "安装Nginx..."
        apt update
        apt install -y nginx
    fi
    
    # 备份现有配置
    if [[ -f "/etc/nginx/sites-available/aurawell" ]]; then
        cp "/etc/nginx/sites-available/aurawell" "/etc/nginx/sites-available/aurawell.backup.$(date +%Y%m%d_%H%M%S)"
        log_info "已备份现有配置"
    fi
    
    # 部署新配置
    cp "nginx/aurawell.conf" "/etc/nginx/sites-available/aurawell"
    ln -sf "/etc/nginx/sites-available/aurawell" "/etc/nginx/sites-enabled/aurawell"
    
    # 禁用默认站点
    rm -f "/etc/nginx/sites-enabled/default"
    
    # 测试并重载
    nginx -t
    systemctl reload nginx
    
    log_info "✅ 配置部署完成"
}

# 部署SSL配置
deploy_ssl() {
    check_sudo "ssl"
    ./nginx/deploy_nginx.sh ssl
}

# 重载配置
reload_nginx() {
    check_sudo "reload"
    log_step "重载Nginx配置..."
    
    nginx -t
    systemctl reload nginx
    
    log_info "✅ 配置重载完成"
}

# 重启服务
restart_nginx() {
    check_sudo "restart"
    log_step "重启Nginx服务..."
    
    systemctl restart nginx
    
    log_info "✅ 服务重启完成"
}

# 测试配置
test_config() {
    log_step "测试Nginx配置..."
    
    if nginx -t; then
        log_info "✅ 配置测试通过"
    else
        log_error "❌ 配置测试失败"
        exit 1
    fi
}

# 查看日志
show_logs() {
    log_step "显示Nginx日志..."
    
    echo "选择要查看的日志:"
    echo "1) 访问日志 (access.log)"
    echo "2) 错误日志 (error.log)"
    echo "3) AuraWell访问日志"
    echo "4) AuraWell错误日志"
    echo "5) 实时监控所有日志"
    
    read -p "请选择 (1-5): " choice
    
    case $choice in
        1)
            tail -f /var/log/nginx/access.log
            ;;
        2)
            tail -f /var/log/nginx/error.log
            ;;
        3)
            if [[ -f "/var/log/nginx/aurawell_access.log" ]]; then
                tail -f /var/log/nginx/aurawell_access.log
            else
                log_warn "AuraWell访问日志不存在"
            fi
            ;;
        4)
            if [[ -f "/var/log/nginx/aurawell_error.log" ]]; then
                tail -f /var/log/nginx/aurawell_error.log
            else
                log_warn "AuraWell错误日志不存在"
            fi
            ;;
        5)
            tail -f /var/log/nginx/*.log
            ;;
        *)
            log_error "无效选择"
            ;;
    esac
}

# 启用站点
enable_site() {
    check_sudo "enable"
    log_step "启用AuraWell站点..."
    
    if [[ ! -f "/etc/nginx/sites-available/aurawell" ]]; then
        log_error "AuraWell配置文件不存在，请先部署配置"
        exit 1
    fi
    
    ln -sf "/etc/nginx/sites-available/aurawell" "/etc/nginx/sites-enabled/aurawell"
    nginx -t
    systemctl reload nginx
    
    log_info "✅ 站点已启用"
}

# 禁用站点
disable_site() {
    check_sudo "disable"
    log_step "禁用AuraWell站点..."
    
    rm -f "/etc/nginx/sites-enabled/aurawell"
    systemctl reload nginx
    
    log_info "✅ 站点已禁用"
}

# 备份配置
backup_config() {
    check_sudo "backup"
    log_step "备份Nginx配置..."
    
    BACKUP_DIR="/etc/nginx/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    cp -r /etc/nginx/sites-available "$BACKUP_DIR/"
    cp -r /etc/nginx/sites-enabled "$BACKUP_DIR/"
    
    log_info "✅ 配置已备份到: $BACKUP_DIR"
}

# 主函数
main() {
    case "${1:-help}" in
        status)
            show_status
            ;;
        deploy)
            deploy_config
            ;;
        ssl)
            deploy_ssl
            ;;
        reload)
            reload_nginx
            ;;
        restart)
            restart_nginx
            ;;
        test)
            test_config
            ;;
        logs)
            show_logs
            ;;
        enable)
            enable_site
            ;;
        disable)
            disable_site
            ;;
        backup)
            backup_config
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
