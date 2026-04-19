# Project Init Template

> Claude Code 项目初始化模板

## 目录结构

```
.
├── .claude/
│   ├── CLAUDE.md              # 项目配置（必读）
│   ├── rules/
│   │   └── project-rules.md   # 项目规则
│   ├── skills/
│   │   └── project-skill/
│   │       └── SKILL.md       # 项目技能
│   └── settings.json          # Hook 配置
└── README.md                  # 本文件
```

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
