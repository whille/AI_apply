# CDN 调度智能 Agent 技术设计方案

> 基于 Harness Engineering 方法论的务实落地指南

---

## 一、需求分析

### 业务场景

| 需求 | 技术挑战 | Harness 要求 |
|------|----------|--------------|
| **数据获取展示** | 多源数据整合、实时性 | 工具层设计、MCP 协议 |
| **问题归因分析** | 多步推理、因果链追溯 | 三层记忆系统、可观测性 |
| **交互记忆进化 Skill** | 长期学习、能力固化 | 记忆整合 + Skill 插件体系 |
| **Git PR 工程化** | 沙箱隔离、权限控制 | 六级信任模型、审计日志 |

---

## 二、技术选型决策

### 核心结论

| 组件 | 推荐方案 | 理由 |
|------|----------|------|
| **Runtime（持久化/容错）** | **LangGraph** | 生产级、成熟、节省 80% 工作量 |
| **Harness 核心** | **自研** | 无通用方案满足 CDN 业务语义 |
| **工具层** | **MCP 协议 + 自研 CDN 工具** | 标准化，可复用生态 |
| **记忆系统** | **自研（参考三层架构）** | 通用方案太重，需业务定制 |

### 复用决策矩阵

| 能力 | 复用方案 | 自研比例 | 说明 |
|------|----------|----------|------|
| 持久化/容错 | LangGraph | 0% | 100% 复用 Checkpoints |
| 状态机/循环 | LangGraph | 10% | 90% 复用，10% 业务定制 |
| MCP 协议 | anthropic MCP SDK | 20% | 标准协议，定制 CDN 工具 |
| 向量检索 | pgvector/Qdrant | 30% | 选型后简单集成 |
| 记忆系统 | 参考 MiniHarness 设计 | 80% 自研 | 业务数据结构需定制 |
| 安全模型 | 参考 Citadel 四层路由 | 90% 自研 | CDN 权限语义不同 |
| CDN 领域工具 | 无 | 100% 自研 | 核心业务逻辑 |
| 归因分析 | 无 | 100% 自研 | 核心业务逻辑 |
| Skill 进化 | 无 | 100% 自研 | 创新能力 |

---

## 三、框架深度对比

### 3.1 LangGraph — Runtime 层首选

**位置**：https://github.com/langchain-ai/langgraph

**核心能力**：

| 特性 | 说明 |
|------|------|
| **Checkpoints** | 状态快照，支持断点续传 |
| **Threads** | 会话隔离，历史回放 |
| **流式输出** | Token 级流式 |
| **Human-in-the-loop** | 中断等待人工确认 |
| **Reducers** | 状态累积策略 |

**代码示例**：

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END

# 构建图
workflow = StateGraph(AgentState)
workflow.add_node("plan", plan_step)
workflow.add_node("execute", execute_step)
workflow.add_node("verify", verify_step)
workflow.set_entry_point("plan")

# 编译时注入持久化
graph = workflow.compile(checkpointer=MemorySaver())

# 调用时指定 thread_id
result = await graph.ainvoke(
    {"task": task},
    {"configurable": {"thread_id": "session-1"}}
)

# 恢复中断的会话
history = graph.get_state_history(config)
await graph.ainvoke(None, config)  # 从上次中断处继续
```

**推荐理由**：持久化 + 容错 + 回放 = 需要的 80% Runtime 能力

---

### 3.2 DeepAgents — Harness 参考

**位置**：https://github.com/langchain-ai/deepagents

**开箱即用能力**：

| 工具 | 功能 |
|------|------|
| `write_todos` | 任务分解与进度跟踪 |
| `read_file/write_file/edit_file` | 文件操作 |
| `execute` | Shell 执行（带沙箱） |
| `task` | 子代理委派 |

**快速启动**：

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model=init_chat_model("openai:gpt-4o"),
    tools=[my_custom_tool],
    system_prompt="..."
)
result = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
```

