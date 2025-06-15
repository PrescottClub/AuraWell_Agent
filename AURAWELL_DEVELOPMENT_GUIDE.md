# AuraWell 健康AI Agent 项目开发完整指南

## 📋 项目概览

**AuraWell** 是一个超个性化健康生活方式编排AI Agent，整合健身目标、日常作息、饮食偏好、工作日程及社交活动，提供情境化建议与习惯养成支持。

### 🎯 核心功能模块
- **健康建议生成系统** (五模块：饮食、运动、体重、睡眠、心理)
- **用户档案管理系统** (UserProfileLookup工具链)
- **健康指标计算系统** (CalcMetrics工具链)
- **知识检索系统** (SearchKnowledge工具链)
- **MCP智能自动化系统** (13个MCP服务器协作)

---

## 🚀 Phase 1: 项目检查评估 (CRITICAL - 已开始)

### ✅ 已完成的检查项目

#### 1.1 语法错误修复 ✅
- **问题**: `aurawell/langchain_agent/agent.py` 存在缩进错误
- **解决**: 已修复第101行、108行和141行的缩进问题
- **状态**: ✅ 完成，语法检查通过

#### 1.2 核心架构分析 ✅
```
项目结构:
aurawell/
├── langchain_agent/          # LangChain集成层
│   ├── agent.py             # ✅ 健康建议Agent (已修复)
│   ├── services/            # 服务层
│   │   ├── health_advice_service.py  # ✅ 核心服务
│   │   └── parsers.py       # ✅ 五模块解析器
│   ├── tools/               # 工具层
│   │   └── health_advice_tool.py     # ✅ LangChain工具适配
│   └── templates/           # 提示词模板
├── core/                    # 核心组件
├── models/                  # 数据模型
├── database/                # 数据库层
├── integrations/            # 外部集成
└── interfaces/              # API接口
```

### 🔍 待完成的检查项目

#### 1.3 依赖问题检查
```bash
# 执行命令检查依赖
python -c "import aurawell; print('✅ 主模块导入成功')"
python -m pytest aurawell/langchain_agent/test_health_advice.py -v
```

**发现的警告**:
- Pydantic v2 迁移警告 (PydanticDeprecatedSince20)
- FastAPI on_event 过时API警告

#### 1.4 功能完整性评估
- [ ] 健康建议生成端到端测试
- [ ] 用户档案CRUD操作测试  
- [ ] 健康指标计算准确性验证
- [ ] DeepSeek API集成测试
- [ ] 数据库连接和查询测试

#### 1.5 性能瓶颈识别
- [ ] 数据库查询优化分析
- [ ] API响应时间评估
- [ ] 内存使用情况检查
- [ ] 并发处理能力测试

#### 1.6 安全性审查
- [ ] API密钥管理检查
- [ ] 数据加密验证
- [ ] 输入验证和注入防护
- [ ] 权限控制机制

---

## 🔧 Phase 2: 核心问题修复 (URGENT)

### 2.1 Pydantic v2 兼容性修复
**优先级**: 🔴 HIGH

```python
# 需要更新的文件和问题:
# 1. aurawell/models/*.py - 使用 ConfigDict 替代 class Config
# 2. aurawell/langchain_agent/services/parsers.py - 更新Pydantic模型

# 修复示例:
from pydantic import BaseModel, ConfigDict

class HealthAdviceSection(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    # 原来的 class Config 需要替换
```

### 2.2 FastAPI 生命周期事件更新
**优先级**: 🟡 MEDIUM

```python
# 需要更新 aurawell/interfaces/api_interface.py
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup 逻辑
    yield
    # shutdown 逻辑

app = FastAPI(lifespan=lifespan)
# 替代 @app.on_event("startup") 和 @app.on_event("shutdown")
```

### 2.3 导入循环依赖解决
**优先级**: 🟡 MEDIUM

```python
# 分析和修复模块间循环导入
# 重点检查:
# - aurawell/__init__.py
# - aurawell/langchain_agent/__init__.py
# - aurawell/interfaces/__init__.py
```

### 2.4 数据库连接池优化
**优先级**: 🟡 MEDIUM

