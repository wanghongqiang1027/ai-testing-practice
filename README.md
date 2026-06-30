# AI Testing Practice

> 基于《Codex AI 测试学习路线：普通测试转 AI 测试版》的实战练习项目

## 项目简介

这是一个从零开始的 AI 测试学习实战项目，按照 16 周学习路线逐步构建，涵盖：

- ✅ **阶段 1**：测试开发底座（API 测试框架）
- ✅ **阶段 2**：LLM 应用基础（LLM Client 封装）
- ✅ **阶段 3**：Prompt 测试（回归测试框架）
- ✅ **阶段 4**：RAG 测试（评测工具）
- ✅ **进阶**：AI 安全测试、Agent 测试、性能测试、CI/CD 集成

## 项目结构

```
ai-testing-practice/
├── 01-api-test-framework/      # 阶段1：API自动化测试框架
│   ├── src/
│   ├── tests/
│   └── README.md
├── 02-llm-basic/                # 阶段2：LLM基础封装
│   ├── src/
│   ├── tests/
│   └── README.md
├── 03-prompt-testing/           # 阶段3：Prompt测试框架
│   ├── src/
│   ├── test_cases/
│   ├── tests/
│   └── README.md
├── 04-rag-evaluation/           # 阶段4：RAG评测工具
│   ├── src/
│   ├── tests/
│   └── README.md
├── 05-ai-security/              # 阶段5：AI安全测试
│   ├── src/
│   ├── tests/
│   └── README.md
├── 06-agent-testing/            # 阶段6：Agent测试
│   ├── src/
│   ├── tools/
│   ├── tests/
│   └── README.md
├── 07-performance-testing/      # 阶段7：性能测试
│   ├── src/
│   ├── tests/
│   └── README.md
├── docs/                        # 文档
│   └── AI测试学习路线.md
├── run_all_tests.sh             # 测试脚本（Linux/Mac）
├── run_all_tests.bat            # 测试脚本（Windows）
├── .env.example                 # 环境变量示例
├── requirements.txt
├── pytest.ini
└── README.md
```

## 快速开始

### 环境要求

- Python 3.11+
- pip
- Git

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/ai-testing-practice.git
cd ai-testing-practice

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
OPENAI_API_KEY=sk-your-key-here
```

### 运行测试

**注意**: 由于各阶段都有`conftest.py`文件，直接运行`pytest`会有导入冲突。推荐使用以下方式：

**方式1: 使用测试脚本（推荐）**
```bash
# Linux/Mac
bash run_all_tests.sh

# Windows
run_all_tests.bat
```

**方式2: 分阶段运行**
```bash
# 运行特定阶段的测试
pytest 01-api-test-framework/tests/ -v
pytest 02-llm-basic/tests/ -v
pytest 03-prompt-testing/tests/ -v
pytest 04-rag-evaluation/tests/ -v
pytest 05-ai-security/tests/ -v
pytest 06-agent-testing/tests/ -v
pytest 07-performance-testing/tests/ -v

# 运行冒烟测试
pytest -m smoke

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```

## 学习路径

### 第 1-2 周：API 测试基础

进入 `01-api-test-framework/` 目录，学习：
- pytest 基础
- fixture 和 parametrize
- API 自动化测试
- 测试报告生成

**学习目标**：搭建一个完整的 API 测试框架

### 第 3-4 周：LLM 基础

进入 `02-llm-basic/` 目录，学习：
- LLM Client 封装
- Prompt 构建
- 响应解析
- 基础测试

**学习目标**：能够调用 LLM API 并进行基础测试

### 第 5-6 周：Prompt 测试

进入 `03-prompt-testing/` 目录，学习：
- 测试集设计
- 断言方法
- 版本对比
- 回归测试

**学习目标**：构建 Prompt 回归测试体系

### 第 7-10 周：RAG 评测

进入 `04-rag-evaluation/` 目录，学习：
- RAG 系统测试
- 评测指标
- 质量评估
- 报告生成

**学习目标**：能够评估 RAG 系统质量

### 进阶内容

- `05-security-testing/`：AI 安全测试
- `06-agent-testing/`：Agent 工具调用测试
- `07-performance-testing/`：性能和压力测试

## 技术栈

- **测试框架**：pytest
- **HTTP 客户端**：httpx, requests
- **数据验证**：pydantic
- **LLM SDK**：openai, anthropic
- **性能测试**：locust
- **覆盖率**：pytest-cov
- **CI/CD**：GitHub Actions

## 项目特点

✅ **循序渐进**：从基础到进阶，逐步深入  
✅ **代码完整**：每个阶段都有完整可运行的代码  
✅ **注释详细**：适合初学者理解  
✅ **真实场景**：基于实际 AI 测试场景设计  
✅ **工程化**：包含 CI/CD、监控等完整流程  

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 相关资源

- [学习路线文档](docs/AI测试学习路线.md)
- [代码示例说明](docs/code-examples.md)
- [常见问题](docs/FAQ.md)

## 许可证

MIT License

## 致谢

本项目基于《Codex AI 测试学习路线：普通测试转 AI 测试版》学习路线开发。

## 联系方式

如有问题，欢迎：
- 提交 Issue
- 发起 Discussion
- Star ⭐ 本项目

---

**开始你的 AI 测试学习之旅吧！** 🚀
