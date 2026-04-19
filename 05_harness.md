# Harness 配置

> skill/rules/hook 最佳实践

## 问题清单

- skill/rules/hook 怎么高效使用？
- /review、/refactoring 怎么自动触发？
- 深度项目 review 怎么做好？
- 如何组织项目级配置？

## 解决方案

### Skill 配置

- **触发条件**：需要扩展 Claude 能力
- **执行步骤**：
  1. 在项目根目录创建 `.claude/skills/` 目录
  2. 为每个 skill 创建独立目录
  3. 编写 skill.md 定义触发条件和行为
  4. 测试 skill 触发和执行
- **验收标准**：skill 能正确触发、执行符合预期
- **依赖工具**：skill 目录结构

**目录结构**：
```
.claude/
├── skills/
│   ├── my-skill/
│   │   └── skill.md
│   └── another-skill/
│       └── skill.md
└── settings.json
```

**skill.md 模板**：
```markdown
---
name: my-skill
description: 技能描述
trigger: 触发条件（关键词/正则）
---

# 技能名称

## 触发条件
- 用户输入包含 "xxx"
- 或明示调用 /my-skill

## 执行流程
1. Step 1
2. Step 2

## 输出格式
[输出内容规范]
```

### 现有 Skills 清单（47 个）

按场景分类：

#### 开发类
| Skill | 触发条件 | 用途 |
|-------|----------|------|
| python-patterns | Python 开发 | Python 最佳实践 |
| python-testing | 测试相关 | pytest 使用指南 |
| frontend-patterns | 前端开发 | React/Next.js 模式 |
| frontend-slides | 创建演示 | HTML 幻灯片生成 |
| tdd-workflow | 新功能/Bug修复 | TDD 流程引导 |
| simplify | 代码变更后自动 | 检查复用、质量、效率 |

#### API/集成类
| Skill | 触发条件 | 用途 |
|-------|----------|------|
| claude-api | 导入 anthropic SDK | Claude API 开发指南 |
| mcp-setup | 配置 MCP | MCP 服务器配置 |
| dependencies-analyzer | 分析依赖 | 任务依赖 DAG 构建 |

#### 研究/分析类
| Skill | 触发条件 | 用途 |
|-------|----------|------|
| deep-research | 深度研究请求 | 多源综合研究 |
| exa-search | Exa 神经搜索 | 代码/网页搜索 |
| trace | 问题追踪 | 根因分析 |
| sciomc | 科学分析 | 并行科学实验 |

#### 知识管理类
| Skill | 触发条件 | 用途 |
|-------|----------|------|
| llm-wiki | 明确提到知识库 | 个人知识库构建 |
| wiki | 同上 | OMC wiki 模式 |
| llm-wiki-upgrade | 升级 llm-wiki | 版本更新 |

#### 规划/执行类
| Skill | 触发条件 | 用途 |
|-------|----------|------|
| prd | 创建 PRD | 需求文档生成 |
| ralph | 转换 prd 格式 | prd.json 生成 |
| omc-plan | 战略规划 | OMC 规划模式 |
| autopilot | 自主执行 | 端到端自动完成 |
| ultrawork | 高吞吐任务 | 并行执行 |

#### 安全/质量类
| Skill | 触发条件 | 用途 |
|-------|----------|------|
| security-review | 安全相关代码 | 安全审查清单 |
| code-reviewer | 代码审查 | OMC 审查模式 |

### 推荐组合

| 场景 | Skills 组合 | Rules |
|------|------------|-------|
| Python 后端项目 | python-patterns + python-testing + tdd-workflow | dev-guide + bug-prevention |
| 前端项目 | frontend-patterns + tdd-workflow | dev-guide |
| API 集成 | claude-api + security-review | security |
| 安全敏感项目 | security-review + tdd-workflow | security + bug-prevention |
| 知识库项目 | llm-wiki + deep-research | dev-guide |
| 新项目规划 | prd + ralph + dependencies-analyzer | dev-guide |

### OMC 专用 Skills

| Skill | 用途 |
|-------|------|
| team | 多 agent 并行编排 |
| ralplan | 共识规划入口 |
| omc-teams | CLI-team 运行时 |
| hud | 状态栏显示 |
| cancel | 取消任何活动模式 |

### Rules 配置

- **触发条件**：需要定义开发规范和约束
- **执行步骤**：
  1. 全局 rules 存放在 `~/.claude/rules/`
  2. 项目 rules 存放在 `.claude/rules/`
  3. 规则文件按职责命名
  4. 在 CLAUDE.md 中引用
- **验收标准**：Claude 能遵循规则执行任务
- **依赖工具**：CLAUDE.md 配置

**现有 Rules**：

