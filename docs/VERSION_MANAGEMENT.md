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
- **当前版本**: `v0.5.0`
- **发布日期**: 2025-06-09
- **主要特性**: 后端API标准化和性能优化

### 下一个版本计划
- **目标版本**: `v0.6.0`
- **预计发布**: Q1 2025
- **主要特性**: 前端界面完善和用户体验优化

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

## 📈 版本历史

### v0.5.0 (2025-06-09)
**主要更新：后端API标准化和性能优化**

#### 新增功能
- ✅ 统一API响应格式标准化（BaseResponse, SuccessResponse, ErrorResponse）
- ✅ 70+业务错误码系统，分类清晰的错误处理
- ✅ 集中式异常处理中间件，统一错误响应
- ✅ 请求追踪ID和时间戳，便于调试和监控
- ✅ 强化数据验证（密码强度、用户名格式、跨字段验证）
- ✅ 完整分页系统（PaginationParams, PaginationMeta, 排序过滤）
- ✅ 批量操作功能（健康目标批量管理）
- ✅ Redis缓存系统，支持自动降级
- ✅ 异步任务处理系统，后台任务管理
- ✅ 性能监控和指标收集系统

#### 技术架构
- ✅ 泛型响应模型，类型安全的API设计
- ✅ 多层验证体系（字段验证、业务逻辑验证、跨字段验证）
- ✅ 灵活的查询系统（分页、排序、过滤、搜索）
- ✅ 缓存装饰器，针对不同数据类型的缓存策略
- ✅ 连接池和查询优化工具
- ✅ 请求性能监控，慢请求检测

#### API改进
- ✅ 新增分页健康目标端点，支持完整查询功能
- ✅ 批量健康目标操作端点
- ✅ 系统性能监控端点
- ✅ 统一的错误响应格式
- ✅ 详细的API文档和参数描述

#### 开发体验
- ✅ 完善的测试套件，验证新响应格式
- ✅ 性能基准测试，确保<2s响应时间
- ✅ 代码质量提升，遵循最佳实践
- ✅ 详细的开发文档和使用指南

### v0.4.0 (2025-06-07)
**主要更新：SQLAlchemy数据库集成**

#### 新增功能
- ✅ 集成SQLAlchemy 2.0+ 异步ORM数据库层
- ✅ 实现Repository模式数据访问层
- ✅ 添加数据库迁移和初始化工具
- ✅ 支持SQLite和PostgreSQL数据库
- ✅ 完整的数据持久化：用户档案、健康数据、成就系统
- ✅ 数据库服务层和事务管理
- ✅ 全面的数据库集成测试套件

#### 技术架构
- ✅ 7个核心数据表设计和ORM模型
- ✅ 异步数据库操作和连接池管理
- ✅ Repository模式和服务层抽象
- ✅ 完整的CRUD操作和复杂查询支持
- ✅ 数据库健康检查和监控工具

#### 开发工具
- ✅ 数据库初始化脚本 (init_database.py)
- ✅ 完整的集成测试套件
- ✅ 数据库迁移和模式验证工具
- ✅ 详细的技术文档和使用指南

### v0.3.0 (2025-06-06)
**主要更新：前端框架集成与代码质量提升**

#### 新增功能
- ✅ 集成Vue 3 + Vite前端框架
- ✅ 添加现代化的前端开发环境
- ✅ 实现前后端分离架构

#### Bug修复
- ✅ 修复ConversationAgent演示模式bug
- ✅ 解决urllib3版本兼容性问题
- ✅ 修复数据模型验证逻辑错误
- ✅ 统一代码格式和风格

#### 技术改进
- ✅ 重构测试框架，提升断言逻辑
- ✅ 添加数据验证工具模块
- ✅ 完善错误处理机制
- ✅ 优化项目结构和文档

### v0.2.0 (2025-06-05)
**主要更新：智能工具注册与调用系统**

#### 新增功能
- ✅ 智能工具注册中心 (HealthToolsRegistry)
- ✅ 5个核心健康操作工具
- ✅ 对话智能体核心 (ConversationAgent)
- ✅ 命令行界面 (CLI)
- ✅ OpenAI Function Calling兼容

#### 技术架构
- ✅ 完全异步的工具调用系统
- ✅ 动态工具注册和发现机制
- ✅ 自然语言到工具调用的映射
- ✅ 演示模式和真实AI模式支持

### v0.1.0 (2025-06-04)
**初始版本：基础架构和数据模型**

#### 基础功能
- ✅ 核心数据模型 (Pydantic)
- ✅ 健康数据解析器
- ✅ 基础配置管理
- ✅ 项目结构搭建
