# 业务数据分析 Agent 架构设计

> 面向研发工作，智能查询、分析多数据源，自动固化常用查询为 Skill

---

## 一、需求分析

### 1.1 核心需求

| 需求 | 说明 | 优先级 |
|------|------|--------|
| 多数据源查询 | MySQL / ES / API 统一接入 | P0 |
| 业务逻辑理解 | 项目上下文、表结构、字段含义 | P0 |
| 智能分析 | 数据洞察、异常识别、趋势分析 | P1 |
| 问题归类 | 自动分类、归档、关联 | P1 |
| Skill 固化 | 常用查询自动沉淀为 Skill | P2 |
| 自我进化 | 从失败中学习，持续优化 | P2 |

### 1.2 典型场景

```
场景 1：订单查询
用户: "查询用户 12345 最近一月的订单，分析消费趋势"
Agent:
  1. 理解 → 需要查询订单表
  2. 查询 → SELECT * FROM orders WHERE user_id = 12345 AND created_at > NOW() - INTERVAL 1 MONTH
  3. 分析 → 消费频次、金额趋势、品类偏好
  4. 归类 → 用户画像标签

场景 2：问题排查
用户: "为什么订单 88888 一直显示 pending？"
Agent:
  1. 理解 → 需要查询订单状态流转
  2. 查询 → 订单详情 + 支付记录 + 物流状态
  3. 分析 → 支付回调未触发？物流未推送？
  4. 归类 → 支付问题 → 中断流程
  5. 固化 → 下次直接用此排查流程
```

---

## 二、架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                      业务数据分析 Agent                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  用户层     │  │  对话管理    │  │  结果展示    │             │
│  │  CLI/Web    │──▶│  Session    │──▶│  Report     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      核心引擎层                             │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │                                                             │ │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │   │ 意图理解    │──▶│ 任务规划    │──▶│ 工具调度    │        │ │
│  │   │ (LLM)      │  │ (Planner)   │  │ (Executor)  │        │ │
│  │   └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  │                            │                                │ │
│  └────────────────────────────┼───────────────────────────────┘ │
│                               ▼                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      工具层（MCP）                           │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │                                                             │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │ │
│  │  │ MySQL    │ │ ES       │ │ API      │ │ Cache    │      │ │
│  │  │ Adapter  │ │ Adapter  │ │ Adapter  │ │ Manager  │      │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │ │
│  │                                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                               │                                  │
│                               ▼                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      知识层                                  │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │                                                             │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │ │
│  │  │业务逻辑  │ │ 表结构   │ │ 查询模板 │ │ 问题分类 │      │ │
│  │  │KNOWLEDGE │ │ SCHEMA   │ │ TEMPLATE │ │ CATEGORY │      │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │ │
│  │                                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                               │                                  │
│                               ▼                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    进化层（借鉴 Hermes）                     │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │                                                             │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │ │
│  │  │Skill生成 │ │ 模式检测 │ │ 失败改进 │ │ 效果评估 │      │ │
│  │  │ Generator│ │ Detector │ │ Improver │ │ Evaluator│      │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │ │
│  │                                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、核心模块设计

### 3.1 核心引擎层

#### 3.1.1 意图理解

```python
class IntentParser:
    """解析用户意图，识别查询类型"""

    INTENTS = {
        "query": "数据查询",
        "analyze": "数据分析",
        "diagnose": "问题排查",
        "compare": "数据对比",
        "summarize": "数据汇总"
    }

    def parse(self, user_input: str) -> dict:
        """
        输入: "查询用户12345最近一月订单，分析消费趋势"
        输出: {
            "intent": "query+analyze",
            "entities": {"user_id": "12345", "time_range": "1 month"},
            "action": "订单查询 + 趋势分析"
        }
        """
        # LLM 解析意图
        prompt = f"""
        分析用户意图：
        用户输入：{user_input}

        可用意图类型：{self.INTENTS}

        返回 JSON：
        - intent: 意图类型
        - entities: 提取的实体
        - action: 执行动作
        """
        return self.llm.parse(prompt)
```

