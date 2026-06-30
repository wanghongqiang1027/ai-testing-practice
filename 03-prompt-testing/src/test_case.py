"""
测试用例数据模型
定义 Prompt 测试用例的结构
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class TestCase(BaseModel):
    """Prompt测试用例模型"""

    id: str = Field(..., description="测试用例唯一标识")
    input: str = Field(..., description="用户输入/Prompt")
    category: Optional[str] = Field(None, description="测试类别")
    tags: List[str] = Field(default_factory=list, description="标签")

    # 断言条件
    expected_keywords: List[str] = Field(default_factory=list, description="应该包含的关键词")
    forbidden_keywords: List[str] = Field(default_factory=list, description="不应包含的关键词")
    must_include: List[str] = Field(default_factory=list, description="必须包含的短语")

    max_length: Optional[int] = Field(None, gt=0, description="最大长度限制")
    min_length: Optional[int] = Field(None, gt=0, description="最小长度限制")

    regex_pattern: Optional[str] = Field(None, description="正则表达式匹配")
    format: Optional[Literal["json", "list", "code", "plain"]] = Field(None, description="输出格式")

    # 参考答案
    reference_answer: Optional[str] = Field(None, description="参考答案")
    acceptable_answers: List[str] = Field(default_factory=list, description="可接受的答案列表")

    # 语义相似度
    semantic_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="语义相似度阈值")

    # 情感要求
    sentiment: Optional[Literal["positive", "negative", "neutral"]] = Field(None, description="期望的情感倾向")

    # 元数据
    description: Optional[str] = Field(None, description="测试用例描述")
    priority: Literal["high", "medium", "low"] = Field(default="medium", description="优先级")
    enabled: bool = Field(default=True, description="是否启用")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "qa_001",
                "input": "什么是Python？",
                "category": "基础问答",
                "tags": ["python", "编程"],
                "expected_keywords": ["编程语言", "解释型"],
                "forbidden_keywords": ["Java", "C++"],
                "max_length": 200,
                "priority": "high"
            }
        }


class TestResult(BaseModel):
    """测试结果模型"""

    test_case_id: str = Field(..., description="测试用例ID")
    status: Literal["passed", "failed", "skipped", "error"] = Field(..., description="测试状态")

    # 响应信息
    response: str = Field(..., description="LLM响应内容")
    latency_ms: float = Field(..., description="响应延迟(毫秒)")
    tokens_used: int = Field(..., description="使用的token数")
    cost_usd: float = Field(..., description="调用成本(美元)")

    # 断言结果
    assertions: Dict[str, bool] = Field(default_factory=dict, description="各项断言结果")
    failed_assertions: List[str] = Field(default_factory=list, description="失败的断言列表")

    # 错误信息
    error: Optional[str] = Field(None, description="错误信息")

    # 时间戳
    timestamp: datetime = Field(default_factory=datetime.now, description="执行时间")

    class Config:
        json_schema_extra = {
            "example": {
                "test_case_id": "qa_001",
                "status": "passed",
                "response": "Python是一种高级编程语言...",
                "latency_ms": 1250.5,
                "tokens_used": 120,
                "cost_usd": 0.00024,
                "assertions": {
                    "keywords": True,
                    "forbidden": True,
                    "length": True
                },
                "failed_assertions": []
            }
        }


class TestSummary(BaseModel):
    """测试摘要"""

    total: int = Field(..., description="总测试数")
    passed: int = Field(..., description="通过数")
    failed: int = Field(..., description="失败数")
    skipped: int = Field(..., description="跳过数")
    error: int = Field(..., description="错误数")

    pass_rate: float = Field(..., ge=0.0, le=1.0, description="通过率")

    total_latency_ms: float = Field(..., description="总延迟")
    avg_latency_ms: float = Field(..., description="平均延迟")

    total_tokens: int = Field(..., description="总token数")
    total_cost_usd: float = Field(..., description="总成本")
    avg_cost_usd: float = Field(..., description="平均成本")

    duration_seconds: float = Field(..., description="执行时长(秒)")

    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")


class ComparisonResult(BaseModel):
    """版本对比结果"""

    baseline_version: str = Field(..., description="基线版本")
    new_version: str = Field(..., description="新版本")

    baseline_summary: TestSummary = Field(..., description="基线版本摘要")
    new_summary: TestSummary = Field(..., description="新版本摘要")

    # 对比指标
    pass_rate_change: float = Field(..., description="通过率变化")
    latency_change_percent: float = Field(..., description="延迟变化百分比")
    cost_change_percent: float = Field(..., description="成本变化百分比")

    # 回归用例
    regression_cases: List[str] = Field(default_factory=list, description="回归用例ID列表")
    improvement_cases: List[str] = Field(default_factory=list, description="改进用例ID列表")

    recommendation: str = Field(..., description="推荐结论")
