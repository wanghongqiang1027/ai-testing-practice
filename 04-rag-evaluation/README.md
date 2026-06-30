# 阶段 4：RAG 评测工具

## 学习目标

- 理解 RAG 系统的工作原理
- 掌握 RAG 评测的核心指标
- 实现检索质量评测
- 实现生成质量评测
- 构建端到端 RAG 测试框架
- 使用 LLM-as-Judge 进行质量评分

## 项目结构

```
04-rag-evaluation/
├── src/
│   ├── __init__.py
│   ├── rag_system.py          # RAG系统封装
│   ├── retrieval_evaluator.py # 检索评测器
│   ├── generation_evaluator.py # 生成评测器
│   ├── end_to_end_evaluator.py # 端到端评测器
│   ├── llm_judge.py           # LLM评分器
│   └── models.py              # 数据模型
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_retrieval.py      # 检索测试
│   ├── test_generation.py     # 生成测试
│   └── test_end_to_end.py     # 端到端测试
├── datasets/
│   ├── qa_pairs.jsonl         # 问答对数据集
│   ├── documents.jsonl        # 文档库
│   └── golden_chunks.jsonl    # 黄金检索块
├── configs/
│   └── evaluation_config.yaml # 评测配置
└── README.md
```

## 快速开始

### 1. 准备测试数据

```jsonl
# datasets/qa_pairs.jsonl
{"question": "什么是Python？", "answer": "Python是一种高级编程语言", "context": ["doc_001", "doc_002"], "golden_chunks": ["chunk_001"]}
```

### 2. 运行评测

```bash
# 检索评测
python src/retrieval_evaluator.py --dataset datasets/qa_pairs.jsonl

# 生成评测
python src/generation_evaluator.py --dataset datasets/qa_pairs.jsonl

# 端到端评测
python src/end_to_end_evaluator.py --dataset datasets/qa_pairs.jsonl
```

### 3. 查看报告

```bash
# 生成HTML报告
python src/reporter.py --results results.json --output report.html
```

## 核心知识点

### 1. RAG 系统架构

```text
用户问题
  ↓
检索器 (Retriever)
  - Embedding相似度搜索
  - 返回Top-K相关文档
  ↓
相关文档 (Chunks)
  ↓
生成器 (Generator)
  - 将问题+文档组合成Prompt
  - LLM生成答案
  ↓
最终答案
```

### 2. RAG 评测维度

#### 检索评测 (Retrieval Metrics)

| 指标 | 说明 | 计算方式 |
|---|---|---|
| Hit Rate | 命中率 | Top-K中是否包含相关文档 |
| MRR | 平均倒数排名 | 第一个相关文档的位置 |
| Precision@K | 精确率 | Top-K中相关文档占比 |
| Recall@K | 召回率 | Top-K中召回的相关文档占比 |
| NDCG@K | 归一化折损累计增益 | 考虑排序的质量指标 |

#### 生成评测 (Generation Metrics)

| 指标 | 说明 | 评测方法 |
|---|---|---|
| Faithfulness | 忠实度 | 答案是否基于检索内容 |
| Answer Relevancy | 答案相关性 | 答案是否回答问题 |
| Context Relevancy | 上下文相关性 | 检索内容是否相关 |
| Context Precision | 上下文精确度 | 相关文档的排序质量 |
| Context Recall | 上下文召回率 | 是否召回所有相关信息 |

### 3. LLM-as-Judge

使用 LLM 作为评分器评估 RAG 输出质量：

```python
def evaluate_faithfulness(question, context, answer):
    """评估答案忠实度"""
    prompt = f"""
请评估以下答案是否基于给定的上下文。

问题: {question}

上下文:
{context}

答案: {answer}

评分标准:
1分 - 答案完全基于上下文
0分 - 答案包含上下文中没有的信息

只返回分数(0或1)。
"""
    score = llm.evaluate(prompt)
    return score
```

### 4. 测试数据集设计

**最小数据集**:
- 50-100 个问答对
- 覆盖主要知识领域
- 包含简单和复杂问题

**完整数据集**:
- 500-1000 个问答对
- 多样化的问题类型
- 包含边界和困难案例

**Golden Chunks**:
- 每个问题的标准答案文档
- 用于计算检索准确率

## 评测指标详解

### 1. Faithfulness (忠实度)

**定义**: 答案中的陈述是否都能在检索到的文档中找到支持

**计算方式**:
```python
# 将答案拆分成多个陈述
statements = extract_statements(answer)

# 检查每个陈述是否有支持
supported = 0
for statement in statements:
    if is_supported_by_context(statement, context):
        supported += 1

faithfulness = supported / len(statements)
```

**示例**:
- 问题: "Python是什么时候发布的？"
- 上下文: "Python由Guido van Rossum创建于1991年"
- 答案1: "Python是1991年发布的" → 忠实度: 1.0 ✅
- 答案2: "Python是1989年发布的" → 忠实度: 0.0 ❌

### 2. Answer Relevancy (答案相关性)

**定义**: 答案是否直接回答了问题

**计算方式**:
```python
# 使用embedding计算相似度
question_embedding = embed(question)
answer_embedding = embed(answer)

relevancy = cosine_similarity(question_embedding, answer_embedding)
```

### 3. Context Precision (上下文精确度)

**定义**: 检索到的文档中，相关文档在排序中的位置

**计算方式**:
```python
precision_scores = []
relevant_count = 0

for i, chunk in enumerate(retrieved_chunks):
    if chunk in golden_chunks:
        relevant_count += 1
        precision_at_i = relevant_count / (i + 1)
        precision_scores.append(precision_at_i)

context_precision = mean(precision_scores)
```

