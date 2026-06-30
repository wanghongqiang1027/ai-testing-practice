"""
检索评测器
评估检索质量的核心指标
"""

from typing import List, Dict
import math
from models import RetrievedChunk, RetrievalMetrics


class RetrievalEvaluator:
    """
    检索评测器

    实现核心检索评测指标:
    - Hit Rate: 命中率
    - MRR: 平均倒数排名
    - Precision@K: 精确率
    - Recall@K: 召回率
    - NDCG@K: 归一化折损累计增益

    Example:
        evaluator = RetrievalEvaluator()
        metrics = evaluator.evaluate(
            retrieved_chunks=retrieved,
            golden_chunks=["chunk_001", "chunk_002"]
        )
    """

    def evaluate(
        self,
        retrieved_chunks: List[RetrievedChunk],
        golden_chunks: List[str],
        k: int = 5
    ) -> RetrievalMetrics:
        """
        评估检索质量

        Args:
            retrieved_chunks: 检索到的文档块列表
            golden_chunks: 黄金文档块ID列表（标准答案）
            k: 评估的Top-K

        Returns:
            检索评测指标
        """
        # 限制到Top-K
        retrieved_k = retrieved_chunks[:k]
        retrieved_ids = [chunk.id for chunk in retrieved_k]

        # 计算各项指标
        hit_rate = self.calculate_hit_rate(retrieved_ids, golden_chunks)
        mrr = self.calculate_mrr(retrieved_ids, golden_chunks)
        precision = self.calculate_precision(retrieved_ids, golden_chunks)
        recall = self.calculate_recall(retrieved_ids, golden_chunks)
        ndcg = self.calculate_ndcg(retrieved_ids, golden_chunks)

        return RetrievalMetrics(
            hit_rate=hit_rate,
            mrr=mrr,
            precision=precision,
            recall=recall,
            ndcg=ndcg
        )

    @staticmethod
    def calculate_hit_rate(retrieved_ids: List[str], golden_chunks: List[str]) -> float:
        """
        计算命中率

        定义: Top-K中是否至少包含一个相关文档

        Args:
            retrieved_ids: 检索到的文档ID列表
            golden_chunks: 相关文档ID列表

        Returns:
            命中率 (0.0 或 1.0)
        """
        for retrieved_id in retrieved_ids:
            if retrieved_id in golden_chunks:
                return 1.0
        return 0.0

    @staticmethod
    def calculate_mrr(retrieved_ids: List[str], golden_chunks: List[str]) -> float:
        """
        计算平均倒数排名 (Mean Reciprocal Rank)

        定义: 第一个相关文档位置的倒数

        Args:
            retrieved_ids: 检索到的文档ID列表
            golden_chunks: 相关文档ID列表

        Returns:
            MRR分数 (0.0-1.0)

        Example:
            retrieved = ["doc1", "doc2", "doc3"]
            golden = ["doc2"]
            MRR = 1/2 = 0.5
        """
        for i, retrieved_id in enumerate(retrieved_ids, start=1):
            if retrieved_id in golden_chunks:
                return 1.0 / i
        return 0.0

    @staticmethod
    def calculate_precision(retrieved_ids: List[str], golden_chunks: List[str]) -> float:
        """
        计算精确率 Precision@K

        定义: Top-K中相关文档的比例

        Args:
            retrieved_ids: 检索到的文档ID列表
            golden_chunks: 相关文档ID列表

        Returns:
            精确率 (0.0-1.0)

        Example:
            retrieved = ["doc1", "doc2", "doc3", "doc4", "doc5"]
            golden = ["doc2", "doc4"]
            Precision@5 = 2/5 = 0.4
        """
        if len(retrieved_ids) == 0:
            return 0.0

        relevant_count = sum(1 for rid in retrieved_ids if rid in golden_chunks)
        return relevant_count / len(retrieved_ids)

    @staticmethod
    def calculate_recall(retrieved_ids: List[str], golden_chunks: List[str]) -> float:
        """
        计算召回率 Recall@K

        定义: 相关文档中被检索到的比例

        Args:
            retrieved_ids: 检索到的文档ID列表
            golden_chunks: 相关文档ID列表

        Returns:
            召回率 (0.0-1.0)

        Example:
            retrieved = ["doc1", "doc2", "doc3"]
            golden = ["doc2", "doc4", "doc5"]
            Recall@3 = 1/3 = 0.33
        """
        if len(golden_chunks) == 0:
            return 0.0

        retrieved_relevant = sum(1 for rid in retrieved_ids if rid in golden_chunks)
        return retrieved_relevant / len(golden_chunks)

    @staticmethod
    def calculate_ndcg(retrieved_ids: List[str], golden_chunks: List[str]) -> float:
        """
        计算归一化折损累计增益 (Normalized Discounted Cumulative Gain)

        定义: 考虑排序位置的质量指标

        Args:
            retrieved_ids: 检索到的文档ID列表
            golden_chunks: 相关文档ID列表

        Returns:
            NDCG分数 (0.0-1.0)

        Example:
            retrieved = ["doc1", "doc2", "doc3"]  # doc2是相关的
            golden = ["doc2"]
            DCG = 0 + 1/log2(3) + 0 = 0.63
            IDCG = 1/log2(2) = 1.0
            NDCG = 0.63 / 1.0 = 0.63
        """
        if len(golden_chunks) == 0:
            return 0.0

        # 计算DCG (Discounted Cumulative Gain)
        dcg = 0.0
        for i, retrieved_id in enumerate(retrieved_ids, start=1):
            if retrieved_id in golden_chunks:
                # rel = 1 如果相关，0 如果不相关
                # DCG += rel / log2(i + 1)
                dcg += 1.0 / math.log2(i + 1)

        # 计算IDCG (Ideal DCG)
        # 理想情况：所有相关文档都在最前面
        idcg = 0.0
        for i in range(1, min(len(golden_chunks), len(retrieved_ids)) + 1):
            idcg += 1.0 / math.log2(i + 1)

        if idcg == 0.0:
            return 0.0

        return dcg / idcg


class RetrievalBatchEvaluator:
    """
    批量检索评测

    对多个问题的检索结果进行批量评估
    """

    def __init__(self):
        self.evaluator = RetrievalEvaluator()

    def evaluate_batch(
        self,
        results: List[tuple[List[RetrievedChunk], List[str]]],
        k: int = 5
    ) -> Dict[str, float]:
        """
        批量评估

        Args:
            results: [(retrieved_chunks, golden_chunks), ...]
            k: Top-K

        Returns:
            平均指标
        """
        metrics_list = []

        for retrieved_chunks, golden_chunks in results:
            metrics = self.evaluator.evaluate(retrieved_chunks, golden_chunks, k)
            metrics_list.append(metrics)

        # 计算平均值
        avg_metrics = {
            "hit_rate": sum(m.hit_rate for m in metrics_list) / len(metrics_list),
            "mrr": sum(m.mrr for m in metrics_list) / len(metrics_list),
            "precision": sum(m.precision for m in metrics_list) / len(metrics_list),
            "recall": sum(m.recall for m in metrics_list) / len(metrics_list),
            "ndcg": sum(m.ndcg or 0 for m in metrics_list) / len(metrics_list),
        }

        return avg_metrics
