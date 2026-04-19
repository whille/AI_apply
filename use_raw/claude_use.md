# Claude Code 高效使用指南

> **定位：日常使用技巧手册**
> 整理自多个优秀资源的最佳实践 | 更新日期: 2026-03-30
>
> **相关文档：**
> - `claude_init.md` - 安装配置
> - `ECC_use.md` - ECC 插件高级功能

---

## 一、核心命令速查

| 命令 | 功能 |
|------|------|
| `/help` | 查看帮助 |
| `/usage` | 查看使用限额和重置时间 |
| `/stats` | 查看使用统计和活动图 |
| `/clear` | 清空重新开始 |
| `/compact` | 压缩对话释放上下文空间，可接侧重点描述 |
| `/context` | 查看当前上下文占用情况 |
| `/memory` | 查看/编辑记忆文件 |
| `/copy` | 复制最后回复到剪贴板 |
| `/plan` | 进入计划模式 |
| `/mcp` | 管理 MCP 服务器 |
| `/tasks` | 查后台任务进度 |
| `/rewind [n]` | 撤销最近 n 轮对话 |
| `/add-dir ./path` | 选择性添加目录 |

---

## 二、多 Agent 并行执行

### 操作示例

**后台执行 + 前台对话：**
```
后台运行 npm test，同时我们讨论下一个功能的实现方案
```

**并行子代理：**
```
同时启动三个子代理：
1. 分析前端模块架构
2. 分析后端 API 设计
3. 分析数据库结构
最后汇总成一份架构报告
```

**高效做法：**
```
我需要重构用户模块，请：
1. 后台启动一个 agent 分析现有代码结构
2. 后台启动另一个 agent 搜索相关测试用例
3. 同时我们讨论重构方案的设计
等两个 agent 完成后，汇总信息开始重构
```

### 并行执行最佳实践

| 场景 | 推荐方式 |
|------|---------|
| 长时间测试/构建 | `run_in_background: true` |
| 代码搜索/分析 | 后台 Agent + 前台讨论 |
| 多模块并行审查 | 多个后台子代理 |
| Git worktree 并行开发 | 多终端窗口 |

---

## 三、最佳实践清单

- [ ] 创建项目级 `CLAUDE.md` 配置（200行内）
- [ ] 大任务拆分为小步骤
- [ ] 定期 `/compact` 管理上下文
- [ ] 后任务 + 前台对话并行工作
- [ ] 不相关任务分开会话
- [ ] 提供验证方式（测试、截图、预期输出）
- [ ] 大型功能先用采访模式对齐需求

### 采访模式：用苏格拉底式提问对齐需求

对于大型功能，让 Claude 先采访你以明确需求，而不是一开始就写代码。

**AskUserQuestion 工具** 是内置的交互工具，会弹出结构化选择题界面——不需要打字，只需点击选项。

**标准提示模板**
```
我想构建 [简要描述]。用 AskUserQuestion 工具对我进行详细采访。
问我关于技术实现、UI/UX、边界情况、顾虑和权衡的问题。
不要问显而易见的问题，深入挖掘我可能没有考虑到的困难部分。
持续采访直到我们覆盖了所有方面，然后把完整的需求规格写入 SPEC.md。
```

**实战示例：**
```
我想开发一款独特的小游戏，但具体做什么、怎么做还没想好。
请你作为游戏策划顾问，用苏格拉底式提问法帮我从零厘清思路。要求：
- 必须使用 AskUserQuestion 工具向我提问，不要用纯文字提问
- 每轮提问后，根据我的回答总结洞察，再发起下一轮提问
- 至少覆盖以下维度：游戏类型、核心玩法、美术风格、目标平台、技术方案
- 3-5 轮提问结束后，输出一份「游戏设计一页纸」
```

**引申用法 - 排查盲区：**
```
对于这个问题，我们还有哪些没有考虑到的？
使用 AskUserQuestion 工具，像苏格拉底一样帮助我，
无论是技术选型、潜在风险、需求对齐等等任何方向。
```

**适用环境：** IDE Extension 和 CLI 都可用。CLI 中用键盘上下箭头选择选项。

**最佳实践：** 完成采访后，开一个新会话来执行规格。新会话有干净的上下文，完全聚焦于实现。

---

## 四、关键原则总结

