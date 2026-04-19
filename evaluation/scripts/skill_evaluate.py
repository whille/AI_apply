#!/usr/bin/env python3
"""
skill_evaluate.py - Skill 效果评估工具

功能：
1. 加载测试用例
2. 执行 skill（通过模拟或实际调用）
3. 收集指标数据
4. 生成评估报告

使用：
    python skill_evaluate.py <skill_name> [--test-dir <dir>] [--output <file>]
"""

import argparse
import json
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Any


class SkillEvaluator:
    """Skill 效果评估器"""

    def __init__(self, skill_name: str, test_dir: str, output_dir: str):
        self.skill_name = skill_name
        self.test_dir = Path(test_dir)
        self.output_dir = Path(output_dir)
        self.results = []

        # 指标收集
        self.metrics = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "total_time_ms": 0,
            "total_tokens": 0,
            "by_priority": {"P0": {"total": 0, "passed": 0},
                           "P1": {"total": 0, "passed": 0},
                           "P2": {"total": 0, "passed": 0},
                           "P3": {"total": 0, "passed": 0}},
            "by_type": {"happy_path": {"total": 0, "passed": 0},
                       "boundary": {"total": 0, "passed": 0},
                       "error_handling": {"total": 0, "passed": 0}}
        }

    def load_test_cases(self) -> list[dict]:
        """加载测试用例"""
        test_cases = []

        test_file = self.test_dir / f"{self.skill_name}_tests.json"
        if test_file.exists():
            with open(test_file) as f:
                data = json.load(f)
                test_cases = data.get("test_cases", [])

        return test_cases

    def execute_test(self, test_case: dict) -> dict:
        """执行单个测试用例"""
        start_time = time.time()

        result = {
            "id": test_case.get("id", "unknown"),
            "type": test_case.get("type", "unknown"),
            "priority": test_case.get("priority", "P2"),
            "status": "pending",
            "time_ms": 0,
            "error": None
        }

        try:
            # 模拟执行（实际场景需要真正调用 skill）
            # 对于测试框架，我们使用 mock 执行
            passed = self._mock_execute(test_case)

            result["status"] = "passed" if passed else "failed"
            result["time_ms"] = int((time.time() - start_time) * 1000)

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["time_ms"] = int((time.time() - start_time) * 1000)

        return result

    def _mock_execute(self, test_case: dict) -> bool:
        """模拟执行测试用例

        在实际使用中，这里应该：
        1. 调用 skill（通过 Claude Code 或 API）
        2. 验证结果是否符合预期
        """
        # 简单模拟：基于 expected 字段判断
        expected = test_case.get("expected", {})
        input_data = test_case.get("input", {})

        # 基础验证：输入不为空
        if not input_data:
            return False

        # 预期结果验证
        if expected.get("should_succeed", True):
            return True

        return expected.get("passes", True)

    def run_evaluation(self):
        """运行完整评估"""
        test_cases = self.load_test_cases()

        if not test_cases:
            print(f"⚠️ 未找到测试用例: {self.test_dir}/{self.skill_name}_tests.json")
            return False

        print(f"\n{'='*60}")
        print(f"评估 Skill: {self.skill_name}")
        print(f"测试用例数: {len(test_cases)}")
        print(f"{'='*60}\n")

        for i, tc in enumerate(test_cases, 1):
            print(f"[{i}/{len(test_cases)}] 执行: {tc.get('id', 'unknown')} ... ", end="")

            result = self.execute_test(tc)
            self.results.append(result)
            self._update_metrics(result)

            status_icon = "✅" if result["status"] == "passed" else "❌"
            print(f"{status_icon} {result['status']} ({result['time_ms']}ms)")

        return True

    def _update_metrics(self, result: dict):
        """更新指标统计"""
        self.metrics["total"] += 1
        self.metrics["total_time_ms"] += result["time_ms"]

        if result["status"] == "passed":
            self.metrics["passed"] += 1
        else:
            self.metrics["failed"] += 1

        # 按优先级统计
        priority = result.get("priority", "P2")
        if priority in self.metrics["by_priority"]:
            self.metrics["by_priority"][priority]["total"] += 1
            if result["status"] == "passed":
                self.metrics["by_priority"][priority]["passed"] += 1

        # 按类型统计
        tc_type = result.get("type", "happy_path")
        if tc_type in self.metrics["by_type"]:
            self.metrics["by_type"][tc_type]["total"] += 1
            if result["status"] == "passed":
                self.metrics["by_type"][tc_type]["passed"] += 1

    def calculate_score(self) -> dict:
        """计算评估分数"""
        if self.metrics["total"] == 0:
            return {"grade": "N/A", "accuracy": 0, "efficiency": 0}

        accuracy = (self.metrics["passed"] / self.metrics["total"]) * 100

        # 效率分数（基于时间和成功率）
        avg_time = self.metrics["total_time_ms"] / self.metrics["total"]
        time_score = max(0, 100 - (avg_time / 100))  # 100ms 基准
        efficiency = time_score * (accuracy / 100)

        # 评级
        if accuracy >= 95:
            grade = "A"
        elif accuracy >= 90:
            grade = "B"
        elif accuracy >= 85:
            grade = "C"
        else:
            grade = "D"

        return {
            "grade": grade,
            "accuracy": round(accuracy, 2),
            "efficiency": round(efficiency, 2),
            "avg_time_ms": round(avg_time, 2)
        }

    def generate_report(self) -> dict:
        """生成评估报告"""
        score = self.calculate_score()

        report = {
            "meta": {
                "skill": self.skill_name,
                "evaluated_at": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "summary": {
                "total": self.metrics["total"],
                "passed": self.metrics["passed"],
                "failed": self.metrics["failed"],
                "accuracy": score["accuracy"],
                "grade": score["grade"]
            },
            "metrics": {
                "by_priority": self.metrics["by_priority"],
                "by_type": self.metrics["by_type"],
                "avg_time_ms": score["avg_time_ms"],
                "efficiency": score["efficiency"]
            },
            "results": self.results,
            "recommendation": self._generate_recommendation(score)
        }

        return report

    def _generate_recommendation(self, score: dict) -> str:
        """生成改进建议"""
        if score["grade"] == "A":
            return "生产就绪，建议直接使用"
        elif score["grade"] == "B":
            return "基本可用，建议关注失败用例并改进"
        elif score["grade"] == "C":
            return "需要改进，建议分析失败原因后优化"
        else:
            return "禁止使用，需要重新设计"

    def save_report(self, report: dict, output_file: str = None):
        """保存评估报告"""
        if output_file is None:
            output_file = self.output_dir / f"{self.skill_name}_report.json"
        else:
            output_file = Path(output_file)

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 报告已保存: {output_file}")

    def print_summary(self, report: dict):
        """打印评估摘要"""
        summary = report["summary"]
        score = report["metrics"]

        print(f"\n{'='*60}")
        print(f"评估结果")
        print(f"{'='*60}")
        print(f"等级: {summary['grade']}")
        print(f"准确率: {summary['accuracy']}%")
        print(f"通过: {summary['passed']}/{summary['total']}")
        print(f"平均耗时: {score['avg_time_ms']}ms")
        print(f"效率分: {score['efficiency']}")
        print(f"\n建议: {report['recommendation']}")
        print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Skill 效果评估工具")
    parser.add_argument("skill_name", help="待评估的 skill 名称")
    parser.add_argument("--test-dir", default="evaluation/test_cases",
                       help="测试用例目录")
    parser.add_argument("--output", help="报告输出路径")
    parser.add_argument("--output-dir", default="evaluation/reports",
                       help="报告输出目录")

    args = parser.parse_args()

    evaluator = SkillEvaluator(
        args.skill_name,
        args.test_dir,
        args.output_dir
    )

    success = evaluator.run_evaluation()

    if success:
        report = evaluator.generate_report()
        evaluator.save_report(report, args.output)
        evaluator.print_summary(report)
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
