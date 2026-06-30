"""
响应解析器
解析和验证 LLM 响应
"""

import json
import re
from typing import Dict, Any, Optional


class ResponseParser:
    """
    LLM 响应解析器

    Example:
        parser = ResponseParser()
        data = parser.parse_json(response.content)
    """

    @staticmethod
    def parse_json(content: str, strict: bool = True) -> Optional[Dict[str, Any]]:
        """
        解析JSON响应

        Args:
            content: 响应内容
            strict: 是否严格模式（如果解析失败则抛出异常）

        Returns:
            解析后的字典，如果失败返回None（非严格模式）
        """
        try:
            # 尝试直接解析
            return json.loads(content)
        except json.JSONDecodeError:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            if strict:
                raise ValueError(f"Failed to parse JSON from content: {content[:100]}...")
            return None

    @staticmethod
    def extract_code_block(content: str, language: str = "") -> Optional[str]:
        """
        提取代码块

        Args:
            content: 响应内容
            language: 代码语言（如 "python"）

        Returns:
            提取的代码，如果没有找到返回None
        """
        if language:
            pattern = f"```{language}\n(.*?)\n```"
        else:
            pattern = r"```(?:\w+)?\n(.*?)\n```"

        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()

        return None

    @staticmethod
    def extract_list_items(content: str) -> list[str]:
        """
        提取列表项

        支持的格式:
        - 1. item
        - * item
        - - item

        Returns:
            列表项列表
        """
        patterns = [
            r'^\d+\.\s+(.+)$',  # 1. item
            r'^\*\s+(.+)$',      # * item
            r'^-\s+(.+)$',       # - item
        ]

        items = []
        for line in content.split('\n'):
            line = line.strip()
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    items.append(match.group(1))
                    break

        return items

    @staticmethod
    def validate_required_fields(
        data: Dict[str, Any],
        required_fields: list[str]
    ) -> tuple[bool, list[str]]:
        """
        验证必需字段

        Args:
            data: 数据字典
            required_fields: 必需字段列表

        Returns:
            (是否全部存在, 缺失字段列表)
        """
        missing = [field for field in required_fields if field not in data]
        return len(missing) == 0, missing

    @staticmethod
    def clean_text(content: str) -> str:
        """
        清理文本

        - 移除多余空白
        - 规范化换行
        """
        # 移除多余空白
        content = re.sub(r'\s+', ' ', content)
        # 规范化换行
        content = content.strip()
        return content
