# ECC 使用指南

> **定位：ECC 插件高级功能手册**
>
> **相关文档：**
> - `claude_init.md` - 安装配置
> - `claude_use.md` - 日常使用技巧

## 命令分类：主动 vs 被动

**被动技能**：配置后自动触发，无需用户调用。Instincts 自动生效。

**主动命令**：用户必须输入 `/xxx` 才能触发。

---

## 学习进化系统

### Instincts（直觉系统）

持续学习后自动应用的行为。

| 特性 | 说明 |
|------|------|
| 自动观察 | 通过 hooks 观察用户行为 |
| 置信度 | 0.3-0.9，低于阈值不应用 |
| 项目范围 | 默认项目隔离，防止污染 |
| 自动触发 | 满足触发条件时自动应用 |

**示例**：用户多次纠正代码风格后，系统自动创建 instinct，之后写代码时自动应用该风格。

### Instincts → Learn → Evolve 关系

```
用户行为纠正
      ↓
┌─────────────┐
│  Instincts  │ ← 自动观察，记录行为模式，置信度 0.3-0.9
│  (直觉)     │   自动触发应用
└──────┬──────┘
       │ 手动调用
       ↓
┌─────────────┐
│   /learn    │ ← 从当前会话可重用模式
│  (学习)     │   生成 skill 文件
└──────┬──────┘
       │ 手动调用
       ↓
┌─────────────┐
│   /evolve   │ ← 聚类多个 instincts，进化为高级结构
│  (进化)     │   生成 Command/Skill/Agent
└─────────────┘
```

**对比：**

| 功能 | 触发 | 输入 | 输出 |
|------|------|------|------|
|incts | 自动 | 用户行为观察 | 行为规则 |
| /learn | 手动 | 当前会话 | Skill 文件 |
| /evolve | 手动 | 多个 instincts | Command/Skill/Agent |

### /learn vs /skill-create

| 特性 | /learn | /skill-create |
|--------------|---------------|
| **输入源** | 当前会话内容 | Git 历史记录 |
| **分析范围** | 单次会话中的问题解决 | 整个项目的提交历史 |
| **触发时机** | 解决问题后手动调用 | 新项目/初始化时调用 |
| **提取内容** | 错误解决、调试技巧、workaround | 提交约定、架构模式、工作流 |
| **输出位置** | `~/.claude/skills/learned/` | 项目内或 `./skills/` |

**简单理解：
- **skill-create**：从历史中学习「这个项目怎么做」
- **learn**：从当前会话学习「这个问题怎么解」

---

## 核心组件

### Skills 和 Commands

工作流规则，存储在：
- `~/.claude/skills/` - 更广泛的工作流定义
- `~/.claude/commands/` - 用户可调用的命令

**核心工作流命令：**
| 命令 | 用途 |
|------|------|
| `/plan` | 重述需求、评估风险、分阶段实施。**关键**：不写代码直到确认 |
| `/tdd` | 测试驱动开发：写用户旅程 → 生成测试 → 写代码通过测试 → 重构 |
| `/code-review` | 审查代码变更，按风险分级（高/中/低），给出修复建议 |
| `/build-fix` | 修复构建错误 |
| `/verify` | 完整验证循环 |

**其他常用命令：**
| 命令 | 用途 |
|------|------|
| `/refactor-clean` | 清理死代码 |
| `/e2e` | E2E 测试 |
| `/test-coverage` | 测试覆盖率检查 |
| `/docs` | 查找文档 |
| `/aside` | 快速回答问题，不打断当前任务 | `/quality-gate` | 质量门禁 |

**链式调用：**
```
/refactor-clean && /tdd && /e2e
```

**命令类型对比：**

| 类型 | 路径 | 说明 |
|------|------|------|
| Skills | `~/.claude/skills` | 更广泛的工作流定义 |
| Commands | `~/.claude/commands` | 用户可用的命令 |

---

### Hooks（钩子）

基于触发器的自动化系统。

> 详细配置见 `claude_init.md` 五、配置 Hooks

| Hook 类型 | 触发时机 |
|----------|---------|
| PreToolUse | 工具执行前 |
| PostToolUse | 工具执行后 |
| UserPromptSubmit | 发送消息时 |
| Stop | 会话结束时 |
| PreCompact | 上下文压缩前 |
| Notification | 权限请求时 |

**实用 Hook 示例：**
- tmux 提醒：长时间运行命令前
- prettier 格式化：代码修改后
- console.log 检测：提交前

