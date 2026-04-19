# AI Apply

> 扩展 AI 能力的设计和方法论

---

## 项目结构

```
AI_apply/
├── skills/                    # 自研 Skills（Git 追踪）
│   ├── info-tracker/         # 信息源跟踪
│   ├── bilibili-analyzer/    # B站视频分析
│   ├── log-analyzer/         # 日志分析
│   └── test-case-generator/  # 测试用例生成
├── hooks/                     # 自研 Hooks
│   └── review-trigger.py    # 代码提交前安全扫描
├── docs/                      # 设计文档
│   ├── skills/               # 工具调研文档
│   ├── skill-evaluation.md   # 效果评估方法
│   ├── self-evolution-design.md
│   ├── information-tracking-design.md
│   ├── bilibili-workflow.md
│   └── auto-review-design.md
├── templates/                 # 项目模板
│   └── project-init/
├── link-skills.sh            # 软链接脚本
└── prd.json                  # 项目需求文档
```

---

## 快速开始

### 1. Clone 项目

```bash
git clone https://github.com/whille/AI_apply.git
cd AI_apply
```

### 2. 创建软链接

```bash
# 将自研 Skills 软链接到 ~/.claude/skills/
./link-skills.sh
```

这会将 AI_apply 的 Skills 链接到 Claude Code 的全局 Skills 目录：

```
~/.claude/skills/info-tracker     → AI_apply/skills/info-tracker
~/.claude/skills/bilibili-analyzer → AI_apply/skills/bilibili-analyzer
~/.claude/skills/log-analyzer      → AI_apply/skills/log-analyzer
~/.claude/skills/test-case-generator → AI_apply/skills/test-case-generator
```

### 3. 使用 Skills

软链接创建后，在任何项目中都可以使用：

```bash
/info-tracker daily              # 每日信息扫描
/info-tracker bilibili Claude    # B站关键词搜索

/bilibili-analyzer Claude Agent  # 分析B站视频

/log-analyzer /var/log/          # 分析日志

/test-case-generator file.py    # 生成测试用例
```

---

## Skills 说明

### info-tracker

统一信息源跟踪，整合 B站/GitHub/RSS。

```bash
/info-tracker [daily|weekly]           # 定时扫描
/info-tracker bilibili <关键词>         # B站搜索
/info-tracker github trending          # GitHub Trending
/info-tracker rss <URL>                 # RSS 订阅
```

### bilibili-analyzer

B站视频分析和可信度评估。

```bash
/bilibili-analyzer <关键词>             # 关键词搜索分析
/bilibili-analyzer --uploader <UID>    # 分析UP主视频
/bilibili-analyzer <BV号>              # 分析指定视频
```

### log-analyzer

日志分析和根因定位。详见 `skills/log-analyzer/SKILL.md`。

### test-case-generator

测试用例生成。详见 `skills/test-case-generator/SKILL.md`。

---

## 维护说明

### Skills 维护

在 `AI_apply/skills/` 目录修改 Skills，软链接自动生效。

### ~/.claude 维护

`~/.claude` 是独立的 git 仓库（myclaude），管理个人配置。

- omc 安装的 Skills：保持在 `~/.claude/skills/`（不 git 追踪）
- 自研 Skills：通过软链接指向 AI_apply（git 追踪）

---

## 设计文档

| 文档 | 描述 |
|------|------|
| [docs/skills/](docs/skills/) | 工具调研（yt-dlp, bilibili-api, RSS） |
| [docs/skill-evaluation.md](docs/skill-evaluation.md) | Skills 效果评估方法 |
| [docs/self-evolution-design.md](docs/self-evolution-design.md) | Hermes Agent 自我进化调研 |
| [docs/information-tracking-design.md](docs/information-tracking-design.md) | 信息源跟踪系统设计 |
| [docs/bilibili-workflow.md](docs/bilibili-workflow.md) | B站视频分析流程 |
| [docs/auto-review-design.md](docs/auto-review-design.md) | 自动代码审查机制 |

---

## 项目状态

- **任务数**: 14/14 完成
- **Skills**: 4 个已实现
- **决策点**: 全部解决

详见 [prd.json](prd.json)。