| 原则 | 说明 |
|------|------|
| 任务隔离 | 不相关任务分开会话 |
| 及时压缩 | 主动使用 `/compact` |
| 精简 CLAUDE.md | 保持 200 行以内 |
| 提供验证 | 给出测试或预期输出 |
| 早纠正 | 按 Esc 中断，两次 Esc 或 `/rewind` 恢复 |
| 优先级叠加 | 更具体的层级覆盖高层级（类似 Git） |
| 并行思维 | 后台执行 + 前台讨论 |

---

## 五、Claude 内置核心功能

### Extended Thinking（深度推理）

| 特性 | 说明 |
|------|------|
| **功能** | 回答前先内部思考，再输出结果 |
| **默认** | 开启，最多 31999 tokens 思考空间 |
| **切换** | `Option+T` (macOS) / `Alt+T` (Windows/Linux) |
| **查看思考** | `Ctrl+O` 显示/隐藏思考过程 |

**适用场景：**
- ✅ 复杂架构决策、代码重构、调试复杂问题
- ⚠️ 简单任务可关闭节省 token

**配置方式：**
```json
// ~/.claude/settings.json
{ "alwaysThinkingEnabled": true }
```
```bash
# 限制思考 token 数量
export MAX_THINKING_TOKENS=10000
```

### Auto Memory（自动记忆）

| 特性 | 说明 |
|------|------|
| **功能** | 跨会话持久化存储知识 |
| **位置** | `~/.claude/projects/<project>/memory/` |
| **主文件** | `MEMORY.md` - 快速索引 |
| **专题文件** | `patterns.md`, `debugging.md` 等 |

**使用方式：**
```
/memory           # 查看记忆文件
/memory edit      # 编辑记忆
```

**最佳实践：**
- `MEMORY.md` 保持简洁，作为索引
- 详细内容放专题文件（patterns.md, debugging.md）
- 不重复存储，通过引用链接

---

## 六、Worktree 并行开发

### 核心概念

Git worktree 让同一仓库的多个分支可以同时 checkout 到不同目录，实现真正的并行开发。

### 使用场景

| 场景 | 说明 |
|------|------|
| 紧急修复 | 在 feature 分支开发时，快速切换到fix |
| 对比测试 | 两个分支同时运行，对比行为差异 |
| 多 Claude 实例 | 每个 worktree 独立 Claude 会话，互不干扰 |

### 常用命令（可让 Claude 执行）

| 操作 | 描述性提示词 |
|------|-------------|
| 创建 worktree | "创建一个 worktree，目录名 xxx，基于 xxx 分支" |
| 列出 worktree | "列出所有 worktree" |
| 删除 worktree | "删除 xxx 目录的 worktree" |

### 重要注意事项

| 事项 | 说明 |
|------|------|
| ❗ 正确清理 | 必须用 `git worktree remove`，直接 `rm -rf` 会残留元数据 |
| ❗ 分支互斥 | 同一分支不能同时在多个 worktree 中 checkout |
| ⚠️ Docker 路径 | 使用 Docker 时注意路径绑定变化 |
| 💡 命名规范 | 建议用 `wip/`、`exp/`、`tmp/` 前缀标识用途 |

### 场景化提示词

**场景 1：紧急修复（开发切出热修复）**
```
我在 feature/user-dashboard 分支开发中，需要紧急 production 的登录。
帮我：
1. 创建一个 worktree 在 .claude/worktrees/hotfix-login 目录
2. 切换到 main 分支并拉取最新代码
3. 创建 hotfix/login-bug 分支
完成后告诉我下一步操作
```

**场景 2：对比测试两个分支**
```
帮我对比 feature/new-api 和 main 分支的 响应：
1. 创建两个临时 worktree
2. 分别启动两个实例
3. 告诉我如何对比测试
```

**场景 3：并行开发多功能**
```
我需要同时开发两个独立功能（认证优化 + 数据导出）。
帮我：
1. 为每个功能创建独立的 worktree
2. 创建对应的 feature 分支
3. 告诉我两个的工作目录
```

**场景 4：清理完成的 worktree**
```
列出所有 worktree，帮我清理已经合并分支的 worktree
```

**场景 5：正确清理（强调用法）**
```
帮我清理 experiment-xxx 这个 worktree，注意用 git worktree remove 命令
```

### Claude Code 配合

每个 worktree 有独立的 memory 目录，互不影响。

**最佳实践：**
- Worktree 目录放在 `.claude/worktrees/` 下（自动 gitignore）
- 完成后记得将有用记忆迁移回主 worktree
- 用 `wip/` 前缀标识实验性工作，`exp/` 前缀标识尝试性探索
- 清理时用 `git worktree remove` 而非直接删除目录

---

## 七、Auto Memory 最佳实践

### 目录结构

