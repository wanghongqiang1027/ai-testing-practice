"""
LLM 基础测试
测试 LLM 客户端的基本功能
"""

import pytest
from models import LLMResponse
from response_parser import ResponseParser


class TestLLMBasic:
    """LLM基础功能测试"""

    @pytest.mark.smoke
    @pytest.mark.requires_api
    def test_simple_chat_openai(self, openai_client, sample_messages):
        """测试OpenAI简单对话"""
        response = openai_client.chat(
            messages=sample_messages,
            model="gpt-3.5-turbo",
            temperature=0.7
        )

        # 验证响应状态
        assert response.status == "success", f"Expected success, got: {response.error}"

        # 验证内容
        assert len(response.content) > 0, "响应内容不应为空"
        assert "python" in response.content.lower(), "响应应该包含Python相关内容"

        # 验证token使用
        assert response.usage.prompt_tokens > 0, "应该有输入tokens"
        assert response.usage.completion_tokens > 0, "应该有输出tokens"
        assert response.usage.total_tokens > 0, "应该有总tokens"

        # 验证延迟
        assert response.latency_ms > 0, "应该记录延迟"
        assert response.latency_ms < 30000, "延迟不应超过30秒"

        # 验证成本
        assert response.cost_usd is not None, "应该计算成本"
        assert response.cost_usd > 0, "成本应该大于0"

    @pytest.mark.requires_api
    def test_system_message(self, openai_client, sample_system_messages):
        """测试系统消息"""
        response = openai_client.chat(
            messages=sample_system_messages,
            model="gpt-3.5-turbo"
        )

        assert response.status == "success"
        assert "装饰器" in response.content or "decorator" in response.content.lower()

    @pytest.mark.requires_api
    def test_temperature_control(self, openai_client):
        """测试温度参数控制"""
        messages = [{"role": "user", "content": "说一个数字"}]

        # 低温度 - 应该更确定
        response_low = openai_client.chat(
            messages=messages,
            model="gpt-3.5-turbo",
            temperature=0.1
        )

        # 高温度 - 应该更随机
        response_high = openai_client.chat(
            messages=messages,
            model="gpt-3.5-turbo",
            temperature=1.5
        )

        assert response_low.status == "success"
        assert response_high.status == "success"

    @pytest.mark.requires_api
    def test_max_tokens_limit(self, openai_client):
        """测试输出长度限制"""
        messages = [{"role": "user", "content": "写一篇500字的文章"}]

        response = openai_client.chat(
            messages=messages,
            model="gpt-3.5-turbo",
            max_tokens=50  # 限制为50个tokens
        )

        assert response.status == "success"
        assert response.usage.completion_tokens <= 50, "输出tokens应该不超过限制"

    @pytest.mark.requires_api
    def test_different_models(self, openai_client):
        """测试不同模型"""
        messages = [{"role": "user", "content": "Hello"}]

        # GPT-3.5
        response_35 = openai_client.chat(
            messages=messages,
            model="gpt-3.5-turbo"
        )

        assert response_35.status == "success"
        assert "gpt-3.5" in response_35.model

    def test_cost_calculation(self, openai_client):
        """测试成本计算"""
        # 模拟响应
        cost = openai_client._calculate_cost(
            model="gpt-3.5-turbo",
            input_tokens=1000,
            output_tokens=500
        )

        # GPT-3.5: 输入$0.0015/1K, 输出$0.002/1K
        expected_cost = (1000 * 0.0015 / 1000) + (500 * 0.002 / 1000)
        assert abs(cost - expected_cost) < 0.0001, f"成本计算错误: {cost} vs {expected_cost}"


class TestPromptTemplate:
    """Prompt模板测试"""

    def test_load_templates(self, prompt_manager):
        """测试加载模板"""
        templates = prompt_manager.list_templates()

        assert len(templates) > 0, "应该有模板"
        assert "customer_service" in templates
        assert "json_extractor" in templates

    def test_get_template(self, prompt_manager):
        """测试获取模板"""
        template = prompt_manager.get_template("simple_qa")

        assert template is not None
        assert template.name == "simple_qa"
        assert len(template.system_prompt) > 0

    def test_render_template(self, prompt_manager):
        """测试渲染模板"""
        rendered = prompt_manager.render(
            "customer_service",
            company="ABC公司",
            product="智能手机"
        )

        assert "ABC公司" in rendered
        assert "智能手机" in rendered

    def test_template_variables(self, prompt_manager):
        """测试模板变量"""
        template = prompt_manager.get_template("customer_service")

        assert "company" in template.variables
        assert "product" in template.variables


class TestResponseParser:
    """响应解析器测试"""

    def test_parse_json(self):
        """测试JSON解析"""
        parser = ResponseParser()

        # 正常JSON
        content = '{"name": "John", "age": 30}'
        data = parser.parse_json(content)

        assert data is not None
        assert data["name"] == "John"
        assert data["age"] == 30

    def test_parse_json_with_text(self):
        """测试带文字的JSON解析"""
        parser = ResponseParser()

        # JSON前后有文字
        content = '这是一个对象: {"name": "John", "age": 30} 就是这样'
        data = parser.parse_json(content, strict=False)

        assert data is not None
        assert data["name"] == "John"

    def test_parse_json_invalid(self):
        """测试无效JSON"""
        parser = ResponseParser()

        content = "这不是JSON"

        # 非严格模式应该返回None
        data = parser.parse_json(content, strict=False)
        assert data is None

        # 严格模式应该抛出异常
        with pytest.raises(ValueError):
            parser.parse_json(content, strict=True)

    def test_extract_code_block(self):
        """测试提取代码块"""
        parser = ResponseParser()

        content = """
这是一段代码：

```python
def hello():
    print("Hello")
```

就是这样。
"""

        code = parser.extract_code_block(content, "python")
        assert code is not None
        assert "def hello():" in code
        assert 'print("Hello")' in code

    def test_extract_list_items(self):
        """测试提取列表项"""
        parser = ResponseParser()

        content = """
以下是步骤：

1. 第一步
2. 第二步
3. 第三步
"""

        items = parser.extract_list_items(content)
        assert len(items) == 3
        assert "第一步" in items[0]
        assert "第二步" in items[1]

    def test_validate_required_fields(self):
        """测试字段验证"""
        parser = ResponseParser()

        data = {"name": "John", "age": 30}

        # 所有字段都在
        valid, missing = parser.validate_required_fields(data, ["name", "age"])
        assert valid is True
        assert len(missing) == 0

        # 缺少字段
        valid, missing = parser.validate_required_fields(data, ["name", "email"])
        assert valid is False
        assert "email" in missing
