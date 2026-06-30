"""
RAG 评测数据模型
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class Document(BaseModel):
    """文档模型"""
    id: str = Field(..., description="文档ID")
    content: str = Field(..., description="文档内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class RetrievedChunk(BaseModel):
    """检索到的文档块"""
    id: str = Field(..., description="文档块ID")
    content: str = Field(..., description="内容")
    score: float = Field(..., description="相似度分数")
    rank: int = Field(..., description="排名")


class QAPair(BaseModel):
    """问答对"""
    id: str = Field(..., description="问答对ID")
    question: str = Field(..., description="问题")
    answer: Optional[str] = Field(None, description="参考答案")
    golden_chunks: List[str] = Field(default_factory=list, description="黄金文档块ID列表")
    category: Optional[str] = Field(None, description="类别")


class RetrievalMetrics(BaseModel):
    """检索评测指标"""
    hit_rate: float = Field(..., ge=0.0, le=1.0, description="命中率")
    mrr: float = Field(..., ge=0.0, le=1.0, description="平均倒数排名")
    precision: float = Field(..., ge=0.0, le=1.0, description="精确率")
    recall: float = Field(..., ge=0.0, le=1.0, description="召回率")
    ndcg: Optional[float] = Field(None, ge=0.0, le=1.0, description="归一化折损累计增益")


class GenerationMetrics(BaseModel):
    """生成评测指标"""
    faithfulness: float = Field(..., ge=0.0, le=1.0, description="忠实度")
    answer_relevancy: float = Field(..., ge=0.0, le=1.0, description="答案相关性")
    context_precision: Optional[float] = Field(None, ge=0.0, le=1.0, description="上下文精确度")
    context_recall: Optional[float] = Field(None, ge=0.0, le=1.0, description="上下文召回率")


class RAGResult(BaseModel):
    """RAG查询结果"""
    question: str = Field(..., description="问题")
    retrieved_chunks: List[RetrievedChunk] = Field(..., description="检索到的文档块")
    generated_answer: str = Field(..., description="生成的答案")
    latency_ms: float = Field(..., description="总延迟(毫秒)")
    retrieval_latency_ms: float = Field(..., description="检索延迟(毫秒)")
    generation_latency_ms: float = Field(..., description="生成延迟(毫秒)")
    cost_usd: float = Field(..., description="成本(美元)")


class EvaluationResult(BaseModel):
    """评测结果"""
    qa_pair_id: str = Field(..., description="问答对ID")
    question: str = Field(..., description="问题")

    # RAG结果
    retrieved_chunks: List[RetrievedChunk] = Field(..., description="检索到的文档")
    generated_answer: str = Field(..., description="生成的答案")

    # 评测指标
    retrieval_metrics: RetrievalMetrics = Field(..., description="检索指标")
    generation_metrics: GenerationMetrics = Field(..., description="生成指标")

    # 性能指标
    latency_ms: float = Field(..., description="延迟")
    cost_usd: float = Field(..., description="成本")

    # 参考答案
    reference_answer: Optional[str] = Field(None, description="参考答案")

    timestamp: datetime = Field(default_factory=datetime.now, description="评测时间")


class EvaluationSummary(BaseModel):
    """评测摘要"""
    total_cases: int = Field(..., description="总测试数")

    # 检索指标汇总
    avg_hit_rate: float = Field(..., description="平均命中率")
    avg_mrr: float = Field(..., description="平均MRR")
    avg_precision: float = Field(..., description="平均精确率")
    avg_recall: float = Field(..., description="平均召回率")

    # 生成指标汇总
    avg_faithfulness: float = Field(..., description="平均忠实度")
    avg_answer_relevancy: float = Field(..., description="平均答案相关性")

    # 性能指标
    avg_latency_ms: float = Field(..., description="平均延迟")
    total_cost_usd: float = Field(..., description="总成本")

    # 失败案例
    failed_cases: List[str] = Field(default_factory=list, description="失败案例ID")

    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    duration_seconds: float = Field(..., description="执行时长")
