---
name: bilibili-analyzer
description: 分析B站视频，提取关键信息并生成结构化报告。支持关键词搜索、UP主可信度评估、AI摘要。Use when: 分析b站, bilibili分析, b站视频, analyze bilibili, b站搜索.
user-invocable: true
argument-hint: "<关键词> 或 --uploader <UID>"
triggers:
  - "分析b站"
  - "bilibili分析"
  - "b站视频"
  - "analyze bilibili"
  - "b站搜索"
  - "B站"
---

# B站视频分析器

从搜索到结构化总结的完整流程。

---

## 功能

1. **关键词搜索**：发现相关视频
2. **可信度评估**：筛选高质量内容
3. **内容提取**：获取字幕/简介
4. **AI 总结**：结构化摘要
5. **价值判断**：是否值得深入

---

## 使用方式

### 关键词搜索分析

```bash
/bilibili-analyzer Claude Agent
```

搜索关键词并分析前 10 个高可信度视频。

### 分析 UP 主最新视频

```bash
/bilibili-analyzer --uploader 12345678
```

分析指定 UP 主最近 10 个视频。

### 分析指定视频

```bash
/bilibili-analyzer BV1xx411c7mC
```

分析单个视频详情。

---

## 工作流程

```
输入关键词/BV号
    │
    ▼
┌─────────────────┐
│ 1. 搜索/获取视频  │
│ - 关键词搜索    │
│ - UP主视频列表  │
│ - 单视频详情    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. 获取 UP 信息  │
│ - User.get_user_info │
│ - User.get_relation │
│ - User.get_up_stat │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. 计算可信度    │
│ - 粉丝数 (40%)  │
│ - 等级 (15%)    │
│ - 认证 (20%)    │
│ - 播放量 (15%)  │
│ - 大会员 (10%)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. 可信度筛选    │
│ - ≥60: 高价值   │
│ - 40-59: 中等  │
│ - <40: 过滤    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. 获取视频详情  │
│ - Video.get_info │
│ - Video.get_subtitle │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. AI 结构化总结 │
│ - 一句话摘要    │
│ - 核心观点      │
│ - 技术价值      │
│ - 是否值得深入  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 7. 输出报告      │
│ - Markdown 格式 │
│ - 按可信度排序  │
└─────────────────┘
```

---

## 可信度计算模型

```python
def calculate_credibility(user_info, relation_info, up_stat):
    """
    计算 UP 主信服力分数

    返回:
        score: 0-100 分数
        level: S/A/B/C/D 等级
    """
    score = 0

    # 1. 粉丝数 (40分)
    follower = relation_info.get("follower", 0)
    if follower >= 1000000: score += 40
    elif follower >= 100000: score += 30
    elif follower >= 10000: score += 20
    elif follower >= 1000: score += 10
    else: score += 5

    # 2. 等级 (15分)
    level = user_info.get("level", 0)
    score += min(level * 2.5, 15)

    # 3. 认证状态 (20分)
    official_role = user_info.get("official", {}).get("role", 0)
    if official_role == 2: score += 20  # 机构认证
    elif official_role == 1: score += 15  # 个人认证
    else: score += 5

    # 4. 总播放量 (15分)
    archive_view = up_stat.get("archive", {}).get("view", 0)
    if archive_view >= 10000000: score += 15
    elif archive_view >= 1000000: score += 10
    elif archive_view >= 100000: score += 5
    else: score += 2

    # 5. 大会员 (10分)
    vip_type = user_info.get("vip", {}).get("type", 0)
    score += 10 if vip_type >= 1 else 3

    # 分级
    if score >= 80: level_letter = "S"
    elif score >= 60: level_letter = "A"
    elif score >= 40: level_letter = "B"
    elif score >= 20: level_letter = "C"
    else: level_letter = "D"

    return {"score": score, "level": level_letter}
```

### 分级含义

