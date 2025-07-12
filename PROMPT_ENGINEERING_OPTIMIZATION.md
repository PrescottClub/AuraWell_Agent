# AuraWell项目 - 世界级Prompt工程优化白皮书

## 1. 核心理念：从“静态模板”到“动态智能Prompt系统”

目前，AuraWell的Prompt主要以 `.template` 文件的形式存在，这在项目初期是高效的。然而，要成为世界级的AI Agent，我们必须超越“静态模板”的思维模式，构建一个**动态、自适应、可度量、持续进化**的智能Prompt系统。

**核心转变：** 将Prompt视为与代码同等重要的核心资产，为其建立一套完整的生命周期管理（`Prompt-as-Code`）流程，涵盖设计、开发、测试、部署、监控和优化。

**最终目标：** 让Prompt系统具备自我学习和优化的能力，根据用户反馈和业务目标自动迭代，实现真正意义上的“千人千面”个性化交互。

---

## 2. 现状分析与优化目标

### 2.1 现有优势 (Strengths)

- **强大的MCP工具编排**：`.cursorrules` 定义了先进的自动化工作流，是我们的核心优势。
- **上下文感知**：能够将工具执行结果动态注入到Prompt中 (`_build_mcp_enhanced_prompt`)。
- **优秀的底层客户端**：`DeepSeekClient` 支持流式响应和Tool Calling。
- **意图分析引擎**：`IntentAnalyzer` 为场景化Prompt提供了基础。
- **调试工具雏形**：`PromptPlayground.vue` 提供了手动测试环境。

### 2.2 优化空间 (Opportunities for Improvement)

- **Prompt结构单一**：核心逻辑集中在少数几个大的模板文件中，难以维护和扩展。
- **缺乏版本控制**：无法追踪Prompt变更历史，难以进行效果对比和回滚。
- **无自动化反馈闭环**：无法根据用户真实反馈自动优化Prompt。
- **推理过程黑盒**：AI的决策过程不够透明，难以调试和建立用户信任。
- **上下文利用率低**：大量的上下文信息以非结构化方式传入，模型难以高效利用。

### 2.3 优化目标 (Key Performance Indicators)

1.  **用户满意度 (User Satisfaction)**：通过引入反馈机制，将用户满意度评分提升 **20%**。
2.  **首次回答准确率 (First-Time Accuracy)**：减少用户追问和澄清的次数，将首次回答直接解决问题的比例提升至 **95%**。
3.  **工具调用成功率 (Tool Call Success Rate)**：通过优化Prompt，将大模型自主调用MCP工具的准确率和成功率提升 **15%**。
4.  **Prompt维护效率 (Maintenance Efficiency)**：通过模块化和版本控制，将迭代和测试新Prompt的时间缩短 **50%**。

---

## 3. 详细优化方案 (The Optimization Blueprint)

### 3.1. Prompt架构重构：分层与模块化

告别巨大的 `.template` 文件，我们将构建一个分层、模块化的Prompt管理系统。

**1. 创建新的目录结构：**

在 `src/aurawell/` 下创建新目录 `prompts/`：

```
src/aurawell/prompts/
├── system/                 # 核心系统级Prompt
│   ├── identity_v1.json
│   └── safety_v1.json
├── scenarios/              # 场景化主Prompt
│   ├── health_advice_v3.1.json
│   └── nutrition_planning_v1.0.json
├── components/             # 可复用的Prompt组件
│   ├── reasoning/
│   │   ├── chain_of_thought.json
│   │   └── react_pattern.json
│   └── context/
│       ├── user_profile_structure.json
│       └── tool_results_structure.json
└── formats/                # 输出格式化指令
    ├── five_section_report.json
    └── json_output.json
```

**2. 设计`PromptManager`服务：**

创建一个 `src/aurawell/core/prompt_manager.py` 来动态组装Prompt。

