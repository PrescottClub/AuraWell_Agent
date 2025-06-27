#!/bin/bash

# AuraWell 测试运行脚本
# 用于快速运行 test_rag_upgrade.py 和 test_translation_service.py

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查conda是否可用
check_conda() {
    if ! command -v conda &> /dev/null; then
        print_error "conda 命令未找到，请确保已安装 Anaconda 或 Miniconda"
        exit 1
    fi
}

# 激活conda环境
activate_conda_env() {
    print_info "激活 AuraWellPython310 conda环境..."
    
    # 尝试不同的conda初始化路径
    if [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
        source /opt/anaconda3/etc/profile.d/conda.sh
    elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
        source $HOME/miniconda3/etc/profile.d/conda.sh
    elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
        source $HOME/anaconda3/etc/profile.d/conda.sh
    else
        print_warning "未找到conda初始化脚本，尝试直接激活环境"
    fi
    
    # 激活环境
    if conda activate AuraWellPython310 2>/dev/null; then
        print_success "成功激活 AuraWellPython310 环境"
    else
        print_error "无法激活 AuraWellPython310 环境，请确保环境存在"
        print_info "可用的conda环境："
        conda env list
        exit 1
    fi
}

# 检查Python环境
check_python_env() {
    print_info "检查Python环境..."
    python_version=$(python --version 2>&1)
    print_info "当前Python版本: $python_version"
    
    # 检查是否在正确的conda环境中
    if [[ "$CONDA_DEFAULT_ENV" == "AuraWellPython310" ]]; then
        print_success "已在 AuraWellPython310 环境中"
    else
        print_warning "当前环境: $CONDA_DEFAULT_ENV"
    fi
}

# 运行单个测试文件
run_test_file() {
    local test_file=$1
    local test_name=$2
    
    print_info "运行 $test_name 测试..."
    echo "=================================================="
    
    if python -m unittest "$test_file" -v; then
        print_success "$test_name 测试通过"
        return 0
    else
        print_error "$test_name 测试失败"
        return 1
    fi
}

# 运行pytest测试
run_pytest_file() {
    local test_file=$1
    local test_name=$2
    
    print_info "使用pytest运行 $test_name 测试..."
    echo "=================================================="
    
    if python -m pytest "$test_file" -v --tb=short; then
        print_success "$test_name 测试通过"
        return 0
    else
        print_error "$test_name 测试失败"
        return 1
    fi
}

# 主函数
main() {
    print_info "开始运行AuraWell测试套件"
    print_info "测试文件: test_rag_upgrade.py, test_translation_service.py"
    echo "=================================================="
    
    # 检查conda
    check_conda
    
    # 激活环境
    activate_conda_env
    
    # 检查Python环境
    check_python_env
    
    # 切换到项目根目录
    cd "$(dirname "$0")/.."
    print_info "当前工作目录: $(pwd)"
    
    # 运行测试统计
    total_tests=0
    passed_tests=0
    failed_tests=0
    
    # 测试文件列表
    declare -a test_files=(
        "tests/test_rag_upgrade.py"
        "tests/test_translation_service.py"
    )

    declare -a test_names=(
        "RAG升级测试"
        "翻译服务测试"
    )
    
    # 选择测试运行器
    if command -v pytest &> /dev/null; then
        print_info "使用pytest作为测试运行器"
        test_runner="pytest"
    else
        print_info "使用unittest作为测试运行器"
        test_runner="unittest"
    fi
    
    # 运行每个测试文件
    for i in "${!test_files[@]}"; do
        test_file="${test_files[$i]}"
        test_name="${test_names[$i]}"
        total_tests=$((total_tests + 1))

        echo ""
        print_info "开始运行: $test_name"

        if [ "$test_runner" == "pytest" ]; then
            if run_pytest_file "$test_file" "$test_name"; then
                passed_tests=$((passed_tests + 1))
            else
                failed_tests=$((failed_tests + 1))
            fi
        else
            # 转换文件路径为模块路径
            module_path=$(echo "$test_file" | sed 's/\//./g' | sed 's/\.py$//')
            if run_test_file "$module_path" "$test_name"; then
                passed_tests=$((passed_tests + 1))
            else
                failed_tests=$((failed_tests + 1))
            fi
        fi
    done
    
    # 输出测试总结
    echo ""
    echo "=================================================="
    print_info "测试总结"
    echo "=================================================="
    print_info "总测试文件: $total_tests"
    print_success "通过: $passed_tests"
    if [ $failed_tests -gt 0 ]; then
        print_error "失败: $failed_tests"
    else
        print_info "失败: $failed_tests"
    fi
    
    # 计算通过率
    if [ $total_tests -gt 0 ]; then
        pass_rate=$((passed_tests * 100 / total_tests))
        print_info "通过率: ${pass_rate}%"
    fi
    
    # 生成测试报告
    generate_test_report "$total_tests" "$passed_tests" "$failed_tests"
    
    # 返回适当的退出码
    if [ $failed_tests -eq 0 ]; then
        print_success "所有测试通过！"
        exit 0
    else
        print_error "有测试失败，请检查上面的错误信息"
        exit 1
    fi
}

# 生成测试报告
generate_test_report() {
    local total=$1
    local passed=$2
    local failed=$3
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    local report_file="tests/test_run_report.txt"
    
    cat > "$report_file" << EOF
=== AuraWell 测试运行报告 ===
运行时间: $timestamp
测试环境: $CONDA_DEFAULT_ENV
Python版本: $(python --version 2>&1)

=== 测试结果 ===
总测试文件: $total
通过测试: $passed
失败测试: $failed
通过率: $((passed * 100 / total))%

=== 测试文件详情 ===
1. test_rag_upgrade.py - RAG升级测试
2. test_translation_service.py - 翻译服务测试

=== 运行命令 ===
bash tests/run_tests.sh

=== 注意事项 ===
- 确保在AuraWellPython310环境中运行
- 如有失败，请检查导入路径和依赖包
- 建议使用pytest获得更详细的测试输出
EOF

    print_info "测试报告已保存到: $report_file"
}

# 显示帮助信息
show_help() {
    echo "AuraWell 测试运行脚本"
    echo ""
    echo "用法: bash tests/run_tests.sh [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -v, --verbose  详细输出模式"
    echo ""
    echo "示例:"
    echo "  bash tests/run_tests.sh"
    echo "  bash tests/run_tests.sh --verbose"
    echo ""
    echo "测试文件:"
    echo "  - test_rag_upgrade.py: RAG模块升级测试"
    echo "  - test_translation_service.py: 翻译服务测试"
}

# 解析命令行参数
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -v|--verbose)
        set -x  # 启用详细输出
        main
        ;;
    "")
        main
        ;;
    *)
        print_error "未知选项: $1"
        show_help
        exit 1
        ;;
esac
