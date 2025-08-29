# AuraWell Agent Makefile
# 简化开发工作流的 Make 配置

.PHONY: help install test test-backend test-frontend lint format security coverage clean build dev

# 默认目标
help:
	@echo "AuraWell Agent 开发工具"
	@echo ""
	@echo "可用命令:"
	@echo "  install        安装所有依赖 (后端和前端)"
	@echo "  test           运行所有测试"
	@echo "  test-backend   运行后端测试"
	@echo "  test-frontend  运行前端测试"
	@echo "  lint           代码检查和格式化"
	@echo "  format         自动格式化代码"
	@echo "  security       安全检查"
	@echo "  coverage       生成覆盖率报告"
	@echo "  clean          清理临时文件"
	@echo "  build          构建项目"
	@echo "  dev            启动开发服务器"

# 安装依赖
install:
	@echo "安装后端依赖..."
	uv sync --all-extras
	uv add --dev pytest pytest-asyncio pytest-cov black isort mypy safety bandit
	@echo "安装前端依赖..."
	cd frontend && npm ci

# 运行所有测试
test: test-backend test-frontend

# 后端测试
test-backend:
	@echo "运行后端测试..."
	export PYTHONPATH="$(PWD)/src:$$PYTHONPATH" && \
	uv run pytest tests/ -v --tb=short

# 前端测试
test-frontend:
	@echo "运行前端测试..."
	cd frontend && \
	npm run lint && \
	npm run format:check && \
	npm run type-check && \
	npm run test

# 代码检查
lint:
	@echo "运行后端代码检查..."
	uv run black --check --diff src/ tests/
	uv run isort --check-only --diff src/ tests/
	uv run mypy src/
	@echo "运行前端代码检查..."
	cd frontend && npm run lint

# 自动格式化
format:
	@echo "格式化后端代码..."
	uv run black src/ tests/
	uv run isort src/ tests/
	@echo "格式化前端代码..."
	cd frontend && npm run lint:fix && npm run format

# 安全检查
security:
	@echo "运行安全检查..."
	uv run safety check
	uv run bandit -r src/

# 覆盖率报告
coverage:
	@echo "生成覆盖率报告..."
	export PYTHONPATH="$(PWD)/src:$$PYTHONPATH" && \
	uv run pytest tests/ \
		--cov=src/aurawell \
		--cov-report=html \
		--cov-report=term-missing \
		--cov-report=xml
	@echo "覆盖率报告已生成在 htmlcov/ 目录"

# 清理临时文件
clean:
	@echo "清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -f test*.db
	rm -f .env.test
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -f coverage.xml
	cd frontend && rm -rf node_modules/.cache

# 构建项目
build:
	@echo "构建后端..."
	uv build
	@echo "构建前端..."
	cd frontend && npm run build

# 启动开发服务器
dev:
	@echo "启动开发服务器..."
	@echo "启动后端服务器 (端口 8000)..."
	export PYTHONPATH="$(PWD)/src:$$PYTHONPATH" && \
	uv run uvicorn aurawell.main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "启动前端开发服务器 (端口 3000)..."
	cd frontend && npm run dev

# CI 模拟
ci: install lint test security coverage
	@echo "CI 检查完成!"

# 快速检查 (适合提交前)
check: format lint test-backend
	@echo "快速检查完成!"