```python
// src/aurawell/core/prompt_manager.py

import json
from pathlib import Path

class PromptManager:
    def __init__(self, prompts_base_path="src/aurawell/prompts"):
        self.base_path = Path(prompts_base_path)

    def _load_prompt_component(self, path: str) -> str:
        with open(self.base_path / f"{path}.json") as f:
            return json.load(f)["content"]

    def construct_prompt(self, scenario: str, version: str, context: dict) -> list:
        """Dynamically assembles a prompt from modular components."""
        
        # 1. Load System & Safety Layers
        identity = self._load_prompt_component("system/identity_v1")
        safety = self._load_prompt_component("system/safety_v1")
        
        # 2. Load Core Scenario Template
        scenario_template = self._load_prompt_component(f"scenarios/{scenario}_{version}")

        # 3. Inject Reasoning Component
        cot_reasoning = self._load_prompt_component("components/reasoning/chain_of_thought")
        system_prompt_content = f"{identity}\n{cot_reasoning}\n{safety}"
        
        # 4. Format User-facing Prompt and inject context
        user_prompt_content = scenario_template.format(**context)
        
        return [
            {"role": "system", "content": system_prompt_content},
            {"role": "user", "content": user_prompt_content}
        ]

# Usage Example:
# prompt_manager = PromptManager()
# messages = prompt_manager.construct_prompt("health_advice", "v3.1", user_context)
```

**收益**：极大地提高了Prompt的可维护性、复用性和可测试性。

### 3.2. 增强推理能力：集成CoT与ReAct模式

让AI不仅知其然，更知其所以然。

**1. 集成思维链 (Chain-of-Thought - CoT):**

在 `prompts/components/reasoning/chain_of_thought.json` 中定义：

```json
{
  "name": "Chain of Thought Reasoning",
  "content": """
## 🤔 决策推理框架 (Chain-of-Thought)
在生成任何建议前，请在内心遵循以下思考步骤，并以简洁的形式向用户展示关键推理：
1.  **数据洞察 (Data Insight)**：分析用户数据，关键指标是什么？(例如：用户近7天平均步数5200，低于目标8000)。
2.  **模式识别 (Pattern Recognition)**：数据反映了什么趋势或行为模式？(例如：工作日活跃度低，周末活跃度高)。
3.  **问题定义 (Problem Definition)**：核心问题或优化点是什么？(例如：平日久坐不动是主要健康风险)。
4.  **科学依据 (Scientific Backing)**：我的建议基于什么科学原理或研究？(例如：引用《WHO身体活动指南》)。
5.  **个性化适配 (Personalization)**：如何结合用户偏好 (如：喜欢游泳) 和限制 (如：膝盖有旧伤) 来调整建议？
6.  **方案生成 (Solution Generation)**：制定具体、可行的行动方案。
"""
}
```

**2. 引入ReAct模式 (Reason + Act):**

这完美契合AuraWell的MCP工具使用。在系统Prompt中强化指令：

```json
{
  "name": "ReAct Tool Use Pattern",
  "content": """
## 🛠️ 智能工具执行 (ReAct Pattern)
当你需要信息时，不要猜测。使用工具！
1.  **思考 (Thought)**: 我需要什么信息来回答用户问题？哪个工具能提供？
2.  **行动 (Action)**: 调用 `tool_name` with `parameters`。
3.  **观察 (Observation)**: 查看工具返回的结果。
4.  **再思考 (Thought)**: 这个结果足够了吗？我还需要调用其他工具吗？还是现在可以回答用户了？
...(重复直到可以回答)
"""
}
```

**收益**：提升AI响应的逻辑性、透明度和工具使用准确率。

### 3.3. 闭环优化：自动化反馈与自适应学习

这是方案的核心，实现系统的自我进化。

**1. 数据库扩展：**

在 `src/aurawell/database/models.py` 添加新模型：

```python
// src/aurawell/database/models.py

class PromptPerformanceLog(Base):
    __tablename__ = 'prompt_performance_logs'
    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True)
    prompt_scenario = Column(String)
    prompt_version = Column(String)
    user_rating = Column(Integer)  # 1-5
    response_relevance = Column(Float) # Model-based evaluation score
    tool_call_success = Column(Boolean)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**2. 前端集成反馈组件：**

在 `frontend/src/components/chat/ChatMessage.vue` 的每条AI消息下，添加点赞/点踩按钮。

```vue
// ChatMessage.vue
<div class="feedback-buttons">
  <button @click="submitFeedback('like')">👍</button>
  <button @click="submitFeedback('dislike')">👎</button>
