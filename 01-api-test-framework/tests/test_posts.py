"""
帖子API测试
测试帖子相关的CRUD操作
"""

import pytest
from models import Post


class TestPostAPI:
    """帖子API测试类"""

    @pytest.mark.smoke
    def test_get_post(self, api_client):
        """测试获取单个帖子"""
        response = api_client.get("/posts/1")

        assert response.status_code == 200
        assert response.data is not None
        assert "id" in response.data
        assert "title" in response.data
        assert "body" in response.data
        assert "userId" in response.data

        # 使用Pydantic验证数据
        post = Post(**response.data)
        assert post.id == 1

    def test_get_all_posts(self, api_client):
        """测试获取所有帖子"""
        response = api_client.get("/posts")

        assert response.status_code == 200
        assert response.data is not None
        assert isinstance(response.data, list)
        assert len(response.data) > 0

    def test_create_post(self, api_client, sample_post_data):
        """测试创建帖子"""
        response = api_client.post("/posts", sample_post_data)

        assert response.status_code == 201
        assert response.data is not None
        assert response.data["title"] == sample_post_data["title"]
        assert response.data["body"] == sample_post_data["body"]
        assert response.data["userId"] == sample_post_data["userId"]

    @pytest.mark.parametrize("user_id", [1, 2, 3])
    def test_create_post_for_different_users(self, api_client, user_id):
        """参数化测试：为不同用户创建帖子"""
        post_data = {
            "userId": user_id,
            "title": f"Post for user {user_id}",
            "body": "Test content"
        }

        response = api_client.post("/posts", post_data)

        assert response.status_code == 201
        assert response.data["userId"] == user_id

    def test_update_post(self, api_client):
        """测试更新帖子"""
        updated_data = {
            "id": 1,
            "userId": 1,
            "title": "Updated Title",
            "body": "Updated content"
        }

        response = api_client.put("/posts/1", updated_data)

        assert response.status_code == 200
        assert response.data["title"] == updated_data["title"]

    def test_delete_post(self, api_client):
        """测试删除帖子"""
        response = api_client.delete("/posts/1")
        assert response.status_code == 200


class TestPostAPIValidation:
    """帖子API数据验证测试"""

    def test_post_required_fields(self, api_client):
        """测试必填字段验证"""
        # 缺少title字段
        incomplete_data = {
            "userId": 1,
            "body": "Content without title"
        }

        # JSONPlaceholder不会真正验证，但我们可以用Pydantic验证
        with pytest.raises(Exception):
            Post(**incomplete_data)

    def test_post_field_types(self, api_client):
        """测试字段类型验证"""
        # userId应该是整数
        invalid_data = {
            "userId": "not_a_number",
            "title": "Test",
            "body": "Content"
        }

        with pytest.raises(Exception):
            Post(**invalid_data)
