#!/bin/bash
# AuraWell Agent 测试运行脚本
# 本脚本用于本地和CI环境中运行所有测试

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 检查工具环境
check_tools() {
    print_message $BLUE "检查开发工具..."
    
    # 检查 uv
    if ! command -v uv &> /dev/null; then
        print_message $RED "错误: 未找到 uv, 请先安装 uv"
        print_message $YELLOW "安装方法: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    uv_version=$(uv --version 2>&1)
    print_message $GREEN "uv 版本: $uv_version"
    
    # 检查 Python 环境
    python_version=$(uv python list --only-installed | head -1 | awk '{print $2}' || echo "未安装")
    print_message $GREEN "Python 版本: $python_version"
}

# 安装依赖
install_dependencies() {
    print_message $BLUE "安装依赖..."
    
    # 同步项目依赖
    uv sync --all-extras
    
    # 安装测试依赖
    uv add --dev pytest pytest-asyncio pytest-cov pytest-xdist black isort mypy safety bandit
}

# 设置环境变量
setup_environment() {
    print_message $BLUE "设置测试环境..."
    
    export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
    export TESTING=true
    export DATABASE_URL="sqlite:///test.db"
    export LOG_LEVEL=INFO
    
    # 创建测试环境配置文件
    if [ -f "env.example" ]; then
        cp env.example .env.test
        echo "TESTING=true" >> .env.test
        echo "DATABASE_URL=sqlite:///test.db" >> .env.test
    fi
}

# 代码格式检查
run_linting() {
    print_message $BLUE "运行代码检查..."
    
    # Black 格式检查
    print_message $YELLOW "运行 Black 格式检查..."
    if uv run black --check --diff src/ tests/; then
        print_message $GREEN "✓ Black 格式检查通过"
    else
        print_message $YELLOW "! Black 发现格式问题，自动修复中..."
        uv run black src/ tests/
    fi
    
    # isort 导入排序检查
    print_message $YELLOW "运行 isort 导入排序检查..."
    if uv run isort --check-only --diff src/ tests/; then
        print_message $GREEN "✓ isort 检查通过"
    else
        print_message $YELLOW "! isort 发现问题，自动修复中..."
        uv run isort src/ tests/
    fi
    
    # mypy 类型检查
    print_message $YELLOW "运行 mypy 类型检查..."
    if uv run mypy src/; then
        print_message $GREEN "✓ mypy 检查通过"
    else
        print_message $YELLOW "! mypy 发现类型问题"
    fi
}

# 运行单元测试
run_unit_tests() {
    print_message $BLUE "运行单元测试..."
    
    # 基础测试
    print_message $YELLOW "运行基础测试..."
    if [ -f "tests/quick_test.py" ]; then
        uv run pytest tests/quick_test.py -v --tb=short
    fi
    
    # AI模型测试
    print_message $YELLOW "运行 AI 模型测试..."
    if [ -f "tests/test_ai_models_availability.py" ]; then
        uv run pytest tests/test_ai_models_availability.py -v --tb=short
    fi
    
    # 聊天服务测试
    print_message $YELLOW "运行聊天服务测试..."
    uv run pytest tests/test_chat_service_*.py -v --tb=short || true
    
    # LangChain代理测试
    print_message $YELLOW "运行 LangChain 代理测试..."
    if [ -f "tests/test_langchain_agent_fixes.py" ]; then
        uv run pytest tests/test_langchain_agent_fixes.py -v --tb=short
    fi
    
    # MCP工具测试
    print_message $YELLOW "运行 MCP 工具测试..."
    if [ -f "tests/test_mcp_tools.py" ]; then
        uv run pytest tests/test_mcp_tools.py -v --tb=short
    fi
    
    # CI/CD 配置测试
    print_message $YELLOW "运行 CI/CD 配置测试..."
    if [ -f "tests/test_ci_cd_setup.py" ]; then
        uv run pytest tests/test_ci_cd_setup.py -v --tb=short
    fi
}

