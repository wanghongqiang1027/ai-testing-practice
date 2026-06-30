"""
断言框架
实现多维度的Prompt测试断言
"""

import re
import json
from typing import List, Optional, Dict, Any


class Assertor:
    """
    Prompt测试断言器

    提供多种断言方法验证LLM响应

    Example:
        assertor = Assertor()
        assertor.assert_keywords(response, ["Python", "编程"])
    """

    @staticmethod
    def assert_keywords(response: str, keywords: List[str], mode: str = "all") -> tuple[bool, str]:
        """
        断言关键词

        Args:
            response: LLM响应
            keywords: 关键词列表
            mode: "all" 所有关键词都必须存在, "any" 至少一个关键词存在

        Returns:
            (是否通过, 失败原因)
        """
        if not keywords:
            return True, ""

        response_lower = response.lower()
        found_keywords = [kw for kw in keywords if kw.lower() in response_lower]

        if mode == "all":
            if len(found_keywords) == len(keywords):
                return True, ""
            missing = set(keywords) - set(found_keywords)
            return False, f"缺少关键词: {missing}"

        elif mode == "any":
            if len(found_keywords) > 0:
                return True, ""
            return False, f"未找到任何关键词: {keywords}"

        else:
            raise ValueError(f"Unknown mode: {mode}")

    @staticmethod
    def assert_forbidden(response: str, forbidden: List[str]) -> tuple[bool, str]:
        """
        断言禁止词

        Args:
            response: LLM响应
            forbidden: 禁止词列表

        Returns:
            (是否通过, 失败原因)
        """
        if not forbidden:
            return True, ""

        response_lower = response.lower()
        found_forbidden = [word for word in forbidden if word.lower() in response_lower]

        if len(found_forbidden) == 0:
            return True, ""

        return False, f"包含禁止词: {found_forbidden}"

    @staticmethod
    def assert_length(
        response: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ) -> tuple[bool, str]:
        """
        断言长度

        Args:
            response: LLM响应
            min_length: 最小长度
            max_length: 最大长度

        Returns:
            (是否通过, 失败原因)
        """
        length = len(response)

        if min_length is not None and length < min_length:
            return False, f"长度过短: {length} < {min_length}"

        if max_length is not None and length > max_length:
            return False, f"长度过长: {length} > {max_length}"

        return True, ""

    @staticmethod
    def assert_must_include(response: str, phrases: List[str]) -> tuple[bool, str]:
        """
        断言必须包含的短语

        Args:
            response: LLM响应
            phrases: 必须包含的短语列表

        Returns:
            (是否通过, 失败原因)
        """
        if not phrases:
            return True, ""

        missing = [phrase for phrase in phrases if phrase not in response]

        if len(missing) == 0:
            return True, ""

        return False, f"缺少短语: {missing}"

    @staticmethod
    def assert_regex(response: str, pattern: str) -> tuple[bool, str]:
        """
        断言正则表达式匹配

        Args:
            response: LLM响应
            pattern: 正则表达式

        Returns:
            (是否通过, 失败原因)
        """
        if not pattern:
            return True, ""

        if re.search(pattern, response):
            return True, ""

        return False, f"未匹配正则表达式: {pattern}"

    @staticmethod
    def assert_json_format(response: str, required_fields: Optional[List[str]] = None) -> tuple[bool, str]:
        """
        断言JSON格式

        Args:
            response: LLM响应
            required_fields: 必需字段列表

        Returns:
            (是否通过, 失败原因)
        """
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)

            # 检查必需字段
            if required_fields:
                missing = [field for field in required_fields if field not in data]
                if missing:
                    return False, f"缺少必需字段: {missing}"

            return True, ""

        except json.JSONDecodeError as e:
            return False, f"JSON格式错误: {str(e)}"

    @staticmethod
    def assert_list_format(response: str, min_items: int = 1) -> tuple[bool, str]:
        """
        断言列表格式

        支持的格式:
        - 1. item
        - * item
        - - item

        Args:
            response: LLM响应
            min_items: 最少列表项数

        Returns:
            (是否通过, 失败原因)
        """
        patterns = [
            r'^\d+\.\s+(.+)$',  # 1. item
            r'^\*\s+(.+)$',      # * item
            r'^-\s+(.+)$',       # - item
        ]

        items = []
        for line in response.split('\n'):
            line = line.strip()
            for pattern in patterns:
                if re.match(pattern, line):
                    items.append(line)
                    break

        if len(items) >= min_items:
            return True, ""

        return False, f"列表项数量不足: {len(items)} < {min_items}"

    @staticmethod
    def assert_code_block(response: str, language: Optional[str] = None) -> tuple[bool, str]:
        """
        断言代码块格式

        Args:
            response: LLM响应
            language: 期望的编程语言

        Returns:
            (是否通过, 失败原因)
        """
        if language:
            pattern = f"```{language}\n(.*?)\n```"
        else:
            pattern = r"```(?:\w+)?\n(.*?)\n```"

        if re.search(pattern, response, re.DOTALL):
            return True, ""

        return False, f"未找到代码块{f'({language})' if language else ''}"

    @staticmethod
    def assert_not_empty(response: str) -> tuple[bool, str]:
        """
        断言响应非空

        Args:
            response: LLM响应

        Returns:
            (是否通过, 失败原因)
        """
        if response and response.strip():
            return True, ""

        return False, "响应为空"

    @staticmethod
    def assert_contains_url(response: str) -> tuple[bool, str]:
        """
        断言包含URL

        Args:
            response: LLM响应

        Returns:
            (是否通过, 失败原因)
        """
        url_pattern = r'https?://[^\s]+'
        if re.search(url_pattern, response):
            return True, ""

        return False, "未找到URL"

    @staticmethod
    def assert_sentiment(response: str, expected: str) -> tuple[bool, str]:
        """
        断言情感倾向

        简单实现：基于关键词判断
        生产环境建议使用专门的情感分析模型

        Args:
            response: LLM响应
            expected: 期望的情感 ("positive", "negative", "neutral")

        Returns:
            (是否通过, 失败原因)
        """
        positive_words = ["好", "棒", "优秀", "满意", "喜欢", "成功", "赞"]
        negative_words = ["差", "糟糕", "失败", "不满", "讨厌", "错误", "问题"]

        response_lower = response.lower()

        positive_count = sum(1 for word in positive_words if word in response_lower)
        negative_count = sum(1 for word in negative_words if word in response_lower)

        if expected == "positive" and positive_count > negative_count:
            return True, ""
        elif expected == "negative" and negative_count > positive_count:
            return True, ""
        elif expected == "neutral" and positive_count == negative_count:
            return True, ""

        return False, f"情感不符: 期望{expected}, 实际positive={positive_count}, negative={negative_count}"