#### 3.1.2 任务规划

```python
class TaskPlanner:
    """将复杂任务拆解为执行序列"""

    def plan(self, intent: dict, context: dict) -> list[dict]:
        """
        输入: 意图解析结果 + 上下文
        输出: 执行计划列表
        """
        # 查询 Skills 库，是否有匹配的已有流程
        skill = self.skill_repo.find_match(intent)

        if skill:
            # 直接复用 Skill
            return skill.steps

        # 否则，动态规划
        return self._dynamic_plan(intent, context)

    def _dynamic_plan(self, intent, context) -> list[dict]:
        """
        根据意图生成执行计划

        示例输出：
        [
            {"step": 1, "action": "query_mysql", "params": {...}},
            {"step": 2, "action": "analyze_data", "params": {...}},
            {"step": 3, "action": "save_skill", "condition": "complex"}
        ]
        """
```

#### 3.1.3 工具调度

```python
class ToolExecutor:
    """执行工具调用，管理结果缓存"""

    def __init__(self):
        self.cache = CacheManager()
        self.adapters = {
            "mysql": MySQLAdapter(),
            "es": ESAdapter(),
            "api": APIAdapter()
        }

    def execute(self, plan: list[dict]) -> dict:
        """按计划执行工具调用"""
        results = []

        for step in plan:
            tool = step["action"]

            # 检查缓存
            cache_key = self._cache_key(step)
            if cached := self.cache.get(cache_key):
                results.append(cached)
                continue

            # 执行工具
            adapter = self.adapters.get(tool.split("_")[0])
            result = adapter.execute(step["params"])

            # 缓存结果
            self.cache.set(cache_key, result, ttl=300)
            results.append(result)

        return self._aggregate(results)
```

---

### 3.2 工具层（MCP）

#### 3.2.1 MySQL 适配器

```python
# mcp_adapters/mysql_adapter.py

class MySQLAdapter:
    """MySQL 数据源适配器"""

    def __init__(self, config: dict):
        self.connections = {
            "order_db": create_connection(config["order_db"]),
            "user_db": create_connection(config["user_db"]),
            # ... 更多数据库
        }
        self.schema_cache = self._load_schemas()

    def execute(self, params: dict) -> dict:
        """
        执行 SQL 查询

        params:
            database: 数据库名
            sql: SQL 语句
            explain: 是否返回执行计划
        """
        conn = self.connections[params["database"]]

        # 安全检查
        if self._is_dangerous(params["sql"]):
            raise SecurityError("危险 SQL 被拦截")

        # 执行查询
        result = conn.execute(params["sql"])

        return {
            "columns": result.keys(),
            "rows": result.fetchall(),
            "affected": result.rowcount,
            "schema": self.schema_cache.get(params["database"])
        }

    def _load_schemas(self) -> dict:
        """加载表结构信息"""
        # 从 SCHEMA.md 或数据库元信息加载
        ...
```

#### 3.2.2 ES 适配器

```python
class ESAdapter:
    """Elasticsearch 数据源适配器"""

    def execute(self, params: dict) -> dict:
        """
        执行 ES 查询

        params:
            index: 索引名
            query: DSL 查询语句
            aggs: 聚合配置
        """
        client = self._get_client(params["index"])

        response = client.search(
            index=params["index"],
            query=params.get("query"),
            aggs=params.get("aggs"),
            size=params.get("size", 100)
        )

        return {
            "hits": response["hits"]["hits"],
            "total": response["hits"]["total"]["value"],
            "aggregations": response.get("aggregations")
        }
```

#### 3.2.3 API 适配器

```python
class APIAdapter:
    """业务 API 适配器"""

    def __init__(self, api_config: dict):
        self.apis = api_config  # API 定义

    def execute(self, params: dict) -> dict:
        """
        调用业务 API

        params:
            endpoint: API 端点
            method: HTTP 方法
            data: 请求数据
        """
        api = self.apis[params["endpoint"]]

        response = requests.request(
            method=params.get("method", "GET"),
            url=api["url"],
            json=params.get("data"),
            headers=api.get("headers")
        )

        return response.json()
```

