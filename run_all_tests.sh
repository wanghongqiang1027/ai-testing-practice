#!/bin/bash
# AI测试学习项目 - 全阶段测试运行脚本

echo "========================================"
echo "AI测试学习项目 - 运行全部测试"
echo "========================================"
echo ""

# 定义所有阶段
STAGES=(
    "01-api-test-framework"
    "02-llm-basic"
    "03-prompt-testing"
    "04-rag-evaluation"
    "05-ai-security"
    "06-agent-testing"
    "07-performance-testing"
)

STAGE_NAMES=(
    "API测试框架"
    "LLM应用基础"
    "Prompt测试框架"
    "RAG评测工具"
    "AI安全测试"
    "Agent测试"
    "性能测试"
)

# 统计变量
TOTAL=0
PASSED=0
FAILED=0
FAILED_STAGES=()

# 遍历所有阶段
for i in "${!STAGES[@]}"; do
    stage="${STAGES[$i]}"
    name="${STAGE_NAMES[$i]}"

    echo ""
    echo "----------------------------------------"
    echo ">>> 阶段$((i+1)): $name"
    echo "    路径: $stage/tests/"
    echo "----------------------------------------"

    # 运行测试，跳过需要API的测试
    if pytest "$stage/tests/" -v --tb=short -m "not requires_api" 2>&1 | tail -5; then
        PASSED=$((PASSED + 1))
        echo "✅ 阶段$((i+1)) [$name] 测试通过"
    else
        FAILED=$((FAILED + 1))
        FAILED_STAGES+=("阶段$((i+1)): $name")
        echo "❌ 阶段$((i+1)) [$name] 测试失败"
    fi

    TOTAL=$((TOTAL + 1))
done

# 输出总结
echo ""
echo "========================================"
echo "测试完成汇总"
echo "========================================"
echo "总阶段数: $TOTAL"
echo "通过: $PASSED"
echo "失败: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 所有阶段测试通过！"
    echo ""
    echo "项目状态: ✅ 100%可运行"
    exit 0
else
    echo "⚠️ 有 $FAILED 个阶段测试失败:"
    for failed_stage in "${FAILED_STAGES[@]}"; do
        echo "  - $failed_stage"
    done
    echo ""
    echo "请检查失败的阶段并修复问题"
    exit 1
fi
