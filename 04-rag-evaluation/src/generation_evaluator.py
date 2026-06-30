"""
生成评测器
评估RAG生成质量
"""

import sys
from pathlib import Path
from typing import Optional

# 添加父目录到路径
llm_basic_path = str(Path(__file__).parent.parent.parent / "02-llm-basic" / "src")
sys.path.insert(0, llm_basic_path)

from llm_client import LLMClient

# 移除llm_basic路径，避免冲突
sys.path.remove(llm_basic_path)

# 导入本地models
from models import GenerationMetrics


class GenerationEvaluator:
    """
    生成质量评测器

    实现核心生成评测指标:
    - Faithfulness: 忠实度（答案是否基于上下文）
    - Answer Relevancy: 答案相关性（是否回答问题）
    - Context Precision: 上下文精确度
    - Context Recall: 上下文召回率

    Example:
        evaluator = GenerationEvaluator(llm_client)
        metrics = evaluator.evaluate(
            question="什么是Python？",
            context="Python是一种编程语言...",
            answer="Python是编程语言",
            reference_answer="Python是高级编程语言"
        )
    """

    def __init__(self, llm_client: LLMClient):
        """
        初始化评测器

        Args:
            llm_client: LLM客户端（用于LLM-as-Judge）
        """
        self.llm_client = llm_client

    def evaluate(
        self,
        question: str,
        context: str,
        answer: str,
        reference_answer: Optional[str] = None
    ) -> GenerationMetrics:
        """
        评估生成质量

        Args:
            question: 问题
            context: 检索到的上下文
            answer: 生成的答案
            reference_answer: 参考答案（可选）

        Returns:
            生成评测指标
        """
        # 评估忠实度
        faithfulness = self.evaluate_faithfulness(question, context, answer)

        # 评估答案相关性
        answer_relevancy = self.evaluate_answer_relevancy(question, answer)

        # 如果有参考答案，评估上下文指标
        context_precision = None
        context_recall = None
        if reference_answer:
            context_precision = self.evaluate_context_precision(context, answer)
            context_recall = self.evaluate_context_recall(context, reference_answer)

        return GenerationMetrics(
            faithfulness=faithfulness,
            answer_relevancy=answer_relevancy,
            context_precision=context_precision,
            context_recall=context_recall
        )

    def evaluate_faithfulness(self, question: str, context: str, answer: str) -> float:
        """
        评估忠实度

        使用LLM-as-Judge判断答案是否基于上下文

        Args:
            question: 问题
            context: 上下文
            answer: 答案

        Returns:
            忠实度分数 (0.0-1.0)
        """
        prompt = f"""请评估以下答案是否完全基于给定的上下文。

问题: {question}

上下文:
{context}

答案: {answer}

评分标准:
1.0 - 答案完全基于上下文，没有任何额外信息
0.5 - 答案大部分基于上下文，但有少量推测
0.0 - 答案包含上下文中没有的信息

请只返回一个数字分数(0.0, 0.5, 或 1.0)，不要有其他文字。
"""

        try:
            response = self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=10
            )

            # 提取分数
            score_text = response.content.strip()
            score = float(score_text)

            # 限制范围
            return max(0.0, min(1.0, score))

        except Exception as e:
            print(f"忠实度评估失败: {e}")
            return 0.5  # 默认中等分数

    def evaluate_answer_relevancy(self, question: str, answer: str) -> float:
        """
        评估答案相关性

        使用LLM-as-Judge判断答案是否回答了问题

        Args:
            question: 问题
            answer: 答案

        Returns:
            相关性分数 (0.0-1.0)
        """
        prompt = f"""请评估以下答案是否直接回答了问题。

问题: {question}

答案: {answer}

评分标准:
1.0 - 答案完全直接回答了问题
0.5 - 答案部分回答了问题
0.0 - 答案没有回答问题或答非所问

请只返回一个数字分数(0.0, 0.5, 或 1.0)，不要有其他文字。
"""

        try:
            response = self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=10
            )

            score_text = response.content.strip()
            score = float(score_text)

            return max(0.0, min(1.0, score))

        except Exception as e:
            print(f"相关性评估失败: {e}")
            return 0.5

    def evaluate_context_precision(self, context: str, answer: str) -> float:
        """
        评估上下文精确度

        判断上下文中有多少内容被用于生成答案

        Args:
            context: 上下文
            answer: 答案

        Returns:
            精确度分数 (0.0-1.0)
        """
        prompt = f"""请评估上下文中有多少内容被用于生成答案。

上下文:
{context}

答案: {answer}

评分标准:
1.0 - 答案使用了上下文的大部分内容
0.5 - 答案使用了上下文的部分内容
0.0 - 答案几乎没有使用上下文

请只返回一个数字分数(0.0, 0.5, 或 1.0)。
"""

        try:
            response = self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=10
            )

            score_text = response.content.strip()
            score = float(score_text)

            return max(0.0, min(1.0, score))

        except Exception as e:
            print(f"上下文精确度评估失败: {e}")
            return 0.5

    def evaluate_context_recall(self, context: str, reference_answer: str) -> float:
        """
        评估上下文召回率

        判断上下文是否包含了参考答案所需的所有信息

        Args:
            context: 上下文
            reference_answer: 参考答案

        Returns:
            召回率分数 (0.0-1.0)
        """
        prompt = f"""请评估上下文是否包含了参考答案所需的所有信息。

上下文:
{context}

参考答案: {reference_answer}

评分标准:
1.0 - 上下文包含了参考答案所需的所有信息
0.5 - 上下文包含了参考答案所需的部分信息
0.0 - 上下文缺少参考答案所需的关键信息

请只返回一个数字分数(0.0, 0.5, 或 1.0)。
"""

        try:
            response = self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=10
            )

            score_text = response.content.strip()
            score = float(score_text)

            return max(0.0, min(1.0, score))

        except Exception as e:
            print(f"上下文召回率评估失败: {e}")
            return 0.5


class SimpleGenerationEvaluator:
    """
    简单生成评测器（不需要LLM）

    基于规则的评估方法
    """

    @staticmethod
    def evaluate_faithfulness_simple(context: str, answer: str) -> float:
        """
        简单忠实度评估

        基于关键词匹配
        """
        # 提取答案中的关键词
        answer_words = set(answer.lower().split())

        # 检查有多少答案词在上下文中
        context_lower = context.lower()
        matched = sum(1 for word in answer_words if word in context_lower)

        if len(answer_words) == 0:
            return 0.0

        return matched / len(answer_words)

    @staticmethod
    def evaluate_answer_relevancy_simple(question: str, answer: str) -> float:
        """
        简单相关性评估

        基于关键词重叠
        """
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())

        # 计算Jaccard相似度
        intersection = question_words & answer_words
        union = question_words | answer_words

        if len(union) == 0:
            return 0.0

        return len(intersection) / len(union)