**评价**：
- ✅ 学习工具集设计
- ❌ 编码导向，不懂 CDN 语义
- ❌ 安全模型固定，无六级信任

---

### 3.3 Citadel — 最有价值的参考

**位置**：https://github.com/SethGammon/Citadel

**四层路由（零 Token 损耗）**：

| 层级 | 机制 | Token 消耗 |
|------|------|------------|
| Pattern Match | 正则匹配 | 0 |
| Session State | 会话状态检查 | 0 |
| Keyword Lookup | Skill 关键词 | 0 |
| LLM Classification | 结构化分析 | ~500 |

**Campaign 持久化**：

```bash
# 启动任务
/do refactor-auth-module

# 关闭笔记本，第二天恢复
/do continue
```

**Fleet 并行**：

```bash
# 隔离 worktree 并行执行
/do --fleet test-multiple-modules
```

**可借鉴点**：
- 四层路由思想
- Campaign 跨会话持久化
- Worktree 隔离（做 Git PR 需要）

**问题**：治理层、审计日志在 Roadmap 尚未实现

---

### 3.4 MiniHarness — 教学原型

**位置**：https://yeasy.gitbook.io/harness_engineering_guide

**设计目标**：

| 原则 | 说明 |
|------|------|
| 最小完整 | 包含核心概念但去复杂度 |
| 教学友好 | 代码简洁、注释充分 |
| 易于扩展 | 架构清晰 |

**项目结构**：

```
miniharness/
├── core/           # 消息、工具、Agent 接口
├── runtime/        # Agent 循环、流式处理
├── tools/          # 工具注册、执行流水线
├── memory/         # 存储、上下文组装
├── models/         # Provider 抽象
├── orchestration/  # 任务分解、多智能体协调
├── mcp/            # MCP 客户端
├── reliability/    # 日志、追踪、监控
├── security/       # 权限、护栏
└── utils/          # 配置管理
```

**与生产差距**：

| 差距 | 说明 |
|------|------|
| 推理模拟 | 内置"推理桩"而非真实模型 |
| 无优化 | 去除了生产环境复杂度 |
| 无安全 | 缺少生产级安全措施 |

**定位**：架构设计参考，不用于生产

---

### 3.5 SWE-agent / mini-swe-agent

**位置**：https://github.com/SWE-agent/SWE-agent

**核心设计**：

| 特性 | 说明 |
|------|------|
| ACI (Agent-Computer Interface) | 让 LLM 自主使用工具 |
| YAML 配置驱动 | 单文件治理 |
| 研究导向 | 简单可 Hack |

**mini-swe-agent**：

- 100 行 Python
- SWE-bench 65% 通过率
- 作者推荐作为新起点

---

### 3.6 Inngest AgentKit

**位置**：https://github.com/inngest/agentkit

**核心概念**：

| 组件 | 职责 |
|------|------|
| Agents | LLM 调用 + Prompts + Tools |
| Networks | 多 Agent 协作，共享 State |
| State | 对话历史 + 类型化状态机 |
| Routers | 决定执行流程 |

**与事件驱动的关系**：

```typescript
import { AgentKit, createTool } from "@inngest/agent-kit";

const codeAssistantAgent = new Agent({
  name: "Code Assistant",
  system: "You are a helpful coding assistant.",
  tools: [createTool({ ... })],
});
```

**特点**：故障容错依赖 Inngest 平台

---

## 四、参考架构

### 三层 Harness 架构

