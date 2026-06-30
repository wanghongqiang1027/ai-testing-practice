"""
Agent测试数据模型
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Tool(BaseModel):
    """工具模型"""
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    parameters: Dict[str, Any] = Field(..., description="参数schema")


class ToolCall(BaseModel):
    """工具调用记录"""
    tool_name: str = Field(..., description="工具名称")
    parameters: Dict[str, Any] = Field(..., description="调用参数")
    result: Optional[Any] = Field(None, description="调用结果")
    success: bool = Field(..., description="是否成功")
    error: Optional[str] = Field(None, description="错误信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="调用时间")


class AgentStep(BaseModel):
    """Agent执行步骤"""
    step_number: int = Field(..., description="步骤编号")
    thought: str = Field(..., description="思考过程")
    action: str = Field(..., description="执行动作")
    action_input: Optional[Dict[str, Any]] = Field(None, description="动作输入")
    observation: Optional[str] = Field(None, description="观察结果")
    tool_call: Optional[ToolCall] = Field(None, description="工具调用")


class ConversationMessage(BaseModel):
    """对话消息"""
    role: Literal["user", "assistant", "system"] = Field(..., description="角色")
    content: str = Field(..., description="内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="工具调用")


class AgentState(BaseModel):
    """Agent状态"""
    current_task: Optional[str] = Field(None, description="当前任务")
    conversation_history: List[ConversationMessage] = Field(default_factory=list, description="对话历史")
    completed_steps: List[AgentStep] = Field(default_factory=list, description="已完成步骤")
    intermediate_results: Dict[str, Any] = Field(default_factory=dict, description="中间结果")

    # 元数据
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    status: Literal["running", "completed", "failed", "paused"] = Field(default="running", description="状态")


class AgentResult(BaseModel):
    """Agent执行结果"""
    task: str = Field(..., description="任务描述")
    status: Literal["success", "failure", "partial"] = Field(..., description="执行状态")
    final_answer: str = Field(..., description="最终答案")

    # 执行细节
    steps: List[AgentStep] = Field(default_factory=list, description="执行步骤")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="工具调用")

    # 性能指标
    total_steps: int = Field(..., description="总步骤数")
    total_time_ms: float = Field(..., description="总耗时(毫秒)")
    total_tokens: int = Field(..., description="总token数")
    total_cost_usd: float = Field(..., description="总成本(美元)")

    # 错误信息
    error: Optional[str] = Field(None, description="错误信息")


class AgentTestCase(BaseModel):
    """Agent测试用例"""
    id: str = Field(..., description="测试用例ID")
    task: str = Field(..., description="任务描述")
    expected_tools: List[str] = Field(default_factory=list, description="期望使用的工具")
    expected_answer: Optional[str] = Field(None, description="期望答案")
    expected_keywords: List[str] = Field(default_factory=list, description="期望关键词")
    max_steps: int = Field(default=10, description="最大步骤数")
    timeout_seconds: int = Field(default=60, description="超时时间(秒)")

    # 元数据
    category: Optional[str] = Field(None, description="类别")
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium", description="难度")
    tags: List[str] = Field(default_factory=list, description="标签")


class AgentEvaluationMetrics(BaseModel):
    """Agent评测指标"""
    task_success_rate: float = Field(..., ge=0.0, le=1.0, description="任务成功率")
    tool_calling_accuracy: float = Field(..., ge=0.0, le=1.0, description="工具调用准确率")
    avg_steps: float = Field(..., description="平均步骤数")
    avg_time_ms: float = Field(..., description="平均耗时")
    avg_cost_usd: float = Field(..., description="平均成本")

    # 详细统计
    total_tasks: int = Field(..., description="总任务数")
    successful_tasks: int = Field(..., description="成功任务数")
    failed_tasks: int = Field(..., description="失败任务数")
    total_tool_calls: int = Field(..., description="总工具调用次数")
    correct_tool_calls: int = Field(..., description="正确工具调用次数")


class AgentEvaluationReport(BaseModel):
    """Agent评测报告"""
    agent_name: str = Field(..., description="Agent名称")
    test_date: datetime = Field(..., description="测试日期")

    # 评测指标
    metrics: AgentEvaluationMetrics = Field(..., description="评测指标")

    # 测试结果
    test_results: List[Dict[str, Any]] = Field(default_factory=list, description="测试结果")

    # 失败案例
    failed_cases: List[str] = Field(default_factory=list, description="失败案例ID")

    # 建议
    recommendations: List[str] = Field(default_factory=list, description="改进建议")