---

### 3.3 知识层

#### 3.3.1 目录结构

```
knowledge/
├── BUSINESS_LOGIC.md    # 业务逻辑说明
├── SCHEMA.md            # 表结构文档
├── TEMPLATES.md         # 查询模板库
├── CATEGORIES.md        # 问题分类规则
└── GLOSSARY.md          # 业务术语表
```

#### 3.3.2 业务逻辑文档

```markdown
# BUSINESS_LOGIC.md

## 项目：订单系统

### 核心概念

- **订单（Order）**: 用户购买行为记录
- **支付（Payment）**: 订单支付状态
- **物流（Logistics）**: 配送信息

### 状态流转

```
pending → paid → shipped → completed
    ↓        ↓
  cancelled refunded
```

### 数据源

| 数据 | 存储位置 | 说明 |
|------|----------|------|
| 订单详情 | MySQL.order_db.orders | 主订单表 |
| 订单事件 | ES.order_events | 状态变更日志 |
| 支付记录 | MySQL.payment_db.payments | 支付流水 |

### 常见查询

1. **查询订单详情**
   ```sql
   SELECT * FROM orders WHERE order_id = {order_id}
   ```

2. **查询用户订单列表**
   ```sql
   SELECT * FROM orders
   WHERE user_id = {user_id}
   ORDER BY created_at DESC
   LIMIT {limit}
   ```

3. **查询订单状态变更**
   ```
   GET /order_events/_search
   {
     "query": {
       "term": {"order_id": "{order_id}"}
     },
     "sort": [{"timestamp": "asc"}]
   }
   ```

---

## 项目：用户系统

...
```

#### 3.3.3 表结构文档

```markdown
# SCHEMA.md

## order_db.orders

| 字段 | 类型 | 说明 | 索引 |
|------|------|------|------|
| id | bigint | 主键 | PK |
| user_id | bigint | 用户ID | IDX |
| status | varchar(20) | 状态 | IDX |
| amount | decimal(10,2) | 金额 | - |
| created_at | datetime | 创建时间 | IDX |
| updated_at | datetime | 更新时间 | - |

### 状态枚举

- pending: 待支付
- paid: 已支付
- shipped: 已发货
- completed: 已完成
- cancelled: 已取消
- refunded: 已退款

---
```

#### 3.3.4 问题分类规则

```markdown
# CATEGORIES.md

## 问题分类体系

### 一级分类

| 分类 | 关键词 | 数据源 |
|------|--------|--------|
| 支付问题 | 支付、退款、回调 | payment_db |
| 订单问题 | 订单、状态、创建 | order_db |
| 物流问题 | 配送、快递、轨迹 | logistics_db |
| 用户问题 | 账号、登录、权限 | user_db |

### 二级分类

#### 支付问题
- 支付失败: 关键词 "失败"、"超时"
- 退款异常: 关键词 "退款"、"未到账"
- 回调丢失: 关键词 "回调"、"pending"

#### 订单问题
- 创建失败: 关键词 "创建"、"下单"
- 状态异常: 关键词 "卡住"、"不变"
- 数据不一致: 关键词 "不一致"、"对不上"

---
```

---

### 3.4 进化层（核心）

#### 3.4.1 Skill 自动生成

