# Claude Code 完整初始化指南

> **定位：安装配置手册（初始化用）**
> 最后更新: 2026-03-30
>
> **相关文档：**
> - `claude_use.md` - 日常使用技巧
> - `ECC_use.md` - ECC 插件高级功能

---

## 一、前置要求

### 必装工具
```bash
git
ripgrep
jq
ruff      # Python 格式化/lint
tmux      # 长时间运行任务
```

---

## 三、安装 ECC 插件（推荐）

⭐ 115K+ stars | Anthropic Hackathon 获胜者项目

```bash
claude plugin marketplace add affaan-m/everything-claude-code
claude plugin install everything-cla-code@everything-claude-code
```

# 复制规则
> ⚠️ Claude Code 插件无法自动分发 `rules`，需手动安装
```
mkdir -p ~/.claude/rules
cp -r everything-claude-code/rules/common ~/.claude/rules/
cp -r everything-claude-code/rules/{typescript,python,golang} ~/.claude/rules/  # 按需选择
```

### Hooks 配置
将 `hooks/hooks.json` 中的内容复制到 `~/.claude/settings.json`

### MCP 配置

1. 从 `mcp-configs/mcp-servers.json` 复制所需服务器到 `~/.claude.json`
2. 替换 `YOUR_*_HERE` 占位符为实际 API 密钥


### multi-* 命令额外配置

使用 `/multi-plan`、`/multi-execute` 等命令需安装运行时：
```bash
npx ccg-workflow
```

---

## 四、配置 settings.json

编辑 `~/.claude/settings.json`：

```json
{
  "includeCoAuthoredBy": false,
  "language": "中文",
  "skipDangerousModePermissionPrompt": true,
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline-command.sh"
  },
}
```

--- 五、配置

将以下内容添加到 `~/.claude/settings.json` 的 `hooks` 字段：

```json
{
  "hooks":
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": " \"$HOME/.claude/plugins/marketplaces/everything-claude-code/scripts/hooks/run-with-flags.js\" \"pre:bash:tmux-reminder\" \"scripts/hooks/pre-bash-tmux-reminder.js\"strict\""
          }
        ],
        "description": "提醒使用 tmux 运行长时间命令"
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node \"$HOME/.claude/plugins/marketplaces/everything-claude-code/scripts/hooks/run-with-flags.js\" \"pre:bash:git-push-reminder\" \"scripts/hooks/pre-bash-git-push-reminder.js\" \"strict\""
          }
        ],
        "description": "git push 前提醒审查更改"
      },
      {
        "matcher": "Edit|Write
        "hooks": [
          {
            "type": "command",
            "command": "node \"$HOME/.claude/plugins/marketplaces/everything-claude-code/scripts/hooks/run-with-flags.js\" \"pre:edit-write:suggest-compact\" \"scripts/hooks/suggest-compact.js\" \"standard,strict\""
          }
        ],
        "description": "在逻辑间隔手动压缩上下文"
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "node \"$HOME/.claude/plugins/marketplaces/everything-claude-code/scripts/hooks/run-with-flags.js\" \"post:edit:format\" \"scripts/hooks/post-edit-format.js\" \"standard,strict\""
          }
        ],
        "description": "编辑后自动格式化 JS/TS 文件"
      },
      {
        "matcher": "Edit",
        "": [
          {
            "type": "",
            "command": "node \"$HOME/.claude/plugins/marketplaces/everything-claude-code/scripts/hooks/run-with-flags.js\" \"post:edit:typecheck\" \"scripts/hooks/post-edit-typecheck.js\" \"standard,strict\""
          }
        ],
        "description": "编辑 .ts/.tsx 文件后进行 TypeScript 检查
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "node \"$HOME/.claude/plugins/marketplaces/everything-claude-code/scripts/run-with-flags.js\" \"post:edit:python-format\" \"scripts/hooks/post-edit-python-format.js\" \"standard,strict\""
          }
        ],
        "description": "编辑后用 ruff 自动格式化 Python 文件"
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "node \"$HOME/.claude/plugins/marketplaces/everything-claude-code/scripts/hooks/run-with-flags.js\" \"post:edit:python-lint\" \"scripts/hooks/post-edit-python-lint.js\" \"standard,strict\""
          }
        ],
        "description":编辑后用 ruff 检查 Python 文件"
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "node \"$HOME/.claude/plugins/mplaces/every-claude-code/scripts/hooks/run-with-flags.js\" \"post:edit:doc-sync\" \"scripts/hooks/post-edit-doc-sync.js\" \"standard,strict\""
          }
        ],
        "description": "当代码更改匹配模式时建议文档更新"
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "",
            "command": "node \"$HOME/.claude/plugins/marketplaces/everything-claude-code/scripts/hooks/run-with-flags.js\" \"stop:check-console-log\" \"scripts/hooks/check-console-log.js\" \"standard,strict\""
          }
        ],
        "description": "每次响应后检查文件中的 console"
      }
    ],
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "node \"$HOME/.claude/plugins/marketplaces/everything-claude-code/scripts/hooks/run-with-flags.js\" \"session:start\" \"scripts/hooks/session-start.js\" \"minimal,standard,strict\""
          }
        ],
        "description": "新会话加载之前的上下文并检测包管理器"
      }
    ]
  }
}
```

---

## 六、配置状态栏脚本
---

## 七、配置 MCP 服务器（可选）

编辑 `~/.claude.json`，添加需要的 MCP 服务器：

### 国内可用 · 推荐

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN":你的GitHub PAT"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp", "--browser", "chrome"]
    },
    "MiniMax": {
      "command": "uvx",
      "args": ["minimax-coding-plan-mcp", "-y"],
      "env": {
        "MINIMAX_API_KEY": "你的API Key",
        "MINIMAX_API_HOST": "https://api.minimaxi.com"
      }
    }
  }
}
```

### MCP 说明

| MCP | 功能 | 国内可用 | 费用 |
|-----|------|---------|------|
| **github** | PR/Issue/代码审查 | ✅ | 免费 |
| **playwright** | 浏览器自动化/E2E测试 | ✅ | 免费 |
| **MiniMax** | 网页搜索 + 图片理解 | ✅ | 付费 |

> MiniMax 获取 API Key: https://platform.minimaxi.com


---
