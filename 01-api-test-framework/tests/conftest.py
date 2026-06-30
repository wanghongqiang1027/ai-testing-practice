"""
pytest配置文件
定义全局fixtures和配置
"""

import pytest
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from api_client import APIClient


@pytest.fixture(scope="session")
def base_url():
    """测试API的基础URL"""
    return "https://jsonplaceholder.typicode.com"


@pytest.fixture(scope="function")
def api_client(base_url):
    """
    创建API客户端实例
    使用function级别的scope，每个测试函数都会创建新的客户端
    """
    client = APIClient(base_url=base_url)
    yield client
    client.close()


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "username": "testuser"
    }


@pytest.fixture
def sample_post_data():
    """示例帖子数据"""
    return {
        "userId": 1,
        "title": "Test Post",
        "body": "This is a test post content."
    }
