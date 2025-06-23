@echo off
REM Windows 11 RAG测试运行脚本
REM 设置UTF-8编码以支持中文字符

echo 🚀 设置Windows控制台编码为UTF-8...
chcp 65001 > nul

echo.
echo ================================================================================
echo 🧪 Windows 11 RAG测试套件
echo ================================================================================
echo.

echo 📋 运行基础测试...
python simple_test.py
if %ERRORLEVEL% neq 0 (
    echo ❌ 基础测试失败
    pause
    exit /b 1
)

echo.
echo 📋 运行调试测试...
python debug_test.py
if %ERRORLEVEL% neq 0 (
    echo ❌ 调试测试失败
    pause
    exit /b 1
)

echo.
echo 📋 运行文件分析测试...
python test_file_analysis_windows.py
if %ERRORLEVEL% neq 0 (
    echo ❌ 文件分析测试失败
    pause
    exit /b 1
)

echo.
echo 📋 运行引用检测测试...
python test_reference_detection.py
if %ERRORLEVEL% neq 0 (
    echo ❌ 引用检测测试失败
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo 🎉 所有测试完成！
echo ================================================================================
echo.

pause
