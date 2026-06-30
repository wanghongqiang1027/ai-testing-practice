# 阶段 6：Agent 测试

## 学习目标

- 理解 AI Agent 的工作原理
- 掌握 Agent 行为测试方法
- 实现工具调用验证
- 测试多轮对话能力
- 验证状态管理和记忆
- 构建 Agent 评测框架

## 项目结构

```
06-agent-testing/
├── src/
│   ├── __init__.py
│   ├── agent.py               # Agent基础封装
│   ├── tool_executor.py       # 工具执行器
│   ├── conversation.py        # 对话管理器
│   ├── state_manager.py       # 状态管理器
│   ├── agent_evaluator.py     # Agent评测器
│   └── models.py              # 数据模型
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_tool_calling.py   # 工具调用测试
│   ├── test_conversation.py   # 多轮对话测试
│   ├── test_state.py          # 状态管理测试
│   └── test_reasoning.py      # 推理能力测试
├── tools/
│   ├── calculator.py          # 计算器工具
│   ├── search.py              # 搜索工具
│   └── weather.py             # 天气查询工具
└── README.md
```

## 快速开始

### 1. 创建一个简单的Agent

```python
from agent import Agent
from tools import Calculator, Search

# 创建Agent
agent = Agent(
    name="助手",
    tools=[Calculator(), Search()],
    llm_client=llm_client
)

# 运行任务
result = agent.run("帮我计算 25 * 4 + 10")
print(result)
```

### 2. 运行Agent测试

```bash
# 运行所有Agent测试
pytest 06-agent-testing/tests/ -v

# 运行工具调用测试
pytest 06-agent-testing/tests/test_tool_calling.py -v

# 运行多轮对话测试
pytest 06-agent-testing/tests/test_conversation.py -v
```

## 核心知识点

### 1. Agent 架构

```text
用户输入
  ↓
Agent (Orchestrator)
  ├─ 理解任务
  ├─ 规划步骤
  ├─ 选择工具
  ├─ 执行工具
  ├─ 处理结果
  └─ 生成响应
  ↓
最终输出
```

**核心组件**:
- **LLM**: 大脑，负责推理和决策
- **Tools**: 工具集，扩展Agent能力
- **Memory**: 记忆，保存对话历史
- **Planner**: 规划器，拆解复杂任务
- **Executor**: 执行器，调用工具

### 2. Agent 类型

#### ReAct Agent (Reasoning + Acting)

```
思考 → 行动 → 观察 → 思考 → ...
```

**示例**:
```
用户: 北京今天天气怎么样？

思考: 我需要查询北京的天气
行动: 调用weather_tool("北京")
观察: 返回"晴天，25°C"
思考: 已获得天气信息，可以回答
回答: 北京今天天气晴朗，气温25度
```

#### Plan-and-Execute Agent

```
规划 → 执行步骤1 → 执行步骤2 → ... → 汇总
```

**示例**:
```
用户: 帮我订一张去上海的机票

规划:
1. 查询用户偏好（时间、舱位）
2. 搜索可用航班
3. 比较价格
4. 预订机票
5. 确认订单

执行: 按步骤依次执行
```

#### Tool-using Agent

```
分析问题 → 选择工具 → 调用工具 → 解析结果
```

### 3. 工具调用 (Tool/Function Calling)

**工具定义**:
```python
class Tool:
    name: str           # 工具名称
    description: str    # 工具描述
    parameters: dict    # 参数schema
    
    def execute(self, **kwargs):
        """执行工具"""
        pass
```

**工具示例**:
```python
class Calculator(Tool):
    name = "calculator"
    description = "执行数学计算"
    parameters = {
        "expression": {
            "type": "string",
            "description": "数学表达式，如 '2+2'"
        }
    }
    
    def execute(self, expression: str) -> float:
        return eval(expression)
```

### 4. 多轮对话

**对话上下文管理**:
```python
conversation = [
    {"role": "user", "content": "我叫张三"},
    {"role": "assistant", "content": "你好张三！"},
    {"role": "user", "content": "我叫什么？"},
    {"role": "assistant", "content": "你叫张三"}
]
```

**上下文窗口**:
- 滑动窗口：只保留最近N轮
- 摘要压缩：长期记忆压缩成摘要
- 关键信息提取：提取重要信息保留

### 5. 状态管理

**Agent状态**:
```python
class AgentState:
    current_task: str           # 当前任务
    conversation_history: list  # 对话历史
    tool_calls: list           # 工具调用记录
    intermediate_results: dict  # 中间结果
    completed_steps: list      # 已完成步骤
```

## 测试维度

### 1. 工具调用测试

**测试点**:
- ✅ 工具选择正确性
- ✅ 参数提取准确性
- ✅ 调用时机合理性
- ✅ 结果处理正确性
- ✅ 错误处理完善性

**示例**:
```python
def test_tool_selection():
    """测试工具选择"""
    agent = Agent(tools=[Calculator(), Search()])
    
    # 数学问题应该选择计算器
    result = agent.run("25 * 4 是多少？")
    assert "calculator" in result.tool_calls
    
    # 信息查询应该选择搜索
    result = agent.run("Python是什么？")
    assert "search" in result.tool_calls
```

### 2. 多轮对话测试

**测试点**:
- ✅ 上下文理解
- ✅ 信息记忆
- ✅ 指代消解
- ✅ 话题连贯性

**示例**:
```python
def test_conversation_context():
    """测试对话上下文"""
    agent = Agent()
    
    # 第1轮：介绍自己
    agent.chat("我叫张三")
    
    # 第2轮：询问名字（测试记忆）
    response = agent.chat("我叫什么名字？")
    assert "张三" in response
```

### 3. 推理能力测试

