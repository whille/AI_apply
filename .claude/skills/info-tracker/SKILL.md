---
name: info-tracker
description: 扫描并分析信息源，生成每日报告。整合 B站/GitHub/RSS 等多源信息，基于可信度筛选高质量内容。Use when: 信息扫描, 每日报告, info scan, daily scan, track sources.
user-invocable: true
argument-hint: "[daily|weekly] 或 [bilibili|github|rss] <关键词>"
triggers:
  - "信息扫描"
  - "每日报告"
  - "info scan"
  - "daily scan"
  - "track sources"
  - "信息源"
---

# Info Tracker

统一信息源跟踪和分析工具。

---

## 功能

1. **多源扫描**：B站 / GitHub / RSS 统一入口
2. **可信度评估**：自动筛选高质量内容
3. **AI 总结**：提取关键信息和洞察
4. **结构化报告**：Markdown 格式输出

---

## 使用方式

### 每日扫描

```bash
/info-tracker daily
```

扫描所有已配置的信息源，生成每日报告。

### 单源扫描

```bash
# B站关键词搜索
/info-tracker bilibili Claude Agent

# GitHub Trending
/info-tracker github trending

# RSS 订阅
/info-tracker rss https://example.com/feed
```

### 每周汇总

```bash
/info-tracker weekly
```

---

## 工作流程

```
触发扫描
    │
    ▼
┌─────────────────┐
│ 1. 识别扫描源    │
│ - 读取配置      │
│ - 确定范围      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. 信息采集      │
│ - B站: bilibili-api │
│ - GitHub: gh CLI │
│ - RSS: WebFetch  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. 可信度评估    │
│ - B站: 粉丝+等级+认证 │
│ - GitHub: Stars+更新 │
│ - RSS: 来源声誉  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. 质量筛选      │
│ - 可信度 ≥ 60: 高 │
│ - 可信度 40-59: 中│
│ - 可信度 < 40: 低 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. AI 总结      │
│ - 高价值内容深入 │
│ - 中价值内容简述 │
│ - 低价值内容过滤 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. 生成报告      │
│ - Markdown 格式  │
│ - 按价值排序    │
│ - 行动建议      │
└─────────────────┘
```

---

## B站信息源

### 扫描 UP 主更新

使用 `User.get_videos()` 获取最新投稿：

```python
from bilibili_api import user

u = user.User(uid=UP主UID)
videos = await u.get_videos(pn=1, ps=10)
```

### 关键词搜索

使用搜索功能发现相关视频：

```python
from bilibili_api import search

results = await search.search("Claude Agent")
```

### 可信度判断

```python
def calc_bilibili_credibility(user_info, relation_info):
    """B站 UP 主可信度计算"""
    score = 0

    # 粉丝数 (40分)
    follower = relation_info.get("follower", 0)
    if follower >= 1000000: score += 40
    elif follower >= 100000: score += 30
    elif follower >= 10000: score += 20
    elif follower >= 1000: score += 10

    # 等级 (15分)
    level = user_info.get("level", 0)
    score += min(level * 2.5, 15)

    # 认证 (20分)
    if user_info.get("official", {}).get("role"):
        score += 20

    # 总播放量 (15分)
    archive_view = user_info.get("archive_view", 0)
    if archive_view >= 10000000: score += 15
    elif archive_view >= 1000000: score += 10

    return min(score, 100)
```

---

## GitHub 信息源

### Trending 扫描

```bash
gh api repos --method GET -F q="language:python" -F sort="stars" -F order="desc"
```

### 项目分析

```bash
# GitMCP 概览
gh repo view owner/repo

# Repomix 打包
repomix --include "**/*.py"
```

### 可信度判断

```python
def calc_github_credibility(repo_info):
    """GitHub 项目可信度计算"""
    score = 0

    # Stars (30分)
    stars = repo_info.get("stargazers_count", 0)
    if stars >= 10000: score += 30
    elif stars >= 1000: score += 20
    elif stars >= 100: score += 10

    # 最近更新 (25分)
    updated = repo_info.get("updated_at")
    days = (now - updated).days
    if days <= 7: score += 25
    elif days <= 30: score += 20
    elif days <= 90: score += 10

    # Forks (20分)
    forks = repo_info.get("forks_count", 0)
    if forks >= 1000: score += 20
    elif forks >= 100: score += 10

    return min(score, 100)
```

---

## RSS 信息源

### RSS 解析

```python
import feedparser

feed = feedparser.parse("https://example.com/feed")
for entry in feed.entries[:10]:
    print(f"Title: {entry.title}")
    print(f"Link: {entry.link}")
    print(f"Published: {entry.published}")
```

### 内容提取

```bash
# WebFetch 获取正文
# 使用 Claude 的 WebFetch 工具
```

---

## 报告模板

```markdown
# 信息扫描报告

> 扫描时间：{timestamp}
> 扫描源：{sources}

---

## 📊 统计

| 指标 | 数值 |
|------|------|
| 扫描项目 | {total} |
| 高价值 | {high} |
| 中等价值 | {medium} |
| 低价值 | {low} |

---

## 🌟 高价值内容 (可信度 ≥ 60)

### 1. [{title}]({url})

| 属性 | 值 |
|------|---|
| 来源 | {source} |
| 可信度 | {score} |

**摘要**：{summary}

**行动建议**：{action}

---

## 📝 中等价值内容 (40-59)

> 共 {count} 项

---

## 📋 低价值内容 (< 40)

> 已自动过滤

---

## 💡 趋势观察

- {trend_1}
- {trend_2}
```

---

## 配置文件

创建 `~/.claude/config/info-tracker.yaml`：

```yaml
# B站关注配置
bilibili:
  follow_uids:
    - 12345678
  keywords:
    - "Claude"
    - "Agent"
  min_credibility: 40

# GitHub 配置
github:
  trending_languages:
    - python
    - typescript
  watch_repos:
    - "anthropics/claude-code"

# RSS 配置
rss:
  feeds:
    - name: "Anthropic Blog"
      url: "https://www.anthropic.com/rss"

# 输出配置
output:
  path: "~/notes/info-tracker/"
  daily_retention: 30
```

---

## 输出示例

执行 `/info-tracker bilibili Claude Agent` 后：

1. 搜索 B站关键词 "Claude Agent"
2. 获取 UP 主信息，计算可信度
3. 筛选可信度 ≥ 40 的视频
4. AI 总结高价值内容
5. 输出 Markdown 报告

---

## 注意事项

1. **频率限制**：B站 API 有频率限制，控制并发数
2. **代理问题**：YouTube/Twitter 需代理，暂不扫描
3. **缓存利用**：UP 主信息可缓存，减少重复请求
