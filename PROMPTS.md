# AuraWell Prompt工程系统文档

## 🎯 核心设计理念

AuraWell的Prompt工程系统基于**模块化、数据驱动、持续优化**的设计理念，旨在构建世界级的AI交互体验。

### 设计原则

1. **模块化组装** - 将Prompt拆分为可复用的组件，支持灵活组合
2. **版本管理** - 每个组件都有明确的版本控制，支持A/B测试和回滚
3. **数据驱动** - 基于用户反馈和性能数据进行持续优化
4. **推理透明** - 集成CoT（思维链）和ReAct模式，提升AI推理可解释性
5. **安全第一** - 内置安全指南和免责声明，确保负责任的AI应用

## 📁 目录结构说明

```
src/aurawell/prompts/
├── system/                 # 系统级组件
│   ├── identity_v1.json   # AI身份定义
│   └── safety_v1.json     # 安全指南和免责声明
├── scenarios/              # 场景模板
│   ├── health_advice_v3_1.json    # 健康建议场景
│   ├── nutrition_planning_v1.json  # 营养规划场景
│   └── exercise_guidance_v1.json   # 运动指导场景
├── components/             # 可复用组件
│   ├── reasoning/          # 推理组件
│   │   ├── chain_of_thought.json  # CoT思维链
│   │   └── react_pattern.json     # ReAct模式
│   └── context/            # 上下文组件
│       ├── user_profile.json      # 用户画像
│       └── health_metrics.json    # 健康指标
└── formats/                # 输出格式
    ├── five_section_report.json   # 五模块报告格式
    └── structured_advice.json     # 结构化建议格式
```

### 各目录用途详解

#### 1. system/ - 系统级组件
- **用途**: 定义AI的核心身份、使命和安全边界
- **特点**: 所有场景都会加载的基础组件
- **示例**: AI身份定义、安全指南、服务条款

#### 2. scenarios/ - 场景模板
- **用途**: 特定业务场景的主要Prompt模板
- **特点**: 支持上下文变量注入，可配置推理模式
- **命名规范**: `{场景名}_{版本号}.json`

#### 3. components/ - 可复用组件
- **用途**: 跨场景复用的功能性组件
- **子目录**:
  - `reasoning/`: 推理逻辑组件（CoT、ReAct等）
  - `context/`: 上下文处理组件
- **特点**: 高度模块化，支持按需组合

#### 4. formats/ - 输出格式
- **用途**: 定义AI响应的结构化格式
- **特点**: 确保输出的一致性和可读性
- **示例**: 五模块健康建议、结构化数据报告

## 🔧 如何新增Prompt版本

### 步骤1: 创建新版本文件

```bash
# 复制现有版本作为基础
cp src/aurawell/prompts/scenarios/health_advice_v3_1.json \
   src/aurawell/prompts/scenarios/health_advice_v3_2.json
```

### 步骤2: 更新版本元数据

```json
{
  "name": "Health Advice v3.2",
  "version": "v3_2",
  "description": "新功能描述",
  "content": "...",
  "tags": ["health", "advice", "experimental"],
  "created_at": "2025-07-12",
  "author": "开发者姓名"
}
```

### 步骤3: 注册版本到数据库

```python
from src.aurawell.services.prompt_version_service import prompt_version_service

await prompt_version_service.register_prompt_version(
    scenario="health_advice",
    version="v3_2",
    name="Health Advice v3.2",
    description="新功能描述",
    author="开发者姓名",
    is_experimental=True  # 新版本建议先标记为实验性
)
```

### 步骤4: 配置A/B测试（可选）

```python
# 设置A/B测试，将10%流量分配给新版本
await prompt_version_service.setup_ab_test(
    scenario="health_advice",
    version_a="v3_1",  # 当前版本
    version_b="v3_2",  # 新版本
    traffic_split=(90.0, 10.0),  # 流量分配
    duration_days=7  # 测试持续时间
)
```

### 步骤5: 监控和优化

1. 使用PromptPlayground 2.0进行测试
2. 监控性能指标和用户反馈
3. 根据数据决定是否推广新版本

## ✅ Prompt变更评审清单

### 代码质量检查
- [ ] **JSON格式验证**: 确保所有JSON文件格式正确
- [ ] **必需字段检查**: 验证`name`、`version`、`content`字段存在
- [ ] **版本号规范**: 遵循语义化版本号规范（如v3_1, v3_2）
- [ ] **内容长度**: 确保content字段不为空且长度合理

### 功能性验证
- [ ] **变量占位符**: 检查所有`{VARIABLE}`占位符都有对应的上下文数据
- [ ] **推理组件**: 验证CoT和ReAct组件集成正确
- [ ] **安全性**: 确保包含适当的安全指南和免责声明
- [ ] **输出格式**: 验证输出格式符合预期结构

### 性能与兼容性
- [ ] **向后兼容**: 新版本不破坏现有API接口
- [ ] **性能基准**: 在PromptPlayground中测试响应时间和质量
- [ ] **多场景测试**: 在不同用户场景下验证Prompt效果
- [ ] **错误处理**: 测试异常情况下的降级处理

### 文档与流程
- [ ] **变更日志**: 更新CHANGELOG.md记录主要变更
- [ ] **版本注册**: 在数据库中正确注册新版本
- [ ] **团队通知**: 通知相关团队成员版本变更
- [ ] **监控设置**: 配置性能监控和告警

### 部署前检查
- [ ] **数据库迁移**: 如需要，准备相应的数据库迁移脚本
- [ ] **环境配置**: 验证所有环境的配置文件更新
- [ ] **回滚计划**: 准备版本回滚方案
- [ ] **监控仪表板**: 确保监控系统能够跟踪新版本

## 🔄 版本管理最佳实践

### 版本命名规范
- **主版本**: `v{major}_{minor}` (如 v3_1, v3_2)
- **实验版本**: 添加`_test`或`_exp`后缀 (如 v3_2_test)
- **热修复**: 添加`_hotfix`后缀 (如 v3_1_hotfix)

### 发布流程
1. **开发阶段**: 在`_test`版本中开发和测试
2. **A/B测试**: 小流量验证新版本效果
3. **逐步推广**: 根据数据逐步增加流量
4. **全量发布**: 性能验证通过后设为默认版本
5. **版本清理**: 定期清理过期的实验版本

### 监控指标
- **用户评分**: 平均用户满意度评分
- **响应相关性**: AI响应与用户需求的匹配度
- **工具成功率**: MCP工具调用的成功率
- **错误率**: 系统错误和异常的发生率
- **响应时间**: 从请求到响应的平均时间

## 🚨 应急处理流程

### 版本回滚
```python
# 紧急回滚到稳定版本
await prompt_version_service.setup_ab_test(
    scenario="health_advice",
    version_a="v3_0",  # 稳定版本
    version_b="v3_1",  # 问题版本
    traffic_split=(100.0, 0.0),  # 全部流量切到稳定版本
    duration_days=1
)
```

### 问题排查
1. **检查监控指标**: 查看错误率、响应时间等关键指标
2. **分析用户反馈**: 查看最近的用户评分和反馈内容
3. **日志分析**: 检查应用日志中的错误信息
4. **版本对比**: 使用PromptPlayground对比问题版本和稳定版本

## 📞 联系方式

- **技术负责人**: AuraWell开发团队
- **紧急联系**: 通过项目管理系统创建高优先级工单
- **文档维护**: 本文档由Prompt工程团队维护，如有问题请及时反馈

---

*最后更新: 2025-07-12*
*版本: v1.0*