```python
# 检查 aurawell/database/connection.py
# 确保连接池配置合理，避免连接泄漏
```

---

## ⚡ Phase 3: 功能开发完善 (DEVELOPMENT)

### 3.1 健康建议系统增强 🎯
**负责模块**: `langchain_agent/services/health_advice_service.py`

#### A. 五模块解析器完善
```python
# TODO: 增强 FiveSectionParser 类
class FiveSectionParser:
    def __init__(self):
        self.section_validators = {
            'diet': self._validate_diet_section,
            'exercise': self._validate_exercise_section,
            'weight': self._validate_weight_section,
            'sleep': self._validate_sleep_section,
            'mental_health': self._validate_mental_health_section
        }
    
    def _validate_diet_section(self, content: str) -> bool:
        # 验证饮食建议包含必要元素
        required_elements = ['热量', '营养素', '食材', '时间安排']
        return all(elem in content for elem in required_elements)
```

#### B. 个性化算法优化
```python
# TODO: 增强个性化推荐算法
class PersonalizationEngine:
    def calculate_nutrition_needs(self, user_profile, health_metrics):
        # 基于BMR/TDEE计算精确营养需求
        pass
    
    def generate_exercise_plan(self, fitness_level, goals, constraints):
        # 生成循序渐进的运动计划
        pass
```

### 3.2 用户档案管理系统 👤
**负责模块**: `repositories/user_repository.py`

#### A. 用户画像构建
```python
# TODO: 实现用户健康画像系统
class HealthProfileBuilder:
    async def build_comprehensive_profile(self, user_id: str):
        # 整合多数据源构建完整用户画像
        profile = await self._get_basic_profile(user_id)
        health_data = await self._get_health_history(user_id)
        preferences = await self._get_user_preferences(user_id)
        return self._merge_profile_data(profile, health_data, preferences)
```

#### B. 偏好学习系统
```python
# TODO: 实现用户偏好学习
class PreferenceLearning:
    def learn_from_feedback(self, user_id: str, advice_id: str, rating: int):
        # 从用户反馈中学习偏好
        pass
```

### 3.3 数据集成API系统 🔗
**负责模块**: `integrations/`

#### A. 健康平台集成完善
```python
# TODO: 完善三大健康平台集成
# 1. 小米健康API - xiaomi_health_client.py
# 2. 苹果健康HealthKit - apple_health_client.py  
# 3. 薄荷健康API - bohe_health_client.py

class HealthDataIntegrator:
    async def sync_all_platforms(self, user_id: str):
        # 同步所有平台数据
        xiaomi_data = await self.sync_xiaomi_data(user_id)
        apple_data = await self.sync_apple_data(user_id)
        bohe_data = await self.sync_bohe_data(user_id)
        return self._merge_health_data(xiaomi_data, apple_data, bohe_data)
```

### 3.4 MCP工具集成系统 🤖
**优先级**: 🔴 HIGH (核心功能)

#### A. 13个MCP服务器自动协作
```bash
# 已配置的MCP工具:
1. database-sqlite      # ✅ 数据库查询
2. brave-search        # ✅ 搜索最新信息  
3. memory              # ✅ 用户画像存储
4. sequential-thinking # ✅ 深度分析
5. quickchart         # ✅ 数据可视化
6. calculator         # ✅ 健康指标计算
7. fetch              # ✅ 内容抓取
8. time               # ✅ 时间管理
9. weather            # ✅ 运动环境
10. run-python        # ✅ 代码执行
11. filesystem        # ✅ 文件管理
12. github            # ✅ 代码协作
13. notion            # ✅ 文档管理

# TODO: 实现智能工作流触发器
class MCPWorkflowManager:
    def __init__(self):
        self.triggers = {
            "健康分析": self._health_analysis_workflow,
            "营养规划": self._nutrition_planning_workflow, 
            "运动计划": self._exercise_planning_workflow,
            "数据可视化": self._data_visualization_workflow
        }
```

---

## 🧹 Phase 4: 代码清理优化 (CLEANUP)

