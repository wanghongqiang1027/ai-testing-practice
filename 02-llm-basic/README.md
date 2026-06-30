# 阶段 2：LLM 应用基础

## 学习目标

- 理解 LLM API 的基本概念
- 封装统一的 LLM 客户端
- 掌握 Prompt 模板管理
- 学会记录和分析 LLM 调用指标
- 编写 LLM 基础测试

## 项目结构

```
02-llm-basic/
├── src/
│   ├── __init__.py
│   ├── llm_client.py          # LLM客户端封装
│   ├── prompt_template.py     # Prompt模板管理
│   ├── response_parser.py     # 响应解析器
│   └── models.py              # 数据模型
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # pytest配置
│   ├── test_llm_basic.py      # 基础测试
│   ├── test_structured_output.py  # 结构化输出测试
│   └── test_error_handling.py # 错误处理测试
├── prompts/
│   └── system_prompts.yaml    # 系统提示词配置
└── README.md
```

## 快速开始

### 1. 配置环境变量

```bash
# 在项目根目录的 .env 文件中添加
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 2. 安装依赖

```bash
pip install openai anthropic
```

### 3. 运行测试

```bash
# 运行所有LLM测试
pytest 02-llm-basic/tests/ -v

# 运行冒烟测试
pytest 02-llm-basic/tests/ -m smoke -v

# 跳过需要API Key的测试
pytest 02-llm-basic/tests/ -m "not requires_api" -v
```

## 核心知识点

### 1. LLM Client 封装

**目标**: 封装不同LLM提供商的API，提供统一接口

```python
class LLMClient:
    def chat(
        self,
        messages: List[Message],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """统一的聊天接口"""
        pass
```

**关键功能**:
- 支持多个提供商 (OpenAI, Anthropic)
- 记录 token 消耗和延迟
- 统一的响应格式
- 错误处理和重试

### 2. Prompt 模板

**目标**: 管理和复用 Prompt 模板

```python
# prompts/system_prompts.yaml
customer_service:
  role: "你是一个专业的客服助手"
  guidelines:
    - "始终保持礼貌和耐心"
    - "如果不确定答案，诚实说明"
    - "引用相关政策时需标注来源"
```

### 3. 响应解析

**目标**: 解析和验证 LLM 响应

- JSON 格式解析
- 结构化数据提取
- 错误恢复

### 4. 指标记录

**重要指标**:
- `prompt_tokens`: 输入 token 数
- `completion_tokens`: 输出 token 数
- `total_tokens`: 总 token 数
- `latency_ms`: 响应延迟（毫秒）
- `cost_usd`: 调用成本（美元）

## 练习任务

### 必做任务

- [ ] 实现 OpenAI 客户端封装
- [ ] 实现 Anthropic 客户端封装
- [ ] 创建 Prompt 模板管理器
- [ ] 编写基础聊天测试
- [ ] 实现 JSON 格式输出测试
- [ ] 添加 token 使用统计

### 进阶任务

- [ ] 添加请求重试机制
- [ ] 实现请求缓存
- [ ] 添加流式输出支持
- [ ] 实现成本追踪
- [ ] 添加多模型对比测试

## 测试场景

### 1. 基础聊天测试

```python
def test_simple_chat(llm_client):
    """测试简单对话"""
    response = llm_client.chat([
        {"role": "user", "content": "什么是Python?"}
    ])
    
    assert response.status == "success"
    assert len(response.content) > 0
    assert response.tokens_used > 0
```

### 2. 结构化输出测试

```python
def test_json_output(llm_client):
    """测试JSON格式输出"""
    response = llm_client.chat(
        messages=[
            {"role": "user", "content": "生成一个用户对象，包含姓名和年龄"}
        ],
        response_format={"type": "json_object"}
    )
    
    data = json.loads(response.content)
    assert "name" in data
    assert "age" in data
```

### 3. 错误处理测试

```python
def test_api_error_handling(llm_client):
    """测试API错误处理"""
    # 使用无效的API Key
    client = LLMClient(api_key="invalid_key")
    
    with pytest.raises(AuthenticationError):
        client.chat([{"role": "user", "content": "test"}])
```

## 常见问题

### Q: 如何选择模型？

A: 根据场景选择：
- **简单任务**: GPT-3.5-turbo (快速、便宜)
- **复杂推理**: GPT-4 (准确、贵)
- **长上下文**: Claude 3 (100K+ tokens)

### Q: 如何控制成本？

A: 
1. 使用 `max_tokens` 限制输出长度
2. 简单任务用便宜模型
3. 实现结果缓存
4. 监控每日消耗

### Q: 如何提高响应速度？

A:
1. 减少输入 tokens (压缩 prompt)
2. 限制输出长度
3. 使用更快的模型
4. 实现缓存机制

## 学习资源

- OpenAI API文档: https://platform.openai.com/docs/api-reference
- Anthropic API文档: https://docs.anthropic.com/
- Prompt工程指南: https://www.promptingguide.ai/

## 预期成果

完成本阶段后，你将能够：

✅ 封装统一的 LLM 客户端  
✅ 管理和使用 Prompt 模板  
✅ 解析和验证 LLM 响应  
✅ 记录和分析调用指标  
✅ 编写完整的 LLM 测试  
✅ 处理常见错误场景  

## 下一步

完成阶段2后，进入阶段3：Prompt 测试框架
