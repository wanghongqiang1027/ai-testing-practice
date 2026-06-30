"""
AI安全测试数据模型
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class AttackPayload(BaseModel):
    """攻击载荷"""
    id: str = Field(..., description="载荷ID")
    payload: str = Field(..., description="攻击载荷内容")
    type: Literal["direct", "role_play", "delimiter", "impersonation", "encoding"] = Field(..., description="攻击类型")
    severity: Literal["high", "medium", "low"] = Field(..., description="严重程度")
    language: str = Field(default="zh", description="语言")
    description: Optional[str] = Field(None, description="描述")


class JailbreakPrompt(BaseModel):
    """越狱提示词"""
    id: str = Field(..., description="提示词ID")
    name: str = Field(..., description="越狱技术名称")
    prompt: str = Field(..., description="完整提示词")
    effectiveness: Literal["high", "medium", "low"] = Field(..., description="有效性")
    category: Optional[str] = Field(None, description="类别")


class HarmfulContent(BaseModel):
    """有害内容"""
    id: str = Field(..., description="内容ID")
    content: str = Field(..., description="有害内容")
    category: Literal["violence", "hate", "illegal", "adult", "self_harm", "misinformation"] = Field(..., description="类别")
    severity: Literal["high", "medium", "low"] = Field(..., description="严重程度")


class SecurityTestResult(BaseModel):
    """安全测试结果"""
    test_id: str = Field(..., description="测试ID")
    test_type: Literal["prompt_injection", "jailbreak", "harmful_content", "privacy"] = Field(..., description="测试类型")

    # 输入输出
    input_payload: str = Field(..., description="输入载荷")
    system_response: str = Field(..., description="系统响应")

    # 检测结果
    is_attack_detected: bool = Field(..., description="是否检测到攻击")
    is_attack_successful: bool = Field(..., description="攻击是否成功")

    # 详细信息
    detection_method: Optional[str] = Field(None, description="检测方法")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="置信度")

    # 元数据
    severity: Literal["high", "medium", "low"] = Field(..., description="严重程度")
    timestamp: datetime = Field(default_factory=datetime.now, description="测试时间")


class SecurityMetrics(BaseModel):
    """安全指标"""

    # 攻击成功率
    attack_success_rate: float = Field(..., ge=0.0, le=1.0, description="攻击成功率")

    # 检测率
    detection_rate: float = Field(..., ge=0.0, le=1.0, description="检测率")

    # 误报率
    false_positive_rate: float = Field(..., ge=0.0, le=1.0, description="误报率")

    # 各类型统计
    total_tests: int = Field(..., description="总测试数")
    successful_attacks: int = Field(..., description="成功攻击数")
    detected_attacks: int = Field(..., description="检测到的攻击数")
    false_positives: int = Field(..., description="误报数")


class SecurityReport(BaseModel):
    """安全报告"""

    report_id: str = Field(..., description="报告ID")
    system_name: str = Field(..., description="系统名称")
    test_date: datetime = Field(..., description="测试日期")

    # 总体指标
    overall_metrics: SecurityMetrics = Field(..., description="总体指标")

    # 各类型测试结果
    prompt_injection_results: List[SecurityTestResult] = Field(default_factory=list)
    jailbreak_results: List[SecurityTestResult] = Field(default_factory=list)
    harmful_content_results: List[SecurityTestResult] = Field(default_factory=list)

    # 发现的漏洞
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list, description="发现的漏洞")

    # 建议
    recommendations: List[str] = Field(default_factory=list, description="安全建议")


class DefenseRule(BaseModel):
    """防御规则"""
    rule_id: str = Field(..., description="规则ID")
    name: str = Field(..., description="规则名称")
    description: str = Field(..., description="规则描述")
    pattern: str = Field(..., description="匹配模式")
    action: Literal["block", "warn", "log"] = Field(..., description="动作")
    enabled: bool = Field(default=True, description="是否启用")
