"""
并发测试工具
测试系统在并发负载下的表现
"""

import time
import concurrent.futures
from typing import Callable, List
from models import ConcurrencyMetrics


class ConcurrencyTester:
    """
    并发测试器

    测试系统处理并发请求的能力

    Example:
        tester = ConcurrencyTester()
        metrics = tester.test(
            func=my_function,
            concurrent_users=10,
            requests_per_user=10
        )
    """

    def test(
        self,
        func: Callable,
        concurrent_users: int = 10,
        requests_per_user: int = 10,
        timeout: int = 30,
        *args,
        **kwargs
    ) -> ConcurrencyMetrics:
        """
        执行并发测试

        Args:
            func: 要测试的函数
            concurrent_users: 并发用户数
            requests_per_user: 每个用户的请求数
            timeout: 超时时间(秒)
            *args, **kwargs: 传递给函数的参数

        Returns:
            并发指标
        """
        total_requests = concurrent_users * requests_per_user

        print(f"开始并发测试:")
        print(f"  并发用户: {concurrent_users}")
        print(f"  每用户请求: {requests_per_user}")
        print(f"  总请求: {total_requests}")

        start_time = time.time()
        results = []

        # 使用线程池执行并发请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # 提交所有任务
            futures = []

            for user_id in range(concurrent_users):
                for req_id in range(requests_per_user):
                    future = executor.submit(
                        self._execute_request,
                        func,
                        timeout,
                        user_id,
                        req_id,
                        *args,
                        **kwargs
                    )
                    futures.append(future)

            # 收集结果
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                results.append(result)

                if (i + 1) % 10 == 0:
                    print(f"完成: {i + 1}/{total_requests}")

        duration = time.time() - start_time

        # 计算指标
        metrics = self._calculate_metrics(results, concurrent_users, duration)

        print(f"\n并发测试完成!")
        print(f"成功率: {metrics.success_rate:.1%}")
        print(f"平均延迟: {metrics.avg_latency:.3f}s")
        print(f"QPS: {metrics.qps:.2f}")

        return metrics

    def _execute_request(
        self,
        func: Callable,
        timeout: int,
        user_id: int,
        req_id: int,
        *args,
        **kwargs
    ) -> dict:
        """执行单个请求"""
        start_time = time.time()

        try:
            # 执行函数（带超时）
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                result = future.result(timeout=timeout)

            latency = time.time() - start_time

            return {
                "success": True,
                "latency": latency,
                "user_id": user_id,
                "req_id": req_id,
                "timeout": False
            }

        except concurrent.futures.TimeoutError:
            return {
                "success": False,
                "latency": timeout,
                "user_id": user_id,
                "req_id": req_id,
                "timeout": True,
                "error": "Timeout"
            }

        except Exception as e:
            latency = time.time() - start_time
            return {
                "success": False,
                "latency": latency,
                "user_id": user_id,
                "req_id": req_id,
                "timeout": False,
                "error": str(e)
            }

    def _calculate_metrics(
        self,
        results: List[dict],
        concurrent_users: int,
        duration: float
    ) -> ConcurrencyMetrics:
        """计算并发指标"""
        total = len(results)
        success = sum(1 for r in results if r["success"])
        failure = sum(1 for r in results if not r["success"])
        timeout = sum(1 for r in results if r.get("timeout", False))

        latencies = [r["latency"] for r in results if r["success"]]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        return ConcurrencyMetrics(
            concurrent_users=concurrent_users,
            total_requests=total,
            duration_seconds=duration,
            success_count=success,
            failure_count=failure,
            timeout_count=timeout,
            success_rate=success / total if total > 0 else 0.0,
            avg_latency=avg_latency,
            qps=total / duration if duration > 0 else 0.0
        )


def stress_test(
    func: Callable,
    start_users: int = 1,
    max_users: int = 50,
    step: int = 5,
    requests_per_user: int = 10
) -> List[ConcurrencyMetrics]:
    """
    压力测试：逐步增加并发直到失败

    Args:
        func: 要测试的函数
        start_users: 起始并发数
        max_users: 最大并发数
        step: 每次增加的并发数
        requests_per_user: 每用户请求数

    Returns:
        不同并发级别的指标列表
    """
    tester = ConcurrencyTester()
    results = []

    for users in range(start_users, max_users + 1, step):
        print(f"\n测试 {users} 并发用户...")
        metrics = tester.test(func, users, requests_per_user)
        results.append(metrics)

        # 如果成功率低于80%，停止测试
        if metrics.success_rate < 0.8:
            print(f"\n成功率降至 {metrics.success_rate:.1%}，停止测试")
            break

    return results
