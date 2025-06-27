#!/bin/bash

# AuraWell 快速测试脚本
# 专门用于运行 test_rag_upgrade.py 和 test_translation_service.py

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AuraWell 快速测试脚本 ===${NC}"
echo -e "${BLUE}测试文件: test_rag_upgrade.py, test_translation_service.py${NC}"
echo ""

# 激活conda环境
echo -e "${BLUE}[INFO]${NC} 激活 AuraWellPython310 环境..."
if [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
    source /opt/anaconda3/etc/profile.d/conda.sh
elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source $HOME/miniconda3/etc/profile.d/conda.sh
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source $HOME/anaconda3/etc/profile.d/conda.sh
fi

if conda activate AuraWellPython310 2>/dev/null; then
    echo -e "${GREEN}[SUCCESS]${NC} 环境激活成功"
else
    echo -e "${RED}[ERROR]${NC} 无法激活 AuraWellPython310 环境"
    exit 1
fi

# 切换到项目根目录
cd "$(dirname "$0")/.."
echo -e "${BLUE}[INFO]${NC} 工作目录: $(pwd)"
echo ""

# 运行测试统计
total_tests=0
passed_tests=0

# 测试1: RAG升级测试
echo -e "${BLUE}=== 测试 1: RAG升级测试 ===${NC}"
total_tests=$((total_tests + 1))
if python -m unittest tests.test_rag_upgrade -v; then
    echo -e "${GREEN}[PASS]${NC} RAG升级测试通过"
    passed_tests=$((passed_tests + 1))
else
    echo -e "${RED}[FAIL]${NC} RAG升级测试失败"
fi
echo ""

# 测试2: 翻译服务测试
echo -e "${BLUE}=== 测试 2: 翻译服务测试 ===${NC}"
total_tests=$((total_tests + 1))
if python -m unittest tests.test_translation_service -v; then
    echo -e "${GREEN}[PASS]${NC} 翻译服务测试通过"
    passed_tests=$((passed_tests + 1))
else
    echo -e "${RED}[FAIL]${NC} 翻译服务测试失败"
fi
echo ""

# 输出总结
echo -e "${BLUE}=== 测试总结 ===${NC}"
echo -e "${BLUE}总测试文件:${NC} $total_tests"
echo -e "${GREEN}通过测试:${NC} $passed_tests"
echo -e "${RED}失败测试:${NC} $((total_tests - passed_tests))"

if [ $passed_tests -eq $total_tests ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}❌ 有测试失败${NC}"
    exit 1
fi