### 4.1 删除冗余文件 🗑️
**已删除的文件**:
- ✅ `enhanced_parser.py` (功能已合并到parsers.py)
- ✅ `prompt_manager.py` (功能已整合)
- ✅ `test_refactored_system.py` (过时测试)
- ✅ `demo_health_advice.py` (临时演示文件)
- ✅ `test_health_advice_import.py` (临时测试)

**需要检查清理的文件**:
```bash
# 查找可能的冗余文件
find . -name "*.py" -path "*/test_*" -o -name "*_backup.py" -o -name "*_old.py"
find . -name "*.pyc" -o -name "__pycache__" -exec rm -rf {} +
```

### 4.2 统一编码规范 📝
```python
# 应用Black代码格式化
black aurawell/ --line-length=88 --target-version py312

# 应用flake8检查
flake8 aurawell/ --max-line-length=88 --ignore=E203,W503

# 应用mypy类型检查  
mypy aurawell/ --ignore-missing-imports
```

### 4.3 优化项目结构 📁
```
建议的目录结构优化:
aurawell/
├── core/              # 核心逻辑
│   ├── agents/        # AI代理 (从 langchain_agent 移过来)
│   ├── services/      # 业务服务
│   └── engines/       # 计算引擎
├── data/              # 数据层  
│   ├── models/        # 数据模型
│   ├── repositories/  # 数据仓库
│   └── database/      # 数据库配置
├── integrations/      # 外部集成
├── api/               # API层 (从 interfaces 重命名)
└── utils/             # 工具函数
```

### 4.4 文档更新 📚
```markdown
# 需要更新的文档:
1. README.md - 更新安装和使用说明
2. API文档 - 生成Swagger/OpenAPI文档  
3. 开发文档 - 架构设计和开发规范
4. 部署文档 - Docker和云部署指南
```

---

## ✅ Phase 5: 质量保证测试 (TESTING)

### 5.1 单元测试 🧪
```python
# 测试覆盖率目标: > 80%
pytest aurawell/ --cov=aurawell --cov-report=html

# 关键测试用例:
1. HealthAdviceService.generate_comprehensive_advice()
2. FiveSectionParser.parse_and_validate() 
3. UserRepository CRUD操作
4. 健康指标计算函数
5. MCP工具集成
```

### 5.2 集成测试 🔗
```python
# 端到端测试场景:
1. 新用户注册 -> 档案创建 -> 首次健康建议生成
2. 数据同步 -> 分析处理 -> 个性化建议更新
3. 多平台数据整合 -> 统一健康报告生成
4. MCP工具链协作 -> 完整工作流执行
```

### 5.3 API测试 🌐
```python
# 使用 test_api_endpoints.py 进行API测试
# 关键API端点:
- POST /api/v1/health-advice/generate
- GET /api/v1/users/{user_id}/profile  
- POST /api/v1/health-data/sync
- GET /api/v1/health-data/analysis
```

### 5.4 性能测试 ⚡
```python
# 性能基准:
- 健康建议生成: < 3秒
- 数据库查询: < 500ms
- API响应: < 1秒
- 并发用户: > 100

# 使用工具:
locust -f performance_test.py --host=http://localhost:8000
```

---

## 📦 Phase 6: 生产就绪部署 (DEPLOYMENT)

### 6.1 环境配置 🔧
```bash
# 生产环境变量
DEEPSEEK_API_KEY=sk-xxx
BRAVE_API_KEY=xxx
DATABASE_URL=postgresql://xxx
REDIS_URL=redis://xxx
APP_ENV=production
LOG_LEVEL=INFO
```

