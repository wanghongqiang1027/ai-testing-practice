"""
pytest配置文件
定义LLM测试的fixtures和配置
"""

import pytest
import os
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from llm_client import LLMClient
from prompt_template import PromptManager


@pytest.fixture(scope="session")
def openai_api_key():
    """OpenAI API Key"""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("OPENAI_API_KEY not set")
    return key


@pytest.fixture(scope="session")
def anthropic_api_key():
    """Anthropic API Key"""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return key


@pytest.fixture
def openai_client(openai_api_key):
    """创建OpenAI客户端"""
    return LLMClient(provider="openai", api_key=openai_api_key)


@pytest.fixture
def anthropic_client(anthropic_api_key):
    """创建Anthropic客户端"""
    return LLMClient(provider="anthropic", api_key=anthropic_api_key)


@pytest.fixture
def prompt_manager():
    """创建Prompt管理器"""
    config_file = Path(__file__).parent.parent / "prompts" / "system_prompts.yaml"
    return PromptManager(str(config_file))


@pytest.fixture
def sample_messages():
    """示例消息"""
    return [
        {"role": "user", "content": "什么是Python？"}
    ]


@pytest.fixture
def sample_system_messages():
    """带系统消息的示例"""
    return [
        {"role": "system", "content": "你是一个Python专家。"},
        {"role": "user", "content": "什么是装饰器？"}
    ]
