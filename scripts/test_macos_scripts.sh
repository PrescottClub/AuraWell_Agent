#!/bin/bash

# MacOS 脚本测试工具
# 测试 macOS 启动脚本的基本功能

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

echo "🧪 MacOS 脚本测试工具"
echo "========================"
echo

# 测试脚本语法
log_step "测试脚本语法..."

if bash -n scripts/start_aurawell_macos.sh; then
    log_info "✅ start_aurawell_macos.sh 语法检查通过"
else
    log_error "❌ start_aurawell_macos.sh 语法错误"
    exit 1
fi

if bash -n scripts/restart_aurawell_macos.sh; then
    log_info "✅ restart_aurawell_macos.sh 语法检查通过"
else
    log_error "❌ restart_aurawell_macos.sh 语法错误"
    exit 1
fi

# 测试脚本权限
log_step "测试脚本权限..."

if [[ -x "scripts/start_aurawell_macos.sh" ]]; then
    log_info "✅ start_aurawell_macos.sh 具有执行权限"
else
    log_warn "⚠️  start_aurawell_macos.sh 缺少执行权限"
    chmod +x scripts/start_aurawell_macos.sh
    log_info "✅ 已添加执行权限"
fi

if [[ -x "scripts/restart_aurawell_macos.sh" ]]; then
    log_info "✅ restart_aurawell_macos.sh 具有执行权限"
else
    log_warn "⚠️  restart_aurawell_macos.sh 缺少执行权限"
    chmod +x scripts/restart_aurawell_macos.sh
    log_info "✅ 已添加执行权限"
fi

# 测试系统检测功能
log_step "测试系统检测功能..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    log_info "✅ 当前系统: macOS"
    MACOS_VERSION=$(sw_vers -productVersion)
    log_info "✅ 系统版本: $MACOS_VERSION"
else
    log_warn "⚠️  当前系统不是macOS: $OSTYPE"
fi

# 测试Python检测
log_step "测试Python检测..."

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_info "✅ Python版本: $PYTHON_VERSION"
    
    PYTHON_MAJOR_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f1,2)
    if [[ "$PYTHON_MAJOR_MINOR" == "3.10" ]]; then
        log_info "✅ Python版本符合要求 (3.10.x)"
    else
        log_warn "⚠️  Python版本: $PYTHON_VERSION (推荐3.10.x)"
    fi
else
    log_error "❌ Python3 未安装"
fi

# 测试Node.js检测
log_step "测试Node.js检测..."

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | sed 's/v//')
    log_info "✅ Node.js版本: v$NODE_VERSION"
    
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
    if [[ $NODE_MAJOR -ge 18 ]]; then
        log_info "✅ Node.js版本符合要求 (>= 18.x)"
    else
        log_warn "⚠️  Node.js版本: v$NODE_VERSION (推荐18+)"
    fi
else
    log_error "❌ Node.js 未安装"
fi

# 测试conda检测
log_step "测试conda检测..."

if command -v conda &> /dev/null; then
    log_info "✅ conda 已安装"
    
    if conda env list | grep -q "AuraWellPython310"; then
        log_info "✅ AuraWellPython310 环境存在"
    else
        log_warn "⚠️  AuraWellPython310 环境不存在"
        log_info "💡 可以运行: conda create -n AuraWellPython310 python=3.10"
    fi
else
    log_warn "⚠️  conda 未安装"
fi

# 测试端口检测
log_step "测试端口检测..."

for port in 8001 5173; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        PID=$(lsof -Pi :$port -sTCP:LISTEN -t)
        log_warn "⚠️  端口 $port 被占用 (PID: $PID)"
    else
        log_info "✅ 端口 $port 可用"
    fi
done

# 测试环境文件
log_step "测试环境文件..."

if [[ -f ".env" ]]; then
    log_info "✅ .env 文件存在"
else
    if [[ -f "env.example" ]]; then
        log_warn "⚠️  .env 文件不存在，但 env.example 存在"
        log_info "💡 可以运行: cp env.example .env"
    else
        log_error "❌ .env 和 env.example 文件都不存在"
    fi
fi

# 测试项目文件结构
log_step "测试项目文件结构..."

required_files=(
    "requirements.txt"
    "frontend/package.json"
    "src/aurawell"
)

for file in "${required_files[@]}"; do
    if [[ -e "$file" ]]; then
        log_info "✅ $file 存在"
    else
        log_error "❌ $file 不存在"
    fi
done

echo
echo "========================"
echo "🎯 测试总结"
echo "========================"

log_info "macOS 启动脚本基本功能测试完成"
log_info "如果所有检查都通过，可以尝试运行:"
echo "  • ./scripts/start_aurawell_macos.sh"
echo "  • ./scripts/restart_aurawell_macos.sh"
echo
log_info "如果遇到问题，请参考 DEPLOYMENT_README.md"
echo
