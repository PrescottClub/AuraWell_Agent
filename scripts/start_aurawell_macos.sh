#!/bin/bash

# AuraWell MacOS 启动脚本
# 适用于 macOS 系统开发环境

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

# 检查用户权限（仅提示，不阻止）
check_user() {
    if [[ $EUID -eq 0 ]]; then
        log_warn "检测到root用户运行，请注意文件权限问题"
    else
        log_info "当前用户: $(whoami)"
    fi
}

# 检查系统版本
check_system() {
    log_step "检查系统版本..."
    
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_warn "检测到非macOS系统: $OSTYPE，脚本针对macOS优化，可能需要手动调整"
    else
        MACOS_VERSION=$(sw_vers -productVersion)
        log_info "系统检查通过: macOS $MACOS_VERSION"
    fi
}

# 检查Python版本和uv环境
check_python() {
    log_step "检查Python版本和uv环境..."
    
    # 检查uv是否安装
    if ! command -v uv &> /dev/null; then
        log_error "uv 未安装，请安装uv包管理器"
        log_info "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    log_info "uv版本: $(uv --version)"
    
    # 检查Python版本
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f1,2)
    
    if [[ "$PYTHON_MAJOR_MINOR" == "3.12" ]]; then
        log_info "Python版本检查通过: $PYTHON_VERSION (3.12.x)"
    else
        log_warn "推荐使用Python 3.12.x，当前: $PYTHON_VERSION"
        log_info "尝试继续运行..."
    fi
    
    # 检查uv虚拟环境
    if [[ -f "uv.lock" ]]; then
        log_info "检测到uv项目，使用uv环境"
    else
        log_warn "未找到uv.lock文件，将使用系统Python"
    fi
}

# 检查Node.js版本
check_nodejs() {
    log_step "检查Node.js版本..."
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装，请安装Node.js 18+"
        log_info "推荐使用 Homebrew: brew install node"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
    
    if [[ $NODE_MAJOR -ge 18 ]]; then
        log_info "Node.js版本检查通过: v$NODE_VERSION (>= 18.x)"
    else
        log_warn "推荐使用Node.js 18+，当前: v$NODE_VERSION"
        log_info "尝试继续运行..."
    fi
}

# 检查并释放端口
check_and_free_ports() {
    log_step "检查端口占用情况..."
    
    BACKEND_PORT=8001
    FRONTEND_PORT=5173
    
    # 检查后端端口
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warn "端口 $BACKEND_PORT 被占用，尝试释放..."
        PID=$(lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t)
        if [[ -n "$PID" ]]; then
            kill -9 $PID
            log_info "已终止占用端口 $BACKEND_PORT 的进程 (PID: $PID)"
        fi
    else
        log_info "端口 $BACKEND_PORT 可用"
    fi
    
    # 检查前端端口
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warn "端口 $FRONTEND_PORT 被占用，尝试释放..."
        PID=$(lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t)
        if [[ -n "$PID" ]]; then
            kill -9 $PID
            log_info "已终止占用端口 $FRONTEND_PORT 的进程 (PID: $PID)"
        fi
    else
        log_info "端口 $FRONTEND_PORT 可用"
    fi
    
    # 等待端口释放
    sleep 2
}

# 检查环境文件
check_env_file() {
    log_step "检查环境配置文件..."
    
    # 回到项目根目录
    cd "$(dirname "$0")/.."
    
    if [[ ! -f ".env" ]]; then
        if [[ -f "env.example" ]]; then
            log_warn ".env 文件不存在，从 env.example 复制..."
            cp env.example .env
            log_info "请编辑 .env 文件配置您的API密钥"
        else
            log_error ".env 和 env.example 文件都不存在"
            exit 1
        fi
    else
        log_info "环境配置文件检查通过"
    fi
}

