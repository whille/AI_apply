# Project Init Template

> Claude Code 项目初始化模板

## 目录结构

```
templates/project-init/
├── .claude/
│   ├── CLAUDE.md              # 项目配置模板（必读）
│   ├── rules/
│   │   └── project-rules.md   # 项目规则模板
│   ├── skills/
│   │   └── project-skill/
│   │       └── SKILL.md       # 项目技能模板
│   └── settings.json          # Hook 配置模板
└── README.md                  # 本文件
```

## 模板文件说明

### CLAUDE.md

项目级配置模板，包含：
- 项目基本信息
- 开发规范定义
- Rules/Skills 引用
- 常见问题解答

**编辑指南**：
- 替换 `<PROJECT_NAME>` 等占位符
- 根据技术栈调整 Rules 引用
- 添加项目特定规则

### rules/project-rules.md

项目规则模板，包含：
- 命名规范
- 代码结构规范
- 错误处理规范
- 测试规范
- 安全检查清单

### skills/project-skill/SKILL.md

项目技能模板，包含：
- 触发条件定义
- 执行流程说明
- 参数说明
- 输出格式定义
- 错误处理方案

### settings.json

Hook 配置模板，包含：
- PreToolUse hooks
- PostToolUse hooks
- 权限配置

## 使用方法

### 1. 复制模板到新项目

```bash
cp -r templates/project-init/.claude /path/to/new-project/
```

### 2. 修改 CLAUDE.md

编辑 `.claude/CLAUDE.md`:
- 填写项目信息
- 定义开发规范
- 引入需要的 Rules
- 配置 Skills

### 3. 添加项目规则

在 `.claude/rules/` 目录添加项目特有的规则文件。

### 4. 添加项目 Skills

在 `.claude/skills/` 目录添加项目特有的技能。

## 配置优先级

```
项目级 (.claude/) > 全局级 (~/.claude/)
同名配置：项目级覆盖全局级
```

## 快速开始

### 方式一：直接复制

```bash
# 复制模板到新项目
cp -r templates/project-init/.claude /path/to/new-project/

# 编辑项目配置
vim /path/to/new-project/.claude/CLAUDE.md
```

### 方式二：选择性复制

```bash
# 只复制需要的文件
mkdir -p /path/to/new-project/.claude

# 必需文件
cp templates/project-init/.claude/CLAUDE.md /path/to/new-project/.claude/

# 可选：添加 rules
cp -r templates/project-init/.claude/rules /path/to/new-project/.claude/

# 可选：添加 skills
cp -r templates/project-init/.claude/skills /path/to/new-project/.claude/

# 可选：添加 settings
cp templates/project-init/.claude/settings.json /path/to/new-project/.claude/
```

## 配置步骤

### 1. 修改 CLAUDE.md

编辑 `.claude/CLAUDE.md`:
- 填写项目信息（替换 `<PROJECT_NAME>` 等占位符）
- 定义开发规范
- 引入需要的 Rules
- 配置 Skills

### 2. 自定义项目规则

编辑 `.claude/rules/project-rules.md`:
- 添加命名规范
- 定义代码结构
- 设置测试要求

### 3. 添加项目 Skills

在 `.claude/skills/` 目录添加项目特有的技能：
- 复制 `project-skill/` 目录
- 重命名为你的 Skill 名称
- 编辑 `SKILL.md` 定义触发条件和行为

### 4. 配置 Hooks（可选）

编辑 `.claude/settings.json`:
- 添加 PreToolUse hooks
- 添加 PostToolUse hooks
- 配置权限

## 常用配置组合

| 场景 | Skills | Rules |
|------|--------|-------|
| Python 项目 | python-patterns, python-testing | dev-guide, bug-prevention |
| 前端项目 | frontend-patterns | dev-guide |
| 安全敏感 | security-review, tdd-workflow | security, bug-prevention |
| 知识库项目 | llm-wiki | dev-guide |

## 全局 Resources

以下全局资源会自动加载：

- **Rules**: `~/.claude/rules/*.md`
- **Skills**: `~/.claude/skills/*/SKILL.md`

## 相关文档

- [05_harness.md](../../05_harness.md) - Skill/Rules/Hook 配置详解
- [CLAUDE.md 全局配置](~/.claude/CLAUDE.md)

---

**模板版本**：1.0.0
**更新时间**：2026-04-19
