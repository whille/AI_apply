# OMC Skills 价值评估

> 51 个 Skills 分类和实用建议

---

## 分类评估

### ⭐⭐⭐ 高频使用（强烈推荐）

| Skill | 用途 | 为什么有用 |
|-------|------|------------|
| **simplify** | 代码简化重构 | 自动检测重复代码、优化结构 |
| **claude-api** | Claude API 开发 | 项目用 API 时自动触发 |
| **test-case-generator** | 测试用例生成 | 完整测试覆盖，参数化模板 |
| **security-review** | 安全审查 | OWASP Top 10 检查 |
| **dependencies-analyzer** | 依赖分析 | 识别风险依赖、版本问题 |

### ⭐⭐ 中频使用（推荐）

| Skill | 用途 | 使用场景 |
|-------|------|----------|
| **code-review** (self-improve) | 代码审查 | 提交前审查 |
| **mcp-setup** | MCP 配置 | 新项目初始化 |
| **deep-research** | 深度研究 | 复杂问题调研 |
| **wiki** | 知识库 | 长期知识沉淀 |
| **python-patterns** | Python 模式 | Python 项目 |
| **tdd-workflow** | TDD 流程 | 测试驱动开发 |

### ⭐ 低频使用（按需）

| Skill | 用途 | 使用场景 |
|-------|------|----------|
| **autopilot** | 自主执行 | 需要完全自动执行时 |
| **ralph/ultrawork** | 并发执行 | 大量独立任务 |
| **deep-dive** | 深度分析 | 需要多轮对话深挖 |
| **visual-verdict** | 截图对比 | UI 验证 |

### ❓ 可能冗余

| Skill | 问题 | 替代方案 |
|-------|------|----------|
| ask | 功能不明确 | 直接提问 |
| ccg | 多模型协作需求少 | 单模型足够 |
| deep-interview | 场景有限 | 普通对话 |
| sciomc | omc 内部命令 | 用户不直接用 |
| omc-* 差不多 6个 | omc 内部管理 | 通过 omc-setup 管理 |

### 🔄 功能相似

| 组 | Skills | 建议 |
|----|--------|------|
| 执行引擎 | autopilot, ralph, ultrawork, team | 保留 ultrawork 即可 |
| 研究类 | deep-research, deep-dive, deep-interview | 保留 deep-research |
| 学习类 | learned, learner, self-improve | 合并为一个 |
| Wiki 类 | wiki, llm-wiki, writer-memory | 保留 wiki |
| PRD 类 | prd, ralplan | 功能重叠 |

---

## 推荐精简方案

### 保留核心（15-20个）

```
# 开发类
simplify
claude-api
test-case-generator
security-review
dependencies-analyzer
python-patterns
python-testing

# 工作流类
deep-research
wiki
tdd-workflow
mcp-setup

# 执行类
ultrawork

# 自研（已在 AI_apply）
info-tracker
bilibili-analyzer
log-analyzer
```

### 可移除（30+个）

```
# omc 内部
omc-doctor, omc-plan, omc-reference, omc-setup, omc-teams, sciomc

# 重复执行引擎
autopilot, ralph, team (保留 ultrawork)

# 重复研究
deep-dive, deep-interview (保留 deep-research)

# 重复学习
learned, learner, self-improve (合并)

# 重复 Wiki
llm-wiki, writer-memory (保留 wiki)

# 重复规划
prd, ralplan

# 低频
ask, ccg, configure-notifications, deepinit, exa-search,
external-context, frontend-patterns, frontend-slides,
hud, release, setup, skill, trace, ultraqa, visual-verdict,
cancel, project-session-manager, llm-wiki-upgrade
```

---

## 精简命令

```bash
# 移除不需要的 skills
cd ~/.claude/skills
rm -rf omc-doctor omc-plan omc-reference omc-setup omc-teams sciomc
rm -rf autopilot ralph team  # 保留 ultrawork
rm -rf deep-dive deep-interview  # 保留 deep-research
rm -rf learned learner  # 保留 self-improve
rm -rf llm-wiki writer-memory  # 保留 wiki
rm -rf prd ralplan
rm -rf ask ccg configure-notifications deepinit exa-search external-context
rm -rf frontend-patterns frontend-slides hud release setup skill trace ultraqa
rm -rf visual-verdict cancel project-session-manager llm-wiki-upgrade

# 重新运行 link-skills.sh 恢复自研 skills
cd ~/github.com/AI_apply
./link-skills.sh
```

---

## 精简后约 20 个 Skills

| 分类 | Skills |
|------|--------|
| **开发** | simplify, claude-api, test-case-generator, security-review, dependencies-analyzer, python-patterns, python-testing |
| **研究** | deep-research, wiki |
| **工作流** | tdd-workflow, mcp-setup, ultrawork |
| **自研** | info-tracker, bilibili-analyzer, log-analyzer |
| **保留备选** | self-improve |

---

## 建议

1. **先备份**：`cp -r ~/.claude/skills ~/.claude/skills.backup`
2. **分批移除**：先移除明显不用的
3. **观察效果**：看是否影响日常工作
4. **按需恢复**：发现需要再恢复
