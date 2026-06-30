# 阶段 7：性能测试

## 学习目标

- 理解 AI 系统的性能指标
- 掌握响应时间测试方法
- 实现并发压力测试
- 监控资源消耗
- 分析性能瓶颈
- 提供优化建议

## 项目结构

```
07-performance-testing/
├── src/
│   ├── __init__.py
│   ├── latency_test.py        # 延迟测试
│   ├── throughput_test.py     # 吞吐量测试
│   ├── concurrency_test.py    # 并发测试
│   ├── resource_monitor.py    # 资源监控
│   ├── benchmark.py           # 基准测试
│   └── models.py              # 数据模型
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_latency.py        # 延迟测试
│   ├── test_throughput.py     # 吞吐量测试
│   └── test_concurrency.py    # 并发测试
├── benchmarks/
│   ├── llm_benchmark.py       # LLM性能基准
│   └── rag_benchmark.py       # RAG性能基准
└── README.md
```

## 快速开始

### 1. 运行性能测试

```bash
# 延迟测试
python src/latency_test.py --requests 100

# 并发测试
python src/concurrency_test.py --concurrent 10 --duration 60

# 完整基准测试
python src/benchmark.py --suite all
```

### 2. 查看性能报告

```bash
# 生成HTML报告
python src/reporter.py --results results.json --output performance_report.html
```

## 核心知识点

### 1. 性能指标

#### 延迟 (Latency)

**定义**: 单个请求从发送到接收响应的时间

**关键指标**:
- **P50 (中位数)**: 50%的请求延迟低于此值
- **P95**: 95%的请求延迟低于此值
- **P99**: 99%的请求延迟低于此值
- **平均延迟**: 所有请求的平均值
- **最大延迟**: 最慢的请求

**目标**:
- P50 < 1s
- P95 < 3s
- P99 < 5s

#### 吞吐量 (Throughput)

**定义**: 单位时间内处理的请求数

**单位**: QPS (Queries Per Second) 或 RPS (Requests Per Second)

**目标**:
- 简单查询: > 100 QPS
- 复杂查询: > 10 QPS
- LLM调用: > 1 QPS

#### 并发能力 (Concurrency)

**定义**: 同时处理多个请求的能力

**指标**:
- **最大并发数**: 系统能承受的最大并发请求
- **并发成功率**: 并发情况下的成功率
- **并发延迟**: 并发时的平均延迟

**目标**:
- 支持 >= 10 并发用户
- 并发成功率 > 95%

#### 资源消耗

**CPU使用率**:
- 空闲: < 20%
- 正常负载: 30-60%
- 高负载: 60-80%
- ⚠️ 过载: > 80%

**内存使用**:
- 空闲: < 500MB
- 正常: < 2GB
- ⚠️ 警告: > 4GB

**网络带宽**:
- 监控上传/下载速率
- 检测网络瓶颈

### 2. 性能测试类型

#### 负载测试 (Load Testing)

**目的**: 验证系统在预期负载下的表现

**方法**: 逐步增加负载，观察性能变化

#### 压力测试 (Stress Testing)

**目的**: 找到系统的极限

**方法**: 持续增加负载直到系统崩溃

#### 浸泡测试 (Soak Testing)

**目的**: 验证系统长期运行的稳定性

**方法**: 在正常负载下持续运行（如24小时）

#### 峰值测试 (Spike Testing)

**目的**: 测试系统应对突发流量的能力

**方法**: 短时间内产生大量请求

### 3. 性能瓶颈

#### 常见瓶颈

**网络延迟**:
- API调用时间
- 数据传输时间
- DNS解析时间

**LLM处理**:
- Token生成速度
- 上下文长度影响
- 模型复杂度

**数据库**:
- 查询效率
- 索引缺失
- 连接池不足

**代码逻辑**:
- 循环嵌套
- 不必要的计算
- 内存泄漏

#### 优化策略

**缓存**:
```python
# 缓存LLM响应
cache = {}

def get_llm_response(prompt):
    if prompt in cache:
        return cache[prompt]
    
    response = llm.chat(prompt)
    cache[prompt] = response
    return response
```

**批处理**:
```python
# 批量处理请求
def process_batch(requests):
    # 一次处理多个请求
    return [process(req) for req in requests]
```

**异步处理**:
```python
import asyncio

async def async_llm_call(prompt):
    response = await llm.async_chat(prompt)
    return response
```

**连接池**:
```python
# 使用连接池减少连接开销
from requests import Session

session = Session()
session.mount('http://', HTTPAdapter(pool_connections=10))
```

## 测试场景

### 场景1: LLM延迟测试

```python
def test_llm_latency():
    """测试LLM响应延迟"""
    latencies = []
    
    for _ in range(100):
        start = time.time()
        response = llm.chat("Hello")
        latency = time.time() - start
        latencies.append(latency)
    
    # 计算百分位数
    p50 = percentile(latencies, 50)
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)
    
    assert p50 < 1.0, f"P50延迟过高: {p50}s"
    assert p95 < 3.0, f"P95延迟过高: {p95}s"
    assert p99 < 5.0, f"P99延迟过高: {p99}s"
```

### 场景2: 并发压力测试

```python
def test_concurrent_requests():
    """测试并发请求"""
    import concurrent.futures
    
    def make_request():
        return llm.chat("Test")
    
    # 10个并发请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        results = [f.result() for f in futures]
    
    # 验证成功率
    success_rate = sum(1 for r in results if r.status == "success") / len(results)
    assert success_rate > 0.95, f"并发成功率过低: {success_rate}"
```

### 场景3: 吞吐量测试