```
┌─────────────────────────────────────────────────────────┐
│  应用层：CDN 调度领域 Agent                               │
│  ├── 数据获取 Agent（监控、日志、配置）                    │
│  ├── 归因分析 Agent（根因定位、影响范围）                  │
│  └── Skill 进化器（交互学习、能力固化）                    │
├─────────────────────────────────────────────────────────┤
│  Harness 层（自研核心）                                   │
│  ├── 三层记忆系统（工作/短期/长期）                        │
│  ├── 六级信任模型 + 沙箱                                  │
│  └── 可观测性三支柱（日志/追踪/指标）                      │
├─────────────────────────────────────────────────────────┤
│  Runtime 层（复用成熟组件）                               │
│  ├── LangGraph（持久化状态）                              │
│  └── MCP 协议（工具标准化）                              │
├─────────────────────────────────────────────────────────┤
│  基础设施层                                              │
│  ├── Claude API / OpenAI API（模型）                      │
│  ├── pgvector / Qdrant（长期记忆）                        │
│  └── Docker + Git（工程化）                              │
└─────────────────────────────────────────────────────────┘
```

---

## 五、落地路线图

### Phase 1：LangGraph Runtime 集成（3-5 天）

**目标**：建立持久化基座

```python
# cdn_agent/runtime.py
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    task: str
    context: list
    steps: Annotated[list, operator.add]
    result: dict | None

class CDNAgentRuntime:
    def __init__(self, db_path: str = ":memory:"):
        if db_path == ":memory:":
            self.checkpointer = MemorySaver()
        else:
            self.checkpointer = SqliteSaver.from_conn_string(db_path)
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # 定义节点
        workflow.add_node("plan", self._plan_step)
        workflow.add_node("execute", self._execute_step)
        workflow.add_node("verify", self._verify_step)

        # 定义边
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "execute")
        workflow.add_edge("execute", "verify")
        workflow.add_conditional_edges(
            "verify",
            self._should_continue,
            {"continue": "plan", "end": END}
        )

        return workflow.compile(checkpointer=self.checkpointer)

    async def run(self, task: str, session_id: str = None):
        """启动新会话或继续现有会话"""
        session_id = session_id or f"cdn-{uuid4().hex[:8]}"
        config = {"configurable": {"thread_id": session_id}}

        result = await self.graph.ainvoke(
            {"task": task, "context": [], "steps": [], "result": None},
            config
        )
        return result, session_id

    async def resume(self, session_id: str, checkpoint_id: str = None):
        """恢复中断的会话"""
        config = {"configurable": {"thread_id": session_id}}
        if checkpoint_id:
            config["configurable"]["checkpoint_id"] = checkpoint_id
        return await self.graph.ainvoke(None, config)

    def get_history(self, session_id: str):
        """获取执行历史"""
        config = {"configurable": {"thread_id": session_id}}
        return list(self.graph.get_state_history(config))
```

---

### Phase 2：Harness 核心（2-3 周）

**目录结构**：

```
cdn_agent/
├── runtime/
│   └── graph.py              # LangGraph 包装
├── harness/
│   ├── agent.py              # Agent 主循环
│   ├── memory.py            # 三层记忆
│   └── trust.py             # 六级信任
├── tools/
│   ├── base.py               # 工具基类
│   ├── metrics.py           # 监控获取
│   ├── logs.py               # 日志查询
│   └── git_ops.py           # Git PR 操作
└── security/
    ├── sandbox.py           # 沙箱执行
    └── audit.py             # 审计日志
```

**核心代码 — 六级信任模型**：

