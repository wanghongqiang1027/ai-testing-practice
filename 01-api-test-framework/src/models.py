"""
数据模型定义
使用 Pydantic 进行数据验证
"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    """用户模型"""
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    username: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "username": "johndoe"
            }
        }


class Post(BaseModel):
    """帖子模型"""
    id: Optional[int] = None
    userId: int
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "userId": 1,
                "title": "Sample Post",
                "body": "This is a sample post content."
            }
        }