</div>
```

**3. 创建`PromptOptimizer`服务：**

`src/aurawell/services/prompt_optimizer_service.py`

```python
// src/aurawell/services/prompt_optimizer_service.py
class PromptOptimizerService:
    def analyze_performance(self, scenario: str):
        """
        每晚定时任务，分析过去24小时的prompt表现
        """
        # 1. 从数据库查询指定场景的日志
        # 2. 按版本聚合数据，计算平均用户评分、成功率等
        # 3. 识别表现差的prompt版本 (e.g., v3.0的评分比v3.1低20%)
        # 4. 生成优化建议报告，或在未来自动调整参数
        report = f"Scenario {scenario}: Version v3.1 outperforms v3.0 by 20% in user satisfaction."
        return report

    def get_best_prompt_version(self, scenario: str) -> str:
        """
        动态为新会话选择表现最好的prompt版本
        """
        # 查询分析结果，返回胜出的版本号
        return "v3.1" # or from a cache/db lookup
```

**收益**：建立了一个数据驱动、自动化的质量监控和优化闭环，让Prompt质量持续提升。

### 3.4. 实施路线图 (Implementation Roadmap)

| 阶段 (Phase)      | 时间 (Timeframe) | 核心任务 (Key Tasks)                                                                                                   | 产出物 (Deliverables)                                                                 |
| ----------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **1. 基础建设**   | Sprint 1-2       | 1. 建立新的 `prompts/` 目录结构。<br>2. 实现 `PromptManager` 服务。<br>3. 将现有Prompt迁移并模块化。<br>4. 在核心场景集成CoT。   | 模块化的Prompt文件，可动态组装Prompt的核心服务。                                      |
| **2. 度量与测试** | Sprint 3-4       | 1. 在数据库中添加 `PromptPerformanceLog` 表。<br>2. 在前端添加用户反馈UI。<br>3. 实现Prompt版本控制和简单的A/B测试逻辑。   | 可度量的Prompt性能数据，支持A/B测试的后台系统。                                       |
| **3. 智能进化**   | Sprint 5-6       | 1. 开发 `PromptOptimizerService`。<br>2. 建立分析prompt性能的定时任务。<br>3. 增强 `PromptPlayground` 以支持版本对比。 | 自动化的Prompt性能分析报告，一个具备初步自适应能力的Prompt系统。                      |

---

## 4. 配套工具与流程 (Supporting Tools & Processes)

### 4.1. Prompt Playground 2.0

增强 `frontend/src/views/admin/PromptPlayground.vue`：

-   **版本选择器**：下拉选择不同的Prompt版本进行测试。
-   **并排比较 (Side-by-Side View)**：同时运行两个版本的Prompt，直观对比输出差异。
-   **性能指标展示**：显示Token用量、响应时间、工具调用详情。
-   **上下文注入**：允许粘贴JSON格式的用户上下文来模拟真实场景。

### 4.2. Prompt评审流程

-   **引入`PROMPTS.md`**：在项目根目录建立一个文档，说明核心Prompt的设计理念和演进历史。
-   **PR评审**：任何对 `prompts/` 目录的修改，都必须像代码一样经过Pull Request和至少一位同事的Review。
-   **评审清单 (Review Checklist)**：检查点包括：是否清晰、是否会导致歧义、安全性、是否符合角色设定、是否包含CoT元素等。

---

## 5. 总结

本方案通过**架构重构、推理增强、闭环优化**三大支柱，旨在将AuraWell的Prompt工程提升至行业领先水平。实施该方案将带来**更高质量的AI响应、更强的用户信任、更敏捷的迭代能力**，并为未来集成更先进的AI技术（如多模态、AI自编程）奠定坚实的基础。

这不仅是一次技术升级，更是对AuraWell核心智能的一次根本性重塑。让我们开始吧！ 