class AssertionRunner:
    """
    断言执行器

    批量执行多个断言并收集结果
    """

    def __init__(self):
        self.assertor = Assertor()

    def run_assertions(self, response: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行所有断言

        Args:
            response: LLM响应
            test_case: 测试用例

        Returns:
            断言结果字典
        """
        results = {
            "all_passed": True,
            "assertions": {},
            "failed_assertions": []
        }

        # 关键词断言
        if test_case.get("expected_keywords"):
            passed, reason = self.assertor.assert_keywords(response, test_case["expected_keywords"])
            results["assertions"]["keywords"] = passed
            if not passed:
                results["all_passed"] = False
                results["failed_assertions"].append(f"keywords: {reason}")

        # 禁止词断言
        if test_case.get("forbidden_keywords"):
            passed, reason = self.assertor.assert_forbidden(response, test_case["forbidden_keywords"])
            results["assertions"]["forbidden"] = passed
            if not passed:
                results["all_passed"] = False
                results["failed_assertions"].append(f"forbidden: {reason}")

        # 长度断言
        if test_case.get("min_length") or test_case.get("max_length"):
            passed, reason = self.assertor.assert_length(
                response,
                test_case.get("min_length"),
                test_case.get("max_length")
            )
            results["assertions"]["length"] = passed
            if not passed:
                results["all_passed"] = False
                results["failed_assertions"].append(f"length: {reason}")

        # 必须包含短语
        if test_case.get("must_include"):
            passed, reason = self.assertor.assert_must_include(response, test_case["must_include"])
            results["assertions"]["must_include"] = passed
            if not passed:
                results["all_passed"] = False
                results["failed_assertions"].append(f"must_include: {reason}")

        # 正则表达式
        if test_case.get("regex_pattern"):
            passed, reason = self.assertor.assert_regex(response, test_case["regex_pattern"])
            results["assertions"]["regex"] = passed
            if not passed:
                results["all_passed"] = False
                results["failed_assertions"].append(f"regex: {reason}")

        # 格式断言
        if test_case.get("format") == "json":
            passed, reason = self.assertor.assert_json_format(response)
            results["assertions"]["format"] = passed
            if not passed:
                results["all_passed"] = False
                results["failed_assertions"].append(f"format: {reason}")

        # 非空断言
        passed, reason = self.assertor.assert_not_empty(response)
        results["assertions"]["not_empty"] = passed
        if not passed:
            results["all_passed"] = False
            results["failed_assertions"].append(f"not_empty: {reason}")

        return results
