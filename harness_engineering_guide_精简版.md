# Harness Engineering Guide 精简版

> 面向有 Agent 实现经验的工程师，比原书精简 70%，覆盖 80% 核心价值

---

## 第一部分：核心洞察（快速浏览）

### 四大设计原则

| 原则 | 核心思想 | 实践要点 |
|------|----------|----------|
| **约束优先** | 限制 Agent 能做什么，而非尝试让它"懂事" | 白名单工具、权限分级、路径校验 |
| **可验证性** | 每个动作必须可审计、可回放 | 结构化日志、事件溯源、快照恢复 |
| **渐进信任** | 从低权限逐步提升，而非一次性授权 | 六级信任模型、审批流 |
| **故障假设** | Agent 必然会犯错，设计容错机制 | 重试、隔离、降级、人工介入 |

### 参考架构（你已熟悉，仅列之分层）

```
┌─────────────────────────────────────┐
│  应用层：任务编排 + 多智能体协作      │
├─────────────────────────────────────┤
│  治理层：安全沙箱 + 输出校验 + 审计    │
├─────────────────────────────────────┤
│  核心层：运行时 + 工具层 + 记忆系统    │
└─────────────────────────────────────┘
```

---

## 第二部分：记忆系统设计（重点）

> 你了解概念，这里深入架构实现

### 三层记忆架构

```
┌──────────────────────────────────────────────┐
│  长期记忆（Long-term Memory）                  │
│  - 向量索引 + 语义检索                         │
│  - 生命周期：月~年                             │
│  - 容量：无限                                  │
├──────────────────────────────────────────────┤
│  短期记忆（Short-term Memory）                 │
│  - 会话摘要 + 最近执行结果                     │
│  - 生命周期：小时~周                           │
│  - 容量：有限（自动清理）                      │
├──────────────────────────────────────────────┤
│  工作记忆（Working Memory）                    │
│  - 当前对话上下文窗口                          │
│  - 生命周期：单次对话                          │
│  - 容量：受 LLM 限制                          │
└──────────────────────────────────────────────┘
```

### 关键设计：统一接口

```python
class MemoryManager:
    """写入时分层、读取时统一"""

    async def store_step(self, record: StepRecord, importance: float = 0.5) -> None:
        """短期记忆总是写入；重要性超阈值时同步长期记忆"""

    async def retrieve(
        self,
        query: str = None,     # 有 query → 向量检索
        recent_only: bool = False,  # True → 短期记忆
        top_k: int = 5
    ) -> list[StepRecord]: ...

    async def consolidate(self) -> None:
        """定期整合：压缩摘要、清理过期、更新索引"""
```

### 记忆整合策略（关键洞察）

| 策略 | 触发条件 | 效果 |
|------|----------|------|
| **摘要压缩** | 工作记忆超阈值 | LLM 生成压缩摘要，释放上下文 |
| **重要性提升** | 高频访问记录 | 自动迁移到长期记忆 |
| **过期清理** | 时间衰减 | 低重要性记录自动删除 |

**Claude Code 实践**：`autoDream` 引擎用 LLM 压缩长上下文 → 持久化到 `CLAUDE.md`

### 上下文组装引擎

```python
class ContextAssembler:
    """动态组装上下文，平衡相关性与容量"""

    def assemble(self, task: str, budget_tokens: int) -> list[Message]:
        # 1. 核心提示词（必须包含）
        # 2. 相关历史（语义检索 top-k）
        # 3. 最近对话（工作记忆切片）
        # 4. 可选工具文档（按需加载）
        ...
```

**缓存策略**：
- 工具文档缓存（不变内容）
- 历史记录缓存（压缩后）
- 提示词模板缓存

---

## 第三部分：生产级工程实践（重点）

### 提示词工程：模块化设计

```python
# ❌ 错误：单体提示词
PROMPT = "你是一个助手，需要..."

# ✅ 正确：模块化组合
class PromptTemplate:
    def __init__(self):
        self.system = SystemPrompt()      # 身份 + 角色约束
        self.constraints = ConstraintsPrompt()  # 安全边界
        self.tools = ToolsPrompt()        # 工具说明
        self.examples = FewShotPrompt()   # 示例（可选）

    def build(self, task: str) -> str:
        return self.system + self.constraints + self.tools + task
```

**缓存优化**：静态部分标记为可缓存，减少重复计算。

### 插件体系：四种类型

| 类型 | 触发方式 | 用途 |
|------|----------|------|
| **Plugin** | 显式调用 | 扩展能力（如文件操作） |
| **Skill** | `/command` | 用户快捷指令 |
| **Hook** | 事件触发 | 生命周期拦截（如 pre_tool_use） |
| **Command** | CLI | 用户界面扩展 |