```python
# cdn_agent/harness/trust.py
from enum import Enum
from dataclasses import dataclass
from typing import Callable

class TrustLevel(Enum):
    MANUAL_ONLY = 0      # 完全人工操作
    APPROVE_ALWAYS = 1   # 每步审批
    APPROVE_ONCE = 2     # 任务开始前审批
    ASK_FIRST = 3        # 关键操作前审批
    AUTO_WITH_NOTIFY = 4 # 自动执行 + 通知
    FULL_TRUST = 5       # 完全自主执行

@dataclass
class CDNTool:
    name: str
    description: str
    trust_level: TrustLevel
    executor: Callable
    requires_approval: bool = True

class TrustChecker:
    """权限检查器"""

    def __init__(self):
        self.approved_sessions = set()  # APPROVE_ONCE 已批准的会话

    def check(self, tool: CDNTool, session_id: str) -> tuple[bool, str]:
        """检查是否需要人工审批"""

        if tool.trust_level == TrustLevel.MANUAL_ONLY:
            return False, "此操作需完全人工执行"

        if tool.trust_level == TrustLevel.APPROVE_ALWAYS:
            return False, "需要每步审批"

        if tool.trust_level == TrustLevel.APPROVE_ONCE:
            if session_id in self.approved_sessions:
                return True, "已批准"
            return False, "需要任务开始前审批"

        if tool.trust_level == TrustLevel.ASK_FIRST:
            return False, "需要审批"

        if tool.trust_level == TrustLevel.AUTO_WITH_NOTIFY:
            return True, "自动执行，将发送通知"

        if tool.trust_level == TrustLevel.FULL_TRUST:
            return True, "完全自主"

        return False, "未知信任级别"

    def approve_session(self, session_id: str):
        """批准会话（APPROVE_ONCE 模式）"""
        self.approved_sessions.add(session_id)
```

**核心代码 — 三层记忆系统**：

```python
# cdn_agent/harness/memory.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json

@dataclass
class MemoryRecord:
    id: str
    type: str  # step, analysis, decision, error
    content: dict
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 0.5
    session_id: Optional[str] = None

class CDNMemory:
    """三层记忆系统"""

    def __init__(self, vector_client=None):
        self.working: list[MemoryRecord] = []      # 当前对话
        self.short_term: dict[str, list] = {}      # 会话摘要
        self.vector_client = vector_client         # 长期记忆（向量）

    async def store(self, record: MemoryRecord):
        """写入记忆 - 分层存储"""

        # 1. 工作记忆：总是写入
        self.working.append(record)

        # 2. 短期记忆：按会话存储
        if record.session_id:
            if record.session_id not in self.short_term:
                self.short_term[record.session_id] = []
            self.short_term[record.session_id].append(record)

        # 3. 长期记忆：重要性超阈值时同步
        if record.importance > 0.8 and self.vector_client:
            await self._sync_to_long_term(record)

    async def retrieve(
        self,
        query: str = None,
        session_id: str = None,
        recent_only: bool = False,
        top_k: int = 5
    ) -> list[MemoryRecord]:
        """检索记忆"""

        results = []

        # 1. 最近工作记忆
        if self.working:
            results.extend(self.working[-top_k:])

        # 2. 会话短期记忆
        if session_id and session_id in self.short_term:
            results.extend(self.short_term[session_id][-top_k:])

        # 3. 长期记忆：语义检索
        if query and self.vector_client and not recent_only:
            long_term = await self._vector_search(query, top_k)
            results.extend(long_term)

        # 去重并按重要性排序
        seen = set()
        unique = []
        for r in results:
            if r.id not in seen:
                seen.add(r.id)
                unique.append(r)

        return sorted(unique, key=lambda x: -x.importance)[:top_k]

    async def consolidate(self, session_id: str):
        """记忆整合 - 会话结束时调用"""

        if session_id not in self.short_term:
            return

        records = self.short_term[session_id]

        # 1. 生成会话摘要
        summary = await self._generate_summary(records)

        # 2. 关键发现存入长期记忆
        for record in records:
            if record.importance > 0.7:
                await self._sync_to_long_term(record)

        # 3. 清理短期记忆
        del self.short_term[session_id]

    async def _sync_to_long_term(self, record: MemoryRecord):
        """同步到长期记忆"""
        if self.vector_client:
            await self.vector_client.upsert(
                id=record.id,
                embedding=await self._embed(record.content),
                metadata=record.__dict__
            )

    async def _vector_search(self, query: str, top_k: int) -> list[MemoryRecord]:
        """向量检索"""
        if not self.vector_client:
            return []

        embedding = await self._embed(query)
        results = await self.vector_client.query(embedding, top_k)
        return [MemoryRecord(**r.metadata) for r in results]
```

---

