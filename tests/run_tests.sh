#!/bin/bash
# pytest测试运行脚本
# 提供便捷的测试运行方式

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AuraWell项目pytest测试运行器 ===${NC}"
echo -e "${BLUE}项目根目录: $PROJECT_ROOT${NC}"
echo

# 检查conda环境
if [[ "$CONDA_DEFAULT_ENV" == "AuraWellPython310" ]]; then
    echo -e "${GREEN}✅ 当前在AuraWellPython310环境中${NC}"
else
    echo -e "${YELLOW}⚠️  当前不在AuraWellPython310环境中${NC}"
    echo -e "${YELLOW}建议运行: conda activate AuraWellPython310${NC}"
fi

# 检查pytest是否安装
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest未安装${NC}"
    echo -e "${YELLOW}正在安装pytest...${NC}"
    pip install pytest pytest-cov
fi

# 函数：运行特定测试
run_specific_test() {
    local test_file=$1
    local description=$2
    
    echo -e "${BLUE}🧪 运行测试: $description${NC}"
    echo -e "${BLUE}文件: $test_file${NC}"
    echo "----------------------------------------"
    
    if python -m pytest "$test_file" -v; then
        echo -e "${GREEN}✅ $description 测试通过${NC}"
    else
        echo -e "${RED}❌ $description 测试失败${NC}"
    fi
    echo
}

# 函数：运行所有测试
run_all_tests() {
    echo -e "${BLUE}🧪 运行所有pytest测试${NC}"
    echo "----------------------------------------"
    
    if python -m pytest tests/ -v; then
        echo -e "${GREEN}✅ 所有测试通过${NC}"
    else
        echo -e "${RED}❌ 部分测试失败${NC}"
    fi
    echo
}

# 函数：运行带标记的测试
run_marked_tests() {
    local marker=$1
    local description=$2
    
    echo -e "${BLUE}🧪 运行标记测试: $description${NC}"
    echo -e "${BLUE}标记: $marker${NC}"
    echo "----------------------------------------"
    
    if python -m pytest tests/ -m "$marker" -v; then
        echo -e "${GREEN}✅ $description 测试通过${NC}"
    else
        echo -e "${RED}❌ $description 测试失败${NC}"
    fi
    echo
}

# 主菜单
show_menu() {
    echo -e "${BLUE}请选择要运行的测试:${NC}"
    echo "1. 运行所有测试"
    echo "2. 运行RAG索引测试"
    echo "3. 运行增强RAG测试"
    echo "4. 运行OSS集成测试"
    echo "5. 运行RAG相关测试 (标记: rag)"
    echo "6. 运行OSS相关测试 (标记: oss)"
    echo "7. 运行快速测试 (排除slow标记)"
    echo "8. 运行集成测试 (标记: integration)"
    echo "9. 生成测试覆盖率报告"
    echo "0. 退出"
    echo
}

# 处理用户选择
handle_choice() {
    local choice=$1
    
    case $choice in
        1)
            run_all_tests
            ;;
        2)
            run_specific_test "tests/test_rag_index.py" "RAG索引功能"
            ;;
        3)
            run_specific_test "tests/test_enhanced_rag.py" "增强RAG功能"
            ;;
        4)
            run_specific_test "tests/test_oss_integration.py" "OSS集成功能"
            ;;
        5)
            run_marked_tests "rag" "RAG相关功能"
            ;;
        6)
            run_marked_tests "oss" "OSS相关功能"
            ;;
        7)
            run_marked_tests "not slow" "快速测试"
            ;;
        8)
            run_marked_tests "integration" "集成测试"
            ;;
        9)
            echo -e "${BLUE}🧪 生成测试覆盖率报告${NC}"
            echo "----------------------------------------"
            python -m pytest tests/ --cov=src --cov-report=html --cov-report=term -v
            echo -e "${GREEN}✅ 覆盖率报告已生成到 htmlcov/ 目录${NC}"
            ;;
        0)
            echo -e "${GREEN}退出测试运行器${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选择，请重新输入${NC}"
            ;;
    esac
}

# 主循环
main() {
    # 如果有命令行参数，直接执行
    if [[ $# -gt 0 ]]; then
        case $1 in
            "all")
                run_all_tests
                ;;
            "rag")
                run_marked_tests "rag" "RAG相关功能"
                ;;
            "oss")
                run_marked_tests "oss" "OSS相关功能"
                ;;
            "fast")
                run_marked_tests "not slow" "快速测试"
                ;;
            "coverage")
                python -m pytest tests/ --cov=src --cov-report=html --cov-report=term -v
                ;;
            *)
                echo -e "${RED}未知参数: $1${NC}"
                echo "可用参数: all, rag, oss, fast, coverage"
                exit 1
                ;;
        esac
        return
    fi
    
    # 交互式菜单
    while true; do
        show_menu
        read -p "请输入选择 (0-9): " choice
        echo
        handle_choice "$choice"
        
        echo -e "${YELLOW}按Enter键继续...${NC}"
        read
        clear
    done
}

# 运行主函数
main "$@"
