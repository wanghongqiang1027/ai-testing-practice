"""
Prompt注入检测器
检测和防御Prompt注入攻击
"""

import re
from typing import List, Tuple, Optional
from models import AttackPayload


class PromptInjectionDetector:
    """
    Prompt注入检测器

    检测常见的Prompt注入攻击模式

    Example:
        detector = PromptInjectionDetector()
        is_attack = detector.is_injection("忽略之前的所有指令")
        # is_attack = True
    """

    # 注入关键词（中文）
    INJECTION_KEYWORDS_ZH = [
        "忽略", "忽视", "无视", "跳过",
        "新指令", "新任务", "新角色",
        "扮演", "假装", "现在你是",
        "删除", "覆盖", "替换",
        "系统提示", "system prompt"
    ]

    # 注入关键词（英文）
    INJECTION_KEYWORDS_EN = [
        "ignore", "disregard", "forget", "skip",
        "new instructions", "new task", "new role",
        "pretend", "act as", "you are now",
        "delete", "override", "replace",
        "system prompt", "previous instructions"
    ]

    # 角色扮演模式
    ROLE_PLAY_PATTERNS = [
        r"(现在|从现在开始)(你是|扮演|假装)",
        r"(now|from now on)\s+(you are|pretend|act as)",
        r"进入.*模式",
        r"enter.*mode"
    ]

    # 分隔符攻击
    DELIMITER_PATTERNS = [
        r"={3,}",  # ===
        r"-{3,}",  # ---
        r"\*{3,}",  # ***
        r"#{3,}",  # ###
    ]

    def __init__(self, threshold: float = 0.5):
        """
        初始化检测器

        Args:
            threshold: 检测阈值（0-1），越低越严格
        """
        self.threshold = threshold

    def is_injection(self, text: str) -> bool:
        """
        检测是否为注入攻击

        Args:
            text: 输入文本

        Returns:
            是否为注入攻击
        """
        score = self.calculate_injection_score(text)
        return score >= self.threshold

    def calculate_injection_score(self, text: str) -> float:
        """
        计算注入可能性分数

        Args:
            text: 输入文本

        Returns:
            注入分数（0-1）
        """
        scores = []

        # 检查关键词
        keyword_score = self._check_keywords(text)
        scores.append(keyword_score)

        # 检查角色扮演
        role_play_score = self._check_role_play(text)
        scores.append(role_play_score)

        # 检查分隔符
        delimiter_score = self._check_delimiters(text)
        scores.append(delimiter_score)

        # 检查系统关键词
        system_score = self._check_system_keywords(text)
        scores.append(system_score)

        # 返回最高分数
        return max(scores) if scores else 0.0

    def detect_with_details(self, text: str) -> Tuple[bool, List[str]]:
        """
        检测并返回详细信息

        Args:
            text: 输入文本

        Returns:
            (是否为注入攻击, 触发的规则列表)
        """
        triggered_rules = []

        # 检查各种模式
        if self._check_keywords(text) > 0:
            triggered_rules.append("包含注入关键词")

        if self._check_role_play(text) > 0:
            triggered_rules.append("检测到角色扮演模式")

        if self._check_delimiters(text) > 0:
            triggered_rules.append("检测到分隔符攻击")

        if self._check_system_keywords(text) > 0:
            triggered_rules.append("包含系统关键词")

        is_injection = len(triggered_rules) > 0

        return is_injection, triggered_rules

    def _check_keywords(self, text: str) -> float:
        """检查注入关键词"""
        text_lower = text.lower()

        # 检查中文关键词
        zh_matches = sum(1 for kw in self.INJECTION_KEYWORDS_ZH if kw in text_lower)

        # 检查英文关键词
        en_matches = sum(1 for kw in self.INJECTION_KEYWORDS_EN if kw in text_lower)

        total_matches = zh_matches + en_matches

        if total_matches >= 3:
            return 1.0
        elif total_matches >= 2:
            return 0.8
        elif total_matches >= 1:
            return 0.6

        return 0.0

    def _check_role_play(self, text: str) -> float:
        """检查角色扮演模式"""
        for pattern in self.ROLE_PLAY_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return 1.0

        return 0.0

    def _check_delimiters(self, text: str) -> float:
        """检查分隔符攻击"""
        matches = 0

        for pattern in self.DELIMITER_PATTERNS:
            if re.search(pattern, text):
                matches += 1

        if matches >= 2:
            return 0.8
        elif matches >= 1:
            return 0.5

        return 0.0

    def _check_system_keywords(self, text: str) -> float:
        """检查系统关键词"""
        system_keywords = [
            "system", "prompt", "instruction",
            "系统", "提示词", "指令"
        ]

        text_lower = text.lower()
        matches = sum(1 for kw in system_keywords if kw in text_lower)

        if matches >= 2:
            return 0.9

        return 0.0


class AdvancedInjectionDetector(PromptInjectionDetector):
    """
    高级注入检测器

    增加更多检测规则
    """

    def __init__(self, threshold: float = 0.5):
        super().__init__(threshold)

    def calculate_injection_score(self, text: str) -> float:
        """
        计算注入可能性分数（增强版）

        Args:
            text: 输入文本

        Returns:
            注入分数（0-1）
        """
        # 调用父类方法
        base_score = super().calculate_injection_score(text)

        # 额外检查
        encoding_score = self._check_encoding_attack(text)
        instruction_score = self._check_instruction_override(text)

        # 返回最高分数
        return max(base_score, encoding_score, instruction_score)

    def _check_encoding_attack(self, text: str) -> float:
        """检测编码混淆攻击"""
        # 检查Base64编码
        if re.search(r'[A-Za-z0-9+/]{20,}={0,2}', text):
            return 0.6

        # 检查URL编码
        if text.count('%') > 3:
            return 0.6

        # 检查Unicode编码
        if re.search(r'\\u[0-9a-fA-F]{4}', text):
            return 0.5

        return 0.0

    def _check_instruction_override(self, text: str) -> float:
        """检测指令覆盖"""
        override_patterns = [
            r"(忽略|forget|ignore).*(之前|previous|prior)",
            r"(新|new).*(指令|instruction|prompt)",
            r"(覆盖|override|replace).*(系统|system)"
        ]

        for pattern in override_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return 1.0

        return 0.0


class InjectionDefender:
    """
    注入攻击防御器

    提供输入清理和安全响应
    """

    def __init__(self, detector: Optional[PromptInjectionDetector] = None):
        """
        初始化防御器

        Args:
            detector: 注入检测器
        """
        self.detector = detector or PromptInjectionDetector()

    def sanitize_input(self, text: str) -> Tuple[str, bool]:
        """
        清理输入

        Args:
            text: 原始输入

        Returns:
            (清理后的文本, 是否被修改)
        """
        original = text

        # 移除多余的分隔符
        text = re.sub(r'={3,}', '', text)
        text = re.sub(r'-{3,}', '', text)
        text = re.sub(r'\*{3,}', '', text)

        # 限制长度
        if len(text) > 1000:
            text = text[:1000]

        was_modified = (text != original)

        return text, was_modified

    def get_safe_response(self, user_input: str) -> str:
        """
        获取安全响应

        Args:
            user_input: 用户输入

        Returns:
            安全响应文本
        """
        is_injection, rules = self.detector.detect_with_details(user_input)

        if is_injection:
            return self._get_rejection_message(rules)

        return user_input

    def _get_rejection_message(self, triggered_rules: List[str]) -> str:
        """获取拒绝消息"""
        return f"抱歉，您的输入包含不安全的内容，已被拒绝。检测到：{', '.join(triggered_rules)}"
