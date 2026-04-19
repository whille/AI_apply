# Claude 内置能力使用手册

> 原生功能的高效使用指南，随版本更新可能过时

## 文档索引

| 文档 | 内容 | 最后更新 |
|------|------|----------|
| [claude_init.md](./claude_init.md) | 安装配置、ECC 插件、MCP | 2026-03-30 |
| [claude_use.md](./claude_use.md) | 日常使用技巧、命令速查 | 2026-03-30 |
| [ECC_use.md](./ECC_use.md) | ECC 插件高级功能 | 2026-03-30 |
| [cursor.md](./cursor.md) | Cursor IDE 使用 | 2025-09 |

---

## 核心命令速查

| 命令 | 功能 |
|------|------|
| `/help` | 查看帮助 |
| `/compact` | 压缩上下文 |
| `/memory` | 管理记忆 |
| `/plan` | 进入计划模式 |
| `/tasks` | 查看后台任务 |

---

## 内置能力清单（无需扩展）

| 能力 | 说明 | 使用方式 |
|------|------|----------|
| 文件搜索 | Glob/Grep | 直接用，无需配置 |
| 代码编辑 | Edit/Write | 直接用 |
| 网页获取 | WebFetch | 直接用 |
| 多 Agent 并行 | Agent tool | 直接用 |
| 结构化提问 | AskUserQuestion | 直接用 |
| 代码重构 | 内置 reasoning | 直接用 |

---

## 版本说明

- 这些文档描述的是 Claude Code 内置功能
- 随 Claude 版本更新可能过时
- 如有冲突以官方文档为准