```python
# evolution/skill_generator.py

class SkillGenerator:
    """自动生成 Skill（借鉴 Hermes）"""

    def __init__(self, skill_dir: str):
        self.skill_dir = Path(skill_dir)

    def should_generate(self, transcript: dict, tool_calls: list) -> bool:
        """判断是否应该生成 Skill"""
        # 条件1：复杂任务（3+ 工具调用）
        if len(tool_calls) < 3:
            return False

        # 条件2：已有相似 Skill
        if self._find_similar(transcript):
            return False

        # 条件3：用户确认
        return self._ask_user(transcript)

    def generate(self, transcript: dict, tool_calls: list) -> dict:
        """
        从执行轨迹生成 Skill

        输入:
            transcript: 对话记录
            tool_calls: 工具调用序列

        输出:
            Skill 文件内容
        """
        skill = {
            "name": self._extract_name(transcript),
            "trigger": self._extract_trigger(transcript),
            "steps": self._extract_steps(tool_calls),
            "example": transcript["user_input"],
            "created_at": datetime.now().isoformat()
        }

        return skill

    def save(self, skill: dict) -> Path:
        """保存 Skill 文件"""
        skill_path = self.skill_dir / f"{skill['name']}.md"

        content = f"""---
name: {skill['name']}
created: {skill['created_at']}
trigger: {skill['trigger']}
---

# {skill['name']}

## 触发条件

{skill['trigger']}

## 执行步骤

"""
        for i, step in enumerate(skill['steps'], 1):
            content += f"{i}. {step['action']}: {step['params']}\n"

        content += f"""
## 示例

用户输入: {skill['example']}
"""

        skill_path.write_text(content)
        return skill_path

    def _ask_user(self, transcript: dict) -> bool:
        """请求用户确认"""
        print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 检测到可复用模式

任务: {transcript['user_input'][:50]}...

建议生成 Skill 固化此查询流程？
[Y/n]:""")
        return input().lower() != 'n'
```

#### 3.4.2 模式检测 Hook

```python
# hooks/pattern_detector.py

class PatternDetector:
    """检测可复用模式（PostToolUse Hook）"""

    def __init__(self, skill_generator: SkillGenerator):
        self.generator = skill_generator
        self.call_history = []

    def on_tool_call(self, call: dict):
        """记录工具调用"""
        self.call_history.append({
            "tool": call["tool"],
            "params": call["params"],
            "result_summary": self._summarize(call["result"])
        })

    def on_task_complete(self, transcript: dict):
        """任务完成时检查是否生成 Skill"""
        if self.generator.should_generate(transcript, self.call_history):
            skill = self.generator.generate(transcript, self.call_history)
            self.generator.save(skill)
            print(f"✅ 已生成 Skill: {skill['name']}")

        # 清空历史
        self.call_history = []

    def _summarize(self, result: dict) -> str:
        """总结结果（用于 Skill 描述）"""
        if isinstance(result, dict):
            return f"{len(result.get('rows', []))} 行数据"
        return str(result)[:50]
```

#### 3.4.3 失败改进机制

```python
# evolution/improver.py

class SkillImprover:
    """Skill 失败后改进（简化版 GEPA）"""

    def on_failure(self, skill: dict, error: dict, transcript: dict):
        """
        Skill 执行失败时，尝试改进

        流程：
        1. 分析失败原因
        2. 生成改进版本
        3. A/B 测试对比
        4. 用户确认后更新
        """
        # 分析失败
        analysis = self._analyze_failure(skill, error, transcript)

        # 生成改进版本
        improved = self._generate_improvement(skill, analysis)

        # 用户确认
        if self._confirm_improvement(skill, improved, analysis):
            self._update_skill(skill, improved)

    def _analyze_failure(self, skill, error, transcript) -> dict:
        """分析失败原因"""
        prompt = f"""
        分析 Skill 执行失败的原因：

        Skill: {skill['name']}
        步骤: {skill['steps']}
        错误: {error}
        用户输入: {transcript['user_input']}

        输出：
        1. 失败原因
        2. 改进建议
        3. 需要调整的步骤
        """
        return self.llm.analyze(prompt)

    def _generate_improvement(self, skill, analysis) -> dict:
        """生成改进版本"""
        improved = skill.copy()

        # 根据分析调整步骤
        for fix in analysis.get("fixes", []):
            step_idx = fix["step"]
            improved["steps"][step_idx] = fix["new_step"]

        improved["version"] = skill.get("version", 1) + 1
        improved["improved_at"] = datetime.now().isoformat()

        return improved
```

---

## 四、数据流设计

### 4.1 查询流程