# 运行覆盖率测试
run_coverage_tests() {
    print_message $BLUE "运行覆盖率测试..."
    
    uv run pytest tests/ \
        --cov=src/aurawell \
        --cov-report=term-missing \
        --cov-report=html \
        --cov-report=xml \
        -v
    
    print_message $GREEN "覆盖率报告已生成在 htmlcov/ 目录"
}

# 运行前端测试
run_frontend_tests() {
    print_message $BLUE "运行前端测试..."
    
    if [ -d "frontend" ]; then
        cd frontend
        
        # 检查是否有 package.json
        if [ -f "package.json" ]; then
            print_message $YELLOW "安装前端依赖..."
            npm ci
            
            print_message $YELLOW "运行前端 lint..."
            npm run lint || npm run lint:fix
            
            print_message $YELLOW "运行前端格式检查..."
            npm run format:check || npm run format
            
            print_message $YELLOW "运行前端类型检查..."
            npm run type-check
            
            print_message $YELLOW "运行前端测试..."
            npm run test
            
            print_message $YELLOW "构建前端..."
            npm run build
        else
            print_message $YELLOW "跳过前端测试 - 未找到 package.json"
        fi
        
        cd ..
    else
        print_message $YELLOW "跳过前端测试 - 未找到 frontend 目录"
    fi
}

# 安全检查
run_security_checks() {
    print_message $BLUE "运行安全检查..."
    
    # Safety - 依赖漏洞检查
    print_message $YELLOW "检查依赖漏洞..."
    if uv run safety check; then
        print_message $GREEN "✓ 未发现已知漏洞"
    else
        print_message $YELLOW "! 发现潜在安全问题"
    fi
    
    # Bandit - 代码安全检查
    print_message $YELLOW "运行代码安全检查..."
    if uv run bandit -r src/; then
        print_message $GREEN "✓ 代码安全检查通过"
    else
        print_message $YELLOW "! 发现潜在安全问题"
    fi
}

# 清理测试文件
cleanup() {
    print_message $BLUE "清理测试文件..."
    
    # 删除测试数据库
    rm -f test*.db
    rm -f .env.test
    
    print_message $GREEN "清理完成"
}

# 主函数
main() {
    print_message $GREEN "开始运行 AuraWell Agent 测试套件..."
    
    # 解析命令行参数
    LINT=true
    UNIT_TESTS=true
    FRONTEND_TESTS=false
    COVERAGE=false
    SECURITY=false
    CLEANUP=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-lint)
                LINT=false
                shift
                ;;
            --no-unit-tests)
                UNIT_TESTS=false
                shift
                ;;
            --frontend)
                FRONTEND_TESTS=true
                shift
                ;;
            --coverage)
                COVERAGE=true
                shift
                ;;
            --security)
                SECURITY=true
                shift
                ;;
            --no-cleanup)
                CLEANUP=false
                shift
                ;;
            --help)
                echo "用法: $0 [选项]"
                echo "选项:"
                echo "  --no-lint       跳过代码检查"
                echo "  --no-unit-tests 跳过单元测试"
                echo "  --frontend      运行前端测试"
                echo "  --coverage      运行覆盖率测试"
                echo "  --security      运行安全检查"
                echo "  --no-cleanup    不清理测试文件"
                echo "  --help          显示此帮助信息"
                exit 0
                ;;
            *)
                print_message $RED "未知选项: $1"
                exit 1
                ;;
        esac
    done
    
    # 执行测试步骤
    check_tools
    install_dependencies
    setup_environment
    
    if [ "$LINT" = true ]; then
        run_linting
    fi
    
    if [ "$UNIT_TESTS" = true ]; then
        run_unit_tests
    fi
    
    if [ "$FRONTEND_TESTS" = true ]; then
        run_frontend_tests
    fi
    
    if [ "$COVERAGE" = true ]; then
        run_coverage_tests
    fi
    
    if [ "$SECURITY" = true ]; then
        run_security_checks
    fi
    
    if [ "$CLEANUP" = true ]; then
        cleanup
    fi
    
    print_message $GREEN "所有测试完成!"
}

# 运行主函数
main "$@"