```yaml
# 示例：Hook 配置
hooks:
  pre_tool_use:
    - name: validate_path
      action: reject  # 或 warn, log
  post_response:
    - name: auto_save
      action: execute
```

### 特性门控

```python
class FeatureGates:
    """运行时特性开关，支持灰度发布"""

    FEATURES = {
        "streaming_output": True,
        "auto_memory_consolidation": False,
        "multi_agent_mode": None,  # None = 用户可配置
        "experimental_tool_x": False,
    }

    def is_enabled(self, feature: str, user_config: dict = None) -> bool:
        gate = self.FEATURES.get(feature)
        if gate is None:  # 用户可配置
            return user_config.get(feature, False)
        return gate
```

**Claude Code** 有 40+ 编译时特性门控，配置驱动。

### 性能优化关键点

| 维度 | 策略 |
|------|------|
| **令牌效率** | 提示词压缩、历史摘要、工具文档精简 |
| **延迟** | 流式输出、并行工具调用、预加载 |
| **成本** | 模型分级（简单任务用小模型）、缓存复用 |

---

## 第四部分：容错与可靠性（重点）

### 可观测性三支柱

```python
# 结构化日志
@dataclass
class LogEvent:
    event_type: str      # tool_call, agent_step, error
    timestamp: datetime
    trace_id: str        # 分布式追踪
    duration_ms: int
    metadata: dict

# 分布式追踪
class TraceSpan:
    def __init__(self, name: str, parent: "TraceSpan" = None):
        self.trace_id = parent.trace_id if parent else uuid4()
        self.span_id = uuid4()
        self.parent_id = parent.span_id if parent else None
```

### 容错模式

| 模式 | 实现要点 |
|------|----------|
| **智能重试** | 指数退避 + 抖动，区分可重试错误 |
| **执行隔离** | 进程级 → 容器级隔离，故障不扩散 |
| **多轮验证** | 关键操作双重确认（LLM + 规则） |
| **降级策略** | 失败后回退到更简单/更安全的方案 |

### 幻觉防护

```python
class HallucinationGuard:
    """多层防护：输出校验 → 工具调用验证 → 结果确认"""

    def validate_output(self, output: str, context: dict) -> ValidationResult:
        # 1. 事实校验：引用是否存在？
        # 2. 格式校验：是否匹配 schema？
        # 3. 一致性校验：是否与历史矛盾？
        ...

    def validate_tool_call(self, call: ToolCall) -> ValidationResult:
        # 1. 参数类型校验
        # 2. 权限校验（危险命令拦截）
        # 3. 路径/URL 校验
        ...
```

---

## 第五部分：安全体系（重点）

### 六级信任模型

```python
class TrustLevel(Enum):
    MANUAL_ONLY = "manual_only"      # 完全人工操作
    APPROVE_ALWAYS = "approve_always"  # 每步审批
    APPROVE_ONCE = "approve_once"    # 任务开始前审批
    ASK_FIRST = "ask_first"          # 关键操作前审批
    AUTO_WITH_NOTIFY = "auto_notify"  # 自动执行 + 通知
    FULL_TRUST = "full_trust"        # 完全自主执行
```

**应用映射**：
- `DELETE *` → MANUAL_ONLY
- 生产环境部署 → APPROVE_ONCE
- 开发环境测试 → ASK_FIRST
- 日志读取 → AUTO_WITH_NOTIFY

### 沙箱四级隔离

```python
class IsolationLevel(Enum):
    NONE = "none"           # 直接执行
    PROCESS = "process"     # 进程隔离
    CONTAINER = "container" # 容器隔离（推荐）
    VM = "vm"              # 虚拟机隔离（最高安全）
```

### 工具调用护栏

```python
# 危险命令库
DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",           # 删除根目录
    r"DROP\s+TABLE",          # SQL 删除表
    r"sudo\s+",               # 提权
    r">\s*/dev/",             # 设备写入
]

# 路径校验（多层）
def validate_path(path: str, allowed_dirs: list[str]) -> bool:
    # 1. URL 解码后校验
    # 2. Unicode 归一化
    # 3. 符号链接解析后校验
    # 4. 路径穿越检测（../）
    # 5. 白名单目录匹配
    real_path = os.path.realpath(path)
    return any(real_path.startswith(d) for d in allowed_dirs)
```

### 审计日志

```python
@dataclass
class AuditEvent:
    event_type: str       # permission_check, tool_execution, approval_request
    user_id: str
    agent_id: str
    action: str
    resource: str
    result: str           # allowed, denied, error
    timestamp: datetime
    metadata: dict
```

