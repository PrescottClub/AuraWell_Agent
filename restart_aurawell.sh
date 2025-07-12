#!/bin/bash

# AuraWell 云服务器重启脚本
# 适用于 Ubuntu 22.04 系统
# 部署IP: 166.108.224.73

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

# 停止现有服务
stop_services() {
    log_step "停止现有服务..."
    
    # 停止后端服务
    if [[ -f "backend.pid" ]]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            log_info "后端服务已停止 (PID: $BACKEND_PID)"
        fi
        rm -f backend.pid
    fi
    
    # 停止前端服务
    if [[ -f "frontend.pid" ]]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            log_info "前端服务已停止 (PID: $FRONTEND_PID)"
        fi
        rm -f frontend.pid
    fi
    
    # 强制释放端口
    for port in 8001 5173; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            PID=$(lsof -Pi :$port -sTCP:LISTEN -t)
            if [[ -n "$PID" ]]; then
                kill -9 $PID
                log_info "强制停止占用端口$port的进程 (PID: $PID)"
            fi
        fi
    done
    
    # 等待进程完全停止
    sleep 3
}

# 检查系统环境
check_environment() {
    log_step "检查系统环境..."
    
    # 检查Python版本
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f1,2)

    if [[ "$PYTHON_MAJOR_MINOR" == "3.10" ]]; then
        log_info "Python版本: $PYTHON_VERSION ✅"
    else
        log_warn "Python版本: $PYTHON_VERSION (推荐3.10.x)"
    fi

    # 检查Node.js版本
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi

    NODE_VERSION=$(node --version | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)

    if [[ $NODE_MAJOR -ge 18 ]]; then
        log_info "Node.js版本: v$NODE_VERSION ✅"
    else
        log_warn "Node.js版本: v$NODE_VERSION (推荐18+)"
    fi
    
    # 检查conda环境
    if command -v conda &> /dev/null; then
        if conda env list | grep -q "AuraWellPython310"; then
            source $(conda info --base)/etc/profile.d/conda.sh
            conda activate AuraWellPython310
            log_info "已激活conda环境: AuraWellPython310"
        fi
    fi
    
    # 检查环境文件
    if [[ ! -f ".env" ]]; then
        if [[ -f "env.example" ]]; then
            cp env.example .env
            log_warn "已从env.example创建.env文件，请检查配置"
        else
            log_error ".env文件不存在"
            exit 1
        fi
    fi
    
    log_info "环境检查完成"
}

# 更新依赖
update_dependencies() {
    log_step "更新依赖包..."
    
    # 更新Python依赖
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt --upgrade
        log_info "Python依赖更新完成"
    fi
    
    # 更新前端依赖
    if [[ -d "frontend" && -f "frontend/package.json" ]]; then
        cd frontend
        npm install
        cd ..
        log_info "前端依赖更新完成"
    fi
}

# 启动后端服务
start_backend() {
    log_step "启动后端服务..."
    
    # 检查启动文件
    if [[ -f "src/aurawell/main.py" ]]; then
        BACKEND_CMD="python -m src.aurawell.main"
    elif [[ -f "src/aurawell/interfaces/api_interface.py" ]]; then
        BACKEND_CMD="uvicorn src.aurawell.interfaces.api_interface:app --host 0.0.0.0 --port 8001 --reload"
    else
        log_error "找不到后端启动文件"
        exit 1
    fi
    
    # 启动后端
    nohup $BACKEND_CMD > backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid
    
    log_info "后端服务启动中... (PID: $BACKEND_PID)"
    
    # 等待后端启动
    for i in {1..10}; do
        if curl -s http://localhost:8001/api/v1/health >/dev/null 2>&1; then
            log_info "后端服务启动成功"
            return 0
        fi
        sleep 2
        echo -n "."
    done
    
    log_error "后端服务启动超时，请检查backend.log"
    exit 1
}