**Pro Tip：** 使用 `hookify` 插件以声明式方式创建 hooks。

---

### Subagents（子代理）

委托进程，存储在 `~/.claude/agents/`，具有有限作用域：

| Agent | 用途 |
|-------|------|
| planner | 实现规划 |
| architect | 系统设计 |
| code-reviewer | 代码审查 |
| tdd-guide | TDD 指导 |
| security-reviewer | 安全分析 |

**模型选择策略：**
| 任务 | 推荐模型 |
|------|---------|
| 探索/搜索 | Haiku |
| 多文件实现 | Sonnet |
| 复杂架构 | Opus |
| 安全分析 | Opus |

**默认：** 90% 的编码任务使用 Sonnet。

---

### Rules（规则）

最佳实践，存储在 `~/.claude/rules/` 文件夹中的 `.md` 文件：

- `security.md` - 安全规范
- `coding-style.md` - 编码风格
- `testing.md` - 测试要求
- `git-workflow.md` - Git 工作流

**示例规则：**
- 代码库中不使用 emoji
- 部署前必须测试代码
- 优先模块化代码而非巨型函数
- 永不提交 console.logs

---

## MCPs Plugins

### MCPs（模型上下文协议）

将 Claude 连接到外部服务。

> 配置示例见 `claude_init.md` 七、配置 MCP 服务器

**关键原则：**
- 保持启用 MCP < 10 个
- 保持活跃工具 < 80 个
- 用 `/mcp` 查看已启用
- 用 `/plugins` 管理

**MCP 替代方案：**
使用 CLI + skills 代替 MCP 可节省 token：
```
# 用 /gh-pr 命令包装 gh pr create，替代 GitHub MCP
```

### Plugins

安装插件：
``
/plugin marketplace add <marketplace-name>
/plugin install <plugin-name>@<marketplace-name>
```

**LSP Plugins：** 提供 IDE 级别的实时类型检查，无需运行 IDE。

**注意：** 与 MCPs 一样，注意上下文窗口占用。

---

## 上下文和记忆管理

### 会话持久化

保存会话状态到 `.claude/.tmp` 文件：
- 有效的做法（附证据）
- 失败的方法
- 剩余任务

### 动态系统提示注入

```bash
# 创建别名实现精准上下文加载
alias claude-dev='claude --system-prompt "$(cat ~/.claude/contexts/dev.md)"'
```

### 记忆 Hooks

| Hook | 作用 |
|------|------|
| PreCompact Hook | 压缩前保存状态 |
| Stop Hook | 会话结束时持久化学习内容 |
| SessionStart Hook | 加载前一个上下文 |

### 连续学习

当 Claude 重复问题时，将模式追加到 skills。使用 Stop hook（而非 UserPromptSubmit）避免延迟。

---

## Token 优化

### mgrep vs grep

使用 `/mgrep` 技能替代 grep，约减少 50% token。

### 子代理模型选择

见上方表格，默认 Sonnet。

---

## 并行化策略

### Git Worktrees 模式

> 详细使用见 `claude_use.md` 六、Worktree 并行开发

```bash
git worktree add ../project-feature-a feature-a
```

### Cascade 方法

1. 新打开到右边
2. 从左到右扫描，从旧到新
3. 最多关注 3-4 个任务

### /fork 命令

用于非重叠的并行任务。

---

## 工作流最佳实践

### 决策指南

```
需要写代码了？
  ↓
新功能/复杂任务？ → /plan 先
  ↓
写新功能？ → /tdd
  ↓
刚写完？ → /code-review
  ↓
构建失败？ → /build-fix

学习新模式？
  ↓
会话中解决问题？ → /learn
  ↓
有多个 instincts？ → /evolve
  ↓
新项目？ → /skill-create

会话管理？
  ↓
结束前 → /save-session
  ↓
继续工作时 → /resume-session
  ↓
需要多个会话 → /blueprint
```

### 两实例启动法

| 实例 | 职责 |
|------|------|
|例 1 | 脚手架（项目结构、配置） |
| 实例 2 | 深度研究（PRD、图表、文档） |

### 顺序阶段

```
Research → Plan → Implement → Review → Verify
```

### 迭代检索模式

1. 编排器评估子代理返回
2. 提出后续问题
3. 循环直到足够（最多 3 轮）

### 验证循环

- **pass@k**：k 次尝试中至少一次成功
- **pass^k**：所有 k 次尝试都必须成功

---

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+` | 删除整行 |
| `!` | 快速 bash 前缀 |
| `@` | 搜索文件 |
| `/` | 斜杠命令 |
| `Shift+Enter` | 多行输入 |
| `Tab` | 切换思考显示 |

