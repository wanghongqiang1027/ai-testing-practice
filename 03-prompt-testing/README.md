# 阶段 3：Prompt 测试框架

## 学习目标

- 理解 Prompt 测试的核心概念
- 设计结构化的测试用例格式
- 实现多维度断言框架
- 支持 Prompt 版本对比
- 构建回归测试自动化
- 生成可视化测试报告

## 项目结构

```
03-prompt-testing/
├── src/
│   ├── __init__.py
│   ├── test_case.py           # 测试用例模型
│   ├── assertor.py            # 断言框架
│   ├── comparator.py          # 版本对比器
│   ├── runner.py              # 测试执行器
│   └── reporter.py            # 报告生成器
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_assertor.py       # 断言测试
│   ├── test_comparator.py     # 对比测试
│   └── test_runner.py         # 执行器测试
├── test_cases/
│   ├── basic_qa.jsonl         # 基础问答测试集
│   ├── edge_cases.jsonl       # 边界测试集
│   └── security.jsonl         # 安全测试集
├── prompts/
│   ├── v1/
│   │   └── assistant.txt      # Prompt版本1
│   └── v2/
│       └── assistant.txt      # Prompt版本2
└── README.md
```

## 快速开始

### 1. 创建测试用例

```jsonl
{"id": "qa_001", "input": "什么是Python？", "expected_keywords": ["编程语言", "解释型"], "forbidden_keywords": ["Java"], "max_length": 200}
{"id": "qa_002", "input": "1+1等于几？", "exact_answer": "2", "must_include": ["2"]}
```

### 2. 运行测试

```bash
# 运行所有Prompt测试
pytest 03-prompt-testing/tests/ -v

# 运行回归测试
python 03-prompt-testing/src/runner.py --test-cases test_cases/basic_qa.jsonl

# 对比两个版本
python 03-prompt-testing/src/comparator.py --baseline prompts/v1 --new prompts/v2
```

### 3. 生成报告

```bash
# 生成HTML报告
python 03-prompt-testing/src/reporter.py --output report.html
```

## 核心知识点

### 1. 测试用例设计

Prompt测试用例包含以下维度：

```python
{
    "id": "unique_id",              # 唯一标识
    "input": "用户输入",             # 测试输入
    "category": "问答/总结/翻译",    # 测试类别
    
    # 断言维度
    "expected_keywords": [...],      # 应该包含的关键词
    "forbidden_keywords": [...],     # 不应包含的关键词
    "must_include": [...],           # 必须包含的短语
    "max_length": 200,              # 最大长度限制
    "min_length": 50,               # 最小长度限制
    "regex_pattern": "...",         # 正则表达式匹配
    "sentiment": "positive",        # 情感倾向
    "format": "json",               # 输出格式
    
    # 参考答案
    "reference_answer": "...",      # 参考答案
    "acceptable_answers": [...]     # 可接受的答案列表
}
```

### 2. 多维度断言

```python
class Assertor:
    def assert_keywords(self, response, keywords)
    def assert_forbidden(self, response, forbidden)
    def assert_length(self, response, min_len, max_len)
    def assert_format(self, response, format_type)
    def assert_semantic_similarity(self, response, reference)
```

### 3. 版本对比

对比指标：
- **Pass Rate**: 通过率变化
- **Response Quality**: 响应质量对比
- **Latency**: 延迟变化
- **Cost**: 成本变化
- **Regression Cases**: 回归用例数量

### 4. 测试报告

报告内容：
- 测试摘要（通过/失败/跳过）
- 失败用例详情
- 性能指标（延迟、成本）
- 版本对比（如果有）
- 可视化图表

## 断言类型

### 1. 关键词断言

```python
# 必须包含所有关键词
assert_contains_all(response, ["Python", "编程"])

# 必须包含至少一个
assert_contains_any(response, ["快速", "高效", "简单"])

# 不应包含任何一个
assert_not_contains(response, ["错误", "失败"])
```

### 2. 格式断言

```python
# JSON格式
assert_json_format(response)

# 列表格式（1. 2. 3. 或 - * ）
assert_list_format(response)

# 代码块格式
assert_code_block(response, language="python")
```

### 3. 长度断言

```python
# 字符长度
assert_length_between(response, min=50, max=200)

# Token长度
assert_token_count(response, max=100)
```

### 4. 语义相似度断言

```python
# 使用embedding计算相似度
assert_semantic_similarity(
    response,
    reference="这是一个参考答案",
    threshold=0.8
)
```

### 5. 情感断言

```python
# 情感应该是积极的
assert_sentiment(response, expected="positive")
```

## 练习任务

### 必做任务

