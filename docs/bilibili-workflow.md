# B站视频搜索→信息提取工作流

> 从搜索到结构化总结的完整流程设计

---

## 设计目标

1. **关键词搜索**：通过主题词发现相关视频
2. **可信度预筛**：基于 UP 主知名度过滤低质量内容
3. **内容提取**：获取字幕/简介用于分析
4. **AI 总结**：生成结构化摘要和洞察
5. **价值判断**：决定是否值得深入

---

## 一、完整工作流

```
┌─────────────────────────────────────────────────────────────────────┐
│                  B站视频搜索→信息提取工作流                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  用户输入关键词                                                       │
│       │                                                              │
│       ▼                                                              │
│  ┌─────────────┐                                                    │
│  │ Step 1      │                                                    │
│  │ 关键词搜索   │ ← bilibili-api Search                             │
│  └──────┬──────┘                                                    │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────┐                                                    │
│  │ Step 2      │                                                    │
│  │ 批量获取UP信息│ ← User.get_user_info + get_relation             │
│  └──────┬──────┘                                                    │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────┐    可信度 ≥ 40                                      │
│  │ Step 3      │ ───────────────→ 继续                              │
│  │ 可信度筛选   │                                                    │
│  └──────┬──────┘    可信度 < 40                                      │
│         │           └──────────────→ 标记低优先级                    │
│         ▼                                                            │
│  ┌─────────────┐                                                    │
│  │ Step 4      │                                                    │
│  │ 获取视频详情 │ ← Video.get_info + get_subtitle                   │
│  └──────┬──────┘                                                    │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────┐                                                    │
│  │ Step 5      │                                                    │
│  │ AI 结构化   │ ← Claude API                                       │
│  │ 总结        │                                                    │
│  └──────┬──────┘                                                    │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────┐                                                    │
│  │ Step 6      │                                                    │
│  │ 价值判断    │ → 是否值得深入？                                    │
│  └──────┬──────┘                                                    │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────┐                                                    │
│  │ Step 7      │                                                    │
│  │ 输出报告    │ → Markdown 格式                                     │
│  └─────────────┘                                                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 二、各步骤详解

### Step 1: 关键词搜索

```python
import asyncio
from bilibili_api import search

async def search_bilibili_videos(keyword: str, page: int = 1, page_size: int = 20):
    """
    搜索B站视频

    Args:
        keyword: 搜索关键词
        page: 页码
        page_size: 每页数量

    Returns:
        视频列表
    """
    results = await search.search(keyword, page=page, page_size=page_size)

    videos = []
    for item in results.get("result", []):
        videos.append({
            "bvid": item.get("bvid"),
            "title": item.get("title"),
            "author": item.get("author"),
            "mid": item.get("mid"),  # UP主UID
            "play": item.get("play"),  # 播放量
            "danmaku": item.get("danmaku"),
            "pubdate": item.get("pubdate"),
            "duration": item.get("duration"),
        })

    return videos
```

### Step 2: 批量获取 UP 信息

```python
async def get_uploaders_info(mids: list[int]) -> dict[int, dict]:
    """
    批量获取UP主信息

    Args:
        mids: UP主UID列表

    Returns:
        {mid: {user_info, relation_info, up_stat}}
    """
    results = {}

    for mid in mids:
        u = user.User(uid=mid)

        user_info = await u.get_user_info()
        relation_info = await u.get_relation_info()
        up_stat = await u.get_up_stat()

        results[mid] = {
            "user_info": user_info,
            "relation_info": relation_info,
            "up_stat": up_stat,
            "credibility": calculate_credibility(user_info, relation_info, up_stat)
        }

    return results
```

### Step 3: 可信度筛选

```python
def filter_by_credibility(videos: list, uploaders_info: dict, min_score: int = 40):
    """
    按可信度筛选视频

    Args:
        videos: 视频列表
        uploaders_info: UP主信息字典
        min_score: 最低可信度分数

    Returns:
        (high_value, low_value) 分组
    """
    high_value = []
    low_value = []

    for video in videos:
        mid = video["mid"]
        credibility = uploaders_info.get(mid, {}).get("credibility", 0)

        video["credibility_score"] = credibility
        video["credibility_level"] = get_credibility_level(crediility)

        if credibility >= min_score:
            high_value.append(video)
        else:
            low_value.append(video)

    # 按可信度排序
    high_value.sort(key=lambda x: x["credibility_score"], reverse=True)

    return high_value, low_value
```

### Step 4: 获取视频详情

```python
async def get_video_details(bvids: list[str]) -> dict[str, dict]:
    """
    批量获取视频详情

    Args:
        bvids: BV号列表

    Returns:
        {bvid: video_details}
    """
    results = {}

    for bvid in bvids:
        v = video.Video(bvid=bvid)

        info = await v.get_info()

        # 尝试获取字幕
        subtitle = None
        try:
            subtitle_data = await v.get_subtitle()
            subtitle = extract_subtitle_text(subtitle_data)
        except:
            # 无字幕，使用简介
            subtitle = info.get("desc", "")

        results[bvid] = {
            "info": info,
            "subtitle": subtitle,
            "stat": info.get("stat", {}),
        }

    return results
