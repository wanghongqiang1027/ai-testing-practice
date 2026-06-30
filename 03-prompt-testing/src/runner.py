"""
测试执行器
批量执行Prompt测试用例
"""

import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02-llm-basic" / "src"))

from llm_client import LLMClient
from test_case import TestCase, TestResult, TestSummary
from assertor import AssertionRunner


class TestRunner:
    """
    Prompt测试执行器

    Example:
        runner = TestRunner(llm_client)
        results = runner.run_test_cases("test_cases/basic_qa.jsonl")
    """

    def __init__(self, llm_client: LLMClient, system_prompt: str = ""):
        """
        初始化执行器

        Args:
            llm_client: LLM客户端
            system_prompt: 系统提示词
        """
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.assertion_runner = AssertionRunner()

    def load_test_cases(self, file_path: str) -> List[TestCase]:
        """
        加载测试用例

        Args:
            file_path: JSONL文件路径

        Returns:
            测试用例列表
        """
        test_cases = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    test_case = TestCase(**data)
                    if test_case.enabled:
                        test_cases.append(test_case)

        return test_cases

    def run_single_test(self, test_case: TestCase) -> TestResult:
        """
        运行单个测试用例

        Args:
            test_case: 测试用例

        Returns:
            测试结果
        """
        try:
            # 构建消息
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            messages.append({"role": "user", "content": test_case.input})

            # 调用LLM
            response = self.llm_client.chat(messages)

            if response.status == "error":
                return TestResult(
                    test_case_id=test_case.id,
                    status="error",
                    response="",
                    latency_ms=response.latency_ms,
                    tokens_used=0,
                    cost_usd=0.0,
                    error=response.error
                )

            # 运行断言
            assertion_results = self.assertion_runner.run_assertions(
                response.content,
                test_case.dict()
            )

            # 构建结果
            result = TestResult(
                test_case_id=test_case.id,
                status="passed" if assertion_results["all_passed"] else "failed",
                response=response.content,
                latency_ms=response.latency_ms,
                tokens_used=response.usage.total_tokens,
                cost_usd=response.cost_usd or 0.0,
                assertions=assertion_results["assertions"],
                failed_assertions=assertion_results["failed_assertions"]
            )

            return result

        except Exception as e:
            return TestResult(
                test_case_id=test_case.id,
                status="error",
                response="",
                latency_ms=0.0,
                tokens_used=0,
                cost_usd=0.0,
                error=str(e)
            )

    def run_test_cases(self, test_cases: List[TestCase]) -> tuple[List[TestResult], TestSummary]:
        """
        运行多个测试用例

        Args:
            test_cases: 测试用例列表

        Returns:
            (测试结果列表, 测试摘要)
        """
        results = []
        start_time = datetime.now()

        print(f"开始运行 {len(test_cases)} 个测试用例...")

        for i, test_case in enumerate(test_cases, 1):
            print(f"[{i}/{len(test_cases)}] 运行 {test_case.id}...", end=" ")

            result = self.run_single_test(test_case)
            results.append(result)

            status_emoji = {
                "passed": "✅",
                "failed": "❌",
                "skipped": "⏭️",
                "error": "🔥"
            }
            print(f"{status_emoji.get(result.status, '?')} {result.status}")

            if result.status == "failed":
                for assertion_failure in result.failed_assertions:
                    print(f"     {assertion_failure}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 生成摘要
        summary = self._generate_summary(results, start_time, end_time, duration)

        return results, summary

    def _generate_summary(
        self,
        results: List[TestResult],
        start_time: datetime,
        end_time: datetime,
        duration: float
    ) -> TestSummary:
        """生成测试摘要"""

        total = len(results)
        passed = sum(1 for r in results if r.status == "passed")
        failed = sum(1 for r in results if r.status == "failed")
        skipped = sum(1 for r in results if r.status == "skipped")
        error = sum(1 for r in results if r.status == "error")

        pass_rate = passed / total if total > 0 else 0.0

        total_latency = sum(r.latency_ms for r in results)
        avg_latency = total_latency / total if total > 0 else 0.0

        total_tokens = sum(r.tokens_used for r in results)
        total_cost = sum(r.cost_usd for r in results)
        avg_cost = total_cost / total if total > 0 else 0.0

        return TestSummary(
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            error=error,
            pass_rate=pass_rate,
            total_latency_ms=total_latency,
            avg_latency_ms=avg_latency,
            total_tokens=total_tokens,
            total_cost_usd=total_cost,
            avg_cost_usd=avg_cost,
            duration_seconds=duration,
            start_time=start_time,
            end_time=end_time
        )

    def print_summary(self, summary: TestSummary):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("测试摘要")
        print("=" * 60)
        print(f"总用例数: {summary.total}")
        print(f"✅ 通过: {summary.passed} ({summary.pass_rate:.1%})")
        print(f"❌ 失败: {summary.failed}")
        print(f"⏭️  跳过: {summary.skipped}")
        print(f"🔥 错误: {summary.error}")
        print()
        print(f"平均延迟: {summary.avg_latency_ms:.2f}ms")
        print(f"总Token数: {summary.total_tokens}")
        print(f"总成本: ${summary.total_cost_usd:.4f}")
        print(f"平均成本: ${summary.avg_cost_usd:.6f}")
        print(f"执行时长: {summary.duration_seconds:.2f}秒")
        print("=" * 60)


# CLI支持
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="运行Prompt测试")
    parser.add_argument("--test-cases", required=True, help="测试用例文件路径(JSONL)")
    parser.add_argument("--provider", default="openai", help="LLM提供商")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="模型名称")
    parser.add_argument("--system-prompt", default="", help="系统提示词")
    parser.add_argument("--output", help="输出结果文件(JSON)")

    args = parser.parse_args()

    # 创建客户端和执行器
    client = LLMClient(provider=args.provider)
    runner = TestRunner(client, args.system_prompt)

    # 加载并运行测试
    test_cases = runner.load_test_cases(args.test_cases)
    results, summary = runner.run_test_cases(test_cases)

    # 打印摘要
    runner.print_summary(summary)

    # 保存结果
    if args.output:
        output_data = {
            "summary": summary.dict(),
            "results": [r.dict() for r in results]
        }
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n结果已保存到: {args.output}")
