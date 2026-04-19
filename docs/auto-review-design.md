# 深度项目 Review 自动触发机制

> 设计代码变更自动触发 code-reviewer 的机制

---

## 设计目标

1. **自动检测**：识别需要 review 的代码变更
2. **智能触发**：在适当时机启动 review
3. **结果整合**：将 review 结果融入工作流
4. **持续改进**：基于反馈优化触发条件

---

## 一、触发场景分析

### 1.1 应触发的场景

| 场景 | 触发条件 | 优先级 |
|------|----------|--------|
| **代码提交前** | `git commit` 前检查 | P0 |
| **Pull Request** | PR 创建/更新时 | P0 |
| **关键文件变更** | 核心 logic/安全相关文件 | P1 |
| **高风险模式** | 检测到潜在问题模式 | P1 |
| **定期审计** | 每周/每月代码质量扫描 | P2 |

### 1.2 不应触发的场景

| 场景 | 原因 |
|------|------|
| 仅文档变更 | 无代码逻辑 |
| 配置文件微调 | 低风险 |
| 格式化/注释 | 无逻辑变更 |
| 测试文件新增 | 安全操作 |

---

## 二、触发机制设计

### 2.1 基于 Hook 的自动触发

```yaml
# ~/.claude/settings.json

hooks:
  PreToolUse:
    - hook: review-trigger
      matcher:
        tool: "Bash"
        input: "git commit*|git push*"
      command: "python ~/.claude/hooks/review-trigger.py"
      timeout: 30000

  PostToolUse:
    - hook: review-on-write
      matcher:
        tool: "Write|Edit"
        file: "*.py|*.ts|*.js"
      command: "python ~/.claude/hooks/review-on-write.py --file $FILE"
      timeout: 60000
```

### 2.2 PreToolUse Hook: 代码提交前检查

```python
#!/usr/bin/env python3
"""
review-trigger.py - 代码提交前自动 review 触发器

触发条件：
1. git commit 命令
2. 存在未暂存/未提交的代码变更
3. 变更涉及核心文件

动作：
1. 分析变更内容
2. 判断是否需要 review
3. 如需要，调用 code-reviewer
"""

import subprocess
import sys
import os

def get_staged_files():
    """获取暂存文件列表"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True
    )
    return result.stdout.strip().split("\n") if result.stdout.strip() else []

def get_changed_files():
    """获取变更文件列表"""
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True, text=True
    )
    return result.stdout.strip().split("\n") if result.stdout.strip() else []

def should_trigger_review(files: list[str]) -> tuple[bool, str]:
    """
    判断是否需要触发 review

    Returns:
        (should_trigger, reason)
    """

    # 1. 无文件变更
    if not files:
        return False, "无文件变更"

    # 2. 仅文档变更
    code_files = [f for f in files if not f.endswith((".md", ".txt", ".rst"))]
    if not code_files:
        return False, "仅文档变更"

    # 3. 检查文件风险级别
    high_risk_patterns = [
        "auth", "security", "password", "token", "api_key",
        "payment", "user", "permission", "role"
    ]

    for f in code_files:
        for pattern in high_risk_patterns:
            if pattern in f.lower():
                return True, f"高风险文件: {f}"

    # 4. 检查变更大小
    total_lines = 0
    for f in code_files:
        result = subprocess.run(
            ["git", "diff", "--cached", "--stat", f],
            capture_output=True, text=True
        )
        # 解析行数统计

    if total_lines > 100:
        return True, f"大变更: {total_lines} 行"

    # 5. 默认：有代码变更则触发
    return True, f"代码变更: {len(code_files)} 个文件"

def main():
    staged_files = get_staged_files()
    changed_files = get_changed_files()

    all_files = list(set(staged_files + changed_files))

    should_review, reason = should_trigger_review(all_files)

    if should_review:
        print(f"[Review Trigger] {reason}")
        print("建议执行: /code-reviewer 或使用 code-reviewer agent")
        # 可选：自动触发 review
        # subprocess.run(["claude", "skill", "code-reviewer", "--files", ",".join(all_files)])
    else:
        print(f"[Skip] {reason}")

if __name__ == "__main__":
    main()
```

