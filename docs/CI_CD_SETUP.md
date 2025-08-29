# AuraWell Agent CI/CD 配置说明

## 概述

本项目使用 GitHub Actions 实现 CI/CD 自动化，支持前端和后端的独立测试和部署流程。

## 工作流结构

### 1. 主要工作流文件

- `.github/workflows/ci-cd.yml` - 主 CI/CD 流水线
- `.github/workflows/tests.yml` - 后端测试工作流  
- `.github/workflows/frontend.yml` - 前端测试工作流

### 2. 技术栈

**后端:**
- Python 3.13
- uv (依赖管理)
- pytest (测试框架)
- black, isort, mypy (代码质量工具)
- safety, bandit (安全检查)

**前端:**
- Node.js 18/20
- npm (包管理)
- ESLint (代码检查)
- Prettier (代码格式化)
- TypeScript (类型检查)
- Vitest (测试框架)

## 工作流详解

### 主 CI/CD 流水线 (ci-cd.yml)

触发条件:
```yaml
on:
  push:
    branches: [ main, develop, feature/* ]
  pull_request:
    branches: [ main, develop ]
  release:
    types: [published]
```

主要阶段:
1. **变更检测** - 检测前端或后端是否有变更
2. **前端流水线** - 如果前端有变更则运行
3. **后端流水线** - 如果后端有变更则运行
4. **安全扫描** - 依赖漏洞和代码安全检查
5. **覆盖率报告** - 生成测试覆盖率报告
6. **构建** - 构建应用程序
7. **部署** - 部署到测试/生产环境

### 后端测试工作流 (tests.yml)

触发路径:
```yaml
paths:
  - 'src/**'
  - 'tests/**'
  - 'pyproject.toml'
  - 'uv.lock'
```

测试步骤:
1. 安装 uv 和 Python 3.13
2. 同步项目依赖 (`uv sync --all-extras`)
3. 安装开发依赖
4. 代码格式检查 (black, isort)
5. 类型检查 (mypy)
6. 运行所有测试 (`uv run pytest`)
7. 生成覆盖率报告

### 前端测试工作流 (frontend.yml)

触发路径:
```yaml
paths:
  - 'frontend/**'
```

测试步骤:
1. 设置 Node.js 环境 (18, 20)
2. 安装依赖 (`npm ci`)
3. ESLint 检查和自动修复
4. Prettier 格式检查和自动格式化
5. TypeScript 类型检查
6. 运行测试
7. 构建应用
8. 自动提交格式化修复 (仅在 push 时)

## 本地开发工具

### 1. 测试运行脚本

```bash
# 运行所有测试
./scripts/run_tests.sh

# 运行特定测试类型
./scripts/run_tests.sh --frontend      # 前端测试
./scripts/run_tests.sh --coverage     # 覆盖率测试
./scripts/run_tests.sh --security     # 安全检查
./scripts/run_tests.sh --no-cleanup   # 保留测试文件
```

### 2. Makefile 命令

```bash
make help          # 显示所有可用命令
make install       # 安装所有依赖
make test          # 运行所有测试
make test-backend  # 只运行后端测试
make test-frontend # 只运行前端测试
make lint          # 代码检查
make format        # 自动格式化
make security      # 安全检查
make coverage      # 覆盖率报告
make build         # 构建项目
make dev           # 启动开发服务器
make ci            # 模拟 CI 环境
make check         # 提交前快速检查
```

## 配置文件

### 后端配置 (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests",
    "ai_model: Tests requiring AI model APIs",
]

[tool.coverage.run]
source = ["src/aurawell"]
omit = ["*/tests/*", "*/venv/*", "*/__pycache__/*"]

[tool.black]
line-length = 88
target-version = ['py313']

[tool.isort]
profile = "black"
known_first_party = ["aurawell"]
```

### 前端配置

**package.json 脚本:**
```json
{
  "scripts": {
    "lint": "eslint src --ext .js,.vue,.ts",
    "lint:fix": "eslint src --ext .js,.vue,.ts --fix",
    "format": "prettier --write src/**/*.{vue,js,ts,css,scss,json}",
    "format:check": "prettier --check src/**/*.{vue,js,ts,css,scss,json}",
    "type-check": "vue-tsc --noEmit",
    "ci": "npm run lint && npm run format:check && npm run type-check && npm run test"
  }
}
```

**.prettierrc:**
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
```

## 环境变量和密钥

### GitHub Secrets 配置

在 GitHub 仓库设置中添加以下密钥:

```
OPENAI_API_KEY          # OpenAI API 密钥
ANTHROPIC_API_KEY       # Anthropic API 密钥  
GOOGLE_API_KEY          # Google API 密钥
CODECOV_TOKEN           # Codecov 上传令牌 (可选)
```

### 测试环境变量

CI 中自动创建的测试环境配置:
```bash
TESTING=true
DATABASE_URL=sqlite:///test.db
SECRET_KEY=test_secret_key_for_ci
PYTHONPATH=$GITHUB_WORKSPACE/src
```

## 部署策略

### 分支策略

- `main` - 生产分支，自动部署到生产环境
- `develop` - 开发分支，自动部署到测试环境
- `feature/*` - 功能分支，运行测试但不部署

### 部署环境

1. **测试环境 (Staging)**
   - 触发: push 到 `develop` 分支
   - 环境: `staging`
   - 需要手动批准

2. **生产环境 (Production)**
   - 触发: 发布 Release
   - 环境: `production`
   - 需要手动批准

## 故障排除

### 常见问题

1. **uv 安装失败**
   ```bash
   # 本地安装 uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **依赖安装失败**
   ```bash
   # 清理并重新安装
   uv sync --reinstall
   ```

3. **前端依赖问题**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **测试失败**
   ```bash
   # 查看详细错误信息
   uv run pytest tests/ -v --tb=long
   ```

### 调试 CI

1. 查看 GitHub Actions 日志
2. 使用 `workflow_dispatch` 手动触发工作流
3. 在本地运行 `make ci` 模拟 CI 环境

## 最佳实践

1. **提交前检查**
   ```bash
   make check  # 运行格式化、检查和测试
   ```

2. **编写测试时**
   - 为新功能添加单元测试
   - 使用适当的测试标记 (`@pytest.mark.unit`)
   - 保持测试覆盖率 > 80%

3. **代码质量**
   - 提交前运行 `make format` 
   - 解决所有 linting 警告
   - 添加类型注解

4. **前端开发**
   - 使用 ESLint 推荐规则
   - 保持 Prettier 格式一致
   - 编写 TypeScript 类型

## 监控和报告

- **测试覆盖率**: Codecov 报告
- **安全扫描**: Safety 和 Bandit 报告
- **构建状态**: GitHub Actions 徽章
- **依赖更新**: Dependabot 自动 PR

## 扩展配置

如需添加新的检查或工具:

1. 更新 `pyproject.toml` 配置
2. 修改相应的工作流文件
3. 更新 `Makefile` 和测试脚本
4. 添加文档说明
