#!/bin/bash
# GitHub Actions 配置验证脚本

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local status=$1
    local message=$2
    
    if [ "$status" = "success" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "warning" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    elif [ "$status" = "error" ]; then
        echo -e "${RED}❌ $message${NC}"
    else
        echo -e "${BLUE}ℹ️  $message${NC}"
    fi
}

echo -e "${BLUE}=== GitHub Actions 配置验证 ===${NC}"
echo

# 检查工作流文件
print_status "info" "检查 GitHub Actions 工作流配置..."

if [ -d ".github/workflows" ]; then
    print_status "success" "找到 .github/workflows 目录"
    
    workflow_files=(".github/workflows/ci-cd.yml" ".github/workflows/tests.yml" ".github/workflows/frontend.yml")
    
    for file in "${workflow_files[@]}"; do
        if [ -f "$file" ]; then
            print_status "success" "找到工作流文件: $file"
            
            # 检查 YAML 语法
            if command -v python3 &> /dev/null; then
                python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null
                if [ $? -eq 0 ]; then
                    print_status "success" "$file YAML 语法正确"
                else
                    print_status "error" "$file YAML 语法错误"
                fi
            fi
        else
            print_status "error" "缺少工作流文件: $file"
        fi
    done
else
    print_status "error" "未找到 .github/workflows 目录"
fi

echo

# 检查项目配置文件
print_status "info" "检查项目配置文件..."

config_files=(
    "pyproject.toml:后端项目配置"
    "frontend/package.json:前端项目配置"
    "frontend/.prettierrc:Prettier配置"
    "Makefile:Make配置"
    "scripts/run_tests.sh:测试脚本"
)

for item in "${config_files[@]}"; do
    file=$(echo $item | cut -d: -f1)
    desc=$(echo $item | cut -d: -f2)
    
    if [ -f "$file" ]; then
        print_status "success" "找到 $desc: $file"
    else
        print_status "warning" "缺少 $desc: $file"
    fi
done

echo

# 检查工具可用性
print_status "info" "检查开发工具可用性..."

tools=(
    "uv:后端包管理器"
    "npm:前端包管理器"
    "make:构建工具"
)

for item in "${tools[@]}"; do
    tool=$(echo $item | cut -d: -f1)
    desc=$(echo $item | cut -d: -f2)
    
    if command -v "$tool" &> /dev/null; then
        version=$($tool --version 2>&1 | head -1)
        print_status "success" "$desc 可用: $version"
    else
        print_status "warning" "$desc 不可用: $tool"
    fi
done

echo

# 检查 Python 包配置
print_status "info" "检查 Python 包配置..."

if [ -f "pyproject.toml" ]; then
    # 检查是否包含测试配置
    if grep -q "\[tool.pytest.ini_options\]" pyproject.toml; then
        print_status "success" "pyproject.toml 包含 pytest 配置"
    else
        print_status "warning" "pyproject.toml 缺少 pytest 配置"
    fi
    
    if grep -q "\[tool.coverage.run\]" pyproject.toml; then
        print_status "success" "pyproject.toml 包含 coverage 配置"
    else
        print_status "warning" "pyproject.toml 缺少 coverage 配置"
    fi
    
    if grep -q "\[tool.black\]" pyproject.toml; then
        print_status "success" "pyproject.toml 包含 black 配置"
    else
        print_status "warning" "pyproject.toml 缺少 black 配置"
    fi
fi

echo

# 检查前端包配置
print_status "info" "检查前端包配置..."

if [ -f "frontend/package.json" ]; then
    # 检查是否包含必要的脚本
    scripts=("lint" "lint:fix" "format" "format:check" "type-check" "test")
    
    for script in "${scripts[@]}"; do
        if grep -q "\"$script\":" frontend/package.json; then
            print_status "success" "frontend/package.json 包含 $script 脚本"
        else
            print_status "warning" "frontend/package.json 缺少 $script 脚本"
        fi
    done
fi

echo

# 总结
print_status "info" "配置检查完成!"
echo -e "${BLUE}如果有警告或错误，请根据提示进行修复。${NC}"
echo -e "${BLUE}详细配置说明请参考: docs/CI_CD_SETUP.md${NC}"
