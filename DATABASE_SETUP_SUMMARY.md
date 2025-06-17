# AuraWell 数据库设置总结

## 🎯 项目概述

AuraWell 是一个**超个性化健康生活方式编排AI Agent**，具有完整的数据库系统来支持健康管理功能。

## ✅ 数据库现状

### 数据库系统已完整配置
- **数据库类型**: SQLite (支持异步操作)
- **数据库文件**: `aurawell.db` (278KB)
- **备份文件**: `aurawell.db.backup_20250613_135108`
- **连接状态**: ✅ 正常
- **数据表数量**: 17个表
- **数据库结构**: ✅ 有效

## 📊 数据库表结构

### 用户管理 (2个表)
- **user_profiles** (20列) - 用户基本信息和偏好设置
- **user_health_profiles** (8列) - 用户健康档案和医疗历史

### 健康数据 (4个表)
- **activity_summaries** (13列) - 日常活动汇总数据
- **sleep_sessions** (17列) - 睡眠记录和质量分析
- **heart_rate_samples** (11列) - 心率监测数据
- **nutrition_entries** (19列) - 营养摄入记录

### 健康计划系统 (5个表)
- **health_plans** (11列) - 健康计划主表
- **health_plan_modules** (12列) - 计划模块(饮食、运动、睡眠、心理健康)
- **health_plan_progress** (9列) - 计划执行进度跟踪
- **health_plan_feedback** (11列) - 用户反馈和调整建议
- **health_plan_templates** (14列) - 预设计划模板

### 对话系统 (3个表)
- **conversations** (8列) - 健康咨询对话会话
- **messages** (7列) - 对话消息记录
- **conversation_history** (9列) - 历史对话记录

### 其他功能 (3个表)
- **achievement_progress** (12列) - 成就系统和游戏化
- **platform_connections** (13列) - 第三方健康平台连接
- **user_sessions** (9列) - 用户会话管理

## 🛠️ 数据库管理工具

### 1. 数据库初始化脚本
```bash
python init_database.py
```
功能：
- 自动检测数据库配置
- 创建所有必要的数据表
- 验证数据库结构
- 测试数据库连接
- 创建数据库备份

### 2. 数据库管理工具
```bash
python database_manager.py <命令>
```

可用命令：
- `status` - 显示数据库状态信息
- `backup [路径]` - 备份数据库
- `reset` - 重置数据库(删除所有数据)
- `export [文件]` - 导出数据库结构
- `show <表名> [数量]` - 显示表数据
- `help` - 显示帮助信息

## 🔧 配置文件

### 环境配置 (.env)
```env
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./aurawell.db

# DeepSeek AI配置
DEEPSEEK_API_KEY=sk-0852b817bcf24dd29736a04a821bc0e4

# 应用配置
DEBUG=True
LOG_LEVEL=INFO
```

### 数据库连接配置
- **连接池**: 支持SQLite和PostgreSQL
- **异步支持**: 使用aiosqlite驱动
- **WAL模式**: 启用以提高并发性能
- **外键约束**: 已启用
- **自动备份**: 支持SQLite数据库备份

## 🚀 核心功能支持

### 1. 健康数据管理
- 多平台数据同步(小米健康、Apple Health、薄荷健康)
- 实时健康指标监测
- 数据质量评估和验证

### 2. 个性化健康计划
- 5大模块：饮食、运动、体重、睡眠、心理健康
- 多轮对话式计划制定
- 动态计划调整和优化

### 3. AI对话系统
- 健康咨询对话记录
- 上下文感知的多轮对话
- 意图识别和置信度评估

### 4. 成就系统
- 游戏化健康管理
- 进度跟踪和奖励机制
- 用户激励和习惯养成

## 📈 数据库性能优化

### 索引优化
- 用户ID索引：快速用户数据查询
- 时间索引：高效的时间序列查询
- 复合索引：优化多条件查询

### 数据完整性
- 外键约束：确保数据关联完整性
- 唯一约束：防止重复数据
- 非空约束：保证关键字段完整

### 备份策略
- 自动备份：每次重要操作前自动备份
- 时间戳备份：便于版本管理和恢复
- 增量备份：支持大数据量场景

## 🔒 安全考虑

### 数据加密
- 敏感数据字段加密存储
- 访问令牌安全存储
- 医疗历史数据加密

### 访问控制
- 用户数据隔离
- 会话管理和过期控制
- API访问限制

## 📝 使用示例

### 查看数据库状态
```bash
python database_manager.py status
```

### 备份数据库
```bash
python database_manager.py backup ./backups/backup_$(date +%Y%m%d).db
```

### 查看用户数据
```bash
python database_manager.py show user_profiles 5
```

### 导出数据库结构
```bash
python database_manager.py export schema.json
```

## 🎉 总结

AuraWell项目的数据库系统已经**完全配置完成**，具备：

✅ **完整的数据模型** - 17个表覆盖所有健康管理功能
✅ **高性能配置** - 异步操作、索引优化、连接池
✅ **管理工具齐全** - 初始化、备份、监控、维护
✅ **安全可靠** - 数据加密、访问控制、备份策略
✅ **扩展性强** - 支持多种数据库、模块化设计

数据库已准备就绪，可以支持AuraWell的所有健康管理功能！
