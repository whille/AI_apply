# 信息源跟踪系统设计

> 整合 B站/GitHub/RSS 为统一信息源跟踪工作流

---

## 设计目标

1. **统一入口**：单一工作流管理多个信息源
2. **定时扫描**：自动发现新内容
3. **智能过滤**：基于可信度筛选高质量内容
4. **结构化输出**：便于后续处理和归档

---

## 一、信息源分层

### Layer 1: 核心信息源（P0 - 每日扫描）

| 信息源 | 类型 | 扫描频率 | 价值 |
|--------|------|----------|------|
| **GitHub Trending** | 代码仓库 | 每日 | 技术趋势 |
| **Anthropic Blog** | 官方博客 | 每日 | AI 前沿 |
| **B站 UP 主更新** | 视频 | 每日 | 技术视频 |

### Layer 2: 扩展信息源（P1 - 每周扫描）

| 信息源 | 类型 | 扫描频率 | 价值 |
|--------|------|----------|------|
| **RSS 订阅源** | 博客/新闻 | 每周 | 行业动态 |
| **Hacker News** | 社区 | 每周 | 技术讨论 |
| **GitHub Releases** | 版本更新 | 每周 | 库更新 |

### Layer 3: 按需信息源（P2 - 手动触发）

| 信息源 | 类型 | 触发方式 | 价值 |
|--------|------|----------|------|
| **B站关键词搜索** | 视频 | 手动 | 特定主题 |
| **GitHub 项目分析** | 代码 | 手动 | 深度学习 |
| **技术博客搜索** | 文章 | 手动 | 问题解决 |

---

## 二、系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                      信息源跟踪系统架构                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   B站源      │  │  GitHub源    │  │   RSS源      │              │
│  │ bilibili-api │  │ GitMCP+Repox │  │  feedparser  │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                       │
│         ▼                 ▼                 ▼                       │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │                    统一采集层                            │        │
│  │  - 格式标准化                                            │        │
│  │  - 去重处理                                              │        │
│  │  - 时间戳统一                                            │        │
│  └─────────────────────────┬───────────────────────────────┘        │
│                            │                                         │
│                            ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │                    可信度评估层                          │        │
│  │  - UP 主知名度判断 (B站)                                 │        │
│  │  - Star/Fork 数量 (GitHub)                              │        │
│  │  - 来源可信度 (RSS)                                     │        │
│  └─────────────────────────┬───────────────────────────────┘        │
│                            │                                         │
│                            ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │                    AI 总结层                            │        │
│  │  - 获取内容（字幕/README/正文）                          │        │
│  │  - LLM 提取关键信息                                     │        │
│  │  - 生成结构化摘要                                       │        │
│  └─────────────────────────┬───────────────────────────────┘        │
│                            │                                         │
│                            ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │                    输出与推送                            │        │
│  │  - Markdown 报告                                        │        │
│  │  - 每日/每周汇总                                        │        │
│  │  - 高优先级提醒                                         │        │
│  └─────────────────────────────────────────────────────────┘        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 三、核心流程设计

### 3.1 每日扫描流程

```yaml
daily_scan:
  schedule: "0 9 * * *"  # 每天 9:00

  sources:
    - name: "GitHub Trending"
      type: github
      action: trending
      language: ["python", "typescript", "rust"]

    - name: "B站关注UP主"
      type: bilibili
      action: get_updates
      uids: [待用户配置]

    - name: "Anthropic Blog"
      type: rss
      url: "https://www.anthropic.com/rss"

  output:
    format: "markdown"
    path: "~/notes/daily-scan/{date}.md"
```

### 3.2 B站视频处理流程

```
B站视频URL
    │
    ▼
┌─────────────────────┐
│ Step 1: 获取 UP 信息 │
│ - User.get_user_info│
│ - User.get_relation │
│ - 计算可信度分数     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Step 2: 可信度判断   │
│ - 分数 ≥ 60?        │
│ - 是: 继续          │
│ - 否: 标记低优先级   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Step 3: 获取视频信息 │
│ - Video.get_info    │
│ - 提取字幕/简介      │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Step 4: AI 总结     │
│ - 提取关键观点      │
│ - 技术价值判断      │
│ - 生成结构化摘要    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Step 5: 输出        │
│ - 标题/UP主/可信度   │
│ - 摘要/观点/价值    │
│ - 是否值得深入      │
└─────────────────────┘
```

### 3.3 GitHub 项目分析流程