- [ ] 定义测试用例数据模型
- [ ] 实现5种以上断言方法
- [ ] 创建测试执行器
- [ ] 编写30+个测试用例
- [ ] 实现基础测试报告
- [ ] 完成版本对比功能

### 进阶任务

- [ ] 添加语义相似度断言（使用embedding）
- [ ] 实现并行测试执行
- [ ] 支持测试用例标签和过滤
- [ ] 添加失败用例自动重试
- [ ] 生成HTML可视化报告
- [ ] 集成到CI/CD流水线

## 测试场景示例

### 场景1: 基础问答测试

```python
def test_basic_qa():
    """测试基础问答"""
    test_case = {
        "input": "什么是人工智能？",
        "expected_keywords": ["人工智能", "AI", "机器学习"],
        "forbidden_keywords": ["不知道", "无法回答"],
        "max_length": 300
    }
    
    response = run_prompt(test_case["input"])
    
    assertor.assert_keywords(response, test_case["expected_keywords"])
    assertor.assert_forbidden(response, test_case["forbidden_keywords"])
    assertor.assert_length(response, max=test_case["max_length"])
```

### 场景2: 格式化输出测试

```python
def test_json_output():
    """测试JSON格式输出"""
    test_case = {
        "input": "生成一个用户对象，包含姓名和年龄",
        "format": "json",
        "required_fields": ["name", "age"]
    }
    
    response = run_prompt(test_case["input"])
    
    assertor.assert_json_format(response)
    data = json.loads(response)
    assertor.assert_required_fields(data, test_case["required_fields"])
```

### 场景3: Prompt版本对比

```python
def test_version_comparison():
    """对比两个Prompt版本"""
    test_cases = load_test_cases("test_cases/basic_qa.jsonl")
    
    # 版本1
    results_v1 = run_all_tests(prompt_v1, test_cases)
    
    # 版本2
    results_v2 = run_all_tests(prompt_v2, test_cases)
    
    # 对比
    comparison = compare_results(results_v1, results_v2)
    
    print(f"V1 Pass Rate: {comparison['v1_pass_rate']}")
    print(f"V2 Pass Rate: {comparison['v2_pass_rate']}")
    print(f"Regression Cases: {len(comparison['regressions'])}")
```

## 常见问题

### Q: 如何判断Prompt是否变好了？

A: 多维度评估：
1. **通过率**: 新版本通过率是否提升
2. **回归检测**: 是否有原本通过的用例失败
3. **质量评分**: 使用LLM-as-Judge评分
4. **成本**: 成本是否增加
5. **延迟**: 响应速度是否下降

### Q: 测试用例应该包含多少个？

A: 建议：
- **冒烟测试**: 10-20个核心场景
- **回归测试**: 100-300个覆盖主要功能
- **全量测试**: 1000+个覆盖边界和异常

### Q: 如何处理不确定的输出？

A: 策略：
1. 使用关键词而非精确匹配
2. 使用语义相似度而非字符串匹配
3. 使用LLM-as-Judge进行评分
4. 设置多个可接受答案

### Q: 如何减少测试成本？

A: 方法：
1. 使用缓存（相同输入跳过）
2. 优先运行冒烟测试
3. 失败快速停止（--maxfail）
4. 使用便宜模型做初筛

## 测试报告示例

```markdown
# Prompt测试报告

## 摘要
- 总用例: 150
- 通过: 142 (94.7%)
- 失败: 8 (5.3%)
- 跳过: 0

## 失败用例
1. qa_045: 关键词缺失 ["机器学习"]
2. format_012: JSON格式错误
...

## 性能指标
- 平均延迟: 1.2s
- P95延迟: 3.5s
- 总成本: $2.34
- 平均每用例成本: $0.0156

## 版本对比
| 指标 | V1 | V2 | 变化 |
|---|---|---|---|
| 通过率 | 90% | 95% | +5% ✅ |
| 平均延迟 | 1.5s | 1.2s | -20% ✅ |
| 总成本 | $3.00 | $2.34 | -22% ✅ |
```

## 学习资源

- Prompt工程指南: https://www.promptingguide.ai/
- OpenAI Evals: https://github.com/openai/evals
- LangSmith Evaluation: https://docs.langchain.com/langsmith

## 预期成果

完成本阶段后，你将能够：

✅ 设计结构化的Prompt测试用例  
✅ 实现多维度断言框架  
✅ 执行批量Prompt回归测试  
✅ 对比不同Prompt版本的效果  
✅ 生成专业的测试报告  
✅ 将Prompt测试集成到CI/CD  

## 下一步

完成阶段3后，进入阶段4：RAG评测工具
