#!/usr/bin/env python3
"""
test_review_trigger.py - 测试 review-trigger.py 的功能

测试范围：
1. 文件识别函数
2. 高风险文件检测
3. 安全扫描模式
4. 触发条件判断
5. 端到端场景测试
"""

import subprocess
import sys
import os
import tempfile
import json

# 添加 hooks 目录到路径
hooks_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'hooks'))
sys.path.insert(0, hooks_dir)

import importlib.util
spec = importlib.util.spec_from_file_location("review_trigger", os.path.join(hooks_dir, "review-trigger.py"))
review_trigger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review_trigger)

is_code_file = review_trigger.is_code_file
is_high_risk_file = review_trigger.is_high_risk_file
quick_security_scan = review_trigger.quick_security_scan
should_trigger_review = review_trigger.should_trigger_review


class TestResults:
    """测试结果收集器"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def add_pass(self, name):
        self.passed += 1
        self.tests.append({"name": name, "status": "PASS"})

    def add_fail(self, name, error):
        self.failed += 1
        self.tests.append({"name": name, "status": "FAIL", "error": error})

    def summary(self):
        total = self.passed + self.failed
        return f"\n{'='*60}\n测试结果: {self.passed}/{total} 通过\n{'='*60}"


def test_is_code_file():
    """测试代码文件识别"""
    results = TestResults()

    # 正向测试 - 应该识别为代码文件
    code_files = [
        "app.py",
        "index.js",
        "utils.ts",
        "component.tsx",
        "main.go",
        "lib.rs",
        "App.java"
    ]

    for f in code_files:
        if is_code_file(f):
            results.add_pass(f"is_code_file({f})")
        else:
            results.add_fail(f"is_code_file({f})", "应返回 True")

    # 反向测试 - 不应识别为代码文件
    non_code_files = [
        "README.md",
        "config.yaml",
        "styles.css",
        "data.json",
        "image.png"
    ]

    for f in non_code_files:
        if not is_code_file(f):
            results.add_pass(f"is_code_file({f}) == False")
        else:
            results.add_fail(f"is_code_file({f}) == False", "应返回 False")

    return results


def test_is_high_risk_file():
    """测试高风险文件检测"""
    results = TestResults()

    # 高风险文件
    high_risk = [
        "auth/login.py",
        "security/crypto.py",
        "password_hash.go",
        "token_manager.js",
        "api_key_validator.ts",
        "payment_processor.py",
        "user_permissions.go",
        "role_manager.js"
    ]

    for f in high_risk:
        if is_high_risk_file(f):
            results.add_pass(f"is_high_risk_file({f})")
        else:
            results.add_fail(f"is_high_risk_file({f})", "应识别为高风险")

    # 非高风险文件
    low_risk = [
        "utils.py",
        "main.go",
        "index.js",
        "config.ts",
        "helper.py"
    ]

    for f in low_risk:
        if not is_high_risk_file(f):
            results.add_pass(f"is_high_risk_file({f}) == False")
        else:
            results.add_fail(f"is_high_risk_file({f}) == False", "不应识别为高风险")

    return results


def test_quick_security_scan():
    """测试快速安全扫描"""
    results = TestResults()

    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        test_file = f.name

        # 写入包含安全问题的测试代码
        test_code = '''
# 测试文件 - 包含安全问题
password = "hardcoded_secret_123"
api_key = "sk-abc123xyz"
secret = "my_secret_key"

def unsafe_query(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query

def dangerous_eval(user_input):
    result = eval(user_input)
    return result

def run_shell(cmd):
    subprocess.run(cmd, shell=True)
'''
        f.write(test_code)

    try:
        issues = quick_security_scan(test_file)

        # 检查是否检测到预期问题
        issue_types = [i['type'] for i in issues]

        expected_types = ['hardcoded_password', 'hardcoded_key', 'sql_injection', 'eval_usage', 'shell_true']

        for expected in expected_types:
            if expected in issue_types:
                results.add_pass(f"检测到 {expected}")
            else:
                results.add_fail(f"检测到 {expected}", f"未找到，实际: {issue_types}")

        if len(issues) >= 5:
            results.add_pass(f"检测到 {len(issues)} 个问题")
        else:
            results.add_fail(f"检测问题数量", f"预期 >= 5，实际 {len(issues)}")

    finally:
        os.unlink(test_file)

    return results


def test_should_trigger_review():
    """测试触发条件判断"""
    results = TestResults()

    # 场景 1: 无文件
    should, reason, issues = should_trigger_review([])
    if not should and "无文件" in reason:
        results.add_pass("无文件变更不触发")
    else:
        results.add_fail("无文件变更不触发", reason)

    # 场景 2: 仅文档文件
    should, reason, issues = should_trigger_review(["README.md", "CHANGELOG.txt"])
    if not should and "非代码" in reason:
        results.add_pass("仅文档变更不触发")
    else:
        results.add_fail("仅文档变更不触发", reason)

    # 场景 3: 高风险文件
    should, reason, issues = should_trigger_review(["auth/login.py"])
    if should and "高风险" in reason:
        results.add_pass("高风险文件触发")
    else:
        results.add_fail("高风险文件触发", reason)

    # 场景 4: 普通代码文件（非 git 环境）
    # 注意：在非 git 环境下，文件不存在会导致安全扫描返回空
    should, reason, issues = should_trigger_review(["utils.py"])
    if should:
        results.add_pass("普通代码文件触发")
    else:
        results.add_fail("普通代码文件触发", reason)

    return results


def test_end_to_end():
    """端到端测试 - 模拟 git commit 场景"""
    results = TestResults()

    # 创建临时 git 仓库
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # 初始化 git 仓库
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], capture_output=True)

        # 创建测试文件
        test_file = "auth_test.py"
        with open(test_file, 'w') as f:
            f.write('password = "test123"\n')

        # 添加到暂存区
        subprocess.run(["git", "add", test_file], capture_output=True)

        # 运行 review-trigger.py
        script_path = os.path.join(os.path.dirname(__file__), '..', 'hooks', 'review-trigger.py')
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True
        )

        if "建议执行" in result.stdout or "高风险" in result.stdout:
            results.add_pass("端到端: 检测到高风险文件")
        else:
            results.add_fail("端到端: 检测到高风险文件", f"输出: {result.stdout[:200]}")

        if result.returncode == 0:
            results.add_pass("端到端: 脚本执行成功")
        else:
            results.add_fail("端到端: 脚本执行成功", f"返回码: {result.returncode}")

    return results


def main():
    """运行所有测试"""
    print("="*60)
    print("Review Trigger 测试套件")
    print("="*60)

    all_results = []

    # 运行测试
    print("\n[1] 测试代码文件识别...")
    results = test_is_code_file()
    all_results.append(results)
    print(results.summary())

    print("\n[2] 测试高风险文件检测...")
    results = test_is_high_risk_file()
    all_results.append(results)
    print(results.summary())

    print("\n[3] 测试安全扫描...")
    results = test_quick_security_scan()
    all_results.append(results)
    print(results.summary())

    print("\n[4] 测试触发条件...")
    results = test_should_trigger_review()
    all_results.append(results)
    print(results.summary())

    print("\n[5] 端到端测试...")
    results = test_end_to_end()
    all_results.append(results)
    print(results.summary())

    # 汇总
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    total = total_passed + total_failed

    print(f"\n{'='*60}")
    print(f"总测试结果: {total_passed}/{total} 通过")
    if total_failed > 0:
        print(f"❌ {total_failed} 个测试失败")
    else:
        print(f"✅ 所有测试通过!")
    print("="*60)

    # 输出 JSON 报告
    report = {
        "total": total,
        "passed": total_passed,
        "failed": total_failed,
        "tests": [r.tests for r in all_results]
    }

    report_path = os.path.join(os.path.dirname(__file__), 'hook-test-report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n测试报告已保存至: {report_path}")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