### 2.3 PostToolUse Hook: 文件写入后检查

```python
#!/usr/bin/env python3
"""
review-on-write.py - 文件写入后自动检查

触发条件：
1. Write/Edit 工具完成
2. 文件是代码文件
3. 检测到潜在问题模式

动作：
1. 快速静态检查
2. 如发现问题，提示 review
"""

import re
import sys

QUICK_PATTERNS = {
    # 安全风险
    "hardcoded_password": r"password\s*=\s*['\"].+['\"]",
    "hardcoded_key": r"api_key\s*=\s*['\"].+['\"]",
    "sql_injection": r"f[\"'].*\{.*\}.*SELECT",

    # 代码质量
    "todo_fixme": r"#\s*(TODO|FIXME|XXX)",
    "debug_code": r"console\.log|print\(|debugger",

    # 复杂度
    "long_function": r"def\s+\w+\([^)]*\):[^}]{500,}",

    # 风险操作
    "eval": r"eval\s*\(",
    "exec": r"exec\s*\(",
    "shell_true": r"shell\s*=\s*True",
}

def quick_scan(file_path: str) -> list[dict]:
    """快速扫描文件问题"""

    issues = []

    try:
        with open(file_path, "r") as f:
            content = f.read()
    except:
        return issues

    for issue_type, pattern in QUICK_PATTERNS.items():
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[:match.start()].count("\n") + 1
            issues.append({
                "type": issue_type,
                "line": line_num,
                "match": match.group()[:50]
            })

    return issues

def main():
    if len(sys.argv) < 2:
        print("Usage: review-on-write.py --file <path>")
        return

    file_path = sys.argv[sys.argv.index("--file") + 1]

    issues = quick_scan(file_path)

    if issues:
        print(f"\n[Quick Scan] 发现 {len(issues)} 个潜在问题:")
        for issue in issues[:5]:  # 只显示前5个
            print(f"  - {issue['type']}: line {issue['line']}")
        print("\n建议执行 /code-reviewer 进行详细检查")

if __name__ == "__main__":
    main()
```

---

## 三、触发条件配置

### 3.1 配置文件

```yaml
# ~/.claude/config/auto-review.yaml

# 全局开关
enabled: true

# 触发级别
level: "balanced"  # strict | balanced | relaxed

# 文件匹配规则
file_rules:
  # 必须触发
  always_review:
    - "**/auth/**"
    - "**/security/**"
    - "**/api/**"

  # 从不触发
  never_review:
    - "**/*.md"
    - "**/*.txt"
    - "**/tests/**"

  # 按条件触发
  conditional:
    - pattern: "**/*.py"
      min_lines: 50
    - pattern: "**/*.ts"
      min_lines: 30

# 变更大小阈值
change_threshold:
  lines_warning: 100
  lines_critical: 500
  files_warning: 5
  files_critical: 10

# 时间限制
timing:
  # 工作时间内更严格
  work_hours:
    start: 9
    end: 18
  # 周末更宽松
  weekend_relaxed: true
```

### 3.2 触发条件矩阵

```
┌─────────────────────────────────────────────────────────────────┐
│                      Review 触发矩阵                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                 │ Strict │ Balanced │ Relaxed                   │
│    ─────────────┼────────┼──────────┼───────────                │
│    任何代码变更  │   ✅   │    ✅    │    ❓                     │
│    文档变更     │   ❌   │    ❌    │    ❌                     │
│    测试文件     │   ✅   │    ❓    │    ❌                     │
│    大变更(>500行)│   ✅   │    ✅    │    ✅                     │
│    安全相关文件  │   ✅   │    ✅    │    ✅                     │
│    格式化变更   │   ❌   │    ❌    │    ❌                     │
│                                                                  │
│    ✅ = 自动触发                                                 │
│    ❓ = 提示确认                                                 │
│    ❌ = 跳过                                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 四、与 code-reviewer Agent 集成

### 4.1 调用方式

```python
import subprocess
import json

