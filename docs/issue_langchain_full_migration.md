# Issue: AuraWell 后端架构重构：全面迁移至 LangChain + RAG + MCP 统一方案

## 1. 🚀 项目重构概述

本方案提出对AuraWell健康助手后端进行一次性、彻底的架构重构，**完全移除原有的自研Agent架构**，全面迁移到以 **LangChain** 为核心的统一技术栈。此方案旨在最大化技术栈的先进性、标准化和可维护性，同时集成RAG（检索增强生成）和MCP（模型上下文协议）以构建下一代AI能力。

**核心决策：不再保留旧引擎和兼容层，一步到位切换至新架构。**

---

## 2. 🔒 核心原则：API 绝对稳定

尽管后端进行重构，但对前端的承诺坚如磐石：

-   **✅ API接口完全不变：** 所有现有 `REST API` 端点（路径、方法、参数）保持 `100%` 向后兼容。
-   **✅ 请求响应格式不变：** `JSON` 格式和字段结构完全一致。
-   **✅ 前端代码零修改：** 前端开发者无需进行任何代码改动。

---

## 3. 🎯 升级目标

-   **🔄 架构统一与现代化：** 彻底拥抱行业标准的 `LangChain` 框架，消除维护两套系统的成本和复杂性。
-   **🧠 知识驱动的智能：** 集成 `RAG` 架构，引入向量数据库和专业健康知识库，使AI建议有据可查、更加专业。
-   **🔌 无限扩展的工具生态：** 通过 `MCP` 协议，使 `AuraWell` 不仅能使用内部工具，还能发现和调用外部第三方工具，构建开放生态。
-   **📚 资产沉淀：** 构建可复用的医疗、营养、运动知识库，成为项目核心数据资产。

---

## 4. 🏗️ 新后端架构设计（统一模型）

移除兼容层和旧引擎后，架构将变得更加简洁和高效：

```mermaid
graph TD
    subgraph "API Gateway Layer (FastAPI)"
        A[POST /api/v1/chat/message]
        B[GET /api/v1/health/summary]
        C[...]
    end

    subgraph "New Agent Layer (LangChain)"
        D[LangChain Agent Executor]
        E[Tool Registry & Adapter]
        F[Conversation Memory]
    end

    subgraph "Knowledge Layer (RAG - Pluggable)"
        G[Health Knowledge RAG Chain]
        H[Vector Database]
        I[Embedding Service]
    end

    subgraph "MCP Protocol Layer (Pluggable)"
        J[MCP Client]
        K[Tool Discovery]
    end

    subgraph "Shared Data & Services"
        L[Database (SQLite/PostgreSQL)]
        M[Health Data Models (Pydantic)]
        N[Business Logic Services]
    end

    A --> D
    B --> D
    C --> D

    D -- uses --> E
    D -- uses --> F
    D -- can use --> G
    D -- can use --> J

    E -- adapts --> N
    F -- reads/writes --> L
    G -- retrieves from --> H
    H -- powered by --> I
    J -- discovers --> K

```
---

## 5. 📚 详细实施方案

### **Phase 1: LangChain 核心引擎替换 (优先级最高)**

**目标：用 LangChain Agent 完全替换原有 Agent 的核心对话和工具调用功能。**

**1.1 新增模块结构:**

```
aurawell/
├── agent/                     # 🗑️ 移除旧的 agent 模块
├── langchain_agent/           # 🆕 新的 LangChain 核心
│   ├── __init__.py
│   ├── agent.py               # 定义核心 Agent Executor
│   ├── chains/                # 定义专用的 Chain, 如 InsightChain
│   ├── memory.py              # 记忆管理
│   └── tools.py               # 工具适配和注册
├── rag/                       # 🆕 RAG模块 (Phase 2)
├── mcp/                       # 🆕 MCP模块 (Phase 3)
├── api/                       # ✅ API接口层 (仅修改调用逻辑)
│   └── v1/
│       └── endpoints/
│           └── chat.py        # 修改此文件，直接调用 LangChain Agent
└── services/                  # ✅ 业务逻辑服务 (被工具层封装)
```