---

## 第六部分：评估与质量保障（重点）

### 三层评估体系

| 层级 | 关注点 | 指标示例 |
|------|--------|----------|
| **步骤级** | 单个动作正确性 | 工具调用成功率、参数校验通过率 |
| **轨迹级** | 执行路径效率 | 步数、令牌消耗、时间 |
| **任务级** | 最终结果质量 | 完成率、用户满意度、错误率 |

### 端到端测试策略

```python
# 测试用例设计
@dataclass
class TestCase:
    task: str              # 用户任务
    expected_outcome: str  # 期望结果
    constraints: list[str] # 安全约束（不应违反）
    tools_allowed: list[str]  # 允许使用的工具

    def verify(self, trajectory: list[Step]) -> TestResult:
        # 1. 任务是否完成
        # 2. 约束是否违反
        # 3. 工具是否越权
        ...
```

### 基准测试对比

| 基准 | 测试类型 | 覆盖场景 |
|------|----------|----------|
| ToolBench | 工具调用 | 100+ API 集成 |
| AgentBench | 多步推理 | 复杂任务分解 |
| SafetyBench | 安全防护 | 注入、越权 |

### 持续评估

```python
class ContinuousEval:
    """生产环境持续评估"""

    METRICS = {
        "success_rate": [],      # 任务成功率
        "avg_steps": [],         # 平均步数
        "avg_tokens": [],        # 平均令牌消耗
        "error_rate": [],        # 错误率
        "timeout_rate": [],      # 超时率
    }

    def log_run(self, result: TaskResult):
        for key, value in result.metrics.items():
            self.METRICS[key].append(value)

    def report(self) -> EvalReport:
        """生成评估报告：P50/P95 统计"""
        ...
```

---

## 第七部分：任务编排（快速浏览）

### 核心职责

1. **工作流定义**：顺序/分支/并行/循环
2. **依赖管理**：构建执行 DAG
3. **智能体分配**：子任务匹配专家
4. **结果聚合**：验证 + 合并
5. **故障恢复**：重试/切换/降级

### 托管 Agent 虚拟化架构

```
┌─────────────────────────────────────┐
│  Session 层：追加式事件日志           │
│  - getEvents() 支持选择性检索         │
│  - 故障后可从 Session 恢复            │
├─────────────────────────────────────┤
│  Harness 层：无状态循环逻辑           │
│  - 从 Session 恢复上下文              │
│  - 可随时重启                         │
├─────────────────────────────────────┤
│  沙箱层：可替换执行环境               │
│  - 容器故障不影响 Session             │
└─────────────────────────────────────┘
```

---

## 第八部分：实战参考

### MiniHarness 项目结构

```
miniharness/
├── core/           # 基础接口
├── runtime/        # Agent 循环实现
├── tools/          # 工具层
├── memory/         # 记忆系统
├── models/         # 模型集成
├── orchestration/  # 任务编排
├── mcp/            # MCP 集成
├── reliability/    # 可观测性
├── security/       # 安全层
└── tests/          # 测试
```

### 生产化 Checklist

```markdown
## 提交前检查

### 可靠性
- [ ] 结构化日志覆盖
- [ ] 分布式追踪集成
- [ ] 关键路径有重试机制
- [ ] 有降级策略

### 安全
- [ ] 权限分级配置
- [ ] 危险命令拦截
- [ ] 路径白名单校验
- [ ] 审计日志记录

### 评估
- [ ] 端到端测试通过率 > 90%
- [ ] 安全约束无违反
- [ ] 持续评估指标正常
```

---

## 附录：行业参考实现

| 系统 | 特色 |
|------|------|
| **Claude Code** | 五模式权限框架、autoDream 记忆整合、40+ 特性门控 |
| **OpenAI Swarm** | 轻量多智能体编排、确定性流程 |
| **OpenClaw** | SOUL.md 行为约束、Docker 沙箱、三级权限 |
| **LangGraph** | 状态机工作流、图结构定义 |

---

## 核心洞察总结

1. **记忆系统是 Agent 的核心差异化**：三层架构 + 统一接口 + 自动整合，比纯 RAG 更高效
2. **安全是分层的**：信任等级 → 权限 → 沙箱 → 护栏，每一层独立生效
3. **可观测性是生产化的前提**：结构化日志、分布式追踪、性能指标缺一不可
4. **评估体系决定迭代速度**：三层评估 + 持续监控，才能持续改进

---

*原文档：https://yeasy.gitbook.io/harness_engineering_guide*
*精简版生成时间：2026-04-25*
