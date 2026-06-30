"""
检索评测测试
测试检索评测器的各项指标计算
"""

import pytest
from retrieval_evaluator import RetrievalEvaluator, RetrievalBatchEvaluator
from models import RetrievedChunk


class TestRetrievalEvaluator:
    """检索评测器测试"""

    @pytest.mark.smoke
    def test_hit_rate_hit(self):
        """测试命中率 - 命中情况"""
        evaluator = RetrievalEvaluator()

        retrieved = ["doc1", "doc2", "doc3"]
        golden = ["doc2", "doc5"]

        hit_rate = evaluator.calculate_hit_rate(retrieved, golden)

        assert hit_rate == 1.0, "应该命中"

    def test_hit_rate_miss(self):
        """测试命中率 - 未命中情况"""
        evaluator = RetrievalEvaluator()

        retrieved = ["doc1", "doc2", "doc3"]
        golden = ["doc4", "doc5"]

        hit_rate = evaluator.calculate_hit_rate(retrieved, golden)

        assert hit_rate == 0.0, "应该未命中"

    @pytest.mark.smoke
    def test_mrr_first_position(self):
        """测试MRR - 第一位命中"""
        evaluator = RetrievalEvaluator()

        retrieved = ["doc2", "doc1", "doc3"]
        golden = ["doc2"]

        mrr = evaluator.calculate_mrr(retrieved, golden)

        assert mrr == 1.0, "第一位命中MRR应为1.0"

    def test_mrr_second_position(self):
        """测试MRR - 第二位命中"""
        evaluator = RetrievalEvaluator()

        retrieved = ["doc1", "doc2", "doc3"]
        golden = ["doc2"]

        mrr = evaluator.calculate_mrr(retrieved, golden)

        assert mrr == 0.5, "第二位命中MRR应为0.5"

    def test_mrr_no_hit(self):
        """测试MRR - 未命中"""
        evaluator = RetrievalEvaluator()

        retrieved = ["doc1", "doc2", "doc3"]
        golden = ["doc4"]

        mrr = evaluator.calculate_mrr(retrieved, golden)

        assert mrr == 0.0, "未命中MRR应为0.0"

    def test_precision(self):
        """测试精确率"""
        evaluator = RetrievalEvaluator()

        # 5个检索结果中有2个相关
        retrieved = ["doc1", "doc2", "doc3", "doc4", "doc5"]
        golden = ["doc2", "doc4"]

        precision = evaluator.calculate_precision(retrieved, golden)

        assert precision == 0.4, f"精确率应为0.4，实际: {precision}"

    def test_recall(self):
        """测试召回率"""
        evaluator = RetrievalEvaluator()

        # 3个相关文档中召回了2个
        retrieved = ["doc1", "doc2", "doc3"]
        golden = ["doc2", "doc4", "doc5"]

        recall = evaluator.calculate_recall(retrieved, golden)

        expected = 1 / 3
        assert abs(recall - expected) < 0.01, f"召回率应为{expected:.2f}，实际: {recall}"

    def test_ndcg(self):
        """测试NDCG"""
        evaluator = RetrievalEvaluator()

        # doc2在第2位是相关的
        retrieved = ["doc1", "doc2", "doc3"]
        golden = ["doc2"]

        ndcg = evaluator.calculate_ndcg(retrieved, golden)

        # DCG = 1/log2(3) = 0.63
        # IDCG = 1/log2(2) = 1.0
        # NDCG = 0.63
        assert ndcg > 0.6 and ndcg < 0.7, f"NDCG应约为0.63，实际: {ndcg}"

    def test_evaluate_complete(self):
        """测试完整评测流程"""
        evaluator = RetrievalEvaluator()

        # 构建检索结果
        retrieved_chunks = [
            RetrievedChunk(id="doc1", content="内容1", score=0.9, rank=1),
            RetrievedChunk(id="doc2", content="内容2", score=0.8, rank=2),
            RetrievedChunk(id="doc3", content="内容3", score=0.7, rank=3),
        ]
        golden = ["doc2", "doc4"]

        metrics = evaluator.evaluate(retrieved_chunks, golden, k=3)

        assert metrics.hit_rate == 1.0, "应该命中"
        assert metrics.mrr == 0.5, "MRR应为0.5"
        assert metrics.precision > 0, "精确率应大于0"
        assert metrics.recall > 0, "召回率应大于0"
        assert metrics.ndcg is not None, "NDCG应该被计算"


class TestRetrievalBatchEvaluator:
    """批量检索评测测试"""

    def test_batch_evaluation(self):
        """测试批量评测"""
        batch_evaluator = RetrievalBatchEvaluator()

        # 准备多个测试案例
        results = [
            # Case 1: 完美检索
            (
                [
                    RetrievedChunk(id="doc1", content="", score=0.9, rank=1),
                    RetrievedChunk(id="doc2", content="", score=0.8, rank=2),
                ],
                ["doc1"]
            ),
            # Case 2: 第二位命中
            (
                [
                    RetrievedChunk(id="doc3", content="", score=0.9, rank=1),
                    RetrievedChunk(id="doc1", content="", score=0.8, rank=2),
                ],
                ["doc1"]
            ),
        ]

        avg_metrics = batch_evaluator.evaluate_batch(results, k=2)

        assert avg_metrics["hit_rate"] == 1.0, "所有案例都应命中"
        assert avg_metrics["mrr"] == 0.75, "平均MRR应为0.75 (1.0+0.5)/2"
        assert "precision" in avg_metrics
        assert "recall" in avg_metrics


class TestEdgeCases:
    """边界情况测试"""

    def test_empty_retrieved(self):
        """测试空检索结果"""
        evaluator = RetrievalEvaluator()

        retrieved = []
        golden = ["doc1"]

        precision = evaluator.calculate_precision(retrieved, golden)
        assert precision == 0.0

    def test_empty_golden(self):
        """测试空黄金集"""
        evaluator = RetrievalEvaluator()

        retrieved = ["doc1", "doc2"]
        golden = []

        recall = evaluator.calculate_recall(retrieved, golden)
        assert recall == 0.0

    def test_all_relevant(self):
        """测试全部相关"""
        evaluator = RetrievalEvaluator()

        retrieved = ["doc1", "doc2", "doc3"]
        golden = ["doc1", "doc2", "doc3"]

        precision = evaluator.calculate_precision(retrieved, golden)
        recall = evaluator.calculate_recall(retrieved, golden)

        assert precision == 1.0, "精确率应为1.0"
        assert recall == 1.0, "召回率应为1.0"
