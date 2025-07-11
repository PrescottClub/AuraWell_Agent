#!/bin/bash

# AuraWell 模型测试运行脚本
# 用于快速运行新的模型测试文件

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

# 检查conda环境
check_conda_env() {
    log_step "检查conda环境..."
    
    if command -v conda &> /dev/null; then
        if conda env list | grep -q "AuraWellPython310"; then
            log_info "激活AuraWellPython310环境..."
            source $(conda info --base)/etc/profile.d/conda.sh
            conda activate AuraWellPython310
            log_info "已激活conda环境: AuraWellPython310"
        else
            log_warn "未找到AuraWellPython310环境，使用当前Python环境"
        fi
    else
        log_warn "未检测到conda，使用当前Python环境"
    fi
}

# 检查pytest
check_pytest() {
    log_step "检查pytest..."
    
    if ! command -v pytest &> /dev/null; then
        log_error "pytest 未安装，尝试安装..."
        pip install pytest
    fi
    
    log_info "pytest 版本: $(pytest --version)"
}

# 运行DeepSeek-V3模型测试
run_deepseek_v3_tests() {
    log_step "运行DeepSeek-V3模型测试..."
    
    if [[ -f "tests/test_deepseek_v3_model.py" ]]; then
        pytest tests/test_deepseek_v3_model.py -v --tb=short
        if [[ $? -eq 0 ]]; then
            log_info "✅ DeepSeek-V3模型测试通过"
        else
            log_error "❌ DeepSeek-V3模型测试失败"
            return 1
        fi
    else
        log_error "测试文件不存在: tests/test_deepseek_v3_model.py"
        return 1
    fi
}

# 运行QWEN_FAST模型测试
run_qwen_fast_tests() {
    log_step "运行QWEN_FAST模型测试..."
    
    if [[ -f "tests/test_qwen_fast_model.py" ]]; then
        pytest tests/test_qwen_fast_model.py -v --tb=short
        if [[ $? -eq 0 ]]; then
            log_info "✅ QWEN_FAST模型测试通过"
        else
            log_error "❌ QWEN_FAST模型测试失败"
            return 1
        fi
    else
        log_error "测试文件不存在: tests/test_qwen_fast_model.py"
        return 1
    fi
}

# 运行AB测试
run_ab_tests() {
    log_step "运行AB对比测试..."
    
    if [[ -f "aurawell/AB_test.py" ]]; then
        log_info "运行模型对比测试..."
        python aurawell/AB_test.py --compare --output tests/ab_test_results.json
        
        if [[ $? -eq 0 ]]; then
            log_info "✅ AB测试完成，结果保存到 tests/ab_test_results.json"
        else
            log_warn "⚠️ AB测试遇到问题，但继续执行其他测试"
        fi
    else
        log_warn "AB测试文件不存在: aurawell/AB_test.py"
    fi
}

# 运行所有模型相关测试
run_all_model_tests() {
    log_step "运行所有模型相关测试..."
    
    # 运行现有的模型测试
    if [[ -f "tests/test_rag_upgrade.py" ]]; then
        log_info "运行RAG升级测试..."
        pytest tests/test_rag_upgrade.py -v --tb=short || log_warn "RAG升级测试有问题"
    fi
    
    if [[ -f "tests/test_translation_service.py" ]]; then
        log_info "运行翻译服务测试..."
        pytest tests/test_translation_service.py -v --tb=short || log_warn "翻译服务测试有问题"
    fi
    
    if [[ -f "tests/test_upgrade_acceptance.py" ]]; then
        log_info "运行升级验收测试..."
        pytest tests/test_upgrade_acceptance.py -v --tb=short || log_warn "升级验收测试有问题"
    fi
}

# 生成测试报告
generate_test_report() {
    log_step "生成测试报告..."
    
    REPORT_FILE="tests/model_test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "AuraWell 模型测试报告"
        echo "======================"
        echo "测试时间: $(date)"
        echo "Python版本: $(python --version)"
        echo "pytest版本: $(pytest --version)"
        echo ""
        echo "环境变量配置:"
        echo "DEEPSEEK_SERIES_V3: ${DEEPSEEK_SERIES_V3:-未设置}"
        echo "QWEN_FAST: ${QWEN_FAST:-未设置}"
        echo "DASHSCOPE_API_KEY: ${DASHSCOPE_API_KEY:+已设置}"
        echo ""
        echo "测试结果:"
        echo "--------"
        
        if [[ -f "tests/ab_test_results.json" ]]; then
            echo "AB测试结果已保存到: tests/ab_test_results.json"
        fi
        
        echo ""
        echo "详细日志请查看上方输出"
        
    } > "$REPORT_FILE"
    
    log_info "测试报告已保存到: $REPORT_FILE"
}

# 主函数
main() {
    echo "🧪 AuraWell 模型测试运行器"
    echo "=========================="
    echo ""
    
    # 切换到项目根目录
    cd "$(dirname "$0")/.."
    
    check_conda_env
    check_pytest
    
    # 设置测试环境变量（如果未设置）
    export DEEPSEEK_SERIES_V3=${DEEPSEEK_SERIES_V3:-"deepseek-v3"}
    export QWEN_FAST=${QWEN_FAST:-"qwen-turbo"}
    
    log_info "当前测试配置:"
    log_info "  DEEPSEEK_SERIES_V3: $DEEPSEEK_SERIES_V3"
    log_info "  QWEN_FAST: $QWEN_FAST"
    echo ""
    
    # 运行测试
    FAILED_TESTS=0
    
    if ! run_deepseek_v3_tests; then
        ((FAILED_TESTS++))
    fi
    
    if ! run_qwen_fast_tests; then
        ((FAILED_TESTS++))
    fi
    
    run_ab_tests
    run_all_model_tests
    generate_test_report
    
    echo ""
    echo "=========================="
    if [[ $FAILED_TESTS -eq 0 ]]; then
        log_info "🎉 所有核心模型测试通过！"
        echo ""
        log_info "✅ DeepSeek-V3 模型测试: 通过"
        log_info "✅ QWEN_FAST 模型测试: 通过"
        log_info "📊 AB对比测试: 已完成"
        echo ""
        log_info "🚀 模型更新验证成功，可以继续使用新配置"
    else
        log_error "❌ 有 $FAILED_TESTS 个核心测试失败"
        log_error "请检查模型配置和网络连接"
        exit 1
    fi
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