```python
def test_throughput():
    """测试吞吐量"""
    duration = 60  # 测试60秒
    start_time = time.time()
    count = 0
    
    while time.time() - start_time < duration:
        llm.chat("Test")
        count += 1
    
    qps = count / duration
    assert qps > 1.0, f"吞吐量过低: {qps} QPS"
```

### 场景4: 资源监控

```python
def test_resource_usage():
    """测试资源使用"""
    import psutil
    
    # 执行测试
    for _ in range(100):
        llm.chat("Test")
    
    # 检查资源使用
    cpu_percent = psutil.cpu_percent()
    memory_mb = psutil.virtual_memory().used / 1024 / 1024
    
    assert cpu_percent < 80, f"CPU使用率过高: {cpu_percent}%"
    assert memory_mb < 4096, f"内存使用过高: {memory_mb}MB"
```

## 性能基准

### LLM性能基准

| 指标 | gpt-3.5-turbo | gpt-4 | claude-3-sonnet |
|---|---|---|---|
| P50延迟 | 0.8s | 2.5s | 1.2s |
| P95延迟 | 2.0s | 5.0s | 3.0s |
| 吞吐量 | 10 QPS | 3 QPS | 8 QPS |
| 成本/1K tokens | $0.002 | $0.06 | $0.015 |

### RAG性能基准

| 阶段 | 延迟 | 占比 |
|---|---|---|
| 检索 | 0.1s | 10% |
| LLM生成 | 0.8s | 80% |
| 后处理 | 0.1s | 10% |
| **总计** | **1.0s** | **100%** |

## 练习任务

### 必做任务

- [ ] 实现延迟测试工具
- [ ] 实现并发测试工具
- [ ] 实现资源监控
- [ ] 编写性能测试用例
- [ ] 生成性能报告
- [ ] 进行性能优化

### 进阶任务

- [ ] 集成Locust压测工具
- [ ] 实现分布式压测
- [ ] 添加实时监控看板
- [ ] 实现性能回归检测
- [ ] 构建性能CI/CD
- [ ] 自动化性能优化建议

## 性能优化建议

### 1. LLM优化

**减少Token数**:
```python
# 优化前
prompt = "请详细说明Python的历史、特点、应用场景..."

# 优化后
prompt = "简述Python特点"
```

**使用流式输出**:
```python
# 流式输出可以更早开始显示结果
for chunk in llm.stream("Long prompt"):
    print(chunk, end='')
```

**模型选择**:
- 简单任务用便宜快速的模型
- 复杂任务才用高级模型

### 2. RAG优化

**优化检索**:
```python
# 减少检索数量
retrieved = retriever.retrieve(query, k=3)  # 而不是k=10

# 使用向量数据库索引
# FAISS, Pinecone, Weaviate等
```

**并行处理**:
```python
import asyncio

async def parallel_rag(queries):
    tasks = [rag_system.query(q) for q in queries]
    return await asyncio.gather(*tasks)
```

### 3. 缓存策略

**LRU缓存**:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_operation(input):
    return process(input)
```

**Redis缓存**:
```python
import redis

r = redis.Redis()

def get_with_cache(key):
    cached = r.get(key)
    if cached:
        return cached
    
    result = fetch_from_db(key)
    r.setex(key, 3600, result)  # 缓存1小时
    return result
```

## 性能测试报告示例

```markdown
# 性能测试报告

## 测试环境
- CPU: Intel i7-10700K
- 内存: 16GB
- 网络: 100Mbps
- Python: 3.11

## 测试摘要

### 延迟测试
- 请求数: 1000
- P50: 0.85s ✅
- P95: 2.1s ✅
- P99: 4.8s ✅
- 平均: 1.2s
- 最大: 6.5s

### 并发测试
- 并发数: 10
- 总请求: 1000
- 成功率: 98% ✅
- 平均延迟: 1.5s

### 吞吐量
- 测试时长: 60s
- 总请求: 85
- QPS: 1.42 ✅

### 资源使用
- CPU: 45% ✅
- 内存: 1.8GB ✅
- 网络: 10Mbps

## 性能瓶颈
1. LLM调用占用80%时间
2. 网络延迟约200ms
3. 无明显内存泄漏

## 优化建议
1. 启用响应缓存
2. 使用更快的模型
3. 优化Prompt长度
4. 增加连接池大小
```

## 常见问题

### Q: 如何确定性能目标？

A: 
1. 根据用户需求（如聊天应答< 2s）
2. 参考行业标准
3. 对标竞品
4. 逐步优化迭代

### Q: 性能测试应该测多久？

A: 
- **快速验证**: 1-5分钟
- **负载测试**: 15-30分钟
- **浸泡测试**: 1-24小时
- **压力测试**: 直到崩溃

### Q: 如何模拟真实用户行为？

A: 
1. 收集真实访问日志
2. 分析用户行为模式
3. 构建用户场景
4. 按比例模拟负载

### Q: 性能下降如何定位？

A: 
1. 分段计时找瓶颈
2. 使用性能分析工具（cProfile）
3. 检查资源使用
4. 查看日志错误

## 工具推荐

- **Locust**: Python压测工具
- **Apache JMeter**: 通用压测工具
- **wrk**: HTTP基准测试
- **psutil**: 系统资源监控
- **cProfile**: Python性能分析

## 预期成果

完成本阶段后，你将能够：

✅ 测试AI系统响应延迟  
✅ 进行并发压力测试  
✅ 监控资源消耗  
✅ 分析性能瓶颈  
✅ 提供优化建议  
✅ 生成性能报告  

## 项目完成

**恭喜！完成阶段7后，整个AI测试学习项目将100%完成！** 🎉