### Phase 3：CDN 领域工具（2 周）

**工具定义**：

```python
# cdn_agent/tools/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ToolResult:
    success: bool
    data: dict
    message: str
    requires_followup: bool = False

class BaseCDNTool(ABC):
    """CDN 工具基类"""

    def __init__(self, config: dict):
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @property
    @abstractmethod
    def trust_level(self) -> TrustLevel: ...

    @property
    def parameters_schema(self) -> dict:
        return {"type": "object", "properties": {}}

    @abstractmethod
    async def execute(self, params: dict) -> ToolResult: ...
```

**具体工具实现**：

```python
# cdn_agent/tools/metrics.py
from .base import BaseCDNTool, ToolResult
from datetime import datetime, timedelta

class GetMetricsTool(BaseCDNTool):

    @property
    def name(self) -> str:
        return "get_metrics"

    @property
    def description(self) -> str:
        return "获取CDN节点监控数据，包括带宽、延迟、命中率等"

    @property
    def trust_level(self) -> TrustLevel:
        return TrustLevel.AUTO_WITH_NOTIFY

    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "node": {"type": "string", "description": "节点ID"},
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "指标列表: bandwidth, latency, hit_rate"
                },
                "time_range": {
                    "type": "string",
                    "enum": ["1h", "6h", "24h", "7d"],
                    "default": "1h"
                }
            },
            "required": ["node"]
        }

    async def execute(self, params: dict) -> ToolResult:
        node = params["node"]
        metrics = params.get("metrics", ["bandwidth", "latency"])
        time_range = params.get("time_range", "1h")

        # 调用 CDN API
        data = await self._fetch_metrics(node, metrics, time_range)

        return ToolResult(
            success=True,
            data=data,
            message=f"节点 {node} 最近 {time_range} 数据已获取"
        )

    async def _fetch_metrics(self, node, metrics, time_range):
        # 实际 CDN API 调用
        pass
```

```python
# cdn_agent/tools/analysis.py
class AnalyzeRootCauseTool(BaseCDNTool):

    @property
    def name(self) -> str:
        return "analyze_root_cause"

    @property
    def description(self) -> str:
        return "分析问题根因，定位异常原因和影响范围"

    @property
    def trust_level(self) -> TrustLevel:
        return TrustLevel.ASK_FIRST

    async def execute(self, params: dict) -> ToolResult:
        anomaly = params.get("anomaly")
        context = params.get("context", {})

        # 1. 获取相关数据
        metrics = await self._get_related_metrics(anomaly)
        logs = await self._get_related_logs(anomaly)

        # 2. 构建分析提示词
        prompt = self._build_analysis_prompt(anomaly, metrics, logs, context)

        # 3. LLM 分析
        analysis = await self.model.analyze(prompt)

        # 4. 记录归因链（高重要性）
        await self.memory.store(
            MemoryRecord(
                id=str(uuid4()),
                type="root_cause_analysis",
                content={
                    "anomaly": anomaly,
                    "cause": analysis.cause,
                    "confidence": analysis.confidence,
                    "evidence": analysis.evidence
                },
                importance=0.9
            )
        )

        return ToolResult(
            success=True,
            data=analysis.__dict__,
            message=f"分析完成，置信度 {analysis.confidence:.0%}",
            requires_followup=analysis.needs_action
        )
```

```python
# cdn_agent/tools/git_ops.py
class CreatePRTool(BaseCDNTool):

    @property
    def name(self) -> str:
        return "create_pr"

    @property
    def description(self) -> str:
        return "创建 Git PR 更新调度配置"

    @property
    def trust_level(self) -> TrustLevel:
        return TrustLevel.APPROVE_ALWAYS  # 必须审批

    async def execute(self, params: dict) -> ToolResult:
        title = params["title"]
        changes = params["changes"]
        base_branch = params.get("base", "main")

        # 1. 创建 worktree 隔离
        worktree_path = await self._create_worktree()

        # 2. 应用变更
        for file_path, content in changes.items():
            await self._apply_change(worktree_path, file_path, content)

        # 3. 提交并推送
        branch_name = f"cdn-agent/{uuid4().hex[:8]}"
        await self._commit_and_push(worktree_path, branch_name, title)

        # 4. 创建 PR
        pr_url = await self._create_pull_request(
            title=title,
            branch=branch_name,
            base=base_branch
        )

        return ToolResult(
            success=True,
            data={"pr_url": pr_url, "branch": branch_name},
            message=f"PR 已创建: {pr_url}"
        )
```