```
~/.claude/projects/<project>/memory/
├── MEMORY.md          # 索引文件（前 200 行自动加载）
├── patterns.md        # 代码模式笔记
├── debugging.md       # 调试经验
└── api-conventions.md # API 设计决策
```

### 核心原则

| 原则 | 说明 |
|------|------|
| **黄金区域** | MEMORY.md 前 200 行每次会话自动加载 |
| **索引模式** |.md 只放索引，详细内容放 topic 文件 |
| **不重复** | 不重复项目文档，通过引用链接 |
| **分类存储** | 团队规范 → CLAUDE.md；个人经验 → Auto Memory |

### 使用命令

```
/memory           # 查看记忆文件路径
/memory edit      # 编辑记忆
```

### 关闭自动记忆

```json
// ~/.claude/settings.json
{ "autoMemoryEnabled": false }
```

> CI/CD 环境建议关闭，避免污染 runner

---

## 八、Fan-out 批量处理

### 核心概念

用脚本驱动多个 Claude 实例，批量处理多个文件或任务。

### 场景化提示词

**场景 1：批量迁移文件
```
帮 files.txt 中列出的所有文件从 React 迁移到 Vue。
每个文件独立处理，完成后报告成功/失败状态。
```

**场景 2：批量代码审查**
```
审查 main 分支相比的所有修改文件的安全问题。
每个文件输出：PASS/FAIL + 简要原因。
最后汇总问题文件列表。
```

**场景 3：批量生成**
```
为 src/api/ 目录下的每个文件生成 API 文档。
输出到 docs/api/ 目录，保持相同文件名。
```

**场景 4：批量测试执行**
```
对 components/ 目录下的每个组件运行测试。
收集所有失败的测试，汇总成报告。
```

### 关键参数（让 Claude 使用）

| 参数 | 说明 |
|------||
| 非交互模式 | 让 Claude 自动执行不等待确认 |
| 预批准工具 | 提前允许 Edit 和 git 操作 |
| JSON 输出 | 结果格式化便于后续处理 |
| 自动模式 | 减少权限中断 |

### 适用场景

- 批量迁移
- 批量代码审查
- 批量文档生成
- 批量测试执行

---

## 九、长时间运行的任务

### 后台执行

**提示词示例：**
```
后台运行 npm run build，同时我们讨论下一步计划
```

```
后台完整测试套，同时帮我审查这个 PR
```

### tmux 场景化提示词

**场景 1：创建隔离会话**
```
帮我创建一个名为 "build" 的 tmux 会话，在里面运行构建命令。
告诉如何分离和重新连接。
```

**场景 2：多任务**
```
帮我启动两个 tmux 会话：
1. "test" 会话运行测试套件
2. "lint"话运行 lint 检查
告诉我如何查看进度。
```

**场景 3：恢复断开的任务**
```
列出所有 tmux 会话，帮我恢复到 "" 会话查看进度
```

### 后台任务管理

| 命令 | 描述性提示词 |
|------|-------------|
| `/tasks` | "查看后台任务进度" |
| `/tasks <id>` | "查看 xxx 任务的详情" |

### Agent 后台运行

```
后台启动一个 agent 分析整个代码库依赖关系，完成后汇总报告
```

**最佳实践：**
- 长时间任务始终后台运行
- 用 "查看后台任务进度" 定期检查
- 超长任务用 tmux 会话托管

### 自主循环（Autonomous Loop）

对于需要多轮迭代、自我修正的超长任务，使用自主循环插件。

#### ralph-loop（官方插件）

**场景：** 单一任务多轮迭代，直到完成

**场景化提示词：**
```
启动 ralph-loop，任务是：修复所有 lint 错误。
最多迭代 10 次，完成后输出 <promise>DONE</promise>
```

```
启动 ralph-loop，任务是：实现 OAuth2 登录功能。
完成后输出 <promise>TASK COMPLETE</promise>
```

**关键参数：**
| 参数 | 说明 |
|------|------|
| `--max-iterations N` | 最大迭代次数 |
| `--completion-p "文本"` | 完成信号，必须输出 `<promise>文本</promise>` |

**取消循环：**
```
取消当前的 ralph-loop
```

#### ECC Loop Operator（ECC 插件）

**场景：** 复杂多单元项目，需要质量门控和监控

**场景化提示词：**
```
启动 loop-operator，模式是 continuous-pr。
帮我设置质量门控和分支隔离。
```