```

### Step 5: AI 结构化总结

```python
async def ai_summarize_video(video_data: dict, uploader_data: dict) -> dict:
    """
    AI 总结视频内容

    Args:
        video_data: 视频详情
        uploader_data: UP主信息

    Returns:
        结构化总结
    """
    prompt = f"""
分析以下B站视频，生成结构化总结：

## 视频信息
- 标题：{video_data['info']['title']}
- UP主：{video_data['info']['owner']['name']}
- 可信度：{uploader_data['credibility_score']} ({uploader_data['credibility_level']})
- 播放量：{video_data['stat']['view']}
- 时长：{video_data['info']['duration']}秒

## 内容
{video_data['subtitle']}

---

请输出以下内容：

### 1. 一句话摘要（20字内）

### 2. 核心观点（3-5条）

### 3. 技术价值判断
- 技术相关性：高/中/低
- 原创性：高/中/低
- 实用性：高/中/低

### 4. 目标受众

### 5. 是否值得深入（是/否）
理由：...

### 6. 核心关键词（5个）
"""

    response = await claude_api(prompt)

    return parse_summary_response(response)
```

---

## 三、完整示例代码

```python
import asyncio
from bilibili_api import user, video, search

class BilibiliVideoAnalyzer:
    """B站视频分析器"""

    def __init__(self, min_credibility: int = 40):
        self.min_credibility = min_credibility

    async def analyze_keyword(self, keyword: str, max_results: int = 20) -> dict:
        """
        分析关键词相关视频

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数

        Returns:
            分析报告
        """
        # Step 1: 搜索视频
        videos = await search_bilibili_videos(keyword, page_size=max_results)

        # Step 2: 批量获取UP主信息
        mids = list(set(v["mid"] for v in videos))
        uploaders_info = await get_uploaders_info(mids)

        # Step 3: 可信度筛选
        high_value, low_value = filter_by_credibility(
            videos, uploaders_info, self.min_credibility
        )

        # Step 4: 获取高价值视频详情
        bvids = [v["bvid"] for v in high_value[:10]]  # 只分析前10个
        video_details = await get_video_details(bvids)

        # Step 5: AI 总结（并发）
        summaries = await asyncio.gather(*[
            ai_summarize_video(
                video_details[v["bvid"]],
                uploaders_info[v["mid"]]
            )
            for v in high_value[:10]
        ])

        # Step 6: 生成报告
        report = self.generate_report(keyword, high_value, low_value, summaries)

        return report

    def generate_report(self, keyword, high_value, low_value, summaries):
        """生成分析报告"""
        report = {
            "keyword": keyword,
            "total_found": len(high_value) + len(low_value),
            "high_value_count": len(high_value),
            "low_value_count": len(low_value),
            "videos": summaries,
            "recommendations": self.extract_recommendations(summaries)
        }
        return report


# 使用示例
async def main():
    analyzer = BilibiliVideoAnalyzer(min_credibility=40)

    report = await analyzer.analyze_keyword("Claude Agent", max_results=30)

    # 输出报告
    save_report(report, "bilibili-claude-agent-analysis.md")

asyncio.run(main())
```

---

## 四、输出报告模板

```markdown
# B站视频分析报告

> 关键词：{keyword}
> 扫描时间：{timestamp}
> 高价值视频：{high_value_count} 个
> 低价值视频：{low_value_count} 个（已过滤）

---

## 📊 扫描统计

| 指标 | 数值 |
|------|------|
| 搜索结果 | {total_found} |
| 高可信度 | {high_credibility} |
| 中等可信度 | {medium_credibility} |
| 低可信度 | {low_credibility} |

---

## 🌟 高价值视频（可信度 ≥ 60）

### 1. [{title}]({url})

| 属性 | 值 |
|------|-----|
| UP主 | {author} |
| 可信度 | {score} ({level}) |
| 播放量 | {view_count} |
| 时长 | {duration} |

**一句话摘要**：
{one_line_summary}

**核心观点**：
- {point_1}
- {point_2}
- {point_3}

**技术价值**：{tech_value}
**是否值得深入**：{recommendation}

---

## 📝 中等价值视频（可信度 40-59）

> 共 {count} 个，仅列出标题

1. [{title_1}]({url_1}) - 可信度：{score}
2. [{title_2}]({url_2}) - 可信度：{score}

---

## 📋 低价值视频（可信度 < 40）

> 共 {count} 个，已自动过滤

---

## 💡 分析总结

### 主要发现
- {finding_1}
- {finding_2}