| 文件 | 职责 | 核心内容 |
|------|------|----------|
| bug-prevention.md | Bug 预防 | 日期处理、Falsy 陷阱、重复代码检测 |
| dev-guide.md | 开发规范 | 代码质量标准、工作流、Git 规范 |
| refactoring.md | 重构规则 | 重构红线、小步 obrig原则 |
| security.md | 安全规范 | 安全检查、密钥管理 |

**Rules 加载优先级**：
```
项目级 (.claude/rules/) > 全局级 (~/.claude/rules/)
同名规则：项目级覆盖全局级
```

### Hook 配置

- **触发条件**：需要在特定事件时自动执行
- **执行步骤**：
  1. 在 settings.json 中配置 hooks
  2. 定义触发事件类型
  3. 编写 hook 脚本
  4. 测试 hook 执行
- **验收标准**：Hook 能在正确时机触发
- **依赖工具**：settings.json、shell 脚本

**Hook 类型**：

| 类型 | 触发时机 | 用途 |
|------|----------|------|
| PreToolUse | 工具使用前 | 权限验证、环境检查 |
| PostToolUse | 工具使用后 | 结果处理、日志记录 |
| Stop | 会话结束前 | 清理、总结 |
| Notification | 通知事件 | 外部通知 |
| UserPromptSubmit | 用户提交时 | 输入预处理 |

**settings.json 示例**：
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": ["check-command-allowed.sh"]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": ["format-file.sh"]
      }
    ]
  }
}
```

### 深度项目 Review

- **触发条件**：需要全面审查项目
- **执行步骤**：
  1. 使用 `/simplify` 检查代码变更
  2. 使用 `/security-review` 检查安全问题
  3. 使用 `/tdd-workflow` 验证测试覆盖
  4. 汇总审查报告
- **验收标准**：生成完整的审查报告
- **依赖工具**：simplify、security-review、tdd-workflow

**Review 检查清单**：
```markdown
## 项目 Review 报告

### 代码质量
- [ ] 函数长度 < 50 行
- [ ] 文件长度 < 800 行
- [ ] 嵌套层级 ≤ 4 层
- [ ] 无重复代码

### 安全性
- [ ] 无硬编码密钥
- [ ] 输入已验证
- [ ] SQL 注入防护
- [ ] XSS 防护

### 测试
- [ ] 测试覆盖率 ≥ 80%
- [ ] 核心逻辑有测试
- [ ] 边界条件测试

### Bug 预防
- [ ] 无 Falsy 陷阱
- [ ] 日期范围验证
- [ ] 默认参数正确
```

## 配置组合建议

### 新项目初始化

```
.claude/
├── CLAUDE.md              # 项目级配置
├── rules/
│   └── project-rules.md   # 项目特定规则
├── skills/
│   └── project-skill/     # 项目特定技能
└── settings.json          # Hook 等配置
```

### 常用配置组合

| 场景 | Skills | Rules |
|------|--------|-------|
| Python 项目 | python-patterns, python-testing | dev-guide, bug-prevention |
| 前端项目 | frontend-patterns | dev-guide |
| 安全敏感 | security-review, tdd-workflow | security, bug-prevention |
| 知识库项目 | llm-wiki | dev-guide |

## 依赖

- 前置模块：无（基础配置）
- 后置模块：
  - [04_agent_design.md](./04_agent_design.md)（Agent 使用 skill）
  - [08_automation.md](./08_automation.md)（自动化触发）

## 待办

- [x] 整理常用 skill 组合
- [x] 创建项目初始化模板（已完成 T006）
- [ ] 建立技能效果评估方法
- [ ] 测试 hook 自动触发

## 项目初始化模板

模板位置：`templates/project-init/`

### 快速开始

```bash
# 复制模板到新项目
cp -r templates/project-init/.claude /path/to/new-project/

# 编辑项目配置
vim /path/to/new-project/.claude/CLAUDE.md
```

### 模板结构

```
templates/project-init/
├── .claude/
│   ├── CLAUDE.md              # 项目配置模板
│   ├── rules/
│   │   └── project-rules.md   # 项目规则模板
│   ├── skills/
│   │   └── project-skill/
│   │       └── SKILL.md       # 项目技能模板
│   └── settings.json          # Hook 配置模板
└── README.md                  # 使用说明
```

### 模板内容

- **CLAUDE.md**: 项目级配置模板，包含项目信息、开发规范、Rules/Skills 引用
- **project-rules.md**: 项目规则模板，包含命名规范、代码结构、错误处理、测试规范
- **project-skill/**: 项目技能模板，包含触发条件、执行流程、参数说明、输出格式
- **settings.json**: Hook 配置模板，包含 PreToolUse、PostToolUse、权限配置

详细使用说明见 `templates/project-init/README.md`。

## 状态

- 状态：active
- 更新时间：2026-04-19
