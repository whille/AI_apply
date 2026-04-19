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

### Task 2: B站信息获取 ✅

**调研内容**：
- B站 API 是否开放？
- 第三方库（如 bilibili-api）
- 获取 UP 主信息、判断知名度

**核心发现**：
| 能力 | 方法 | 支持情况 |
|------|------|----------|
| 用户基本信息 | `User.get_user_info()` | ✅ |
| 粉丝/关注数 | `User.get_relation_info()` | ✅ |
| UP 主统计 | `User.get_up_stat()` | ✅ |
| 视频信息 | `Video.get_info()` | ✅ |

**库信息**：
- 仓库：github.com/Nemo2011/bilibili-api
- Stars：3,826
- 特点：全异步、维护活跃

**推荐方案**：使用 bilibili-api 库，计算 UP 主信服力分数

**调研状态**：✅ 已完成

**详细文档**：[docs/skills/bilibili-api.md](./docs/skills/bilibili-api.md)

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

### Task 4: 自我进化设计 ⏳

**设计内容**：
- 调研 Hermes 自我进化机制
- 定义 Agent 自我进化适用场景
- 设计进化触发机制和验证流程

**核心问题**：
- 是否需要 Agent 自我进化？
- 适用场景是什么？
- 如何保证进化不退化？

**调研状态**：⏳ 待讨论

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

1. ✅ 调研 B站信息获取方案 → bilibili-api 库可用
2. ⏳ 讨论：是否需要自我进化能力？
3. 验证已有 Skills 效果

## 状态

- 状态：调研完成，待决策自我进化
- 更新时间：2026-04-19
