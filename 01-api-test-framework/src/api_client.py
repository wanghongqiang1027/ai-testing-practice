"""
API Client for testing
封装HTTP请求，提供统一的API调用接口
"""

import httpx
from typing import Dict, Any, Optional, Union, List
from pydantic import BaseModel


class APIResponse(BaseModel):
    """API响应模型"""
    status_code: int
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    error: Optional[str] = None


class APIClient:
    """
    API客户端封装

    Example:
        client = APIClient(base_url="https://api.example.com")
        response = client.get("/users/1")
    """

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client(timeout=timeout)
        self.headers = {
            "Content-Type": "application/json"
        }

    def get(self, endpoint: str, params: Optional[Dict] = None) -> APIResponse:
        """
        发送GET请求

        Args:
            endpoint: API端点，如 "/users/1"
            params: 查询参数

        Returns:
            APIResponse对象
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.client.get(url, params=params, headers=self.headers)

            return APIResponse(
                status_code=response.status_code,
                data=response.json() if response.status_code == 200 else None,
                error=None if response.status_code == 200 else response.text
            )
        except Exception as e:
            return APIResponse(
                status_code=500,
                data=None,
                error=str(e)
            )

    def post(self, endpoint: str, json_data: Dict) -> APIResponse:
        """
        发送POST请求

        Args:
            endpoint: API端点
            json_data: JSON数据

        Returns:
            APIResponse对象
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.client.post(url, json=json_data, headers=self.headers)

            return APIResponse(
                status_code=response.status_code,
                data=response.json() if response.status_code in [200, 201] else None,
                error=None if response.status_code in [200, 201] else response.text
            )
        except Exception as e:
            return APIResponse(
                status_code=500,
                data=None,
                error=str(e)
            )

    def put(self, endpoint: str, json_data: Dict) -> APIResponse:
        """发送PUT请求"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.client.put(url, json=json_data, headers=self.headers)

            return APIResponse(
                status_code=response.status_code,
                data=response.json() if response.status_code == 200 else None,
                error=None if response.status_code == 200 else response.text
            )
        except Exception as e:
            return APIResponse(
                status_code=500,
                data=None,
                error=str(e)
            )

    def delete(self, endpoint: str) -> APIResponse:
        """发送DELETE请求"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.client.delete(url, headers=self.headers)

            return APIResponse(
                status_code=response.status_code,
                data=None,
                error=None if response.status_code == 200 else response.text
            )
        except Exception as e:
            return APIResponse(
                status_code=500,
                data=None,
                error=str(e)
            )

    def close(self):
        """关闭客户端"""
        self.client.close()