---

### Phase 4：Skill 进化机制（2 周）

```python
# cdn_agent/skills/evolver.py
from dataclasses import dataclass
from typing import Optional
import yaml

@dataclass
class SkillCandidate:
    name: str
    description: str
    trigger_patterns: list[str]
    tool_calls: list[dict]
    confidence: float

class SkillEvolver:
    """交互驱动的 Skill 进化"""

    def __init__(self, memory: CDNMemory, skill_registry):
        self.memory = memory
        self.skill_registry = skill_registry

    async def learn_from_session(self, session_id: str) -> Optional[SkillCandidate]:
        """从会话中学习"""

        # 1. 获取会话历史
        records = await self.memory.retrieve(session_id=session_id)

        # 2. 检测重复模式
        patterns = self._detect_patterns(records)
        if not patterns:
            return None

        # 3. 生成 Skill 候选
        candidate = await self._generate_skill(patterns)

        return candidate

    def _detect_patterns(self, records: list[MemoryRecord]) -> list[dict]:
        """检测重复的工具调用模式"""

        tool_sequences = []
        current_seq = []

        for record in records:
            if record.type == "step" and "tool_calls" in record.content:
                current_seq.append(record.content["tool_calls"])

                # 检测重复序列
                if len(current_seq) >= 3:
                    if self._is_repeating(current_seq):
                        tool_sequences.append(current_seq.copy())

        return tool_sequences

    async def _generate_skill(self, patterns: list[dict]) -> SkillCandidate:
        """生成 Skill 定义"""

        # 使用 LLM 总结模式
        summary = await self._summarize_patterns(patterns)

        return SkillCandidate(
            name=f"learned_{uuid4().hex[:6]}",
            description=summary["description"],
            trigger_patterns=summary["triggers"],
            tool_calls=summary["steps"],
            confidence=summary["confidence"]
        )

    async def register_skill(self, candidate: SkillCandidate) -> bool:
        """注册 Skill 到仓库"""

        skill_def = {
            "name": candidate.name,
            "description": candidate.description,
            "triggers": candidate.trigger_patterns,
            "workflow": candidate.tool_calls
        }

        # 保存到 Skill 文件
        skill_path = f"skills/{candidate.name}.yaml"
        with open(skill_path, "w") as f:
            yaml.dump(skill_def, f)

        # 注册到运行时
        self.skill_registry.register(skill_def)

        return True

# Skill 定义示例 (skills/analyze_cdn_anomaly.yaml)
"""
name: analyze_cdn_anomaly
description: 分析 CDN 节点异常，自动定位根因
triggers:
  - "节点.*异常"
  - "延迟升高"
  - "命中率下降"
workflow:
  - tool: get_metrics
    params:
      node: "{{matched_node}}"
      time_range: "1h"
  - tool: get_logs
    params:
      node: "{{matched_node}}"
      level: "error"
  - tool: analyze_root_cause
    params:
      anomaly: "{{user_input}}"
"""
```

---

### Phase 5：安全与可观测性（持续）

