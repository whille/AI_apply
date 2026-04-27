# AI Agent 应用技术分析

## 思路

- 创造性思维 + meta 方法论
- 避免机械性记忆，注重理解与应用
- LLM →（固化）skill/wiki →（重构）工程化
- **趋势判断**（个人判断）：
  - 拖拽式工作流 → skill 化：Coze 等拖拽式工具对复杂流程人工操作多；对 AI agent 而言，工程化（doc/code）更利于改进
  - RAG 工程 → hermes 进化：从静态检索到自改进学习循环

## 手段

### 丰富的 Skill

- 需求驱动：我的需求有没有优秀的实现？没有就自制
- 自制原则：复用优先，避免重复造轮子

### 精简的 Rules & Hooks

- 规则精简，hooks 轻量
- 避免过度工程化

### 少量有用的 MCP

**必要能力**：
- 搜索能力（websearch）：快速调研必备
- 图文理解：多模态分析必备

**按需加入**：playwright 等

### 与文本编辑器配合

- vim 快捷键示例：`copy ~/path_to/foo.py:10-25`
- 非核心手段，可按需使用

## 典型应用

### 怎么搜索知识

```bash
/intel --deep "关键词" --sources bilibili,github,rss
```

**intel 技能**：信息源跟踪系统
- 多信息源并发扫描（bilibili、github、web）
- URL/标题相似度去重
- 质量评分 topN
- 输出结构化报告：总结 + 洞察

### 怎么快速学习

**人机结合学习法**：

```
循环开始
  ┌─────────────────┐
  │ 人机分析效果     │
  └────────┬────────┘
           ↓
  ┌─────────────────┐
  │ agent 对话调整   │
  └────────┬────────┘
           ↓
  ┌─────────────────┐
  │ 改进规则/精简策略│
  └────────┬────────┘
           ↓
      达成目标？──否──→ 继续循环
           │
          是
           ↓
      结束迭代
```

**示例**：精简 Gitbook 电子书

```
需求：精简 https://yeasy.gitbook.io/harness_engineering_guide
目标：比原书信息精简，但保留各章重点和 insight
方法：通过问答测试判断知识储备，侧重整理结果
终止：有限次循环后，获得 80%+ 有用信息的精简版
```

### 实际案例

```bash
# 遍历 Gitbook 文档
/intel --deep \
  --url "https://yeasy.gitbook.io/harness_engineering_guide" \
  --url "https://yeasy.gitbook.io/agentic_ai_guide"

# 或基于已有报告生成 wiki
~/Documents/ai_intel/reports/gitbook-agentic-ai-2026-04-21.md
```

## 实践练习

### 棋牌游戏开发

- 场景：熟悉规则，但管理规则、程序设计细节往往文档不详
- 示例：https://whille.github.io/mahjong/
- 挑战：结果不能一步到位，需要迭代完善
- agent 弥补点：规则边界条件、异常处理逻辑

### 小说文配图

以红楼梦大观园场景为例，实现场景文生图工作流（示例，不细化）。

## 优先思路参考

### Ralph-Loop

**来源**：https://github.com/snarktank/ralph

**核心机制**：
- 自主 AI 代理循环，反复运行直到完成 PRD 中所有待办事项
- 每次迭代启动**新的 AI 实例**，拥有干净的上下文
- 记忆通过 `progress.txt` 和 `prd.json` 在迭代间持久化

**循环流程**：
```
选取优先级最高的任务（passes: false）
  → 实现
  → 运行质量检查
  → 提交
  → 标记完成
  → 重复
```

**扩展思路**：增加依赖关系属性（有向图）做并发开发

### ECC (Everything Claude Code)

**来源**：https://github.com/affaan-m/everything-claude-code

**核心内容**：
- 36+ 专用 agents（planner、architect、多语言 code reviewers）
- 156+ skills（编码标准、文档、测试模式、框架知识）
- 72+ 工作流自动化命令
- Rules：12+ 语言生态规则
- MCP 配置：工具集成
- 跨平台：Claude Code、Codex、Cursor、OpenCode、Gemini

**取舍原则**：理解工具能力边界，按需选用

## 质量评估

**对比测试方法**：

```
同一任务
  ├── 方案 A（原有实现）
  └── 方案 B（改进实现）

使用相同 LLM 模型或 Agent
对比维度：时间、准确率、代码量等
```

## 关键术语

| 术语 | 来源 | 核心特点 |
|------|------|----------|
| **Hermes** | [nousresearch/hermes-agent](https://github.com/nousresearch/hermes-agent) | 自改进 AI 代理，从经验中创建技能，跨会话建立用户模型 |
| **Ralph** | [snarktank/ralph](https://github.com/snarktank/ralph) | 自主循环执行 PRD，每次迭代独立上下文，记忆持久化 |
| **ECC** | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | 140K+ stars 的 Claude Code 配置集合，含 36+ agents、156+ skills |
| **Intel** | 本地 skill | 信息源跟踪系统，多源扫描、去重、评分、结构化输出 |