**测试点**:
- ✅ 逻辑推理
- ✅ 问题拆解
- ✅ 步骤规划
- ✅ 结果汇总

**示例**:
```python
def test_multi_step_reasoning():
    """测试多步推理"""
    agent = Agent(tools=[Calculator()])
    
    # 复杂计算需要多步
    result = agent.run("计算 (10 + 20) * 3 - 15")
    
    assert result.status == "success"
    assert result.final_answer == "75"
    assert len(result.steps) >= 2  # 至少2步
```

### 4. 状态管理测试

**测试点**:
- ✅ 状态保存
- ✅ 状态恢复
- ✅ 状态一致性
- ✅ 状态清理

### 5. 错误处理测试

**测试点**:
- ✅ 工具调用失败
- ✅ 参数错误
- ✅ 超时处理
- ✅ 回退策略

## 评测指标

### 1. 任务成功率 (Task Success Rate)

```
TSR = 成功完成的任务数 / 总任务数
```

**目标**: TSR > 90%

### 2. 工具调用准确率 (Tool Calling Accuracy)

```
TCA = 正确的工具调用次数 / 总工具调用次数
```

**目标**: TCA > 95%

### 3. 平均步骤数 (Average Steps)

```
AS = 总步骤数 / 任务数
```

**目标**: 越少越好（效率）

### 4. 响应时间 (Response Time)

```
RT = 完成任务的总时间
```

**目标**: RT < 10s (简单任务)

### 5. 对话连贯性 (Conversation Coherence)

使用LLM-as-Judge评分

**目标**: 评分 > 0.8

## 练习任务

### 必做任务

- [ ] 实现基础Agent框架
- [ ] 创建3个以上工具（计算器、搜索、天气）
- [ ] 实现工具调用机制
- [ ] 实现对话历史管理
- [ ] 编写工具调用测试
- [ ] 编写多轮对话测试

### 进阶任务

- [ ] 实现ReAct模式Agent
- [ ] 实现Plan-and-Execute模式
- [ ] 添加状态持久化
- [ ] 实现并行工具调用
- [ ] 添加Agent监控和日志
- [ ] 构建Agent评测基准

## 测试场景示例

### 场景1: 工具调用测试

```python
def test_calculator_tool():
    """测试计算器工具"""
    agent = Agent(tools=[Calculator()])
    
    test_cases = [
        ("2 + 2", "4"),
        ("10 * 5", "50"),
        ("100 / 4", "25"),
    ]
    
    for question, expected in test_cases:
        result = agent.run(f"计算 {question}")
        assert expected in result.final_answer
```

### 场景2: 多轮对话测试

```python
def test_multi_turn_conversation():
    """测试多轮对话"""
    agent = Agent()
    
    # 轮1: 设置上下文
    agent.chat("我今年25岁")
    
    # 轮2: 基于上下文的问题
    response = agent.chat("我几岁了？")
    assert "25" in response
    
    # 轮3: 计算问题
    response = agent.chat("10年后我多大？")
    assert "35" in response
```

### 场景3: 复杂任务测试

```python
def test_complex_task():
    """测试复杂任务"""
    agent = Agent(tools=[Calculator(), Search()])
    
    # 需要多个工具协作的任务
    result = agent.run("""
    帮我完成以下任务：
    1. 搜索Python的发布年份
    2. 计算距今多少年
    3. 总结一下
    """)
    
    assert result.status == "success"
    assert len(result.tool_calls) >= 2
    assert "search" in [call.tool for call in result.tool_calls]
    assert "calculator" in [call.tool for call in result.tool_calls]
```

## 常见问题

### Q: Agent和普通LLM有什么区别？

A: 
- **普通LLM**: 只能生成文本
- **Agent**: 可以调用工具、执行操作、多步推理

### Q: 如何选择Agent架构？

A: 
- **简单任务**: Tool-using Agent
- **需要推理**: ReAct Agent
- **复杂任务**: Plan-and-Execute Agent

### Q: 如何处理工具调用失败？

A: 策略：
1. 重试机制（最多3次）
2. 降级策略（用其他工具）
3. 向用户报告错误
4. 记录日志用于调试

### Q: 如何控制Agent成本？

A: 方法：
1. 限制最大步骤数
2. 使用更便宜的模型
3. 缓存工具调用结果
4. 优化Prompt减少token

## Agent评测基准

### 基准任务集

```jsonl
{"id": "calc_001", "task": "计算 123 + 456", "expected": "579", "tools": ["calculator"]}
{"id": "search_001", "task": "搜索Python的创建者", "expected": "Guido van Rossum", "tools": ["search"]}
{"id": "multi_001", "task": "查询北京天气并判断是否适合出行", "expected_tools": ["weather"], "min_steps": 2}
```

### 评测报告示例

```markdown
# Agent 评测报告

## 测试摘要
- 总任务: 50
- 成功: 45
- 失败: 5
- 成功率: 90%

## 工具调用
- 总调用: 120
- 正确: 115
- 错误: 5
- 准确率: 95.8%

## 性能指标
- 平均步骤: 2.4
- 平均时间: 5.2s
- 平均成本: $0.015

## 失败案例
1. calc_025: 复杂公式解析失败
2. search_018: 搜索超时
...
```

## 学习资源

- LangChain Agents: https://python.langchain.com/docs/modules/agents/
- AutoGPT: https://github.com/Significant-Gravitas/AutoGPT
- ReAct Paper: https://arxiv.org/abs/2210.03629

## 预期成果

完成本阶段后，你将能够：

✅ 理解Agent的工作原理  
✅ 实现基础Agent框架  
✅ 创建和集成工具  
✅ 测试工具调用能力  
✅ 验证多轮对话功能  
✅ 评估Agent性能  

## 下一步

完成阶段6后，进入阶段7：性能测试
