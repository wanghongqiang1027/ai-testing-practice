"""
断言器测试
测试各种断言方法
"""

import pytest
from assertor import Assertor, AssertionRunner


class TestAssertor:
    """断言器测试类"""

    @pytest.mark.smoke
    def test_assert_keywords_all(self):
        """测试关键词断言 - all模式"""
        assertor = Assertor()

        # 应该通过
        passed, reason = assertor.assert_keywords(
            "Python是一种编程语言",
            ["Python", "编程语言"],
            mode="all"
        )
        assert passed is True

        # 应该失败
        passed, reason = assertor.assert_keywords(
            "Python是一种编程语言",
            ["Python", "Java"],
            mode="all"
        )
        assert passed is False
        assert "Java" in reason

    def test_assert_keywords_any(self):
        """测试关键词断言 - any模式"""
        assertor = Assertor()

        # 应该通过
        passed, reason = assertor.assert_keywords(
            "Python是一种编程语言",
            ["Python", "Java"],
            mode="any"
        )
        assert passed is True

        # 应该失败
        passed, reason = assertor.assert_keywords(
            "Python是一种编程语言",
            ["Java", "C++"],
            mode="any"
        )
        assert passed is False

    @pytest.mark.smoke
    def test_assert_forbidden(self):
        """测试禁止词断言"""
        assertor = Assertor()

        # 应该通过
        passed, reason = assertor.assert_forbidden(
            "Python是一种编程语言",
            ["Java", "C++"]
        )
        assert passed is True

        # 应该失败
        passed, reason = assertor.assert_forbidden(
            "Python是一种编程语言",
            ["Python", "编程"]
        )
        assert passed is False
        assert "Python" in reason

    def test_assert_length(self):
        """测试长度断言"""
        assertor = Assertor()

        text = "这是一段测试文本"

        # 应该通过
        passed, _ = assertor.assert_length(text, min_length=5, max_length=20)
        assert passed is True

        # 最小长度失败
        passed, reason = assertor.assert_length(text, min_length=20)
        assert passed is False
        assert "过短" in reason

        # 最大长度失败
        passed, reason = assertor.assert_length(text, max_length=5)
        assert passed is False
        assert "过长" in reason

    def test_assert_must_include(self):
        """测试必须包含短语"""
        assertor = Assertor()

        # 应该通过
        passed, _ = assertor.assert_must_include(
            "Python是一种高级编程语言",
            ["Python", "编程语言"]
        )
        assert passed is True

        # 应该失败
        passed, reason = assertor.assert_must_include(
            "Python是一种编程语言",
            ["Python是", "Java"]
        )
        assert passed is False
        assert "Java" in reason

    def test_assert_regex(self):
        """测试正则表达式断言"""
        assertor = Assertor()

        # 应该通过 - 匹配数字
        passed, _ = assertor.assert_regex("订单号：12345", r"\d+")
        assert passed is True

        # 应该失败
        passed, reason = assertor.assert_regex("没有数字", r"\d+")
        assert passed is False

    def test_assert_json_format(self):
        """测试JSON格式断言"""
        assertor = Assertor()

        # 应该通过
        passed, _ = assertor.assert_json_format('{"name": "John", "age": 30}')
        assert passed is True

        # 带文字的JSON也应该通过
        passed, _ = assertor.assert_json_format('这是结果: {"name": "John"}')
        assert passed is True

        # 验证必需字段
        passed, _ = assertor.assert_json_format(
            '{"name": "John", "age": 30}',
            required_fields=["name", "age"]
        )
        assert passed is True

        # 缺少必需字段应该失败
        passed, reason = assertor.assert_json_format(
            '{"name": "John"}',
            required_fields=["name", "age"]
        )
        assert passed is False
        assert "age" in reason

        # 无效JSON应该失败
        passed, reason = assertor.assert_json_format("not json")
        assert passed is False

    def test_assert_list_format(self):
        """测试列表格式断言"""
        assertor = Assertor()

        # 数字列表
        text1 = """
1. 第一项
2. 第二项
3. 第三项
"""
        passed, _ = assertor.assert_list_format(text1, min_items=3)
        assert passed is True

        # 星号列表
        text2 = """
* 项目A
* 项目B
"""
        passed, _ = assertor.assert_list_format(text2, min_items=2)
        assert passed is True

        # 项数不足应该失败
        passed, reason = assertor.assert_list_format(text2, min_items=5)
        assert passed is False

    def test_assert_code_block(self):
        """测试代码块断言"""
        assertor = Assertor()

        # 应该通过
        text = """
这是代码：
```python
def hello():
    print("Hello")
```
"""
        passed, _ = assertor.assert_code_block(text, language="python")
        assert passed is True

        # 无代码块应该失败
        passed, reason = assertor.assert_code_block("没有代码块", language="python")
        assert passed is False

    def test_assert_not_empty(self):
        """测试非空断言"""
        assertor = Assertor()

        # 应该通过
        passed, _ = assertor.assert_not_empty("有内容")
        assert passed is True

        # 应该失败
        passed, reason = assertor.assert_not_empty("")
        assert passed is False

        passed, reason = assertor.assert_not_empty("   ")
        assert passed is False

    def test_assert_sentiment(self):
        """测试情感断言"""
        assertor = Assertor()

        # 积极情感
        passed, _ = assertor.assert_sentiment("这个产品非常好用，我很满意！", "positive")
        assert passed is True

        # 消极情感
        passed, _ = assertor.assert_sentiment("这个产品很差，我很不满意。", "negative")
        assert passed is True


class TestAssertionRunner:
    """断言执行器测试"""

    def test_run_assertions(self):
        """测试批量执行断言"""
        runner = AssertionRunner()

        test_case = {
            "expected_keywords": ["Python", "编程"],
            "forbidden_keywords": ["Java"],
            "max_length": 100,
            "must_include": ["编程语言"]
        }

        response = "Python是一种高级编程语言"

        results = runner.run_assertions(response, test_case)

        assert results["all_passed"] is True
        assert results["assertions"]["keywords"] is True
        assert results["assertions"]["forbidden"] is True
        assert results["assertions"]["length"] is True
        assert len(results["failed_assertions"]) == 0

    def test_run_assertions_with_failures(self):
        """测试有失败的断言"""
        runner = AssertionRunner()

        test_case = {
            "expected_keywords": ["Java"],  # 不存在
            "forbidden_keywords": ["Python"],  # 存在
            "max_length": 5  # 太短
        }

        response = "Python是一种编程语言"

        results = runner.run_assertions(response, test_case)

        assert results["all_passed"] is False
        assert len(results["failed_assertions"]) > 0
