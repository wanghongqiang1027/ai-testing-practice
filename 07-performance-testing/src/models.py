"""
性能测试数据模型
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class LatencyMetrics(BaseModel):
    """延迟指标"""
    total_requests: int = Field(..., description="总请求数")

    # 延迟统计（秒）
    min_latency: float = Field(..., description="最小延迟")
    max_latency: float = Field(..., description="最大延迟")
    avg_latency: float = Field(..., description="平均延迟")
    median_latency: float = Field(..., description="中位数延迟")

    # 百分位数
    p50: float = Field(..., description="P50延迟")
    p95: float = Field(..., description="P95延迟")
    p99: float = Field(..., description="P99延迟")

    # 标准差
    std_deviation: float = Field(..., description="标准差")


class ThroughputMetrics(BaseModel):
    """吞吐量指标"""
    total_requests: int = Field(..., description="总请求数")
    duration_seconds: float = Field(..., description="测试时长(秒)")

    qps: float = Field(..., description="每秒查询数")
    avg_response_time: float = Field(..., description="平均响应时间")

    success_count: int = Field(..., description="成功请求数")
    failure_count: int = Field(..., description="失败请求数")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="成功率")


class ConcurrencyMetrics(BaseModel):
    """并发指标"""
    concurrent_users: int = Field(..., description="并发用户数")
    total_requests: int = Field(..., description="总请求数")
    duration_seconds: float = Field(..., description="测试时长")

    success_count: int = Field(..., description="成功数")
    failure_count: int = Field(..., description="失败数")
    timeout_count: int = Field(..., description="超时数")

    success_rate: float = Field(..., ge=0.0, le=1.0, description="成功率")
    avg_latency: float = Field(..., description="平均延迟")
    qps: float = Field(..., description="每秒查询数")


class ResourceMetrics(BaseModel):
    """资源使用指标"""

    # CPU
    cpu_percent: float = Field(..., ge=0.0, le=100.0, description="CPU使用率(%)")
    cpu_count: int = Field(..., description="CPU核心数")

    # 内存
    memory_used_mb: float = Field(..., description="已使用内存(MB)")
    memory_total_mb: float = Field(..., description="总内存(MB)")
    memory_percent: float = Field(..., ge=0.0, le=100.0, description="内存使用率(%)")

    # 网络（可选）
    network_sent_mb: Optional[float] = Field(None, description="发送数据(MB)")
    network_recv_mb: Optional[float] = Field(None, description="接收数据(MB)")


class PerformanceTestResult(BaseModel):
    """性能测试结果"""
    test_name: str = Field(..., description="测试名称")
    test_type: str = Field(..., description="测试类型")

    # 指标
    latency_metrics: Optional[LatencyMetrics] = Field(None, description="延迟指标")
    throughput_metrics: Optional[ThroughputMetrics] = Field(None, description="吞吐量指标")
    concurrency_metrics: Optional[ConcurrencyMetrics] = Field(None, description="并发指标")
    resource_metrics: Optional[ResourceMetrics] = Field(None, description="资源指标")

    # 元数据
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    duration_seconds: float = Field(..., description="总时长")

    # 环境信息
    environment: Dict[str, Any] = Field(default_factory=dict, description="环境信息")


class PerformanceReport(BaseModel):
    """性能测试报告"""
    report_id: str = Field(..., description="报告ID")
    report_date: datetime = Field(..., description="报告日期")

    # 测试结果
    test_results: List[PerformanceTestResult] = Field(..., description="测试结果列表")

    # 汇总
    summary: Dict[str, Any] = Field(default_factory=dict, description="测试汇总")

    # 性能瓶颈
    bottlenecks: List[str] = Field(default_factory=list, description="性能瓶颈")

    # 优化建议
    recommendations: List[str] = Field(default_factory=list, description="优化建议")


class BenchmarkConfig(BaseModel):
    """基准测试配置"""
    name: str = Field(..., description="基准测试名称")

    # 测试参数
    num_requests: int = Field(default=100, description="请求数量")
    concurrent_users: int = Field(default=1, description="并发用户数")
    duration_seconds: int = Field(default=60, description="测试时长(秒)")

    # 目标指标
    target_p95_latency: Optional[float] = Field(None, description="目标P95延迟")
    target_qps: Optional[float] = Field(None, description="目标QPS")
    target_success_rate: Optional[float] = Field(None, description="目标成功率")

    # 其他配置
    warmup_requests: int = Field(default=10, description="预热请求数")
    timeout_seconds: int = Field(default=30, description="超时时间(秒)")