**循环模式：**
| 模式 | 说明 |
|------||
| `sequential` | 顺序执行，适合单文件变更 |
| `continuous-pr` | 持续 PR 循环，适合多天项目 |
| `rfc-dag` | RFC 驱动的 DAG 编排，适合大型功能 |
| `infinite` | 无限循环，适合内容生成 |

**选择建议：**
| 任务类型 | 推荐方案 |
|----------|----------|
| 单一任务自我修正 | ralph-loop |
| 多天迭代项目 | continuous-pr |
| 大型功能（多单元） | rfc-dag |
| 批量内容生成 | infinite |

---

## 十、GitHub Actions 集成

### Claude GitHub App 概述

**GitHub App 不是本地软件**，它是 GitHub 平台上的"机器人账号"，安装到你的仓库中。

### 安装步骤

1. 访问://github.com/apps/claude
2. 点击 "Install"
3. 选择要安装的仓库（私有库/公开库均可）
4. 配置 `ANTHROPIC_API` 到仓库 Secrets

**快速命令：**
```
/install-github-app
```

### 工作原理`
评论: "@claude 修复这个 bug"
         ↓
GitHub 检测到触发词
         ↓
启动 .github/workflows/claude.yml
         ↓
GitHub Actions Runner（云端虚拟机）执行
         ↓
Claude 读取 Issue → 搜索代码 → 生成修复 → 创建 PR
``

### 工作流配置示例

**基础 @claude 响应**（`.github/workflows/claude.yml`）：
```yaml
name: Claude Code
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
jobs:
  claude:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntuatest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

**自动 PR 审查**：
```yaml
name: Claude PR Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "/review"
          claude_args: "--max-turns 5"
```

**Issue 自动修复**（打标签触发）：
```yaml
name: Claude Fix Issue
on:
  issues:
    types: [labeled]
jobs:
  fix:
    if: github.event.label.name == 'claude-fix'
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            修复 Issue #${{ github.event.issue.number }}。
            读取 Issue → 搜索 → 实现修复 → 编写测试 → 创建 PR
          claude_args: "--max-turns 15"
```

### 触发方式对比

|发方式 | 谁触发 | 示例 |
|---------|--------|------|
| **@ude** | 人工手动 | 评论 `@claude 修复这个bug` |
| **自动触发** | GitHub 事件 | PR 创建时、Issue 打标签时

### 在 PR/Issue 中使用

```
@claude 根据 Issue 描述实现这个功能
@claude 修复用户面板组件中的 TypeError
@claude 审查这个 PR 的安全性
```

### 私有库支持

| 功能 | 私有库 | 公开库 |
||--------|--------|
| 安装 GitHub App | ✅ | ✅ |
| @claude 触发 | ✅ | ✅ |
| Actions 运行 | ✅ | ✅ |

**注意：** 私有库消耗 GitHub Actions 免费分钟数（Free 账户 2000 分钟/月）

### 已知限制

> ⚠️ **Claude GitHub App 不支持 push 事件触发**
>
> 如需 push 触发（如自动修复 lint 错误），需在 runner 中手动安装 Claude CLI 并配置环境变量。

---

---

## 十一、MCP Skill 配置

### 核心区别

| 对比项 | MCP | Skill |
|--------|-----|-------|
| **本质** | 运行中的进程 | 静态文档（Markdown） |
| **加载时机** | 会话启动时全部加载 | 匹配触发时才加载 |
| **内存占用** | 常驻（每个 500-2000 tokens） | 未激活 = 0 |
| **数量建议** | 5-10 个为宜 | 无上限 |

### 为什么 MCP 要常驻

```
Claude 启动时必须知道所有可用工具的定义：

MCP供的工具列表 写入系统提示词 → Claude 才知道能调用什么

每个工具定义约 200-500 tokens：
{
  "name": "web_search",
  "description": "...",
  "parameters": {...}
}
```

### 为什么 Skill 不需要常驻

```
Skill 只是磁盘上的 SKILL.md 文件：
- 未激活：不占内存，只是列表中的一行描述
- 激活时：读取文件内容，作为提示词注入
- 用完后：可被压缩/遗忘
```

### 类比

| 类型 | 类比 |
|------|------|
| **MCP** | 手机 APP（后台运行，占内存） |
| **Skill** | 书架上的书（需要时才拿） |

### 配置建议

```
MCP：精简，只装常用的
  ✅ ksc-local-mcp（本地服务）
  ✅ MiniMax（搜索）
  ⚠️ 控制在 5-10 个以内

Skill：随意装，不嫌多
  ✅ 编码规范、模式、测试...
  ✅ 上百个也没问题
```