# 安装依赖
install_dependencies() {
    log_step "安装Python依赖..."
    
    # 使用uv安装Python依赖
    if [[ -f "pyproject.toml" && -f "uv.lock" ]]; then
        uv sync
        log_info "uv Python依赖安装完成"
    elif [[ -f "requirements.in" ]]; then
        uv pip install -r requirements.in
        log_info "Python依赖安装完成"
    else
        log_error "未找到pyproject.toml或requirements.in文件"
        exit 1
    fi
    
    log_step "安装前端依赖..."
    
    if [[ -d "frontend" && -f "frontend/package.json" ]]; then
        cd frontend
        npm install
        cd ..
        log_info "前端依赖安装完成"
    else
        log_error "前端目录或package.json文件不存在"
        exit 1
    fi
}

# 启动后端服务
start_backend() {
    log_step "启动后端服务..."
    
    # 使用uv运行Python应用
    if [[ -f "src/aurawell/main.py" ]]; then
        BACKEND_CMD="uv run python -m src.aurawell.main"
    elif [[ -f "src/aurawell/interfaces/api_interface.py" ]]; then
        BACKEND_CMD="uv run uvicorn src.aurawell.interfaces.api_interface:app --host 127.0.0.1 --port 8001"
    else
        log_error "找不到后端启动文件"
        exit 1
    fi
    
    log_info "启动命令: $BACKEND_CMD"
    
    # 在后台启动后端
    nohup $BACKEND_CMD > backend.log 2>&1 &
    BACKEND_PID=$!
    
    echo $BACKEND_PID > backend.pid
    log_info "后端服务已启动 (PID: $BACKEND_PID)"
    
    # 等待后端启动
    sleep 5
    
    # 检查后端是否正常启动
    if kill -0 $BACKEND_PID 2>/dev/null; then
        log_info "后端服务运行正常"
    else
        log_error "后端服务启动失败，请检查 backend.log"
        exit 1
    fi
}

# 启动前端服务
start_frontend() {
    log_step "启动前端服务..."
    
    cd frontend
    
    # 在后台启动前端
    nohup npm run dev -- --host 127.0.0.1 --port 5173 > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    cd ..
    echo $FRONTEND_PID > frontend.pid
    log_info "前端服务已启动 (PID: $FRONTEND_PID)"
    
    # 等待前端启动
    sleep 10
    
    # 检查前端是否正常启动
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        log_info "前端服务运行正常"
    else
        log_error "前端服务启动失败，请检查 frontend.log"
        exit 1
    fi
}

# 显示服务状态
show_status() {
    log_step "服务状态检查..."
    
    echo "=================================="
    echo "🚀 AuraWell 服务启动完成!"
    echo "=================================="
    echo
    echo "🌐 访问入口界面:"
    echo "  ┌─────────────────────────────────────────────┐"
    echo "  │  🎯 主要入口: http://localhost:5173         │"
    echo "  │  📚 API文档: http://localhost:8001/docs     │"
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
    echo "  • 后端服务: http://localhost:8001"
    echo "  • 前端服务: http://localhost:5173"
    echo
    echo "📊 进程信息:"
    if [[ -f "backend.pid" ]]; then
        BACKEND_PID=$(cat backend.pid)
        echo "  • 后端进程: $BACKEND_PID"
    fi
    if [[ -f "frontend.pid" ]]; then
        FRONTEND_PID=$(cat frontend.pid)
        echo "  • 前端进程: $FRONTEND_PID"
    fi
    echo
    echo "📝 日志文件:"
    echo "  • 后端日志: tail -f backend.log"
    echo "  • 前端日志: tail -f frontend.log"
    echo
    echo "🔄 管理命令:"
    echo "  • 重启服务: ./scripts/restart_aurawell_macos.sh"
    echo "  • 运行测试: uv run python -m pytest tests/"
    echo "  • 手动停止: kill \$(cat backend.pid frontend.pid)"
    echo
}

# 主函数
main() {
    echo "🌟 AuraWell MacOS 启动脚本"
    echo "=================================="
    echo
    
    check_user
    check_system
    check_python
    check_nodejs
    check_and_free_ports
    check_env_file
    install_dependencies
    start_backend
    start_frontend
    show_status
    
    log_info "🎉 所有服务启动完成！"
    log_info "🌐 请访问 http://localhost:5173 开始使用 AuraWell"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