# 启动前端服务
start_frontend() {
    log_step "启动前端服务..."
    
    cd frontend
    
    # 构建前端（生产模式）
    if [[ "$1" == "production" ]]; then
        npm run build
        log_info "前端构建完成"
        
        # 使用nginx服务静态文件
        if command -v nginx &> /dev/null; then
            sudo cp -r dist/* /var/www/html/
            sudo systemctl reload nginx
            log_info "前端部署到nginx完成"
            cd ..
            return 0
        fi
    fi
    
    # 开发模式启动
    nohup npm run dev -- --host 0.0.0.0 --port 5173 > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    echo $FRONTEND_PID > frontend.pid
    
    log_info "前端服务启动中... (PID: $FRONTEND_PID)"
    
    # 等待前端启动
    for i in {1..15}; do
        if curl -s http://localhost:5173 >/dev/null 2>&1; then
            log_info "前端服务启动成功"
            return 0
        fi
        sleep 2
        echo -n "."
    done
    
    log_error "前端服务启动超时，请检查frontend.log"
    exit 1
}

# 健康检查
health_check() {
    log_step "执行健康检查..."
    
    # 检查后端API
    if curl -s http://localhost:8001/api/v1/health | grep -q "healthy"; then
        log_info "✅ 后端API健康检查通过"
    else
        log_warn "❌ 后端API健康检查失败"
    fi
    
    # 检查前端
    if curl -s http://localhost:5173 >/dev/null 2>&1; then
        log_info "✅ 前端服务健康检查通过"
    else
        log_warn "❌ 前端服务健康检查失败"
    fi
    
    # 检查RAG服务
    if curl -s -X POST http://localhost:8001/api/v1/rag/retrieve \
        -H "Content-Type: application/json" \
        -d '{"user_query":"test","k":1}' | grep -q "documents"; then
        log_info "✅ RAG服务健康检查通过"
    else
        log_warn "❌ RAG服务健康检查失败"
    fi
}

# 显示服务状态
show_status() {
    echo
    echo "=================================="
    echo "🚀 AuraWell 服务重启完成!"
    echo "=================================="
    echo
    echo "🌐 访问入口界面:"
    echo "  ┌─────────────────────────────────────────────┐"
    echo "  │  🎯 主要入口: http://166.108.224.73:5173    │"
    echo "  │  📚 API文档: http://166.108.224.73:8001/docs │"
    echo "  └─────────────────────────────────────────────┘"
    echo
    echo "🧪 测试账号:"
    echo "  • 用户名: test_user"
    echo "  • 密码: test_password"
    echo
    echo "💬 健康助手使用:"
    echo "  • 普通对话: 直接输入问题"
    echo "  • RAG检索: /rag 您的查询内容"
    echo "  • 示例: /rag 高血压的饮食建议"
    echo
    echo "📋 服务信息:"
    echo "  • 后端服务: http://166.108.224.73:8001"
    echo "  • 前端服务: http://166.108.224.73:5173"
    echo "  • 健康检查: http://166.108.224.73:8001/api/v1/health"
    echo
    echo "📊 进程信息:"
    if [[ -f "backend.pid" ]]; then
        echo "  • 后端进程: $(cat backend.pid)"
    fi
    if [[ -f "frontend.pid" ]]; then
        echo "  • 前端进程: $(cat frontend.pid)"
    fi
    echo
    echo "📝 日志文件:"
    echo "  • 后端日志: tail -f backend.log"
    echo "  • 前端日志: tail -f frontend.log"
    echo
    echo "🔄 管理命令:"
    echo "  • 重启服务: ./restart_aurawell.sh"
    echo "  • 运行测试: python run_tests.py"
    echo "  • 停止服务: pkill -f 'uvicorn\\|npm run dev'"
    echo
}

# 主函数
main() {
    echo "🔄 AuraWell 云服务器重启脚本"
    echo "=================================="
    echo
    
    # 解析参数
    MODE="development"
    if [[ "$1" == "production" || "$1" == "prod" ]]; then
        MODE="production"
        log_info "生产模式启动"
    else
        log_info "开发模式启动"
    fi
    
    stop_services
    check_environment
    
    # 可选：更新依赖
    if [[ "$2" == "update" ]]; then
        update_dependencies
    fi
    
    start_backend
    start_frontend $MODE
    
    # 等待服务稳定
    sleep 5
    
    health_check
    show_status
    
    log_info "🎉 AuraWell服务重启完成！"
    log_info "🌐 请访问 http://166.108.224.73:5173 开始使用 AuraWell"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
