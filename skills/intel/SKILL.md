---
name: intel
description: 持续信息跟踪与情报收集。扫描 B站/GitHub/RSS 等多源信息，自动去重、评分、筛选，生成报告并导入 Wiki。Use when: 情报收集, 信息跟踪, intel, scan, 信息源监控.
user-invocable: true
argument-hint: "[scan <主题>] 或 [bilibili|github|rss] <关键词>"
triggers:
  - "情报收集"
  - "信息跟踪"
  - "intel"
  - "信息源监控"
  - "持续跟踪"
  - "scan"
---

# Intel

持续信息跟踪与情报收集工具，参考 [Horizon](https://github.com/Thysrael/Horizon) 架构设计。

---

## 架构设计（参考 Horizon）

```
Pipeline: Fetch → Deduplicate → Score → Filter → Enrich → Summarize → Deploy

 ┌──────────┐                                             ┌──────────┐
 │ Hacker   │                                             │  部署    │
┌─────────┐ │ News  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ │ GitHub   │
│ RSS     │──▶Reddit│──▶│ AI Score │──▶│ Enrich   │──▶│ Summary  │──▶│ Pages    │
│ B站     │ │ GitHub │ │ & Filter │ │ & Search │ │ & Deploy│ │ 本地 MD  │
└─────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

**核心特性**：
1. ✅ 先评估源质量，筛选 TopN
2. ✅ B站完全委托 `/bilibili-analyzer`
3. ✅ 跨源去重（Horizon 方案）

---

## 核心特性

| 特性 | 说明 |
|------|------|
| 多源并行 | B站 / GitHub / RSS 异步采集 |
| 源质量评估 | 先评分，再筛选 TopN |
| 深度内容获取 | 字幕/正文/README，不仅标题 |
| 智能去重 | URL级 + 跨源合并 |
| 持久化 | Markdown 报告 + history.json |

---

## 使用方式

### 扫描某个主题

```bash
/intel Claude Agent
/intel "Rust async 编程"
/intel "量化交易策略"
/intel "鱼菜共生"
```

**必须提供关键词/主题**，技能会：
1. 多源并行搜索（RSS、GitHub、Web）
2. 自动去重、评分筛选
3. 生成 Markdown 报告

### 单源扫描

```bash
# B站：完全委托 bilibili-analyzer
/bilibili-analyzer Claude Agent 2026

# GitHub Trending（指定语言）
/intel github python

# RSS 指定源
/intel rss https://openai.com/blog/rss.xml
```

---

## 定时执行（由调用者控制）

```bash
# 每天 8:00 扫描 AI Agent
0 8 * * * claude "/intel Claude Agent" >> ~/logs/intel-agent.log 2>&1

# 每周一 8:00 扫描另一个主题
0 8 * * 1 claude "/intel 量化交易" >> ~/logs/intel-quant.log 2>&1
```

手动调用：

```bash
# 每日
/intel

# 发现值得深入研究时
/deep-research "某个主题"

# 导入知识库
/llm-wiki ingest ~/.claude/intel/reports/$(date +%Y-%m-%d).md
```

---

## 工作流程

```
触发扫描
    │
    ▼
┌─────────────────────────────────────┐
│ Phase 1: 多源并行扫描（元数据）       │
│ ┌─────────────┐ ┌─────────┐ ┌─────┐ │
│ │ /bilibili-  │ │ gh CLI  │ │RSS  │ │
│ │ analyzer    │ │Trending │ │Fetch│ │
│ │ (B站专用)   │ │         │ │     │ │
│ └──────┬──────┘ └────┬────┘ └──┬──┘ │
└────────┼─────────────┼──────────┼────┘
         │             │          │
         └─────────────┼──────────┘
                       ▼
┌─────────────────────────────────────┐
│ Phase 2: 源质量评估 → TopN 筛选      │
│ ─────────────────────────────────── │
│ 评分公式：                          │
│   Score = 基础分 + 时效性 + 来源权重 │
│                                     │
│ 筛选规则：                          │
│   - Top 20 (Score ≥ 40)            │
│   - 可通过配置调整阈值               │
│                                     │
│ 评分示例：                          │
│ ┌────────────────┬─────┬─────┬────┐│
│ │ 来源           │基础 │时效│总分 ││
│ ├────────────────┼─────┼────┼──── ││
│ │ OpenAI Blog    │ 30  │ +20│ 50  ││
│ │ Hugging Face   │ 20  │ +20│ 40  ││
│ │ r/LocalLLaMA   │ 10  │ +15│ 25  ││
│ │ B站UP主(100万粉)│ 40  │ +10│ 50  ││
│ └────────────────┴─────┴────┴────┘│
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ Phase 3: 获取完整内容                 │
│ ─────────────────────────────────── │
│ B站视频：                            │
│   └─ 委托 /bilibili-analyzer         │
│      └─ 字幕 + 简介 + UP主信息        │
│                                     │
│ 文章：                               │
│   └─ WebFetch 获取正文               │
│                                     │
│ GitHub：                             │
│   └─ gh repo view + README          │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ Phase 4: 跨源去重                    │
│ ─────────────────────────────────── │
│ Horizon 方案：                       │
│   - URL 级去重（主键）               │
│   - 跨源合并（同URL不同来源合并）    │
│                                     │
│ 检查 history.json → 过滤已存在      │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ Phase 5: AI 深度分析                 │
│ ─────────────────────────────────── │
│ 高价值 (≥60)：                       │
│   └─ 完整摘要 + 技术要点 + 行动建议  │
│                                     │
│ 中价值 (40-59)：                     │
│   └─ 简要概述                        │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ Phase 6: 持久化输出                  │
│ ─────────────────────────────────── │
│ ├─ reports/YYYY-MM-DD.md           │
│ ├─ history.json (更新去重索引)      │
│ └─ source_scores.json (源评分历史)  │
└─────────────────────────────────────┘
```

---

## 源质量评估算法

### 评分公式

```python
class SourceScorer:
    """源质量评分引擎"""

    def calc_score(self, item: dict, config: dict) -> int:
        """
        评分公式：
        Score = 基础分 + 时效性 + 来源权重 + 内容质量

        各源基础分：
        - OpenAI Blog: 30
        - Hugging Face: 20
        - r/LocalLLaMA: 10
        - B站(认证UP): 40
        - GitHub(Star>k): 20
        """
        base = config.get("credibility_boost", 10)
        freshness = self._calc_freshness(item.get("published"))
        quality = self._calc_quality(item)

        return min(base + freshness + quality, 100)

    def _calc_freshness(self, published: datetime) -> int:
        """时效性评分（20分上限）"""
        if not published:
            return 0

        age_hours = (datetime.now() - published).total_seconds() / 3600

        if age_hours <= 24:      return 20  # 24h内
        elif age_hours <= 72:    return 15  # 3天内
        elif age_hours <= 168:   return 10  # 7天内
        elif age_hours <= 720:   return 5   # 30天内
        else:                    return 0

    def _calc_quality(self, item: dict) -> int:
        """内容质量评分（30分上限）"""
        score = 0

        # 标题相关度
        if self._is_ai_agent_related(item.get("title", "")):
            score += 15

        # 有完整内容
        if item.get("has_full_content"):
            score += 10

        # 来源可信度
        if item.get("source") in ["openai-blog", "huggingface-blog"]:
            score += 5

        return min(score, 30)

    def filter_topn(self, items: list, limit: int = 20, min_score: int = 40) -> list:
        """筛选 TopN"""
        scored = [(self.calc_score(item, {}), item) for item in items]
        scored.sort(key=lambda x: x[0], reverse=True)

        return [item for score, item in scored
                if score >= min_score][:limit]
```

### 源基础分配置

| 源 | 基础分 | 说明 |
|---|--------|------|
| OpenAI Blog | 30 | 官方权威 |
| Hugging Face Blog | 20 | 技术深度 |
| r/LocalLLaMA | 10 | 社区讨论 |
| GitHub Trending (AI) | 20 | 项目热度 |
| B站认证UP主 | 40 | + 粉丝数加成 |
| Hacker News | 15 | 技术社区 |

---

## B站集成（委托 bilibili-analyzer）

### 完全委托模式

```python
# intel 不直接处理 B站
# 所有 B站相关操作委托给 bilibili-analyzer

async def scan_bilibili(keywords: list, year: int):
    """
    B站扫描完全委托给 /bilibili-analyzer

    调用方式：
    /bilibili-analyzer {keywords} {year}

    bilibili-analyzer 提供：
    - 关键词搜索
    - UP主可信度评估（粉丝+等级+认证）
    - 视频字幕获取
    - AI 视频摘要
    """
    # 通过 Skill 工具调用
    pass
```

### bilibili-analyzer 输出格式

```markdown
# B站分析报告

## 搜索关键词：Claude Agent 2026

### 🌟 高价值视频

#### 1. [视频标题](https://www.bilibili.com/video/BV1xxx)

| 属性 | 值 |
|------|---|
| UP主 | 名称（粉丝数） |
| 可信度 | 75/100 |
| 发布时间 | 2026-04-19 |

**字幕摘要**：
{从字幕提取的关键内容}

**技术要点**：
- 要点1
- 要点2
```

---

## 存储结构

```
~/.claude/intel/
├── history.json              # 去重索引
├── source_scores.json        # 源评分历史（新增）
├── reports/
│   ├── 2026-04-19.md        # 每日报告
│   └── 2026-week16.md       # 每周汇总
└── cache/
    ├── bilibili_up/          # UP主信息缓存
    └── rss_feeds/            # RSS 缓存
```

### source_scores.json（新增）

```json
{
  "sources": {
    "openai-blog": {
      "avg_score": 85,
      "total_items": 120,
      "high_value_rate": 0.75,
      "last_update": "2026-04-19"
    },
    "r/LocalLLaMA": {
      "avg_score": 45,
      "total_items": 200,
      "high_value_rate": 0.30,
      "last_update": "2026-04-19"
    }
  },
  "rankings": [
    {"source": "openai-blog", "score": 85},
    {"source": "huggingface-blog", "score": 78},
    {"source": "bilibili-certified", "score": 72},
    {"source": "github-trending", "score": 65},
    {"source": "r/LocalLLaMA", "score": 45}
  ]
}
```

---

## 配置文件

```yaml
# ~/.claude/config/intel.yaml

# RSS 源池（按标签分类，运行时根据关键词匹配）
rss:
  feeds:
    - name: "OpenAI Blog"
      url: "https://openai.com/blog/rss.xml"
      base_score: 30
      tags: [ai, agent, gpt]

    - name: "Hugging Face Blog"
      url: "https://huggingface.co/blog/feed.xml"
      base_score: 20
      tags: [ai, llm, model]

    - name: "r/LocalLLaMA"
      url: "https://www.reddit.com/r/LocalLLaMA/.rss"
      base_score: 10
      tags: [ai, llm]

# GitHub 配置
github:
  default_languages: [python, typescript, rust]
  trending: true

# B站配置（委托 bilibili-analyzer）
bilibili:
  use_skill: "/bilibili-analyzer"
  min_credibility: 40

# 评分配置
scoring:
  top_n: 20
  min_score: 40

# Wiki 集成
wiki:
  enabled: true
  root: "~/Documents/Knowledge-Wiki"
```

---

## 与 Horizon 对比

| 特性 | Horizon | intel |
|------|---------|--------------|
| 多源聚合 | ✅ 5源 | ✅ 4源 |
| AI 评分 | ✅ 0-10分 | ✅ 0-100分 |
| 跨源去重 | ✅ URL合并 | ✅ 同方案 |
| 内容丰富 | ✅ 搜索+社区 | ⚠️ RSS正文 |
| B站支持 | ❌ 无 | ✅ 完整支持 |
| MCP集成 | ✅ 内置 | ⚠️ 使用 Claude Code 原生 |
| 部署 | GitHub Pages | 本地 MD |

---

## 与 llm-wiki 集成（知识库积累）

### 设计理念

`/intel` 负责**信息扫描**，`/llm-wiki` 负责**知识积累**。

```
┌─────────────────┐      ┌─────────────────┐
│ /intel   │ ───▶ │  /llm-wiki      │
│ 信息扫描        │      │  知识积累        │
│ ─────────────── │      │ ─────────────── │
│ 多源扫描        │      │ 实体提取         │
│ TopN筛选        │ ───▶ │ 主题关联         │
│ MD报告          │      │ 双向链接         │
└─────────────────┘      └─────────────────┘
```

### 协作流程

```
用户: /intel Claude Agent
      ↓
  扫描信息源 → 筛选 TopN → 生成 MD 报告
      ↓
  保存到 reports/2026-04-19-claude-agent.md
      ↓
  自动提示: "是否导入到知识库？[y/n]"
      ↓
用户: y
      ↓
  /llm-wiki ingest <报告路径>
      ↓
  知识库增长:
  ├── wiki/entities/Claude-Agent.md (新增)
  ├── wiki/entities/MCP-Protocol.md (新增)
  ├── wiki/topics/Agent-SDK.md (更新)
  └── wiki/sources/2026-04-19-claude-agent.md (素材页)
```

### 手动导入

```bash
# 扫描后手动导入
/intel Claude Agent
/llm-wiki ingest ~/.claude/intel/reports/2026-04-19-claude-agent.md

# 批量导入历史报告
/llm-wiki batch-ingest ~/.claude/intel/reports/
```

### 自动导入配置

在 `~/.claude/config/intel.yaml` 中配置：

```yaml
wiki:
  enabled: true
  root: "~/Documents/Knowledge-Wiki"
  auto_ingest: true
```

### 输出格式适配 llm-wiki

intel 的报告格式符合 llm-wiki 的 ingest 要求：

```markdown
# 信息扫描报告

> 扫描时间：2026-04-19
> 关键词：Claude Agent

## 🌟 高价值内容

### 1. [OpenAI Agents SDK 更新](https://openai.com/...)

**摘要**：...
**技术要点**：...
**来源**：OpenAI Blog

<!-- llm-wiki 解析时提取：
- 实体：OpenAI Agents SDK
- 主题：Agent SDK
- 来源：OpenAI Blog
-->
```

### 知识库目录结构

```
~/Documents/Knowledge-Wiki/
├── .wiki-schema.md
├── index.md
├── purpose.md
├── raw/
│   └── intel/
│       ├── 2026-04-19-claude-agent.md
│       └── 2026-04-20-rust-async.md
├── wiki/
│   ├── entities/
│   │   ├── Claude-Agent.md
│   │   └── Rust-Async.md
│   ├── topics/
│   │   └── AI-Agent.md
│   └── sources/
│       └── 2026-04-19-claude-agent.md
└── log.md
```

### 初始化知识库

首次使用需要初始化：

```bash
/llm-wiki init
```

### 查询知识库

积累后可以查询：

```bash
# 快速查询
/llm-wiki query Agent SDK 和 MCP 的关系

# 深度报告
/llm-wiki digest AI Agent 技术演进

# 知识图谱
/llm-wiki graph
```

---

## 快速开始

```bash
# 1. 扫描某个主题
/intel Claude Agent

# 2. 测试 B站
/bilibili-analyzer Claude Agent 2026

# 3. 查看报告
cat ~/.claude/intel/reports/$(date +%Y-%m-%d).md

# 4. 导入知识库
/llm-wiki ingest ~/.claude/intel/reports/$(date +%Y-%m-%d).md
```
