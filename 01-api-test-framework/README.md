# 阶段 1：API 自动化测试框架

## 学习目标

- 掌握 pytest 基础用法
- 理解 fixture 和参数化测试
- 学会封装 HTTP 客户端
- 构建可维护的测试框架

## 项目结构

```
01-api-test-framework/
├── src/
│   ├── __init__.py
│   ├── api_client.py          # API客户端封装
│   └── models.py              # 数据模型
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # pytest配置和fixtures
│   ├── test_users.py          # 用户相关测试
│   └── test_posts.py          # 帖子相关测试
├── testdata/
│   └── test_cases.json        # 测试数据
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
cd 01-api-test-framework
pip install -r ../requirements.txt
```

### 2. 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行指定测试文件
pytest tests/test_users.py

# 参数化运行
pytest tests/test_users.py -v

# 生成HTML报告
pytest tests/ --html=reports/report.html --self-contained-html
```

## 核心知识点

### 1. pytest Fixture

```python
@pytest.fixture
def api_client():
    """创建API客户端实例"""
    client = APIClient(base_url="https://jsonplaceholder.typicode.com")
    yield client
    # 清理代码
```

### 2. 参数化测试

```python
@pytest.mark.parametrize("user_id,expected_status", [
    (1, 200),
    (2, 200),
    (999, 404)
])
def test_get_user(api_client, user_id, expected_status):
    response = api_client.get_user(user_id)
    assert response.status_code == expected_status
```

### 3. 数据驱动测试

```python
# 从JSON文件加载测试数据
test_cases = load_test_data("testdata/test_cases.json")

@pytest.mark.parametrize("case", test_cases)
def test_create_user(api_client, case):
    response = api_client.create_user(case["payload"])
    assert response.status_code == case["expected_status"]
```

## 练习任务

- [ ] 完成用户 CRUD 测试
- [ ] 添加断言验证响应结构
- [ ] 实现数据驱动测试
- [ ] 生成测试报告
- [ ] 集成到 CI/CD

## 常见问题

### Q: 如何处理认证？

A: 在 `api_client.py` 中封装认证逻辑：

```python
class APIClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
```

### Q: 如何处理测试数据清理？

A: 使用 fixture 的 yield 机制：

```python
@pytest.fixture
def created_user(api_client):
    # 创建测试数据
    user = api_client.create_user({"name": "Test User"})
    yield user
    # 清理测试数据
    api_client.delete_user(user["id"])
```

## 参考资料

- pytest 官方文档：https://docs.pytest.org/
- JSONPlaceholder API：https://jsonplaceholder.typicode.com/