```
GitHub 项目 URL
    │
    ▼
┌─────────────────────┐
│ Step 1: 获取元信息  │
│ - GitMCP 概览       │
│ - Stars/Forks/更新   │
│ - 技术栈识别        │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Step 2: 初筛        │
│ - Stars ≥ 1000?     │
│ - 最近更新时间?     │
│ - 技术栈匹配?       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Step 3: 深度分析    │
│ - Repomix 打包核心  │
│ - LLM 分析架构      │
│ - 提取 Insight      │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Step 4: 输出        │
│ - 项目定位          │
│ - 核心亮点          │
│ - 学习价值          │
│ - 是否值得深入      │
└─────────────────────┘
```

---

## 四、可信度评估模型

### 4.1 B站 UP 主可信度（已有）

```python
def calculate_bilibili_credibility(user_info, relation_info, up_stat):
    """
    计算 B站 UP 主信服力

    维度权重:
    - 粉丝数: 40%
    - 等级: 15%
    - 认证状态: 20%
    - 总播放量: 15%
    - 大会员: 10%

    分级:
    - S (≥80): 高度可信
    - A (60-79): 较可信
    - B (40-59): 一般
    - C (20-39): 谨慎参考
    - D (<20): 需验证
    """
    # 详见 docs/skills/bilibili-api.md
```

### 4.2 GitHub 项目可信度

```python
def calculate_github_credibility(repo_info, release_info):
    """
    计算 GitHub 项目可信度

    维度权重:
    - Stars: 30%
    - 最近更新: 25%
    - Forks/贡献者: 20%
    - 文档完整性: 15%
    - Issue 响应: 10%

    分级:
    - S (≥80): 成熟稳定
    - A (60-79): 值得信赖
    - B (40-59): 可用但需验证
    - C (20-39): 实验性质
    - D (<20): 不推荐
    """

    score = 0

    # Stars (30分)
    stars = repo_info.get("stargazers_count", 0)
    if stars >= 10000:
        score += 30
    elif stars >= 1000:
        score += 20
    elif stars >= 100:
        score += 10

    # 最近更新 (25分)
    updated = repo_info.get("updated_at")
    days_since_update = (now - updated).days
    if days_since_update <= 7:
        score += 25
    elif days_since_update <= 30:
        score += 20
    elif days_since_update <= 90:
        score += 15
    elif days_since_update <= 365:
        score += 5

    # Forks/贡献者 (20分)
    forks = repo_info.get("forks_count", 0)
    contributors = repo_info.get("contributors", 0)
    if forks >= 1000:
        score += 15
    elif forks >= 100:
        score += 10
    if contributors >= 50:
        score += 5
    elif contributors >= 10:
        score += 3

    # 文档完整性 (15分)
    has_readme = repo_info.get("readme", False)
    has_wiki = repo_info.get("has_wiki", False)
    has_docs = repo_info.get("has_docs", False)
    score += (has_readme * 5 + has_wiki * 5 + has_docs * 5)

    # Issue 响应 (10分)
    open_issues = repo_info.get("open_issues_count", 0)
    if open_issues < 10:
        score += 10
    elif open_issues < 50:
        score += 5

    return min(score, 100)
```

### 4.3 RSS 源可信度

```python
def calculate_rss_credibility(feed_info, source_reputation):
    """
    计算 RSS 源可信度

    维度权重:
    - 来源声誉: 40%
    - 更新频率: 25%
    - 内容质量: 25%
    - 历史准确性: 10%
    """

    score = 0

    # 来源声誉 (40分)
    reputation_scores = {
        "official": 40,      # 官方博客
        "reputable": 30,     # 知名媒体
        "community": 20,     # 社区聚合
        "personal": 10,      # 个人博客
        "unknown": 5         # 未知来源
    }
    score += reputation_scores.get(source_reputation, 5)

    # 更新频率 (25分)
    update_frequency = feed_info.get("update_frequency_days", 30)
    if update_frequency <= 1:
        score += 25
    elif update_frequency <= 7:
        score += 20
    elif update_frequency <= 30:
        score += 10

    # 内容质量 (25分) - 基于历史内容长度和质量
    avg_content_length = feed_info.get("avg_content_length", 0)
    if avg_content_length >= 1000:
        score += 15
    elif avg_content_length >= 500:
        score += 10

    # 历史准确性 (10分)
    accuracy_rate = feed_info.get("accuracy_rate", 0.5)
    score += int(accuracy_rate * 10)

    return min(score, 100)
```

---

## 五、输出格式设计

### 5.1 每日报告模板