def trigger_code_review(files: list[str], context: dict = None):
    """
    触发 code-reviewer agent

    Args:
        files: 待审查文件列表
        context: 额外上下文（如 PR 信息）
    """

    # 方式 1：使用 Agent tool
    from claude import Agent

    agent = Agent(
        subagent_type="code-reviewer",
        prompt=f"""
        Review the following files for:
        1. Security vulnerabilities
        2. Code quality issues
        3. SOLID principle violations
        4. Performance concerns

        Files: {', '.join(files)}

        Provide severity-rated feedback.
        """
    )

    result = agent.run()

    return result

    # 方式 2：调用 skill
    # subprocess.run(["claude", "skill", "code-reviewer", "--files", ",".join(files)])
```

### 4.2 结果处理

```python
def handle_review_result(result: dict):
    """
    处理 review 结果

    Actions:
    1. 显示问题摘要
    2. 阻断高风险提交
    3. 生成修复建议
    """

    critical_issues = [i for i in result["issues"] if i["severity"] == "critical"]
    high_issues = [i for i in result["issues"] if i["severity"] == "high"]

    if critical_issues:
        print(f"❌ 发现 {len(critical_issues)} 个严重问题，建议修复后再提交:")
        for issue in critical_issues:
            print(f"  - {issue['file']}:{issue['line']}: {issue['message']}")

        # 阻断提交
        return False

    if high_issues:
        print(f"⚠️  发现 {len(high_issues)} 个高优先级问题:")
        for issue in high_issues:
            print(f"  - {issue['file']}:{issue['line']}: {issue['message']}")

        # 提示但允许继续
        return True

    print("✅ 代码质量检查通过")
    return True
```

---

## 五、深度 Review 流程

### 5.1 标准 Review 模板

```
┌─────────────────────────────────────────────────────────────────┐
│                    深度项目 Review 流程                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  触发条件满足                                                     │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────┐                                                │
│  │ Phase 1     │                                                │
│  │ 变更分析    │                                                 │
│  │ - 文件列表  │                                                 │
│  │ - 变更大小  │                                                 │
│  │ - 影响范围  │                                                 │
│  └──────┬──────┘                                                │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ Phase 2     │                                                │
│  │ 安全检查    │                                                 │
│  │ - OWASP Top10│                                                │
│  │ - 敏感数据  │                                                 │
│  │ - 权限控制  │                                                 │
│  └──────┬──────┘                                                │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ Phase 3     │                                                │
│  │ 代码质量    │                                                 │
│  │ - SOLID     │                                                 │
│  │ - 复杂度    │                                                 │
│  │ - 命名规范  │                                                 │
│  └──────┬──────┘                                                │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ Phase 4     │                                                │
│  │ 性能评估    │                                                 │
│  │ - 算法复杂度│                                                 │
│  │ - 资源使用  │                                                 │
│  │ - 潜在瓶颈  │                                                 │
│  └──────┬──────┘                                                │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ Phase 5     │                                                │
│  │ 输出报告    │                                                 │
│  │ - 问题列表  │                                                 │
│  │ - 严重程度  │                                                 │
│  │ - 修复建议  │                                                 │
│  └─────────────┘                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Review 范围控制

```python
class ReviewScope:
    """Review 范围控制"""

    # 快速检查（仅安全）
    QUICK = {
        "phases": ["security"],
        "timeout": 30,
        "max_files": 5
    }

    # 标准检查
    STANDARD = {
        "phases": ["security", "quality"],
        "timeout": 60,
        "max_files": 20
    }

    # 深度检查（全部）
    DEEP = {
        "phases": ["security", "quality", "performance", "architecture"],
        "timeout": 120,
        "max_files": 50
    }

    @classmethod
    def auto_select(cls, files: list[str], changes: dict) -> str:
        """自动选择 review 范围"""

        # 高风险文件 → 深度
        if any(is_high_risk(f) for f in files):
            return "DEEP"

        # 大变更 → 标准
        if len(files) > 10 or changes.get("total_lines", 0) > 500:
            return "STANDARD"

        # 默认 → 快速
        return "QUICK"
```

---

## 六、交互式 Review

### 6.1 发现问题时的交互流程

