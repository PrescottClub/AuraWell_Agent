#!/bin/bash

# 本地 GitHub Actions 测试脚本
# 支持 Apple M 系列芯片和其他架构

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 AuraWell CI/CD 本地测试脚本${NC}"
echo "========================================"

# 检查 act 是否安装
if ! command -v act &> /dev/null; then
    echo -e "${RED}❌ 错误: act 未安装${NC}"
    echo "请先安装 act: brew install act"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ 错误: Docker 未运行${NC}"
    echo "请先启动 Docker Desktop"
    exit 1
fi

# 检测架构
ARCH=$(uname -m)
CONTAINER_ARCH=""

if [[ "$ARCH" == "arm64" ]] || [[ "$ARCH" == "aarch64" ]]; then
    echo -e "${YELLOW}⚠️  检测到 Apple M 系列芯片，使用 linux/amd64 架构${NC}"
    CONTAINER_ARCH="--container-architecture linux/amd64"
fi

# 工作流选择菜单
echo ""
echo "请选择要测试的工作流:"
echo "1) 简化本地测试 (推荐)"
echo "2) 前端完整测试"
echo "3) 后端完整测试"
echo "4) 前端专用本地测试"
echo "5) 后端专用本地测试"
echo "6) 完整 CI/CD 流水线"
echo ""
read -p "请输入选项 (1-6): " choice

case $choice in
    1)
        WORKFLOW="local-test.yml"
        JOB=""
        echo -e "${GREEN}✅ 运行简化本地测试${NC}"
        ;;
    2)
        WORKFLOW="frontend.yml"
        JOB=""
        echo -e "${GREEN}✅ 运行前端完整测试${NC}"
        ;;
    3)
        WORKFLOW="tests.yml"
        JOB=""
        echo -e "${GREEN}✅ 运行后端完整测试${NC}"
        ;;
    4)
        WORKFLOW="frontend-only.yml"
        JOB=""
        echo -e "${GREEN}✅ 运行前端专用本地测试${NC}"
        ;;
    5)
        WORKFLOW="backend-only.yml"
        JOB=""
        echo -e "${GREEN}✅ 运行后端专用本地测试${NC}"
        ;;
    6)
        WORKFLOW="ci-cd.yml"
        JOB=""
        echo -e "${YELLOW}⚠️  运行完整 CI/CD 流水线 (可能需要较长时间)${NC}"
        ;;
    *)
        echo -e "${RED}❌ 无效选项${NC}"
        exit 1
        ;;
esac

# 构建 act 命令
ACT_CMD="act"

if [[ -n "$CONTAINER_ARCH" ]]; then
    ACT_CMD="$ACT_CMD $CONTAINER_ARCH"
fi

ACT_CMD="$ACT_CMD -W ./.github/workflows/$WORKFLOW"

if [[ -n "$JOB" ]]; then
    ACT_CMD="$ACT_CMD -j $JOB"
fi

# 添加环境变量
ACT_CMD="$ACT_CMD --env GITHUB_TOKEN=fake_token"

echo ""
echo -e "${GREEN}🔧 执行命令:${NC} $ACT_CMD"
echo ""

# 运行测试
if eval $ACT_CMD; then
    echo ""
    echo -e "${GREEN}✅ 测试成功完成!${NC}"
else
    echo ""
    echo -e "${RED}❌ 测试失败!${NC}"
    echo ""
    echo -e "${YELLOW}💡 常见问题解决方案:${NC}"
    echo "1. 确保 Docker Desktop 正在运行"
    echo "2. 如果遇到架构问题，确保使用了 --container-architecture linux/amd64"
    echo "3. 检查网络连接，确保可以拉取 Docker 镜像"
    echo "4. 查看上方错误日志获取具体问题信息"
    exit 1
fi