```python
# cdn_agent/security/sandbox.py
import docker
import tempfile
import os

class SandboxExecutor:
    """Docker 沙箱执行"""

    def __init__(self, image: str = "python:3.11-slim"):
        self.client = docker.from_env()
        self.image = image

    async def execute(self, code: str, timeout: int = 60) -> dict:
        """在沙箱中执行代码"""

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(code.encode())
            f.flush()

            try:
                container = self.client.containers.run(
                    self.image,
                    f"python {os.path.basename(f.name)}",
                    volumes={os.path.dirname(f.name): {"bind": "/tmp", "mode": "ro"}},
                    timeout=timeout,
                    remove=True
                )
                return {"success": True, "output": container}
            except Exception as e:
                return {"success": False, "error": str(e)}
            finally:
                os.unlink(f.name)
```

```python
# cdn_agent/security/audit.py
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class AuditEvent:
    event_type: str       # tool_call, approval, rejection, error
    session_id: str
    user_id: str
    action: str
    resource: str
    result: str           # allowed, denied, error
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

class AuditLogger:
    """审计日志"""

    def __init__(self, log_path: str = "logs/audit.jsonl"):
        self.log_path = log_path

    async def log(self, event: AuditEvent):
        """记录审计事件"""

        with open(self.log_path, "a") as f:
            f.write(json.dumps(event.__dict__, default=str) + "\n")

        # 同时发送到监控系统
        await self._send_to_monitoring(event)
```

---

## 六、最终项目结构

```
cdn-agent/
├── cdn_agent/
│   ├── runtime/
│   │   └── graph.py              # LangGraph 状态机构建
│   ├── harness/
│   │   ├── agent.py              # Agent 主循环
│   │   ├── memory.py             # 三层记忆系统
│   │   └── trust.py              # 六级信任模型
│   ├── tools/
│   │   ├── base.py               # 工具基类
│   │   ├── metrics.py            # 监控数据获取
│   │   ├── logs.py               # 日志查询
│   │   ├── analysis.py           # 归因分析
│   │   └── git_ops.py            # Git PR 操作
│   ├── skills/
│   │   ├── base.py               # Skill 接口
│   │   ├── evolver.py            # 学习引擎
│   │   └── *.yaml                # Skill 定义文件
│   ├── security/
│   │   ├── sandbox.py            # 沙箱执行
│   │   └── audit.py              # 审计日志
│   └── mcp/
│       └── server.py             # MCP 服务定义
├── tests/
│   ├── test_runtime.py
│   ├── test_memory.py
│   └── test_tools.py
├── skills/                       # Skill 仓库
│   └── analyze_cdn_anomaly.yaml
├── logs/
│   └── audit.jsonl
├── pyproject.toml
└── README.md
```

---

## 七、时间估算

| 阶段 | 内容 | 时间 | 依赖 |
|------|------|------|------|
| Phase 1 | LangGraph Runtime 集成 | 3-5 天 | 无 |
| Phase 2 | Harness 核心实现 | 2-3 周 | Phase 1 |
| Phase 3 | CDN 领域工具 | 2 周 | Phase 2 |
| Phase 4 | Skill 进化机制 | 2 周 | Phase 2, 3 |
| Phase 5 | 安全与可观测性 | 持续 | 全部 |

**总计**：6-10 周达到生产级可用

---

## 八、关键决策总结

### 为什么选择自研 Harness

1. **业务深度**：通用框架不懂 CDN 调度语义
2. **记忆进化**：LangChain Memory 较通用，无法满足交互学习需求
3. **工程控制**：Framework 抽象过厚，调试困难
4. **成本可控**：完全可控的模型调用，可做精细化成本优化

### 为什么复用 LangGraph Runtime

1. **成熟度高**：Checkpoints + Threads + Streaming 已验证
2. **节省时间**：80% Runtime 能力开箱即用
3. **社区活跃**：问题能快速找到解决方案
4. **可观测性**：内置 tracing 和 debugging

### MiniHarness 的价值

| 能用的 | 不能用的 |
|--------|----------|
| 架构设计思路 | 推理是模拟的 |
| 接口定义参考 | 无生产级安全 |
| 模块划分思路 | 无模型集成代码 |
| 目录结构模板 | 无容错机制 |

---

