# AuraWell 变更日志

本文档记录了AuraWell项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 计划中
- FastAPI REST API实现
- 对话记忆管理系统
- 意图识别优化
- 完整的单元测试覆盖

## [v1.0.0-M1] - 2025-06-07

### 🎉 M1阶段：智能工具注册与调用系统

#### 新增功能
- **智能工具注册中心** (`aurawell/agent/tools_registry.py`)
  - HealthToolsRegistry 完整实现
  - 支持动态工具注册和管理
  - OpenAI Function Calling 完全兼容的schema定义

- **健康工具函数集** (`aurawell/agent/health_tools.py`)
  - 5个核心健康操作工具
  - 完全异步支持 (async/await)
  - 基于现有orchestrator_v2.py封装

- **对话智能体核心** (`aurawell/agent/conversation_agent.py`)
  - ConversationAgent 完整的AI对话管理
  - 支持真实AI交互和演示模式
  - 完整的工具调用执行流程
  - 优雅的错误处理和降级机制

- **命令行界面** (`aurawell/interfaces/cli_interface.py`)
  - 功能完整的交互式CLI
  - 支持连续对话
  - 异步架构支持
  - 跨平台兼容性 (Windows/Linux/macOS)

#### 架构改进
- **新增模块结构**:
  - `aurawell/agent/` - 智能体核心功能
  - `aurawell/interfaces/` - 用户交互接口
  - `aurawell/conversation/` - 对话管理 (占位符)

#### 技术特性
- 完全异步架构 (async/await)
- OpenAI Function Calling 兼容
- 演示模式支持 (无API密钥时)
- 优雅的异常处理
- 结构化日志记录

#### 使用方式
```bash
# 启动智能对话助手CLI
python -m aurawell.interfaces.cli_interface

# 配置API密钥（可选）
# 在 .env 文件中设置：DEEPSEEK_API_KEY=your_api_key_here
```

#### 验证测试
- ✅ 所有模块导入正常
- ✅ 基础功能演示正常  
- ✅ 游戏化系统演示正常
- ✅ 前端开发环境正常
- ✅ CLI界面工作正常

## [v0.3.0] - 2025-06-06

### 新增功能
- Vue 3 + Vite前端框架集成
- 现代化前端开发环境

### 修复
- 重大bug和代码质量问题
- 数据模型验证逻辑重构
- urllib3兼容性问题
- 测试框架和断言逻辑完善

### 改进
- 统一代码格式和风格
- 添加数据验证工具模块

## [v0.2.0] - 2025-06-05

### 架构改进
- 简化项目架构，移除微服务相关组件
- 修复循环导入和枚举重复定义问题

### 新增功能
- 完善游戏化成就系统
- 18种健康成就，5个难度等级

### 代码质量
- 增强类型注解
- 改进错误处理
- 完善文档

## [v0.1.0] - 2025-01-15

### 初始版本
- 🚀 项目初始版本
- 基础AI集成和健康平台连接
- 核心数据模型和用户档案系统
- DeepSeek AI集成 (支持deepseek-r1推理模型)
- 统一健康数据模型
- 小米健康/薄荷健康/苹果健康API客户端
- 游戏化成就系统基础框架

---

## 版本说明

### 版本命名规范
- **v1.x.x**: 主要版本，包含重大功能更新
- **v1.x.x-M1/M2**: 里程碑版本，阶段性功能完成
- **v1.x.x-alpha/beta**: 预发布版本

### 发布流程
1. 功能开发完成
2. 测试验证通过
3. 更新CHANGELOG.md
4. 创建Git tag
5. 发布GitHub Release
6. 更新文档

### 下一个版本计划
- **v1.0.0-M2**: 对话智能体增强
  - 完善AI交互和意图识别
  - 添加对话记忆管理
  - 实现FastAPI REST API
  - 扩展更多健康工具
