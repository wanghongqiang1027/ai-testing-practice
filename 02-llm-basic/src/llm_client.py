"""
LLM 客户端封装
支持多个 LLM 提供商的统一接口
"""

import os
import time
from typing import List, Optional, Dict, Any
from openai import OpenAI, AuthenticationError, RateLimitError
from anthropic import Anthropic

from models import Message, LLMResponse, TokenUsage


class LLMClient:
    """
    统一的 LLM 客户端

    支持的提供商:
    - OpenAI (gpt-3.5-turbo, gpt-4, etc.)
    - Anthropic (claude-3, etc.)

    Example:
        client = LLMClient(provider="openai")
        response = client.chat([
            {"role": "user", "content": "Hello!"}
        ])
    """

    # 模型定价 (USD per 1K tokens)
    PRICING = {
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    }

    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        timeout: int = 60
    ):
        """
        初始化客户端

        Args:
            provider: 提供商 ("openai" 或 "anthropic")
            api_key: API密钥，如果为None则从环境变量读取
            timeout: 超时时间(秒)
        """
        self.provider = provider.lower()
        self.timeout = timeout

        if self.provider == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found")
            self.client = OpenAI(api_key=api_key, timeout=timeout)

        elif self.provider == "anthropic":
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key not found")
            self.client = Anthropic(api_key=api_key, timeout=timeout)

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None
    ) -> LLMResponse:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数 (0-2)
            max_tokens: 最大输出token数
            response_format: 响应格式 (如 {"type": "json_object"})

        Returns:
            LLMResponse对象
        """
        start_time = time.time()

        try:
            if self.provider == "openai":
                response = self._call_openai(
                    messages, model, temperature, max_tokens, response_format
                )
            elif self.provider == "anthropic":
                response = self._call_anthropic(
                    messages, model, temperature, max_tokens
                )
            else:
                raise ValueError(f"Unknown provider: {self.provider}")

            latency_ms = (time.time() - start_time) * 1000

            # 计算成本
            cost = self._calculate_cost(
                model,
                response.usage.prompt_tokens,
                response.usage.completion_tokens
            )

            response.latency_ms = latency_ms
            response.cost_usd = cost

            return response

        except AuthenticationError as e:
            return LLMResponse(
                status="error",
                content="",
                model=model,
                usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                latency_ms=(time.time() - start_time) * 1000,
                error=f"Authentication failed: {str(e)}"
            )
        except RateLimitError as e:
            return LLMResponse(
                status="error",
                content="",
                model=model,
                usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                latency_ms=(time.time() - start_time) * 1000,
                error=f"Rate limit exceeded: {str(e)}"
            )
        except Exception as e:
            return LLMResponse(
                status="error",
                content="",
                model=model,
                usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                latency_ms=(time.time() - start_time) * 1000,
                error=f"Unexpected error: {str(e)}"
            )

    def _call_openai(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        response_format: Optional[Dict[str, str]]
    ) -> LLMResponse:
        """调用 OpenAI API"""

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        if response_format:
            kwargs["response_format"] = response_format

        completion = self.client.chat.completions.create(**kwargs)

        return LLMResponse(
            status="success",
            content=completion.choices[0].message.content,
            model=completion.model,
            usage=TokenUsage(
                prompt_tokens=completion.usage.prompt_tokens,
                completion_tokens=completion.usage.completion_tokens,
                total_tokens=completion.usage.total_tokens
            ),
            latency_ms=0,  # 会在外层填充
            finish_reason=completion.choices[0].finish_reason
        )

    def _call_anthropic(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int]
    ) -> LLMResponse:
        """调用 Anthropic API"""

        # Anthropic 需要分离 system 消息
        system_msg = None
        user_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)

        kwargs = {
            "model": model,
            "messages": user_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 1024,
        }

        if system_msg:
            kwargs["system"] = system_msg

        response = self.client.messages.create(**kwargs)

        return LLMResponse(
            status="success",
            content=response.content[0].text,
            model=response.model,
            usage=TokenUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens
            ),
            latency_ms=0,  # 会在外层填充
            finish_reason=response.stop_reason
        )

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        计算调用成本

        Args:
            model: 模型名称
            input_tokens: 输入token数
            output_tokens: 输出token数

        Returns:
            成本(美元)
        """
        # 查找匹配的定价
        pricing = None
        for model_name, price in self.PRICING.items():
            if model_name in model:
                pricing = price
                break

        if not pricing:
            return 0.0

        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]

        return round(input_cost + output_cost, 6)
