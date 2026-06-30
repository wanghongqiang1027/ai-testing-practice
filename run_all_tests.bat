@echo off
REM AI测试学习项目 - 全阶段测试运行脚本 (Windows版本)

echo ========================================
echo AI测试学习项目 - 运行全部测试
echo ========================================
echo.

set TOTAL=0
set PASSED=0
set FAILED=0

REM 阶段1: API测试框架
echo ----------------------------------------
echo ^>^>^> 阶段1: API测试框架
echo     路径: 01-api-test-framework/tests/
echo ----------------------------------------
pytest 01-api-test-framework/tests/ -v --tb=short -m "not requires_api"
if %ERRORLEVEL% EQU 0 (
    echo [32m✅ 阶段1 [API测试框架] 测试通过[0m
    set /a PASSED+=1
) else (
    echo [31m❌ 阶段1 [API测试框架] 测试失败[0m
    set /a FAILED+=1
)
set /a TOTAL+=1
echo.

REM 阶段2: LLM应用基础
echo ----------------------------------------
echo ^>^>^> 阶段2: LLM应用基础
echo     路径: 02-llm-basic/tests/
echo ----------------------------------------
pytest 02-llm-basic/tests/ -v --tb=short -m "not requires_api"
if %ERRORLEVEL% EQU 0 (
    echo [32m✅ 阶段2 [LLM应用基础] 测试通过[0m
    set /a PASSED+=1
) else (
    echo [31m❌ 阶段2 [LLM应用基础] 测试失败[0m
    set /a FAILED+=1
)
set /a TOTAL+=1
echo.

REM 阶段3: Prompt测试框架
echo ----------------------------------------
echo ^>^>^> 阶段3: Prompt测试框架
echo     路径: 03-prompt-testing/tests/
echo ----------------------------------------
pytest 03-prompt-testing/tests/ -v --tb=short -m "not requires_api"
if %ERRORLEVEL% EQU 0 (
    echo [32m✅ 阶段3 [Prompt测试框架] 测试通过[0m
    set /a PASSED+=1
) else (
    echo [31m❌ 阶段3 [Prompt测试框架] 测试失败[0m
    set /a FAILED+=1
)
set /a TOTAL+=1
echo.

REM 阶段4: RAG评测工具
echo ----------------------------------------
echo ^>^>^> 阶段4: RAG评测工具
echo     路径: 04-rag-evaluation/tests/
echo ----------------------------------------
pytest 04-rag-evaluation/tests/ -v --tb=short -m "not requires_api"
if %ERRORLEVEL% EQU 0 (
    echo [32m✅ 阶段4 [RAG评测工具] 测试通过[0m
    set /a PASSED+=1
) else (
    echo [31m❌ 阶段4 [RAG评测工具] 测试失败[0m
    set /a FAILED+=1
)
set /a TOTAL+=1
echo.

REM 阶段5: AI安全测试
echo ----------------------------------------
echo ^>^>^> 阶段5: AI安全测试
echo     路径: 05-ai-security/tests/
echo ----------------------------------------
pytest 05-ai-security/tests/ -v --tb=short -m "not requires_api"
if %ERRORLEVEL% EQU 0 (
    echo [32m✅ 阶段5 [AI安全测试] 测试通过[0m
    set /a PASSED+=1
) else (
    echo [31m❌ 阶段5 [AI安全测试] 测试失败[0m
    set /a FAILED+=1
)
set /a TOTAL+=1
echo.

REM 阶段6: Agent测试
echo ----------------------------------------
echo ^>^>^> 阶段6: Agent测试
echo     路径: 06-agent-testing/tests/
echo ----------------------------------------
pytest 06-agent-testing/tests/ -v --tb=short -m "not requires_api"
if %ERRORLEVEL% EQU 0 (
    echo [32m✅ 阶段6 [Agent测试] 测试通过[0m
    set /a PASSED+=1
) else (
    echo [31m❌ 阶段6 [Agent测试] 测试失败[0m
    set /a FAILED+=1
)
set /a TOTAL+=1
echo.

REM 阶段7: 性能测试
echo ----------------------------------------
echo ^>^>^> 阶段7: 性能测试
echo     路径: 07-performance-testing/tests/
echo ----------------------------------------
pytest 07-performance-testing/tests/ -v --tb=short -m "not requires_api"
if %ERRORLEVEL% EQU 0 (
    echo [32m✅ 阶段7 [性能测试] 测试通过[0m
    set /a PASSED+=1
) else (
    echo [31m❌ 阶段7 [性能测试] 测试失败[0m
    set /a FAILED+=1
)
set /a TOTAL+=1
echo.

REM 输出总结
echo ========================================
echo 测试完成汇总
echo ========================================
echo 总阶段数: %TOTAL%
echo 通过: %PASSED%
echo 失败: %FAILED%
echo.

if %FAILED% EQU 0 (
    echo [32m🎉 所有阶段测试通过！[0m
    echo.
    echo 项目状态: ✅ 100%%可运行
    exit /b 0
) else (
    echo [31m⚠️ 有 %FAILED% 个阶段测试失败[0m
    echo.
    echo 请检查失败的阶段并修复问题
    exit /b 1
)