```
用户输入
    │
    ▼
┌─────────────┐
│ 意图解析    │ → "查询订单 + 分析趋势"
└─────────────┘
    │
    ▼
┌─────────────┐
│ 任务规划    │ → 检查 Skills 库 → 无匹配 → 动态规划
└─────────────┘
    │
    ▼
┌─────────────┐     ┌─────────────┐
│ 知识检索    │ ←── │ 业务逻辑库  │
└─────────────┘     └─────────────┘
    │
    ▼
┌─────────────┐
│ 工具执行    │
│  - MySQL    │ → 查询订单数据
│  - ES       │ → 查询状态变更
│  - 分析     │ → 计算趋势
└─────────────┘
    │
    ▼
┌─────────────┐
│ 结果整合    │ → 生成报告
└─────────────┘
    │
    ▼
┌─────────────┐
│ Skill 检测  │ → 复杂任务？→ 提示生成 Skill
└─────────────┘
    │
    ▼
输出结果 + Skill 建议
```

### 4.2 Skill 固化流程

```
任务完成
    │
    ▼
检查条件
    ├── 工具调用 ≥ 3 次？
    ├── 无相似 Skill？
    └── 有复用价值？
    │
    ▼ (满足)
提示用户确认
    │
    ▼ (确认)
生成 Skill
    ├── 提取名称
    ├── 提取触发条件
    ├── 提取执行步骤
    └── 保存到 skills/
    │
    ▼
下次直接复用
```

---

## 五、目录结构

```
business-data-agent/
├── agent/
│   ├── __init__.py
│   ├── engine.py              # 核心引擎
│   ├── intent_parser.py       # 意图解析
│   ├── task_planner.py        # 任务规划
│   └── tool_executor.py       # 工具调度
│
├── adapters/
│   ├── __init__.py
│   ├── mysql_adapter.py       # MySQL 适配器
│   ├── es_adapter.py          # ES 适配器
│   └── api_adapter.py         # API 适配器
│
├── evolution/
│   ├── __init__.py
│   ├── skill_generator.py     # Skill 生成
│   ├── pattern_detector.py    # 模式检测
│   └── skill_improver.py      # 失败改进
│
├── knowledge/
│   ├── BUSINESS_LOGIC.md      # 业务逻辑
│   ├── SCHEMA.md              # 表结构
│   ├── TEMPLATES.md           # 查询模板
│   └── CATEGORIES.md          # 问题分类
│
├── skills/                     # 生成的 Skills
│   ├── order-query.md
│   ├── payment-diagnose.md
│   └── ...
│
├── config/
│   ├── databases.yaml         # 数据库配置
│   ├── apis.yaml              # API 配置
│   └── settings.yaml          # 全局设置
│
├── cli.py                      # 命令行入口
├── server.py                   # MCP Server
└── README.md
```

---

## 六、实现路线

### Phase 1：核心能力（1 周）

| 任务 | 产出 | 工作量 |
|------|------|--------|
| 项目骨架 | 目录结构 + 依赖 | 0.5 天 |
| MySQL 适配器 | 单数据库查询 | 1 天 |
| 意图解析 | LLM 意图识别 | 1 天 |
| 任务规划 | 简单规划逻辑 | 1 天 |
| 对话管理 | Session 管理 | 0.5 天 |

### Phase 2：知识层（1 周）

| 任务 | 产出 | 工作量 |
|------|------|--------|
| 知识库结构 | 4 个 MD 文件 | 1 天 |
| 业务逻辑录入 | BUSINESS_LOGIC.md | 1 天 |
| 表结构导入 | SCHEMA.md | 1 天 |
| 问题分类 | CATEGORIES.md | 1 天 |
| 知识检索 | 上下文注入 | 1 天 |

### Phase 3：进化层（1 周）

| 任务 | 产出 | 工作量 |
|------|------|--------|
| Skill 生成器 | 自动生成逻辑 | 2 天 |
| 模式检测 Hook | PostToolUse | 1 天 |
| 失败改进 | 简化版 GEPA | 2 天 |

---

## 七、配置示例

### 7.1 数据库配置

