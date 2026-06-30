"""
延迟测试工具
测试系统响应时间
"""

import time
import statistics
from typing import List, Callable, Any
from models import LatencyMetrics


class LatencyTester:
    """
    延迟测试器

    测试单个请求的响应时间分布

    Example:
        tester = LatencyTester()
        metrics = tester.test(func=my_function, num_requests=100)
        print(f"P95延迟: {metrics.p95}s")
    """

    def test(
        self,
        func: Callable,
        num_requests: int = 100,
        warmup: int = 10,
        *args,
        **kwargs
    ) -> LatencyMetrics:
        """
        执行延迟测试

        Args:
            func: 要测试的函数
            num_requests: 请求数量
            warmup: 预热请求数
            *args, **kwargs: 传递给函数的参数

        Returns:
            延迟指标
        """
        print(f"开始延迟测试: {num_requests}个请求...")

        # 预热
        if warmup > 0:
            print(f"预热中 ({warmup}个请求)...")
            for _ in range(warmup):
                try:
                    func(*args, **kwargs)
                except Exception:
                    pass

        # 正式测试
        latencies = []

        for i in range(num_requests):
            start_time = time.time()

            try:
                func(*args, **kwargs)
                latency = time.time() - start_time
                latencies.append(latency)

                if (i + 1) % 10 == 0:
                    print(f"进度: {i + 1}/{num_requests}")

            except Exception as e:
                print(f"请求失败: {e}")
                # 失败的请求也记录延迟
                latency = time.time() - start_time
                latencies.append(latency)

        # 计算指标
        metrics = self._calculate_metrics(latencies)

        print(f"\n延迟测试完成!")
        print(f"P50: {metrics.p50:.3f}s")
        print(f"P95: {metrics.p95:.3f}s")
        print(f"P99: {metrics.p99:.3f}s")

        return metrics

    def _calculate_metrics(self, latencies: List[float]) -> LatencyMetrics:
        """
        计算延迟指标

        Args:
            latencies: 延迟列表

        Returns:
            延迟指标
        """
        if not latencies:
            raise ValueError("没有延迟数据")

        sorted_latencies = sorted(latencies)

        return LatencyMetrics(
            total_requests=len(latencies),
            min_latency=min(latencies),
            max_latency=max(latencies),
            avg_latency=statistics.mean(latencies),
            median_latency=statistics.median(latencies),
            p50=self._percentile(sorted_latencies, 50),
            p95=self._percentile(sorted_latencies, 95),
            p99=self._percentile(sorted_latencies, 99),
            std_deviation=statistics.stdev(latencies) if len(latencies) > 1 else 0.0
        )

    @staticmethod
    def _percentile(sorted_data: List[float], percentile: float) -> float:
        """
        计算百分位数

        Args:
            sorted_data: 排序后的数据
            percentile: 百分位 (0-100)

        Returns:
            百分位数值
        """
        if not sorted_data:
            return 0.0

        k = (len(sorted_data) - 1) * (percentile / 100)
        f = int(k)
        c = f + 1

        if c >= len(sorted_data):
            return sorted_data[-1]

        return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


def measure_latency(func: Callable) -> float:
    """
    测量单次函数调用的延迟

    Args:
        func: 要测量的函数

    Returns:
        延迟(秒)
    """
    start = time.time()
    func()
    return time.time() - start


def compare_latency(
    func1: Callable,
    func2: Callable,
    num_requests: int = 100
) -> dict:
    """
    比较两个函数的延迟

    Args:
        func1: 函数1
        func2: 函数2
        num_requests: 请求数量

    Returns:
        比较结果
    """
    tester = LatencyTester()

    print("测试函数1...")
    metrics1 = tester.test(func1, num_requests)

    print("\n测试函数2...")
    metrics2 = tester.test(func2, num_requests)

    # 计算差异
    improvement = {
        "p50": (metrics1.p50 - metrics2.p50) / metrics1.p50 * 100,
        "p95": (metrics1.p95 - metrics2.p95) / metrics1.p95 * 100,
        "p99": (metrics1.p99 - metrics2.p99) / metrics1.p99 * 100,
    }

    return {
        "func1_metrics": metrics1,
        "func2_metrics": metrics2,
        "improvement_percent": improvement
    }