## 九、风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| LangGraph 学习曲线 | 先做 POC，花 2 天熟悉 API |
| 归因分析准确率 | 建立 golden case 测试集 |
| Skill 进化可能产生劣质 Skill | 人工审核 + 置信度阈值 |
| Git PR 安全 | APPROVE_ALWAYS + worktree 隔离 |

---

## 十、社区洞察

### 10.1 B站评论关键观点

#### Hermes Agent（349 条评论）

| 观点 | 点赞 | 性质 | 对 CDN Agent 启示 |
|------|------|------|-------------------|
| "烧token，一个任务花掉几十块钱" | 89 | 成本痛点 | 需设计成本控制策略 |
| "Skill 只是LLM总结+正则匹配危险操作" | 2 | 技术质疑 | Skill 安全机制需更完善 |
| "本地部署必须花大价钱买硬件" | 89 | 部署门槛 | 考虑云端混合部署 |

#### DeerFlow（110 条评论）

| 观点 | 点赞 | 性质 | 对 CDN Agent 启示 |
|------|------|------|-------------------|
| "Harness 定义过于宽泛" | 14 | 概念质疑 | 明确 CDN Harness 边界 |
| "很少看到有人用它做项目的案例" | 8 | 落地质疑 | 需要先做 MVP 验证 |
| "Ollama 配置报错，API 路径调错了" | 5 | 部署问题 | 文档需详细 |

#### AgentScope（51 条评论）

| 观点 | 点赞 | 性质 | 对 CDN Agent 启示 |
|------|------|------|-------------------|
| "AgentScope 和 LangGraph 谁更好用？" | 18 | 选型困惑 | 本文已做对比分析 |
| "官方教程专业" | 40 | 正面反馈 | 可参考教程设计 |

### 10.2 RSS 信息源洞察

#### OpenAI Blog 相关动态

| 文章 | 启示 |
|------|------|
| **Workspace agents** | OpenAI 官方方案与 Hermes/DeerFlow 理念相似，强调工作流自动化 + 工具连接 |
| GPT-5.5 | 新模型能力提升，Agent 推理能力增强 |
| Codex settings | 代码 Agent 配置最佳实践 |

#### Hugging Face Blog 相关动态

| 文章 | 启示 |
|------|------|
| **DeepSeek-V4** | 百万 token 上下文，Agent 可处理更长的运维日志 |
| Ecom-RLVE | Agent 验证环境设计参考 |
| Cybersecurity Openness | 开源安全模型对 CDN 安全设计有参考价值 |

### 10.3 社区共识与 divergence

| 维度 | 社区共识 | 争议点 | CDN Agent 建议 |
|------|----------|--------|----------------|
| **成本** | Agent 是 Token 消耗大户 | 值不值得投入 | 设计成本监控，按需切换模型 |
| **概念** | Harness 有价值 | 定义过于宽泛 | 明确 CDN Harness 边界 |
| **落地** | 架构设计精良 | 缺少真实案例 | 先做 MVP 验证可行性 |
| **Skill** | 能力固化方向正确 | 机制过于简单 | 结合 Hermes 自进化 + 人工审核 |

### 10.4 对 CDN Agent 的关键启示

1. **成本控制是第一优先级**
   - 评论中 89 赞均指向成本问题
   - 设计策略：主模型 + 轻量模型的分级调用

2. **Skill 进化需更完善机制**
   - 正则匹配被质疑"过于简单"
   - 建议：类型检查 + 语义验证 + 人工审核三层

3. **先做 MVP 验证落地可行性**
   - 社区反馈"缺少真实案例"
   - 建议：2-3 周内完成可演示版本

4. **参考 OpenAI Workspace agents**
   - 官方方案已验证 Agent 工作流价值
   - 设计方向正确，需补充 CDN 业务语义

---

*生成时间：2026-04-26*
*参考资源：awesome-harness-engineering, Harness Engineering Guide, B站评论, RSS 源*