---

## 其他实用命令

| 命令 | 用途 |
|------|------|
| `/statusline` | 自定义状态行 |
| `/checkpoints` | 文件级撤销点 |
| `/compact` | 手动触发上下文压缩 |
| `/rewind` | 回退状态 |
| `/save-session` | 保存会话 |
| `/resume-session` | 恢复会话 |
| `/sessions` | 浏览会话历史 |

---

## 作者设置

- 14 个 MCP 配，但每个项目只启用 5-6 个
- 自定义 hooks：tmux 提醒、prettier 格式化、console.log 检测
- 偏好 Zed 编辑器（Rust 速度 + Claude 集成）

---

## 代码维护与重构

### 命令工具

| 命令 | 用途 | 触发方式 |
|------|------|----------|
| `/simplify` | 审查代码复用性、质量、效率 | 主动调用 |
| `/refactor-clean` | 清理死代码、重复代码 | 主动调用 |
| `/code-review` | 代码审查，风险分级 | 主动调用 |
| `/python-review` | Python 专项审查（PEP8、类型提示） | 主动调用 |

### 自动化 Agents

| Agent | 用途 | 触发时机 |
|-------|------|----------|
| `refactor-cleaner` | 运行 knip/depcheck 分析死代码 | 主动调用 |
| `code-reviewer` | 通用代码审查 | 写完代码后主动调用 |
| `python-reviewer` | Python 专项审查 | 写完 Python 后主动调用 |
| `architect` | 架构设计、重构规划 复杂重构前 |

### 格化与 Lint 工具

**Python：**
```bash
# 一键格式化 + 检查
ruff format . && ruff check --fix .

# 类型检查
mypy .
```

**配置 PostToolUse Hook 自动格式化：**
- 编辑 `.py` 文件后自动运行 `ruff format`
- 编辑 `.py` 文件后自动运行 `ruff check`

---

## 文档更新

### 智能文档同步

**PostToolUse Hook：** 编辑代码后自动匹配文档规则，提示更新相关文档。

**项目配置示例（stockq）：**

| 代码文件模式 | 触发更新文档 |
|--------------|--------------|
| `data/factors.py`, `backtest/factor_*.py` | `doc/因子清单.md` |
| `backtest/strategy_config.py`, `config.py` | `doc/当前策略说明.md` |
| `data/*.py` | `doc/数据清洗指南.md` |
| `backtest/engine.py`, `runner.py` | `doc/向量化回测加速分析.md` |
| `backtest/paper_trading.py` | `doc/实时交易策略指南.md` |

### 文档更新工作流

```
编辑代码
    ↓
Hook 检测文件匹配规则
    ↓
├─ 匹配 → 提示运行 /doc-updater
└─ 不匹配 → 无提示
    ↓
运行 /doc-updater
    ↓
Agent 智能分析代码变更
    ↓
自动更新对应文档
```

### 文档更新命令

| 命令/Agent | 用途 |
|------------|------|
| `/doc-updater` | 文档和 codemap 专项更新 |
| `/update-codemaps` | 更新代码地图 |
| `/update-docs` | 更新 README 和指南 |

---

## 我的 Hooks 配置

### PostToolUse Hooks

| Hook | 触发 | 功能 |
|------|------|------|
| `post-edit-format` | Edit `.ts/.js` | 自动 Biome/Prettier 格式化 |
| `post-edit-typecheck` | Edit `.ts/.tsx` | TypeScript 类型检查 |
| `post-edit-python-format` | Edit/Write `.py` | 自动 ruff format |
| `post-edit-python-lint` | Edit/Write `.py` | ruff check 检查 |
| `post-edit-doc-sync` | Edit/Write `.py` | 智能提示文档更新 |
| `post-edit-console-warn` | Edit | console.log 警告 |

### Git Hooks

| Hook | 功能 |
|------|------|
| `pre-commit` | Python 代码审查（ruff check） |

---

## 参考资源

- 仓库：github.com/affaan-m/everything-claude-code ⭐ 115K+
- Shorthand Guide：the-shortform-guide.md
- Longform Guide：the-longform-guide.md
