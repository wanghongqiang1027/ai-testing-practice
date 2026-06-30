"""
LLM 数据模型
定义 LLM 调用相关的数据结构
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Message(BaseModel):
    """消息模型"""
    role: Literal["system", "user", "assistant"]
    content: str

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "什么是人工智能？"
            }
        }


class TokenUsage(BaseModel):
    """Token使用统计"""
    prompt_tokens: int = Field(..., description="输入token数")
    completion_tokens: int = Field(..., description="输出token数")
    total_tokens: int = Field(..., description="总token数")


class LLMResponse(BaseModel):
    """LLM响应模型"""
    status: Literal["success", "error"] = Field(..., description="响应状态")
    content: str = Field(..., description="响应内容")
    model: str = Field(..., description="使用的模型")
    usage: TokenUsage = Field(..., description="token使用统计")
    latency_ms: float = Field(..., description="响应延迟(毫秒)")
    finish_reason: Optional[str] = Field(None, description="结束原因")
    cost_usd: Optional[float] = Field(None, description="调用成本(美元)")
    error: Optional[str] = Field(None, description="错误信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "content": "人工智能是...",
                "model": "gpt-3.5-turbo",
                "usage": {
                    "prompt_tokens": 20,
                    "completion_tokens": 100,
                    "total_tokens": 120
                },
                "latency_ms": 1250.5,
                "finish_reason": "stop",
                "cost_usd": 0.00024
            }
        }


class PromptTemplate(BaseModel):
    """Prompt模板"""
    name: str = Field(..., description="模板名称")
    system_prompt: str = Field(..., description="系统提示词")
    variables: List[str] = Field(default_factory=list, description="模板变量")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: Optional[int] = Field(None, gt=0, description="最大输出token数")

    def render(self, **kwargs) -> str:
        """渲染模板"""
        result = self.system_prompt
        for var in self.variables:
            if var in kwargs:
                result = result.replace(f"{{{{{var}}}}}", str(kwargs[var]))
        return result

    class Config:
        json_schema_extra = {
            "example": {
                "name": "customer_service",
                "system_prompt": "你是{{company}}的客服助手，请回答用户关于{{product}}的问题。",
                "variables": ["company", "product"],
                "temperature": 0.7,
                "max_tokens": 500
            }
        }