### 6.2 Docker容器化 🐳
```dockerfile
# Dockerfile 优化建议
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "aurawell.interfaces.api_interface:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.3 监控设置 📊
```python
# 集成监控工具:
1. Prometheus + Grafana (系统监控)
2. Sentry (错误追踪)
3. New Relic (APM性能监控)
4. ELK Stack (日志聚合)
```

### 6.4 安全加固 🔒
```python
# 安全检查清单:
- [ ] API密钥轮换机制
- [ ] 数据库连接加密  
- [ ] HTTPS强制使用
- [ ] 输入验证和SQL注入防护
- [ ] 访问日志和审计
- [ ] 备份和恢复策略
```

---

## 🎯 执行优先级矩阵

| 阶段 | 优先级 | 预估时间 | 关键程度 | 状态 |
|------|--------|----------|----------|------|
| Phase 1.3-1.6 | 🔴 HIGH | 2-3天 | CRITICAL | 待开始 |
| Phase 2.1-2.2 | 🔴 HIGH | 1-2天 | HIGH | 待开始 |
| Phase 3.4 MCP | 🔴 HIGH | 3-5天 | CRITICAL | 待开始 |
| Phase 3.1-3.3 | 🟡 MEDIUM | 5-7天 | MEDIUM | 待开始 |
| Phase 4 | 🟢 LOW | 2-3天 | LOW | 待开始 |
| Phase 5 | 🟡 MEDIUM | 3-4天 | HIGH | 待开始 |
| Phase 6 | 🟡 MEDIUM | 2-3天 | MEDIUM | 待开始 |

---

## 📋 每日开发检查清单

### 🌅 每日开始前
- [ ] 拉取最新代码: `git pull origin main`
- [ ] 检查环境变量配置
- [ ] 运行基础测试: `python -m pytest aurawell/langchain_agent/test_health_advice.py`
- [ ] 检查依赖更新: `pip list --outdated`

### 🌆 每日结束前  
- [ ] 代码格式化: `black aurawell/`
- [ ] 类型检查: `mypy aurawell/ --ignore-missing-imports`
- [ ] 运行相关测试套件
- [ ] 提交代码: `git add . && git commit -m "feat: [描述]"`
- [ ] 更新开发日志

### 🔄 每周检查
- [ ] 性能基准测试
- [ ] 依赖安全扫描
- [ ] 代码覆盖率报告
- [ ] 数据库备份验证

---

## 🎉 成功指标 (Definition of Done)

### ✅ 功能完成标准
1. **健康建议生成**: 五模块建议完整性 > 95%
2. **响应速度**: 平均生成时间 < 3秒
3. **准确性**: 健康建议科学性验证通过
4. **个性化**: 用户满意度 > 90%
5. **稳定性**: 系统可用性 > 99.5%

### ✅ 代码质量标准
1. **测试覆盖率**: > 80%
2. **代码规范**: Black + flake8 + mypy 全部通过
3. **性能指标**: 所有API响应 < 1秒
4. **安全检查**: 无高危漏洞
5. **文档完整**: API文档和开发文档齐全

---

## 🚨 风险控制

### ⚠️ 已识别的风险
1. **DeepSeek API限流**: 实现请求队列和重试机制
2. **数据库性能**: 监控查询性能，优化索引
3. **MCP工具依赖**: 实现降级和备用方案
4. **健康数据隐私**: 严格的数据加密和访问控制

### 🛡️ 风险缓解措施
1. **备用服务**: 每个关键组件都有fallback机制
2. **监控告警**: 实时监控和自动告警
3. **灾难恢复**: 定期备份和恢复演练
4. **安全审计**: 定期安全扫描和渗透测试

---

## 📞 团队协作

### 👥 角色分工
- **AI/LangChain开发**: 负责智能代理和MCP集成
- **后端开发**: 负责API和数据库
- **前端开发**: 负责Vue.js界面 (已由其他成员负责)
- **DevOps**: 负责部署和运维 (已由其他成员负责)
- **数据/内容**: 负责健康知识库 (已由其他成员负责)

### 🤝 沟通机制
- **每日站会**: 同步进度和问题
- **代码评审**: 所有PR必须经过review
- **架构讨论**: 重要设计决策集体讨论
- **问题升级**: 阻塞问题及时上报

---

## 📈 进度跟踪

使用此文档作为开发指南，按照Phase顺序执行。每完成一个Phase，更新状态并记录经验教训。

**当前状态**: ✅ Phase 1 部分完成，Phase 2 准备开始

**下一步行动**: 开始执行 Phase 1.3 依赖问题检查

---

*此文档将随着项目进展持续更新。所有团队成员都应该熟悉并遵循此指南。* 