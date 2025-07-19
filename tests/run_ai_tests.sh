#!/bin/bash
# AuraWell AI模型可用性测试快速运行脚本

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🤖 AuraWell AI模型可用性测试${NC}"
echo -e "${BLUE}================================${NC}"

# 检查Python环境
echo -e "\n${YELLOW}🔍 检查Python环境...${NC}"

# 检查是否在conda环境中
if [[ "$CONDA_DEFAULT_ENV" == "AuraWellPython310" ]]; then
    echo -e "${GREEN}✅ 已激活AuraWellPython310 conda环境${NC}"
elif [[ -n "$CONDA_DEFAULT_ENV" ]]; then
    echo -e "${YELLOW}⚠️  当前conda环境: $CONDA_DEFAULT_ENV${NC}"
    echo -e "${YELLOW}   建议切换到AuraWellPython310环境${NC}"
    echo -e "${CYAN}   运行: conda activate AuraWellPython310${NC}"
else
    echo -e "${YELLOW}⚠️  未检测到conda环境${NC}"
fi

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>/dev/null || echo "Python not found")
echo -e "${CYAN}📍 Python版本: $PYTHON_VERSION${NC}"

# 检查项目根目录
echo -e "\n${YELLOW}📂 检查项目结构...${NC}"
if [[ -f "$PROJECT_ROOT/.env" ]]; then
    echo -e "${GREEN}✅ 找到.env配置文件${NC}"
else
    echo -e "${YELLOW}⚠️  .env文件不存在${NC}"
    if [[ -f "$PROJECT_ROOT/env.example" ]]; then
        echo -e "${CYAN}💡 可以复制env.example为.env并配置API密钥${NC}"
        echo -e "${CYAN}   cp env.example .env${NC}"
    fi
fi

# 检查必要的Python包
echo -e "\n${YELLOW}📦 检查Python依赖...${NC}"
REQUIRED_PACKAGES=("openai" "asyncio" "unittest")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✅ $package${NC}"
    else
        echo -e "${RED}❌ $package (缺失)${NC}"
        MISSING_PACKAGES+=("$package")
    fi
done

if [[ ${#MISSING_PACKAGES[@]} -gt 0 ]]; then
    echo -e "\n${RED}❌ 缺少必要的Python包，请先安装依赖:${NC}"
    echo -e "${CYAN}pip install -r requirements.txt${NC}"
    exit 1
fi

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 运行测试
echo -e "\n${PURPLE}🚀 开始运行AI模型可用性测试...${NC}"
echo -e "${PURPLE}================================${NC}"

# 设置Python路径
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

# 运行测试脚本
if python3 tests/test_ai_models_availability.py; then
    echo -e "\n${GREEN}🎉 测试完成!${NC}"
    
    # 检查是否生成了报告文件
    if [[ -f "tests/ai_models_test_report.json" ]]; then
        echo -e "${GREEN}📄 详细报告已生成: tests/ai_models_test_report.json${NC}"
    fi
    
    echo -e "\n${CYAN}💡 提示:${NC}"
    echo -e "${CYAN}  - 查看详细报告: cat tests/ai_models_test_report.json${NC}"
    echo -e "${CYAN}  - 配置API密钥: 编辑 .env 文件${NC}"
    echo -e "${CYAN}  - 重新运行测试: ./tests/run_ai_tests.sh${NC}"
    
else
    echo -e "\n${RED}❌ 测试执行失败${NC}"
    echo -e "${YELLOW}💡 故障排除建议:${NC}"
    echo -e "${YELLOW}  1. 检查Python环境是否正确${NC}"
    echo -e "${YELLOW}  2. 确保已安装所有依赖包${NC}"
    echo -e "${YELLOW}  3. 检查.env文件配置${NC}"
    echo -e "${YELLOW}  4. 查看上方的错误信息${NC}"
    exit 1
fi

echo -e "\n${BLUE}================================${NC}"
echo -e "${BLUE}🤖 AuraWell AI测试脚本结束${NC}"