### 4. Context Recall (上下文召回率)

**定义**: 答案所需的所有相关信息是否都被检索到

**计算方式**:
```python
# 从答案中提取需要的信息点
required_info = extract_required_info(answer, ground_truth)

# 检查上下文中是否包含这些信息
found = 0
for info in required_info:
    if info_in_context(info, context):
        found += 1

context_recall = found / len(required_info)
```

## 练习任务

### 必做任务

- [ ] 实现RAG系统封装
- [ ] 实现检索评测器（Hit Rate, MRR, Precision, Recall）
- [ ] 实现生成评测器（Faithfulness, Relevancy）
- [ ] 创建50个测试问答对
- [ ] 实现LLM-as-Judge评分
- [ ] 生成评测报告

### 进阶任务

- [ ] 添加NDCG@K指标
- [ ] 实现Context Precision/Recall
- [ ] 支持多个检索策略对比
- [ ] 实现A/B测试框架
- [ ] 添加成本和延迟分析
- [ ] 生成可视化图表

## 测试场景示例

### 场景1: 检索质量测试

```python
def test_retrieval_quality():
    """测试检索质量"""
    retriever = Retriever()
    
    question = "什么是Python？"
    golden_chunks = ["chunk_001", "chunk_002"]
    
    # 检索Top-5
    retrieved = retriever.retrieve(question, k=5)
    
    # 计算Hit Rate
    hit = any(chunk.id in golden_chunks for chunk in retrieved)
    assert hit, "未命中相关文档"
    
    # 计算MRR
    mrr = calculate_mrr(retrieved, golden_chunks)
    assert mrr > 0.5, f"MRR过低: {mrr}"
```

### 场景2: 生成质量测试

```python
def test_generation_quality():
    """测试生成质量"""
    rag_system = RAGSystem()
    
    question = "什么是Python？"
    context = "Python是一种高级编程语言..."
    
    # 生成答案
    answer = rag_system.generate(question, context)
    
    # 评估忠实度
    faithfulness = evaluate_faithfulness(question, context, answer)
    assert faithfulness > 0.8, f"忠实度过低: {faithfulness}"
    
    # 评估相关性
    relevancy = evaluate_relevancy(question, answer)
    assert relevancy > 0.7, f"相关性过低: {relevancy}"
```

### 场景3: 端到端测试

```python
def test_end_to_end():
    """端到端RAG测试"""
    rag_system = RAGSystem()
    evaluator = RAGEvaluator()
    
    # 加载测试集
    test_cases = load_qa_pairs("datasets/qa_pairs.jsonl")
    
    results = []
    for case in test_cases:
        # 执行RAG
        answer = rag_system.query(case["question"])
        
        # 评测
        metrics = evaluator.evaluate(
            question=case["question"],
            answer=answer,
            ground_truth=case["answer"],
            retrieved_context=rag_system.last_context
        )
        
        results.append(metrics)
    
    # 汇总
    avg_metrics = aggregate_metrics(results)
    
    assert avg_metrics["faithfulness"] > 0.8
    assert avg_metrics["answer_relevancy"] > 0.7
```

## 常见问题

### Q: 如何快速构建测试数据集？

A: 方法：
1. 从现有FAQ提取问答对
2. 使用LLM生成测试问题
3. 人工标注Golden Chunks
4. 使用合成数据增强

### Q: Faithfulness和Answer Relevancy有什么区别？

A:
- **Faithfulness**: 答案是否基于上下文（防止幻觉）
- **Answer Relevancy**: 答案是否回答问题（防止文不对题）

### Q: 如何选择合适的K值？

A: 考虑因素：
- 业务需求（精确 vs 召回）
- 成本（K越大成本越高）
- 延迟（K越大处理越慢）
- 经验值：K=3-5 适合大多数场景

### Q: LLM-as-Judge 可靠吗？

A: 
- **优点**: 灵活、快速、能理解语义
- **缺点**: 有偏差、成本高、需要验证
- **建议**: 与人工评估结合，定期校准

## 评测报告示例

```markdown
# RAG 系统评测报告

## 测试摘要
- 测试问题数: 100
- 平均延迟: 2.3s
- 总成本: $5.67

## 检索指标
| 指标 | 分数 | 目标 | 状态 |
|---|---|---|---|
| Hit Rate@5 | 0.92 | >0.90 | ✅ |
| MRR | 0.75 | >0.70 | ✅ |
| Precision@5 | 0.68 | >0.60 | ✅ |
| Recall@5 | 0.85 | >0.80 | ✅ |

## 生成指标
| 指标 | 分数 | 目标 | 状态 |
|---|---|---|---|
| Faithfulness | 0.88 | >0.85 | ✅ |
| Answer Relevancy | 0.82 | >0.75 | ✅ |
| Context Precision | 0.71 | >0.65 | ✅ |
| Context Recall | 0.79 | >0.75 | ✅ |

## 失败案例
1. Q: "..." → 检索未命中相关文档
2. Q: "..." → 答案包含幻觉内容

## 建议
- 优化检索策略以提升MRR
- 调整Prompt减少幻觉
```

## 学习资源

- RAGAS框架: https://github.com/explodinggradients/ragas
- LlamaIndex评测: https://docs.llamaindex.ai/en/stable/examples/evaluation/
- LangChain评测: https://python.langchain.com/docs/guides/evaluation

## 预期成果

完成本阶段后，你将能够：

✅ 理解RAG系统的工作原理  
✅ 实现完整的检索评测  
✅ 实现生成质量评测  
✅ 使用LLM-as-Judge评分  
✅ 构建端到端RAG测试  
✅ 生成专业的评测报告  

## 下一步

完成阶段4后，进入阶段5：AI安全测试