**1.2 `LangChainConversationAgent` 实现:**
```python
# In aurawell/langchain_agent/agent.py
class LangChainConversationAgent:
    def __init__(self, user_id: str):
        self.llm = create_deepseek_llm()
        # 从 tools.py 加载所有适配好的工具
        self.tools = load_application_tools() 
        # 从 memory.py 创建与数据库连接的记忆模块
        self.memory = create_database_memory(user_id)
        # 创建核心 Agent Executor
        self.agent_executor = create_agent_executor(self.llm, self.tools, self.memory)

    async def a_run(self, user_message: str) -> str:
        # 这是 Agent 的统一入口
        result = await self.agent_executor.ainvoke({"input": user_message})
        return result["output"]
```

**1.3 工具系统迁移 (`LangChainToolsAdapter`):**
-   在 `aurawell/langchain_agent/tools.py` 中，定义一个 `adapt_service_to_tool` 函数。
-   此函数将 `services/` 目录下的业务逻辑函数（如 `get_sleep_data`, `analyze_nutrition`）动态包装成 `LangChain` 的 `Tool` 或 `StructuredTool`对象。
-   **核心思想：** 业务逻辑保持不变，只添加一层 `LangChain` 的"外壳"。

### **Phase 2: RAG 知识库集成（独立模块）**

**目标：为 Agent 提供外部知识检索能力，提升回复的专业性。**

**2.1 `HealthKnowledgeRAG` 实现:**
-   在 `aurawell/rag/` 中创建 `knowledge_service.py`。
-   实现一个 `HealthKnowledgeRAG` 类，内含向量数据库（推荐 `ChromaDB`）的初始化和检索方法。
-   提供一个 `as_tool()` 方法，将整个 RAG 检索功能包装成一个名为 `knowledge_search` 的 `Tool`，供 `LangChain Agent` 调用。

**2.2 知识库内容规划:**
-   **医疗知识:** 常见疾病、体检指标解读等。
-   **营养知识:** 食物成分、健康食谱、饮食禁忌等。
-   **运动知识:** 训练计划、运动康复、安全指南等。
-   **数据源:** 权威网站、医学百科、专业书籍。需要编写 `scripts/` 来处理和导入这些数据到向量数据库。

### **Phase 3: MCP 协议集成（扩展功能）**

**目标：让 Agent 能够使用外部世界通过 MCP 协议提供的工具。**

**3.1 MCP 客户端实现:**
-   在 `aurawell/mcp/` 中创建 `client.py`。
-   实现 `MCPClient` 类，负责发现和调用外部 MCP 工具服务。
-   同样，将 `discover_and_load_external_tools` 的功能封装成一个 `Tool`，允许 Agent 主动去发现新工具。

---

## 6. 🔧 技术实现细节

**依赖管理:**
创建一个 `requirements_new.txt` 或直接更新 `requirements.txt`，包含：
```
# Core
fastapi
pydantic
sqlalchemy

# LangChain Stack
langchain
langchain-openai  # 或 langchain-community, 取决于LLM实现
langsmith

# RAG Stack (optional)
chromadb
sentence-transformers
faiss-cpu

# MCP Stack (optional)
websockets
asyncio-mqtt
```

---

## 7. 📊 风险控制策略（无回退方案）

由于是完全替换，风险控制重点在于**上线前的质量保证**。

-   **功能覆盖风险：** 必须编写详尽的端到-端测试，确保新 `LangChain` 架构 `100%` 覆盖旧架构的所有功能点。
-   **性能风险：** 进行严格的基准性能测试，确保新架构在响应时间、并发能力上不弱于旧架构。
-   **数据一致性风险：** 测试必须验证，在新架构下，所有数据库的读写操作与旧架构完全一致，不会污染数据。
-   **上线策略：** 推荐采用"蓝绿部署"。先在生产环境部署新架构（绿），但不切流量。经过充分的内部测试和QA验证后，再将流量从旧架构（蓝）一键切换到新架构。

---

## 8. 🎯 验收标准

-   **API 兼容性:** Pass 所有现有的 `test_api_endpoints.py` 测试用例。
-   **功能对等性:** 对于相同的输入，新旧架构的核心业务输出（如健康建议、分析结果）在逻辑上保持一致。
-   **性能达标:** 平均响应时间不高于旧架构的 `110%`。
-   **RAG 有效性:** 当开启 `RAG` 时，针对特定知识类问题，回答的专业性和准确性有显著提升。

---
> **标签:** `enhancement`, `backend-only`, `architecture`, `langchain`, `rag`, `mcp`, `refactor`
> **里程碑:** `M3 - 后端架构升级`
> **核心承诺:** 🔒 前端零影响，API接口完全不变，业务功能完全对等。 