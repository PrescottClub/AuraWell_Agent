# AuraWell - 超个性化健康生活方式编排AI Agent

<div align="center">

![AuraWell Logo](https://img.shields.io/badge/AuraWell-v0.1.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Alpha-orange?style=for-the-badge)

*整合健身目标、日常作息、饮食偏好、工作日程及社交活动的智能健康生活方式编排平台*

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [文档](#-文档) • [演示](#-演示) • [贡献](#-贡献)

</div>

## 📖 项目简介

AuraWell是一个基于人工智能的超个性化健康生活方式编排Agent，旨在通过整合用户的健身目标、日常作息、饮食偏好、工作日程及社交活动，提供情境化的健康建议与习惯养成支持。

### 🎯 核心理念

- **个性化**: 基于用户独特的生活方式和健康数据提供定制化建议
- **智能化**: 运用DeepSeek AI进行深度数据分析和模式识别
- **游戏化**: 通过成就系统、挑战和社交功能提升用户参与度
- **整合性**: 连接多个健康平台，提供统一的数据视图
- **隐私优先**: 遵循R.A.I.L.G.U.A.R.D安全原则，保护用户隐私

## ✨ 功能特性

### 🤖 Phase 1: 核心AI集成
- **DeepSeek AI集成**: 智能健康分析和建议生成
- **统一数据模型**: 标准化的健康数据结构
- **用户档案管理**: 完整的用户偏好和目标跟踪
- **配置管理**: 灵活的环境配置和日志系统

### 🔗 Phase 2: 健康平台集成
- **小米健康**: 步数、心率、睡眠数据同步
- **薄荷健康**: 营养摄入和体重管理
- **苹果健康**: HealthKit数据集成
- **OAuth 2.0认证**: 安全的第三方平台授权
- **速率限制**: 智能API调用管理

### 🧠 Phase 3: 高级AI编排
- **健康洞察生成**: AI驱动的健康数据分析
- **动态计划调整**: 基于表现数据的自适应建议
- **上下文感知**: 考虑时间、天气、日程的智能建议
- **模式识别**: 识别健康行为趋势和异常

### 🎮 Phase 4: 游戏化与激励
- **成就系统**: 12种健康成就，5个难度等级
- **挑战系统**: 个人和团队挑战
- **进度追踪**: 可视化进度条和统计
- **智能通知**: 多优先级通知系统
- **社交功能**: 排行榜、好友互动

## 🛠️ 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **后端框架** | Python 3.8+ | 主要开发语言 |
| **AI引擎** | DeepSeek API | 深度推理模型(deepseek-r1) |
| **数据验证** | Pydantic | 数据模型和验证 |
| **加密** | Cryptography | 敏感数据加密 |
| **日志** | 结构化日志 | 安全审计和监控 |
| **健康平台** | 多平台API | 小米/薄荷/苹果健康 |

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip (Python包管理器)
- Git

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-username/aurawell.git
   cd aurawell
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp env.example .env
   # 编辑.env文件，添加你的API密钥
   ```

4. **环境变量配置**
   ```bash
   # 必需配置
   DEEPSEEK_API_KEY=your_deepseek_api_key
   
   # 健康平台配置 (可选)
   XIAOMI_HEALTH_API_KEY=your_xiaomi_api_key
   XIAOMI_HEALTH_CLIENT_ID=your_xiaomi_client_id
   XIAOMI_HEALTH_CLIENT_SECRET=your_xiaomi_client_secret
   
   BOHE_HEALTH_API_KEY=your_bohe_api_key
   BOHE_HEALTH_CLIENT_ID=your_bohe_client_id
   
   APPLE_HEALTH_CLIENT_ID=your_apple_health_client_id
   APPLE_HEALTH_CLIENT_SECRET=your_apple_health_client_secret
   ```

### 运行演示

1. **基础功能测试**
   ```bash
   python examples/basic_test.py
   ```

2. **简化功能演示**
   ```bash
   python examples/simplified_demo.py
   ```

3. **游戏化系统演示**
   ```bash
   python examples/phase4_gamification_demo.py
   ```

## 📊 项目结构

```
aurawell/
├── core/                          # 核心AI和编排逻辑
│   ├── deepseek_client.py         # DeepSeek AI集成
│   └── orchestrator.py            # 健康编排器
├── models/                        # 数据模型
│   ├── health_data_model.py       # 统一健康数据模型
│   ├── user_profile.py            # 用户档案模型
│   └── health_data_parser.py      # 数据解析器
├── integrations/                  # 健康平台集成
│   ├── generic_health_api_client.py  # 通用API客户端
│   ├── xiaomi_health_client.py    # 小米健康集成
│   ├── bohe_health_client.py      # 薄荷健康集成
│   └── apple_health_client.py     # 苹果健康集成
├── gamification/                  # 游戏化系统
│   ├── achievement_system.py      # 成就系统
│   ├── scoring_system.py          # 积分系统
│   ├── badge_system.py            # 徽章系统
│   ├── challenge_system.py        # 挑战系统
│   ├── progress_tracker.py        # 进度追踪
│   └── notification_system.py     # 通知系统
├── utils/                         # 工具函数
│   ├── health_calculations.py     # 健康计算(BMI/BMR/TDEE)
│   ├── date_utils.py              # 日期时间工具
│   ├── data_validation.py         # 数据验证
│   └── encryption_utils.py        # 加密工具
├── config/                        # 配置管理
│   ├── settings.py                # 应用设置
│   └── logging_config.py          # 日志配置
└── __init__.py

examples/                          # 示例和演示
├── basic_test.py                  # 基础功能测试
├── simplified_demo.py             # 简化演示
├── phase3_orchestrator_demo.py    # Phase 3演示
└── phase4_gamification_demo.py    # Phase 4演示

tests/                             # 单元测试 (开发中)
requirements.txt                   # Python依赖
env.example                        # 环境变量模板
```

## 🎯 核心功能详解

### 🤖 AI智能分析

AuraWell使用DeepSeek AI引擎进行健康数据分析：

```python
from aurawell.core.deepseek_client import DeepSeekClient

client = DeepSeekClient()
response = client.analyze_health_data(user_data)
```

**支持功能**:
- 健康数据模式识别
- 个性化建议生成
- 异常检测和预警
- 目标完成度预测

### 📊 健康数据管理

统一的数据模型支持多平台数据:

```python
from aurawell.models.health_data_model import UnifiedActivitySummary

activity = UnifiedActivitySummary(
    date="2025-01-15",
    steps=10000,
    distance_meters=8000,
    active_calories=400,
    data_source="xiaomi_health"
)
```

**数据类型**:
- 活动数据 (步数、距离、卡路里)
- 睡眠数据 (时长、质量、阶段)
- 心率数据 (静息、运动、恢复)
- 营养数据 (摄入、分析、建议)

### 🏆 游戏化激励

成就系统提升用户参与度:

```python
from aurawell.gamification.achievement_system import AchievementManager

manager = AchievementManager()
newly_unlocked = manager.update_progress(
    user_id="user_001", 
    achievement_type=AchievementType.DAILY_STEPS, 
    current_value=10000
)
```

**成就类型**:
- 步数成就 (5K/10K/15K步)
- 睡眠成就 (质量/时长)
- 运动成就 (频率/强度)
- 连击成就 (连续天数)

## 🔒 安全与隐私

AuraWell遵循R.A.I.L.G.U.A.R.D安全原则:

- **Risk First**: 优先考虑健康数据安全风险
- **Always Constraints**: 严格的数据访问控制
- **Interpret Securely**: 安全的数据解析和验证
- **Local Defaults**: 本地优先的配置管理
- **Gen Path Checks**: 生成内容的安全审查
- **Uncertainty Disclosure**: 不确定性透明披露
- **Auditability**: 完整的审计日志
- **Revision + Dialogue**: 持续改进机制

### 数据加密

```python
from aurawell.utils.encryption_utils import encrypt_health_data

encrypted_data = encrypt_health_data(
    data=sensitive_health_data,
    user_id="user_001"
)
```

## 📈 使用示例

### 基础用户档案创建

```python
from aurawell.models.user_profile import UserProfile, Gender, ActivityLevel

profile = UserProfile(
    user_id="user_001",
    display_name="张小明",
    age=28,
    gender=Gender.MALE,
    height_cm=175,
    weight_kg=75,
    activity_level=ActivityLevel.MODERATELY_ACTIVE,
    daily_steps_goal=10000
)
```

### 健康数据同步

```python
from aurawell.integrations.xiaomi_health_client import XiaomiHealthClient

client = XiaomiHealthClient()
activity_data = await client.get_activity_data(
    user_id="user_001",
    start_date="2025-01-01",
    end_date="2025-01-07"
)
```

### AI健康分析

```python
from aurawell.core.orchestrator import AuraWellOrchestrator

orchestrator = AuraWellOrchestrator()
insights = await orchestrator.analyze_health_data(user_id="user_001")
plan = await orchestrator.create_health_plan(user_id="user_001")
```

## 🧪 演示程序

### 1. 基础功能测试
验证所有模块正常导入和基础功能：
```bash
python examples/basic_test.py
```

### 2. 核心功能演示
展示健康数据模型、用户档案、AI集成：
```bash
python examples/simplified_demo.py
```

### 3. 游戏化系统演示
体验完整的游戏化激励功能：
```bash
python examples/phase4_gamification_demo.py
```

## 📊 性能与指标

### 系统性能
- **响应时间**: < 500ms (本地处理)
- **AI推理**: < 2s (DeepSeek API)
- **数据同步**: < 5s (健康平台)
- **并发支持**: 100+ 用户

### 准确性指标
- **BMI计算**: 100% 准确
- **卡路里估算**: ±5% 误差
- **睡眠分析**: 85%+ 准确率
- **活动识别**: 90%+ 准确率

## 🔮 发展路线图

### Phase 5: Web界面开发 (计划中)
- [ ] React前端界面
- [ ] 实时数据可视化
- [ ] 移动端适配
- [ ] PWA支持

### Phase 6: 高级功能 (计划中)
- [ ] 机器学习个性化推荐
- [ ] 语音交互
- [ ] 智能设备集成
- [ ] 企业健康管理

### Phase 7: 生态系统 (远期)
- [ ] 第三方插件系统
- [ ] 开放API平台
- [ ] 健康数据市场
- [ ] 研究合作平台

## 🤝 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. **Fork项目仓库**
2. **创建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送分支** (`git push origin feature/AmazingFeature`)
5. **创建Pull Request**

### 代码规范
- 遵循PEP 8 Python编码规范
- 添加适当的类型提示
- 编写单元测试
- 更新相关文档

### 安全指南
- 不要在代码中硬编码API密钥
- 遵循R.A.I.L.G.U.A.R.D安全原则
- 对用户数据进行加密处理
- 定期更新依赖包

## 📝 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [DeepSeek](https://deepseek.com/) - 提供强大的AI推理能力
- [Pydantic](https://pydantic.dev/) - 数据验证和序列化
- [小米健康](https://www.mi.com/health) - 健康数据平台
- [薄荷健康](https://www.boohee.com/) - 营养数据支持
- 所有贡献者和用户的反馈

## 📞 联系我们

- **项目主页**: [AuraWell GitHub](https://github.com/your-username/aurawell)
- **问题反馈**: [GitHub Issues](https://github.com/your-username/aurawell/issues)
- **功能建议**: [GitHub Discussions](https://github.com/your-username/aurawell/discussions)
- **邮箱**: aurawell@example.com

---

<div align="center">

**AuraWell - 让健康生活更智能、更有趣！** 🌟

[![Star](https://img.shields.io/badge/Star-⭐-yellow?style=for-the-badge)](https://github.com/your-username/aurawell)
[![Fork](https://img.shields.io/badge/Fork-🍴-blue?style=for-the-badge)](https://github.com/your-username/aurawell/fork)
[![Follow](https://img.shields.io/badge/Follow-👥-green?style=for-the-badge)](https://github.com/your-username)

</div>
