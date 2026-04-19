# AI Apply - 扩展能力方法论

> 原生做不到的，才需要设计和实现

## 定位

**AI_apply 只关注"需扩展自研的能力"**：
- 原生能力不够好，需要 skill/rules/hook 增强
- 原生完全不做，需要 MCP/外部工具补足
- 原生有但场景复杂，需要流程设计

**不包含**：
- Claude Code 使用技巧 → [use_raw/](./use_raw/)
- 原生可直接做的事 → 直接用

---

## 能力分层

| 层级 | 定义 | 文档位置 |
|------|------|----------|
| **原生能力** | 开箱即用 | [use_raw/](./use_raw/) |
| **扩展能力** | skill/rules/hook | 本目录 |
| **外部能力** | MCP/自研工具 | 本目录 + 设计文档 |

---

## 模块导航

| 模块 | 文件 | 状态 | 描述 |
|------|------|------|------|
| **能力生命周期** | [00_capability_lifecycle.md](./00_capability_lifecycle.md) | draft | 判断边界，什么需要扩展 |
| **前沿跟踪** | [01_tracking.md](./01_tracking.md) | 待设计 | 信息源管理，需调研工具 |
| **Harness 配置** | [05_harness.md](./05_harness.md) | draft | skill/rules/hook 已有配置 |
| **学习与吸收** | [09_learning_absorption.md](./09_learning_absorption.md) | draft | 项目学习流程 + 工具调研 |

### 已有 Skill 扩展

| Skill | 用途 | 位置 |
|-------|------|------|
| **dependencies-analyzer** | 从 Markdown 提取任务，分析依赖，生成 DAG 执行计划 | `~/.claude/skills/dependencies-analyzer/` |

### 待设计模块

| 模块 | 优先级 | Gap | 下一步 |
|------|--------|-----|--------|
| Log 分析 | P1 | 无现成工具 | 设计 skill |
| 功能验收 | P2 | 无现成工具 | 设计流程 |
| 信息源跟踪 | P2 | 多工具组合 | 调研后设计 |

---

## 开发流程

```
1. 识别 Gap（原生能不能做）
2. 调研现有工具（能否直接用）
3. 设计方案（skill/MCP/流程）
4. AI 开发落地
5. 验证效果
```

### 示例：前沿跟踪模块

```
Step 1: Gap 分析
  - 原生能获取网页？能
  - 原生能订阅更新？不能
  - 原生能提取视频字幕？不能

Step 2: 工具调研
  - YouTube 字幕：yt-dlp 可用
  - B站字幕：需调研 API
  - 公众号：需特殊工具
  - RSS 订阅：可自研 MCP

Step 3: 设计方案
  - [ ] 调研 yt-dlp 用法
  - [ ] 设计 MCP 或 skill
  - [ ] 输出到 01_tracking.md

Step 4: AI 开发落地
  - 根据设计文档，让 AI 实现
```

---

## 使用方式

```bash
# 让 AI 读取设计文档后实现
请根据 AI_apply/01_tracking.md 的设计，调研可用工具

# 让 AI 继续开发某个模块
请继续完善 AI_apply/05_harness.md
```

---

## 元信息

- **创建时间**: 2026-04-19
- **状态**: draft
- **原则**: 原生能做的不扩展，只设计必须扩展的
