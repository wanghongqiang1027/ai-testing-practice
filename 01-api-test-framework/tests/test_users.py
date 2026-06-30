"""
用户API测试
测试用户相关的CRUD操作
"""

import pytest
from models import User


class TestUserAPI:
    """用户API测试类"""

    @pytest.mark.smoke
    def test_get_user(self, api_client):
        """测试获取单个用户"""
        # 发送请求
        response = api_client.get("/users/1")

        # 断言状态码
        assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"

        # 断言响应数据
        assert response.data is not None, "响应数据不应为空"
        assert "id" in response.data, "响应应包含id字段"
        assert "name" in response.data, "响应应包含name字段"
        assert "email" in response.data, "响应应包含email字段"

        # 验证数据模型
        user = User(**response.data)
        assert user.id == 1

    @pytest.mark.parametrize("user_id,expected_status", [
        (1, 200),
        (2, 200),
        (10, 200),
        (999, 404)  # 不存在的用户
    ])
    def test_get_user_parametrize(self, api_client, user_id, expected_status):
        """参数化测试：获取不同的用户"""
        response = api_client.get(f"/users/{user_id}")
        assert response.status_code == expected_status

    def test_get_all_users(self, api_client):
        """测试获取所有用户列表"""
        response = api_client.get("/users")

        assert response.status_code == 200
        assert response.data is not None
        assert isinstance(response.data, list), "响应应该是列表"
        assert len(response.data) > 0, "用户列表不应为空"

        # 验证第一个用户的数据结构
        first_user = User(**response.data[0])
        assert first_user.id is not None

    def test_create_user(self, api_client, sample_user_data):
        """测试创建用户"""
        response = api_client.post("/users", sample_user_data)

        assert response.status_code == 201
        assert response.data is not None

        # 验证返回的数据包含创建的信息
        created_user = response.data
        assert created_user["name"] == sample_user_data["name"]
        assert created_user["email"] == sample_user_data["email"]
        assert "id" in created_user, "创建的用户应该有ID"

    @pytest.mark.parametrize("invalid_data,expected_field", [
        ({"name": "", "email": "test@example.com"}, "name"),  # 空名称
        ({"name": "Test", "email": "invalid-email"}, "email"),  # 无效邮箱
    ])
    def test_create_user_invalid_data(self, api_client, invalid_data, expected_field):
        """测试创建用户时的数据验证"""
        # 尝试用Pydantic验证，应该失败
        with pytest.raises(Exception):
            User(**invalid_data)

    def test_update_user(self, api_client):
        """测试更新用户"""
        updated_data = {
            "id": 1,
            "name": "Updated Name",
            "email": "updated@example.com",
            "username": "updateduser"
        }

        response = api_client.put("/users/1", updated_data)

        assert response.status_code == 200
        assert response.data is not None
        assert response.data["name"] == updated_data["name"]

    def test_delete_user(self, api_client):
        """测试删除用户"""
        response = api_client.delete("/users/1")

        assert response.status_code == 200

    def test_get_user_posts(self, api_client):
        """测试获取用户的所有帖子"""
        response = api_client.get("/users/1/posts")

        assert response.status_code == 200
        assert response.data is not None
        assert isinstance(response.data, list)

        # 验证帖子属于该用户
        if len(response.data) > 0:
            assert response.data[0]["userId"] == 1


class TestUserAPIEdgeCases:
    """用户API边界测试"""

    def test_get_nonexistent_user(self, api_client):
        """测试获取不存在的用户"""
        response = api_client.get("/users/99999")
        assert response.status_code == 404

    def test_update_nonexistent_user(self, api_client, sample_user_data):
        """测试更新不存在的用户"""
        response = api_client.put("/users/99999", sample_user_data)
        assert response.status_code in [404, 500]

    def test_get_users_with_pagination(self, api_client):
        """测试分页查询用户"""
        # 使用查询参数
        response = api_client.get("/users", params={"_limit": 5})

        assert response.status_code == 200
        assert response.data is not None
        assert len(response.data) <= 5
