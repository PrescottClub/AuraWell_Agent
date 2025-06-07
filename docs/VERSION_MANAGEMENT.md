# AuraWell 版本管理指南

## 📋 版本管理策略

AuraWell 使用 **Git Tags** 和 **CHANGELOG.md** 来跟踪版本历史，确保每个版本的变更都有清晰的记录。

## 🏷️ 版本命名规范

### 语义化版本 (Semantic Versioning)
```
v<主版本>.<次版本>.<修订版本>[-<预发布标识>]
```

### 版本类型
- **主版本** (`v1.0.0`): 重大功能更新，可能包含破坏性变更
- **次版本** (`v1.1.0`): 新功能添加，向后兼容
- **修订版本** (`v1.1.1`): Bug修复，向后兼容

### 特殊版本
- **里程碑版本** (`v1.0.0-M1`, `v1.0.0-M2`): 阶段性功能完成
- **预发布版本** (`v1.0.0-alpha.1`, `v1.0.0-beta.1`): 测试版本
- **候选版本** (`v1.0.0-rc.1`): 发布候选版本

## 📝 变更日志 (CHANGELOG.md)

### 格式规范
基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 标准：

```markdown
## [v1.0.0-M1] - 2025-01-07

### 新增功能
- 智能工具注册中心
- 对话智能体核心

### 修复
- 修复导入错误

### 改进
- 优化异步架构

### 移除
- 移除废弃的API
```

### 变更类型
- **新增功能** (Added): 新功能
- **修复** (Fixed): Bug修复
- **改进** (Changed): 现有功能的变更
- **弃用** (Deprecated): 即将移除的功能
- **移除** (Removed): 已移除的功能
- **安全** (Security): 安全相关的修复

## 🚀 发布流程

### 1. 开发完成
```bash
# 确保所有测试通过
python examples/basic_test.py
python examples/simplified_demo.py
python examples/phase4_gamification_demo.py
```

### 2. 更新变更日志
编辑 `CHANGELOG.md`，添加新版本的变更内容。

### 3. 使用发布脚本
```bash
# 发布里程碑版本
python scripts/release.py --version v1.0.0-M1 --message "M1阶段完成"

# 发布正式版本
python scripts/release.py --version v1.0.0 --message "正式版本发布"

# 预览模式（不实际执行）
python scripts/release.py --version v1.0.0-M2 --message "M2阶段完成" --dry-run
```

### 4. 手动发布流程
如果不使用脚本，可以手动执行：

```bash
# 1. 更新版本号
# 编辑 aurawell/__init__.py 中的 __version__

# 2. 提交更改
git add .
git commit -m "chore: bump version to v1.0.0-M1"

# 3. 创建标签
git tag -a v1.0.0-M1 -m "v1.0.0-M1: M1阶段完成"

# 4. 推送到远程
git push origin HEAD
git push origin v1.0.0-M1
```

### 5. GitHub Release
在 GitHub 上创建 Release，包含：
- 版本标签
- 发布说明（从CHANGELOG.md复制）
- 重要文件（如果有）

## 📊 版本历史查看

### 查看所有标签
```bash
git tag -l
```

### 查看特定版本的变更
```bash
git show v1.0.0-M1
```

### 比较版本差异
```bash
git diff v1.0.0-M1..v1.0.0-M2
```

### 切换到特定版本
```bash
git checkout v1.0.0-M1
```

## 🔄 版本回滚

### 回滚到上一个版本
```bash
# 查看最近的标签
git describe --tags --abbrev=0

# 回滚到指定版本
git checkout v1.0.0-M1
git checkout -b hotfix/rollback-to-m1
```

## 📋 当前版本状态

### 最新版本
- **当前版本**: `v1.0.0-M1`
- **发布日期**: 2025-01-07
- **主要特性**: 智能工具注册与调用系统

### 下一个版本计划
- **目标版本**: `v1.0.0-M2`
- **预计发布**: Q1 2025
- **主要特性**: 对话智能体增强

## 🛠️ 工具和脚本

### 发布脚本
- `scripts/release.py`: 自动化版本发布
- 支持预览模式和版本验证
- 自动更新版本文件和创建标签

### 版本检查
```bash
# 检查当前版本
python -c "import aurawell; print(aurawell.__version__)"

# 检查Git标签
git describe --tags
```

## 📚 最佳实践

1. **每个功能完成后及时更新CHANGELOG**
2. **使用有意义的提交信息**
3. **在发布前进行充分测试**
4. **保持版本号的一致性**
5. **为重要版本创建GitHub Release**
6. **定期清理过期的预发布版本**

## 🔗 相关链接

- [语义化版本规范](https://semver.org/lang/zh-CN/)
- [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)
- [Git标签文档](https://git-scm.com/book/zh/v2/Git-基础-打标签)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