```yaml
# config/databases.yaml

databases:
  order_db:
    type: mysql
    host: ${MYSQL_HOST}
    port: 3306
    database: orders
    user: ${MYSQL_USER}
    password: ${MYSQL_PASSWORD}

  user_db:
    type: mysql
    host: ${MYSQL_HOST}
    port: 3306
    database: users

  order_events:
    type: elasticsearch
    host: ${ES_HOST}
    port: 9200
    index: order_events
```

### 7.2 API 配置

```yaml
# config/apis.yaml

apis:
  payment_callback:
    url: ${API_BASE}/payment/callback
    method: POST
    headers:
      Authorization: Bearer ${API_TOKEN}

  logistics_track:
    url: ${API_BASE}/logistics/track
    method: GET
```

---

## 八、安全设计

### 8.1 SQL 注入防护

```python
class SQLValidator:
    """SQL 安全验证"""

    DANGEROUS_PATTERNS = [
        r"DROP\s+",
        r"DELETE\s+FROM",
        r"TRUNCATE\s+",
        r"UPDATE\s+.*SET",
        r";\s*--",  # 注释注入
    ]

    def validate(self, sql: str) -> bool:
        """检查 SQL 是否安全"""
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                raise SecurityError(f"危险 SQL: {pattern}")
        return True

    def sanitize(self, sql: str) -> str:
        """清理 SQL"""
        # 限制返回行数
        if "LIMIT" not in sql.upper():
            sql += " LIMIT 1000"
        return sql
```

### 8.2 权限控制

```python
class AccessControl:
    """访问权限控制"""

    def __init__(self, config: dict):
        self.permissions = config["permissions"]
        self.user_context = None

    def check(self, user: str, action: str, resource: str) -> bool:
        """检查用户权限"""
        user_perms = self.permissions.get(user, [])

        for perm in user_perms:
            if self._match(perm, action, resource):
                return True

        return False

    def _match(self, perm, action, resource) -> bool:
        """匹配权限规则"""
        return (
            perm["action"] == action and
            re.match(perm["resource"], resource)
        )
```

---

## 九、监控与日志

### 9.1 执行日志

```python
# 监控每次查询执行
{
    "timestamp": "2026-04-20T10:00:00Z",
    "user": "dev_user_1",
    "intent": "query+analyze",
    "tools_used": ["mysql", "analyzer"],
    "duration_ms": 1250,
    "rows_returned": 156,
    "skill_used": "order-query",
    "success": true
}
```

### 9.2 Skill 使用统计

```python
# 统计 Skill 使用频率
{
    "skill": "order-query",
    "total_calls": 45,
    "success_rate": 0.95,
    "avg_duration_ms": 800,
    "last_used": "2026-04-20T10:00:00Z",
    "improvement_count": 2
}
```

---

## 十、与 Hermes 对比

| 能力 | Hermes 实现 | 本方案实现 | 说明 |
|------|-------------|-----------|------|
| 持久记忆 | 四层内存 | MEMORY.md | 简化为单层 |
| Skill 生成 | 自动 + GEPA | 自动 + 用户确认 | 去掉复杂算法 |
| 失败改进 | GEPA 算法 | LLM 分析 + A/B | 简化版 |
| 约束门控 | 完整测试 | 安全检查 + 用户确认 | 精简版 |
| 代码量 | ~10K 行 | ~1K 行 | 10% 复杂度 |

---

## 十一、后续扩展

### 11.1 短期（1-3 月）

- [ ] 多数据库类型支持（PostgreSQL, MongoDB）
- [ ] 可视化查询构建器
- [ ] Skill 版本管理

### 11.2 中期（3-6 月）

- [ ] 团队协作（共享 Skills）
- [ ] 查询性能优化（缓存 + 预计算）
- [ ] 自然语言生成 SQL（Text-to-SQL）

### 11.3 长期（6+ 月）

- [ ] 完整 GEPA 算法集成
- [ ] 图数据库支持（关系推荐）
- [ ] 自动化报表生成

---

*设计版本: 1.0.0*
*创建时间: 2026-04-20*
