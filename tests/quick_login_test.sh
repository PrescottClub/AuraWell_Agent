#!/bin/bash

# AuraWell 快速登录测试脚本
# 用于验证登录功能是否正常工作

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

# 检查服务状态
check_backend() {
    log_step "检查后端服务状态..."
    
    if curl -s http://127.0.0.1:8001/docs > /dev/null 2>&1; then
        log_info "后端服务运行正常 (http://127.0.0.1:8001)"
        return 0
    else
        log_error "后端服务未运行或无法访问"
        return 1
    fi
}

check_frontend() {
    log_step "检查前端服务状态..."
    
    if curl -s http://127.0.0.1:5173 > /dev/null 2>&1; then
        log_info "前端服务运行正常 (http://127.0.0.1:5173)"
        return 0
    else
        log_error "前端服务未运行或无法访问"
        return 1
    fi
}

# 测试登录API
test_login_api() {
    log_step "测试登录API..."
    
    response=$(curl -s -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "test_user", "password": "test_password"}')
    
    if echo "$response" | grep -q '"success":true'; then
        log_info "✅ 登录API测试成功"
        echo "响应: $response" | head -c 100
        echo "..."
        return 0
    else
        log_error "❌ 登录API测试失败"
        echo "响应: $response"
        return 1
    fi
}

# 测试其他测试账号
test_demo_user() {
    log_step "测试demo用户登录..."
    
    response=$(curl -s -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "demo_user", "password": "demo_password"}')
    
    if echo "$response" | grep -q '"success":true'; then
        log_info "✅ demo用户登录成功"
        return 0
    else
        log_warn "⚠️ demo用户登录失败"
        return 1
    fi
}

# 打开浏览器
open_browser() {
    log_step "在浏览器中打开AuraWell应用..."
    
    if command -v open > /dev/null 2>&1; then
        open http://127.0.0.1:5173
        log_info "✅ 已在默认浏览器中打开应用"
    else
        log_warn "⚠️ 无法自动打开浏览器，请手动访问: http://127.0.0.1:5173"
    fi
}

# 显示测试账号信息
show_test_accounts() {
    echo ""
    echo "🧪 测试账号信息:"
    echo "=================================="
    echo "账号1: test_user / test_password"
    echo "账号2: demo_user / demo_password"
    echo ""
    echo "🌐 访问地址:"
    echo "前端应用: http://127.0.0.1:5173"
    echo "API文档: http://127.0.0.1:8001/docs"
    echo "=================================="
}

# 主函数
main() {
    echo "🌟 AuraWell 快速登录测试"
    echo "=================================="
    
    # 检查服务状态
    backend_ok=false
    frontend_ok=false
    
    if check_backend; then
        backend_ok=true
    fi
    
    if check_frontend; then
        frontend_ok=true
    fi
    
    if [ "$backend_ok" = false ] || [ "$frontend_ok" = false ]; then
        log_error "服务未完全启动，请先启动所有服务"
        echo ""
        echo "启动命令:"
        echo "后端: python3 -m uvicorn src.aurawell.interfaces.api_interface:app --host 127.0.0.1 --port 8001"
        echo "前端: cd frontend && yarn dev --host 127.0.0.1 --port 5173"
        exit 1
    fi
    
    # 测试登录功能
    echo ""
    if test_login_api; then
        log_info "🎉 主要登录功能正常！"
        
        # 测试其他账号
        test_demo_user
        
        # 显示账号信息
        show_test_accounts
        
        # 打开浏览器
        open_browser
        
        echo ""
        log_info "✅ 所有测试完成，系统运行正常！"
        log_info "💡 现在可以在浏览器中使用测试账号登录了"
        
    else
        log_error "❌ 登录功能测试失败"
        exit 1
    fi
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