### 推荐深入
- {recommendation_1}
- {recommendation_2}

---

## 关键词云

```
{generated_keywords}
```
```

---

## 五、Skill 封装

### info-tracker Skill 扩展

```yaml
# ~/.claude/skills/bilibili-analyzer/SKILL.md

---
name: bilibili-analyzer
description: 分析B站视频，提取关键信息并生成结构化报告。支持关键词搜索、UP主可信度评估、AI摘要。
user-invocable: true
argument-hint: "<关键词或BV号列表>"
triggers:
  - "分析b站"
  - "bilibili分析"
  - "b站视频"
  - "analyze bilibili"
---

# B站视频分析器

## 功能

1. 关键词搜索 → 发现相关视频
2. 可信度评估 → 筛选高质量内容
3. 内容提取 → 字幕/简介获取
4. AI总结 → 结构化摘要
5. 价值判断 → 是否值得深入

## 使用方式

```bash
# 搜索分析
/bilibili-analyzer Claude Agent

# 指定视频
/bilibili-analyzer BV1xx411c7mC,BV1yy411c7mD

# 指定UP主最近视频
/bilibili-analyzer --uploader 12345678
```

## 输出

Markdown 报告，包含：
- 视频列表和可信度评分
- 核心观点摘要
- 技术价值判断
- 是否值得深入建议
```

---

## 六、性能优化

### 并发处理

```python
import asyncio

async def batch_analyze(bvids: list[str], max_concurrent: int = 5):
    """批量分析视频，控制并发数"""

    semaphore = asyncio.Semaphore(max_concurrent)

    async def analyze_with_limit(bvid):
        async with semaphore:
            return await analyze_single_video(bvid)

    results = await asyncio.gather(*[
        analyze_with_limit(bvid) for bvid in bvids
    ])

    return results
```

### 缓存策略

```python
from functools import lru_cache
import time

# UP主信息缓存（1小时）
@lru_cache(maxsize=100)
def get_cached_uploader_info(mid: int, cache_time: int):
    """
    缓存UP主信息

    cache_time: 缓存时间戳（用于控制过期）
    """
    # 实际获取逻辑
    return fetch_uploader_info(mid)

def get_uploader_with_cache(mid: int):
    """带缓存的UP主信息获取"""
    cache_time = int(time.time() / 3600)  # 每小时更新
    return get_cached_uploader_info(mid, cache_time)
```

---

## 七、错误处理

### 常见错误和处理

| 错误 | 原因 | 处理 |
|------|------|------|
| 视频无字幕 | UP未上传字幕 | 使用简介替代 |
| UP主信息获取失败 | 隐私设置 | 跳过可信度评估 |
| API 限流 | 频率过高 | 添加延时重试 |
| 视频已删除 | 链接失效 | 跳过该视频 |

```python
async def safe_analyze_video(bvid: str) -> dict | None:
    """安全的视频分析，捕获异常"""

    try:
        return await analyze_video(bvid)
    except VideoNotFoundError:
        logger.warning(f"视频已删除: {bvid}")
        return None
    except RateLimitError:
        await asyncio.sleep(60)
        return await analyze_video(bvid)
    except Exception as e:
        logger.error(f"分析失败 {bvid}: {e}")
        return None
```

---

## 八、扩展能力

### 支持更多输入类型

```python
async def analyze(input_type: str, input_value: str):
    """
    统一分析入口

    Args:
        input_type: keyword | bvid | uploader | url
        input_value: 对应的值
    """

    if input_type == "keyword":
        return await analyze_by_keyword(input_value)

    elif input_type == "bvid":
        return await analyze_by_bvids(input_value.split(","))

    elif input_type == "uploader":
        return await analyze_uploader_recent(int(input_value))

    elif input_type == "url":
        bvid = extract_bvid_from_url(input_value)
        return await analyze_single_video(bvid)
```

### 导出格式

```python
def export_report(report: dict, format: str = "markdown"):
    """
    导出报告

    Args:
        format: markdown | json | html | pdf
    """

    if format == "markdown":
        return generate_markdown(report)
    elif format == "json":
        return json.dumps(report, ensure_ascii=False, indent=2)
    elif format == "html":
        return generate_html(report)
    elif format == "pdf":
        return generate_pdf(report)
```

---

## 九、决策点

| 决策点 | 选项 | 建议 |
|--------|------|------|
| 字幕来源 | 自动生成 vs 手动上传 | 优先手动，备选自动 |
| 并发数 | 5 vs 10 vs 20 | 5（避免限流）|
| 缓存时效 | 1小时 vs 24小时 | UP主信息1h，视频信息24h |
| 输出格式 | Markdown vs JSON | Markdown（人类可读）|

---

## 十、与信息源系统集成

```python
# 在 information-tracking-design.md 中

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

---

*设计时间：2026-04-19*
