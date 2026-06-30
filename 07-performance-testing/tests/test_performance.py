"""
性能测试
测试延迟和并发测试工具
"""

import pytest
import time
from latency_test import LatencyTester, measure_latency
from concurrency_test import ConcurrencyTester


def slow_function():
    """模拟慢函数"""
    time.sleep(0.1)
    return "done"


def fast_function():
    """模拟快函数"""
    time.sleep(0.01)
    return "done"


def error_function():
    """模拟错误函数"""
    raise Exception("Test error")


class TestLatencyTester:
    """延迟测试器测试"""

    @pytest.mark.smoke
    def test_basic_latency_test(self):
        """测试基本延迟测试"""
        tester = LatencyTester()

        metrics = tester.test(fast_function, num_requests=10, warmup=2)

        assert metrics.total_requests == 10
        assert metrics.min_latency > 0
        assert metrics.max_latency > metrics.min_latency
        assert metrics.avg_latency > 0
        assert metrics.p50 > 0
        assert metrics.p95 > 0
        assert metrics.p99 > 0

    def test_latency_percentiles(self):
        """测试延迟百分位数"""
        tester = LatencyTester()

        metrics = tester.test(slow_function, num_requests=20, warmup=0)

        # 百分位数应该递增
        assert metrics.p50 <= metrics.p95
        assert metrics.p95 <= metrics.p99
        assert metrics.p99 <= metrics.max_latency

    def test_latency_with_errors(self):
        """测试包含错误的延迟测试"""
        tester = LatencyTester()

        # 即使函数出错，也应该记录延迟
        metrics = tester.test(error_function, num_requests=5, warmup=0)

        assert metrics.total_requests == 5
        assert metrics.avg_latency >= 0

    def test_measure_single_latency(self):
        """测试单次延迟测量"""
        latency = measure_latency(fast_function)

        assert latency > 0
        assert latency < 1.0  # 应该少于1秒


class TestConcurrencyTester:
    """并发测试器测试"""

    @pytest.mark.smoke
    def test_basic_concurrency_test(self):
        """测试基本并发测试"""
        tester = ConcurrencyTester()

        metrics = tester.test(
            fast_function,
            concurrent_users=2,
            requests_per_user=5,
            timeout=5
        )

        assert metrics.concurrent_users == 2
        assert metrics.total_requests == 10  # 2 * 5
        assert metrics.success_count > 0
        assert metrics.success_rate > 0
        assert metrics.qps > 0

    def test_concurrency_with_errors(self):
        """测试包含错误的并发测试"""
        tester = ConcurrencyTester()

        metrics = tester.test(
            error_function,
            concurrent_users=2,
            requests_per_user=3,
            timeout=5
        )

        assert metrics.total_requests == 6
        assert metrics.failure_count > 0
        assert metrics.success_rate == 0  # 所有请求都失败

    def test_concurrency_timeout(self):
        """测试并发超时"""
        def very_slow_function():
            time.sleep(10)  # 超过超时时间

        tester = ConcurrencyTester()

        metrics = tester.test(
            very_slow_function,
            concurrent_users=2,
            requests_per_user=2,
            timeout=1  # 1秒超时
        )

        assert metrics.timeout_count > 0
        assert metrics.success_count == 0

    def test_concurrency_metrics_calculation(self):
        """测试并发指标计算"""
        tester = ConcurrencyTester()

        metrics = tester.test(
            fast_function,
            concurrent_users=3,
            requests_per_user=4,
            timeout=10
        )

        # 验证指标计算
        assert metrics.total_requests == metrics.success_count + metrics.failure_count
        assert 0 <= metrics.success_rate <= 1.0
        assert metrics.avg_latency >= 0
        assert metrics.duration_seconds > 0


class TestPerformanceMetrics:
    """性能指标测试"""

    def test_latency_metrics_validation(self):
        """测试延迟指标验证"""
        tester = LatencyTester()
        metrics = tester.test(fast_function, num_requests=10, warmup=0)

        # 所有指标应该是合理的
        assert metrics.min_latency <= metrics.avg_latency <= metrics.max_latency
        assert metrics.p50 >= metrics.min_latency
        assert metrics.p99 <= metrics.max_latency
        assert metrics.std_deviation >= 0

    def test_qps_calculation(self):
        """测试QPS计算"""
        tester = ConcurrencyTester()

        start = time.time()
        metrics = tester.test(
            fast_function,
            concurrent_users=5,
            requests_per_user=10,
            timeout=10
        )
        duration = time.time() - start

        # QPS应该接近实际值
        expected_qps = metrics.total_requests / metrics.duration_seconds
        assert abs(metrics.qps - expected_qps) < 0.1


class TestEdgeCases:
    """边界情况测试"""

    def test_single_request(self):
        """测试单个请求"""
        tester = LatencyTester()
        metrics = tester.test(fast_function, num_requests=1, warmup=0)

        assert metrics.total_requests == 1
        assert metrics.min_latency == metrics.max_latency
        assert metrics.std_deviation == 0  # 只有一个值，标准差为0

    def test_zero_concurrent_users(self):
        """测试零并发用户"""
        tester = ConcurrencyTester()

        # 至少需要1个并发用户
        metrics = tester.test(
            fast_function,
            concurrent_users=1,
            requests_per_user=0,  # 0个请求
            timeout=5
        )

        assert metrics.total_requests == 0

    def test_high_concurrency(self):
        """测试高并发"""
        tester = ConcurrencyTester()

        # 测试较高的并发
        metrics = tester.test(
            fast_function,
            concurrent_users=20,
            requests_per_user=5,
            timeout=10
        )

        assert metrics.concurrent_users == 20
        assert metrics.total_requests == 100
        # 高并发下成功率应该仍然较高
        assert metrics.success_rate > 0.8
