---
name: intel
version: 1.0.0
description: 持续信息跟踪与情报收集。扫描 B站/GitHub/RSS 等多源信息，自动去重、评分、筛选。
user-invocable: true
argument-hint: "[scan <主题>] 或 [bilibili|github|rss] <关键词>"
triggers:
  - "情报收集"
  - "信息跟踪"
  - "intel"
  - "信息源监控"
  - "持续跟踪"
  - "scan"
last_updated: 2026-04-19
---

# Intel

持续信息跟踪与情报收集工具，参考 [Horizon](https://github.com/Thysrael/Horizon) 架构设计。

---

## 使用方式

### 扫描主题

```bash
/intel scan Claude Agent
```

多源搜索并生成报告。

### 单源扫描

```bash
# B站关键词
/intel bilibili Claude Agent

# GitHub Trending
/intel github trending

# RSS 订阅
/intel rss https://example.com/feed
```

---

## 工作流程

```
输入关键词
    │
    ▼
┌─────────────────┐
│ 1. 多源扫描      │
│ - B站 bilibili-api│
│ - GitHub gh CLI  │
│ - RSS WebFetch   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. 去重合并      │
│ - URL 去重       │
│ - 内容去重       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. 质量评分      │
│ - 来源可信度     │
│ - 内容质量       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. TopN 筛选    │
│ - 默认 Top 10    │
│ - 可配置         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. 生成报告      │
│ - Markdown 格式  │
│ - 导入 Wiki      │
└─────────────────┘
```

---

## B站集成

委托 `bilibili-analyzer` 处理：

```bash
/intel bilibili Claude Agent
  │
  └──▶ /bilibili-analyzer Claude Agent
           │
           └──▶ 返回可信度评分的视频列表
```

---

## 与 Horizon 对比

| 特性 | Horizon | intel |
|------|---------|-------|
| 多源聚合 | ✅ 5源 | ✅ 4源 |
| AI 评分 | ✅ 0-10分 | ✅ 0-100分 |
| B站支持 | ❌ 无 | ✅ 完整支持 |
| 部署 | GitHub Pages | 本地 MD |

**intel 优势**：专注中文生态，B站完整支持。

---

## 详细设计

- [架构设计](../docs/information-tracking-design.md)
- [评分算法](../docs/information-tracking-design.md#可信度评估模型)
- [配置文件](../docs/information-tracking-design.md#用户配置)