```python
async def interactive_review(issues: list[dict]):
    """
    交互式 review 流程

    当发现问题时的交互：
    1. 展示问题摘要
    2. 询问是否继续
    3. 提供修复建议
    4. 支持自动修复
    """

    # 1. 展示摘要
    print(f"\n{'='*60}")
    print(f"Code Review 发现 {len(issues)} 个问题")
    print(f"{'='*60}\n")

    for i, issue in enumerate(issues, 1):
        severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        print(f"{i}. [{severity_icon[issue['severity']]}] {issue['message']}")
        print(f"   文件: {issue['file']}:{issue['line']}")
        print()

    # 2. 获取用户决策
    choice = input("\n选择操作: [c]ontinue / [f]ix / [a]bort: ").lower()

    if choice == "c":
        return "continue"
    elif choice == "f":
        # 提供修复建议
        for issue in issues:
            if issue.get("fix_suggestion"):
                print(f"\n修复建议 ({issue['type']}):")
                print(issue["fix_suggestion"])

        return "fix"
    else:
        return "abort"
```

### 6.2 自动修复建议

```python
def generate_fix_suggestion(issue: dict) -> str:
    """生成自动修复建议"""

    suggestions = {
        "hardcoded_password": """
# 修复建议：使用环境变量
# 之前：
password = "hardcoded_password"

# 之后：
import os
password = os.environ.get("DB_PASSWORD")
""",
        "sql_injection": """
# 修复建议：使用参数化查询
# 之前：
query = f"SELECT * FROM users WHERE id = {user_input}"

# 之后：
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_input,))
""",
        "long_function": """
# 修复建议：拆分函数
# 当前函数过长，建议：
1. 提取独立逻辑为子函数
2. 使用早返回减少嵌套
3. 考虑应用单一职责原则
""",
    }

    return suggestions.get(issue["type"], "建议详细检查该问题")
```

---

## 七、报告输出

### 7.1 Review 报告模板

```markdown
# Code Review 报告

> 审查时间：{timestamp}
> 审查范围：{scope}
> 文件数量：{file_count}

---

## 📊 执行摘要

| 指标 | 数值 |
|------|------|
| 总问题数 | {total_issues} |
| 严重 | {critical_count} |
| 高 | {high_count} |
| 中 | {medium_count} |
| 低 | {low_count} |

---

## 🔴 严重问题

### 1. {issue_title}

| 属性 | 值 |
|------|---|
| 文件 | {file}:{line} |
| 类型 | {type} |
| 影响 | {impact} |

**问题描述**：
{description}

**修复建议**：
```{language}
{fix_suggestion}
```

---

## 🟠 高优先级问题

> 共 {count} 个

---

## 🟡 中等优先级问题

> 共 {count} 个

---

## 📈 代码质量评分

| 维度 | 分数 | 建议 |
|------|------|------|
| 安全性 | {security_score}/100 | {security_advice} |
| 可维护性 | {maintainability_score}/100 | {maintainability_advice} |
| 性能 | {performance_score}/100 | {performance_advice} |

---

## ✅ 通过检查

- {passed_check_1}
- {passed_check_2}

---

## 后续行动

- [ ] 修复严重问题
- [ ] 处理高优先级问题
- [ ] 考虑重构建议
```

---

## 八、决策点 D4

**D4: 信息源跟踪方案确定后，是否需要实现自动化工具？**

| 选项 | 说明 | 建议 |
|------|------|------|
| **A. 立即实现 Python 脚本** | 完整自动化，需要维护 | 适合高频使用 |
| **B. 设计为 Skill，手动触发** | 灵活，按需使用 | ⭐ 推荐 |
| **C. 仅保留设计文档** | 无开发成本，依赖手动 | 适合低频使用 |

---

## 九、实现建议

### Phase 1：基础框架（1天）

1. 实现 PreToolUse hook 基础逻辑
2. 配置文件结构设计
3. 与 code-reviewer agent 集成

### Phase 2：智能检测（2天）

1. 文件风险级别判断
2. 变更大小阈值检测
3. 快速静态扫描

### Phase 3：交互优化（1天）

1. 交互式确认流程
2. 自动修复建议生成
3. 报告格式优化

---

*设计时间：2026-04-19*
