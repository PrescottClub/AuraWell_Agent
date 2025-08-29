# GitHub Actions 本地测试指南

## 🎯 问题解决总结

### 原始问题
1. **Docker 多进程启动**: 矩阵策略导致多个并行作业
2. **Rollup 架构兼容性**: `@rollup/rollup-linux-x64-gnu` 模块缺失
3. **paths-filter 配置错误**: 缺少 base 分支配置
4. **Apple M 芯片兼容性**: 需要指定 `linux/amd64` 架构

### 解决方案

#### 1. 简化矩阵策略
```yaml
# 原来: 两个 Node.js 版本并行运行
strategy:
  matrix:
    node-version: [18, 20]

# 修改为: 本地测试只用一个版本
strategy:
  matrix:
    node-version: [20]
```

#### 2. 修复 Rollup 架构问题
- 添加 `install-rollup` npm 脚本
- 创建 `vitest.config.js` 配置文件
- 添加 `test-setup.js` 处理平台特定警告

#### 3. 修复 paths-filter 配置
```yaml
# 添加 base 分支配置
- uses: dorny/paths-filter@v2
  id: changes
  with:
    base: main  # 关键修复
    filters: |
      frontend:
        - 'frontend/**'
```

#### 4. 创建专用本地测试工作流
- `local-test.yml`: 简化的单作业测试
- `frontend-local.yml`: 前端专用测试
- 避免复杂的依赖关系

## 🚀 使用方法

### 方法一: 使用测试脚本 (推荐)
```bash
# 运行交互式测试脚本
./scripts/test_local_ci.sh
```

### 方法二: 直接使用 act 命令

#### Apple M 系列芯片 (必须指定架构):
```bash
# 简化测试
act -W ./.github/workflows/local-test.yml --container-architecture linux/amd64

# 前端测试
act -W ./.github/workflows/frontend-local.yml --container-architecture linux/amd64

# 后端测试
act -W ./.github/workflows/tests.yml --container-architecture linux/amd64
```

#### Intel 芯片:
```bash
# 可以不指定架构
act -W ./.github/workflows/local-test.yml
```

### 方法三: 测试特定作业
```bash
# 只测试前端 CI
act -W ./.github/workflows/frontend.yml -j frontend-ci --container-architecture linux/amd64

# 只测试后端
act -W ./.github/workflows/tests.yml -j backend-tests --container-architecture linux/amd64
```

## 📋 工作流文件说明

| 文件 | 用途 | 特点 |
|------|------|------|
| `ci-cd.yml` | 完整 CI/CD 流水线 | 包含所有步骤，适合生产环境 |
| `frontend.yml` | 前端测试 | 支持矩阵策略，全面的前端检查 |
| `tests.yml` | 后端测试 | Python 环境，使用 uv 包管理 |
| `local-test.yml` | 简化本地测试 | 单作业，快速验证 |
| `frontend-local.yml` | 前端本地测试 | 无矩阵策略，专门用于本地调试 |

## 🔧 故障排除

### 常见错误及解决方案

#### 1. Docker 连接超时
```bash
# 检查 Docker 是否运行
docker info

# 重启 Docker Desktop
```

#### 2. 架构兼容性问题
```bash
# Apple M 芯片必须添加
--container-architecture linux/amd64
```

#### 3. Rollup 模块缺失
```bash
# 进入前端目录手动安装
cd frontend
npm run install-rollup
```

#### 4. 网络问题
```bash
# 使用代理或更换 Docker 源
# 或者预先拉取镜像
docker pull catthehacker/ubuntu:act-latest
```

### 调试技巧

#### 1. 详细输出
```bash
act -W ./.github/workflows/local-test.yml --verbose
```

#### 2. 干运行 (检查配置不执行)
```bash
act -W ./.github/workflows/local-test.yml --dryrun
```

#### 3. 列出所有作业
```bash
act -W ./.github/workflows/ci-cd.yml --list
```

#### 4. 使用特定镜像
```bash
act -P ubuntu-latest=catthehacker/ubuntu:act-latest
```

## 📊 性能优化

### 减少 Docker 拉取时间
```bash
# 预先拉取常用镜像
docker pull catthehacker/ubuntu:act-latest
docker pull node:20
```

### 使用本地缓存
```bash
# act 会自动缓存 Docker 镜像和 npm 包
# 后续运行会更快
```

## ✅ 验证清单

- [ ] Docker Desktop 正在运行
- [ ] 使用正确的架构参数 (Apple M 芯片)
- [ ] 网络连接正常
- [ ] 前端依赖已安装 (`npm install`)
- [ ] 后端环境已配置 (`uv sync`)
- [ ] Git 仓库状态正常

---

🎉 **现在您可以在本地完美地测试 GitHub Actions 工作流了！**
