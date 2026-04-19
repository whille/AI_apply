# 前沿跟踪

> 信息获取与技术辨识 - 需调研后确定方案

## 问题清单

- 怎么跟踪前沿 AI 技术？YouTube、X、B站？
- 怎么快速分辨技术含金量？
- 如何避免信息过载？
- 怎么从视频/公众号内容提取关键价值？

---

## Gap 分析

| 需求 | 原生能力 | Gap |
|------|----------|-----|
| 网页阅读 | WebFetch ✅ | 无 |
| RSS 订阅 | ❌ | 需 MCP 或外部工具 |
| YouTube 字幕 | ❌ | 需工具（暂缓，需代理） |
| B站字幕 | ❌ | 需工具 |
| Twitter/X 订阅 | ❌ | 需工具 |

---

## 调研任务

### Task 1: YouTube 字幕提取 ✅

**调研内容**：
- yt-dlp 是否支持字幕下载？ ✅ **支持**
- YouTube Data API 可用性？ → 不需要，yt-dlp 已覆盖
- 是否需要 Whisper 转录？ → **备选方案**，优先 yt-dlp

**核心发现**：
| 能力 | 支持情况 | 命令 |
|------|----------|------|
| 手动上传字幕 | ✅ | `--write-subs` |
| 自动生成字幕 | ✅ (仅YouTube) | `--write-auto-subs` |
| 中文字幕 | ✅ | `--sub-langs zh` |
| 字幕格式选择 | ✅ | `--sub-format srt` |

**常用命令**：
```bash
# 查看可用字幕
yt-dlp --list-subs "URL"

# 下载中文字幕
yt-dlp --write-subs --sub-langs zh --skip-download "URL"

# 下载自动生成字幕
yt-dlp --write-auto-subs --sub-langs zh --skip-download "URL"

# 使用代理
yt-dlp --proxy socks5://127.0.0.1:1080 --write-subs --sub-langs zh "URL"
```

**决策**：封装为 CLI Skill（推荐），MCP Server 成本高，手动使用效率低

**调研状态**：✅ 已完成

**详细文档**：[docs/skills/youtube-subtitle.md](./docs/skills/youtube-subtitle.md)

---

### Task 2: B站字幕提取

**调研内容**：
- B站 API 是否开放字幕？
- 第三方工具（如 bilibili-API-collect）
- 是否需要 Whisper 转录？

**调研状态**：⏳ 待开始

---

### Task 3: RSS 订阅 ✅

**调研内容**：
- 是否需要自研 MCP？
- 现有 RSS MCP 可用性？

**核心发现**：
| 项目 | 结果 |
|------|------|
| 官方 MCP Servers | ❌ 无 RSS 实现 |
| 社区 MCP Servers | ❌ 无 RSS 实现 |
| Python feedparser | ✅ 成熟稳定 |
| 自研工作量 | 约 1-2 天 |

**决策**：自研轻量级 RSS MCP Server，核心功能约 200 行 Python

**调研状态**：✅ 已完成

**详细文档**：[docs/skills/rss-subscription.md](./docs/skills/rss-subscription.md)

---

## 信息源分层（待工具确定后填充）

```yaml
core_sources:
  twitter:
    - handle: "@anthropicai"
      priority: P0
  blogs:
    - name: "Anthropic Blog"
      url: "https://anthropic.com/research"
      priority: P0

video_sources:
  youtube:
    - channel: "Andrej Karpathy"
      priority: P0
  bilibili:
    - channel: "待补充"
      priority: P1
```

---

## 下一步

1. 执行调研任务，确定可用工具
2. 设计 MCP 或 skill 流程
3. AI 开发落地
4. 验证效果

## 状态

- 状态：待调研
- 更新时间：2026-04-19