```markdown
# 每日信息扫描报告

> 扫描时间：{date} {time}
> 扫描源：GitHub Trending, B站关注, RSS 订阅

---

## 📊 扫描统计

| 指标 | 数值 |
|------|------|
| 扫描项目 | 25 |
| 高价值 | 5 |
| 中等价值 | 12 |
| 低价值 | 8 |

---

## 🌟 高价值内容 (可信度 ≥ 70)

### 1. [{title}]({url})

| 属性 | 值 |
|------|-----|
| 来源 | {source} |
| 可信度 | {credibility_score} ({credibility_level}) |
| 类型 | {content_type} |

**摘要**：
{ai_summary}

**关键观点**：
- {insight_1}
- {insight_2}
- {insight_3}

**建议**：{action_recommendation}

---

## 📝 中等价值内容 (可信度 40-69)

### 2. [{title}]({url})
- 来源：{source}
- 可信度：{credibility_score}
- 简述：{brief_summary}

---

## 📋 低价值内容 (可信度 < 40)

> 共 {count} 项，已自动过滤

---

## 📈 趋势观察

- {trend_1}
- {trend_2}

---

## 明日计划

- [ ] 深入分析：{project_to_deep_dive}
- [ ] 验证源：{source_to_verify}
```

### 5.2 单项目分析报告模板

```markdown
# 项目分析：{project_name}

> 分析时间：{date}

---

## 基本信息

| 属性 | 值 |
|------|-----|
| 来源 | {source} |
| URL | {url} |
| 可信度 | {score} ({level}) |
| 类型 | {type} |

---

## 内容摘要

{content_summary}

---

## Insight 清单

### Insight 1: {insight_title}
- **发现**：{finding}
- **价值**：{value}
- **应用场景**：{use_case}

---

## 行动建议

| 优先级 | 建议 |
|--------|------|
| P0 | {action_p0} |
| P1 | {action_p1} |

---

## 是否值得深入

**结论**：{recommendation}

**理由**：
- {reason_1}
- {reason_2}
```

---

## 六、实现方案

### Phase 1：手动触发 Skill（推荐先实现）

```yaml
# ~/.claude/skills/info-tracker/SKILL.md

name: info-tracker
description: 扫描并分析信息源，生成每日报告
user-invocable: true
argument-hint: "[daily|weekly|source_type]"

triggers:
  - "信息扫描"
  - "每日报告"
  - "info scan"
  - "daily scan"
```

### Phase 2：Python 脚本（后续实现）

```bash
# 项目结构
info-tracker/
├── main.py              # 主入口
├── sources/
│   ├── bilibili.py      # B站源
│   ├── github.py        # GitHub源
│   └── rss.py           # RSS源
├── models/
│   ├── credibility.py   # 可信度模型
│   └── report.py        # 报告生成
├── config.yaml          # 配置文件
└── output/              # 输出目录
```

### Phase 3：定时任务（最终形态）

```yaml
# 使用 cron 或 Python schedule

jobs:
  daily_scan:
    schedule: "0 9 * * *"
    command: "python main.py --mode daily"

  weekly_scan:
    schedule: "0 10 * * 1"  # 每周一 10:00
    command: "python main.py --mode weekly"
```

---

## 七、用户配置

### 配置文件模板

```yaml
# config.yaml

# B站关注列表
bilibili:
  follow_uids:
    - 12345678    # UP主UID
    - 87654321
  keywords:
    - "Claude"
    - "Agent"
    - "LLM"
  min_credibility: 40  # 最低可信度阈值

# GitHub 关注
github:
  trending_languages:
    - python
    - typescript
    - rust
  min_stars: 100
  watch_repos:
    - "anthropics/claude-code"
    - "anthropics/anthropic-sdk-python"

# RSS 订阅源
rss:
  feeds:
    - name: "Anthropic Blog"
      url: "https://www.anthropic.com/rss"
      reputation: official

    - name: "Hacker News"
      url: "https://hnrss.org/frontpage"
      reputation: community

  min_credibility: 30

# 输出配置
output:
  path: "~/notes/info-tracker/"
  format: "markdown"
  daily_retention: 30  # 保留天数
```

---

## 八、与现有系统集成

### 与 09_learning_absorption.md 整合

```
信息源跟踪 → 项目分析 → Insight提取 → 知识沉淀
     ↓            ↓          ↓          ↓
 info-tracker  project   wiki/llm-wiki  MEMORY.md
               -notes/    skill
```

### 与 bilibili-api 整合

```
调用链:
info-tracker → bilibili-api skill → Video/Subtitle → AI Summary
```

---

## 九、决策点

| 决策点 | 选项 | 建议选择 |
|--------|------|----------|
| 实现方式 | Skill vs Script | 先 Skill，后 Script |
| 扫描频率 | 手动 vs 定时 | 先手动，后定时 |
| 存储位置 | 本地 md vs 数据库 | 本地 md |
| AI 模型 | Claude API vs 本地模型 | Claude API（已有） |

---

## 十、下一步

1. **T012.1**: 创建 `info-tracker` Skill
2. **T013**: 完善 B站视频搜索→总结流程
3. **D4**: 决定是否实现自动化脚本

---

*设计时间：2026-04-19*