| 等级 | 分数 | 粉丝参考 | 信服力 |
|------|------|----------|--------|
| **S** | ≥80 | 100万+ | 高度可信 |
| **A** | 60-79 | 10万-100万 | 较可信 |
| **B** | 40-59 | 1万-10万 | 一般可信 |
| **C** | 20-39 | 1千-1万 | 谨慎参考 |
| **D** | <20 | <1千 | 需验证 |

---

## AI 总结模板

执行分析时，使用以下 Prompt：

```
分析以下B站视频，生成结构化总结：

## 视频信息
- 标题：{title}
- UP主：{author}
- 可信度：{score} ({level})
- 播放量：{view}
- 时长：{duration}秒

## 内容
{subtitle_or_desc}

---

请输出：

### 1. 一句话摘要（20字内）

### 2. 核心观点（3-5条）

### 3. 技术价值判断
- 技术相关性：高/中/低
- 原创性：高/中/低
- 实用性：高/中/低

### 4. 是否值得深入（是/否）
理由：...

### 5. 核心关键词
```

---

## 报告模板

```markdown
# B站视频分析报告

> 关键词：{keyword}
> 分析时间：{timestamp}
> 高价值视频：{high_count} 个

---

## 📊 统计

| 指标 | 数值 |
|------|------|
| 搜索结果 | {total} |
| 高可信度 (S/A) | {high} |
| 中等可信度 (B) | {medium} |
| 低可信度 (C/D) | {low} |

---

## 🌟 高价值视频

### 1. [{title}]({url})

| 属性 | 值 |
|------|---|
| UP主 | {author} |
| 可信度 | {score} ({level}) |
| 播放量 | {view} |
| 时长 | {duration} |

**一句话摘要**：{summary}

**核心观点**：
- {point_1}
- {point_2}
- {point_3}

**技术价值**：{tech_value}

**是否值得深入**：{recommendation}

---

## 📝 中等价值视频

> 共 {count} 个

1. [{title}]({url}) - 可信度：{score}
2. ...

---

## 💡 分析总结

### 主要发现
- {finding_1}
- {finding_2}

### 推荐深入
- {rec_1}
```

---

## 前置依赖

### 安装 bilibili-api

```bash
pip install bilibili-api
```

### Python 示例代码

```python
import asyncio
from bilibili_api import user, video

async def analyze_uploader(uid: int):
    """分析 UP 主"""
    u = user.User(uid=uid)

    # 获取信息
    user_info = await u.get_user_info()
    relation_info = await u.get_relation_info()
    up_stat = await u.get_up_stat()
    videos = await u.get_videos(pn=1, ps=10)

    # 计算可信度
    credibility = calculate_credibility(user_info, relation_info, up_stat)

    return {
        "user_info": user_info,
        "credibility": credibility,
        "videos": videos
    }

async def analyze_video(bvid: str):
    """分析视频"""
    v = video.Video(bvid=bvid)

    info = await v.get_info()
    owner = info["owner"]

    # 获取 UP 主可信度
    u = user.User(uid=owner["mid"])
    relation = await u.get_relation_info()
    up_stat = await u.get_up_stat()

    credibility = calculate_credibility({}, relation, up_stat)

    # 获取字幕
    try:
        subtitle = await v.get_subtitle()
    except:
        subtitle = info.get("desc", "")

    return {
        "info": info,
        "subtitle": subtitle,
        "credibility": credibility
    }
```

---

## 注意事项

1. **API 频率**：控制并发数，避免限流
2. **无字幕视频**：使用简介替代
3. **隐私设置**：部分 UP 主信息可能获取失败
4. **已删除视频**：跳过处理

---

## 与 info-tracker 集成

```yaml
# info-tracker 配置中

bilibili:
  follow_uids:
    - 12345678
  keywords:
    - "Claude"
    - "Agent"
  min_credibility: 40

# 调用流程
info-tracker → bilibili-analyzer → AI Summary → Report
```
