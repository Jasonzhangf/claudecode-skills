@echo off
:: Sysmem v2.0 Windows 一键安装脚本
:: 智能检测系统环境，自动同步代码并安装

setlocal enabledelayedexpansion

:: 项目信息
set "PROJECT_NAME=Sysmem"
set "PROJECT_VERSION=2.0.0"
set "PROJECT_DESCRIPTION=项目架构链条化管理系统 - 支持智能交互式更新"

:: 颜色代码（Windows 10+）
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "CYAN=[96m"
set "NC=[0m"

:: 显示欢迎信息
call :show_welcome

:: 检查系统环境
call :check_system

:: 检查项目变更
call :check_changes

:: 执行安装
call :perform_installation

:: 运行智能检查
call :run_smart_check

:: 显示完成信息
call :show_completion

goto :eof

:: 函数定义
:show_welcome
cls
echo.
echo %CYAN%╔══════════════════════════════════════════════════════════════╗%NC%
echo %CYAN%║                                                              ║%NC%
echo %CYAN%║           🌟 %PROJECT_NAME% v%PROJECT_VERSION% 一键安装脚本          ║%NC%
echo %CYAN%║                                                              ║%NC%
echo %CYAN%║  %PROJECT_DESCRIPTION%  ║%NC%
echo %CYAN%║                                                              ║%NC%
echo %CYAN%║  支持智能交互式更新、模块化管理                        ║%NC%
echo %CYAN%║                                                              ║%NC%
echo %CYAN%╚══════════════════════════════════════════════════════════════╝%NC%
echo.
goto :eof

:check_system
echo %BLUE%ℹ️  检查系统环境%NC%

:: 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%❌ 未找到 Python，请先安装 Python 3.8+%NC%
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo %GREEN%✅ Python: %PYTHON_VERSION%%NC%

:: 检查Python版本
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%❌ Python版本过低，需要 3.8 或更高版本%NC%
    pause
    exit /b 1
)

echo %GREEN%✅ Python版本满足要求 (>= 3.8)%NC%

:: 检查pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    python -m pip --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo %RED%❌ 未找到 pip%NC%
        pause
        exit /b 1
    ) else (
        echo %GREEN%✅ pip: python -m pip%NC%
    )
) else (
    for /f "tokens=2" %%i in ('pip --version 2^>^&1') do set "PIP_VERSION=%%i"
    echo %GREEN%✅ pip: %PIP_VERSION%%NC%
)

:: 检查Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%⚠️  未找到 Git，某些功能可能受限%NC%
) else (
    for /f "tokens=3" %%i in ('git --version 2^>^&1') do set "GIT_VERSION=%%i"
    echo %GREEN%✅ Git: git version !GIT_VERSION!%NC%
)

goto :eof

:check_changes
echo %PURPLE%🔍 检查项目变更%NC%

git rev-parse --git-dir >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('git status --porcelain ^| find /c /v ""') do set "CHANGED_FILES=%%i"
    if !CHANGED_FILES! gtr 0 (
        echo %YELLOW%⚠️  检测到 !CHANGED_FILES! 个文件变更%NC%
        echo %BLUE%主要变更文件:%NC%
        git status --porcelain | head -5
    ) else (
        echo %GREEN%✅ 工作目录干净，无未提交变更%NC%
    )
) else (
    echo %BLUE%ℹ️  Git不可用，跳过变更检测%NC%
)

goto :eof

:perform_installation
echo %PURPLE%🚀 执行安装%NC%

:: 检查项目结构
if not exist "pyproject.toml" (
    if not exist "setup.py" (
        echo %RED%❌ 未找到项目配置文件 (pyproject.toml 或 setup.py)%NC%
        pause
        exit /b 1
    )
)

echo %GREEN%✅ 项目结构验证通过%NC%

:: 升级pip
echo %BLUE%ℹ️  升级pip...%NC%
python -m pip install --upgrade pip setuptools wheel

:: 安装项目
echo %BLUE%ℹ️  安装 %PROJECT_NAME%...%NC%

python -m pip install -e .
if %errorlevel% neq 0 (
    echo %RED%❌ 安装失败%NC%
    pause
    exit /b 1
)

echo %GREEN%✅ 安装成功%NC%

:: 验证安装
python -c "import sysmem; print(f'Sysmem安装成功')" >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%✅ 安装验证通过%NC%
) else (
    echo %YELLOW%⚠️  安装验证失败，但安装可能已成功%NC%
)

goto :eof

:run_smart_check
echo %PURPLE%🤖 运行智能安装检查%NC%

if exist "scripts\install_project.py" (
    echo %BLUE%ℹ️  运行智能安装脚本...%NC%
    python scripts\install_project.py
) else (
    echo %YELLOW%⚠️  智能安装脚本不存在，跳过%NC%
)

goto :eof

:show_completion
echo %PURPLE%🎉 安装完成%NC%

echo.
echo %GREEN%🎉 %PROJECT_NAME% v%PROJECT_VERSION% 安装成功！%NC%
echo.
echo %CYAN%📋 快速开始:%NC%
echo 1. 智能交互式更新:
echo    python scripts\collect_data.py --interactive
echo.
echo 2. 列出可用模块:
echo    python scripts\collect_data.py --list-modules
echo.
echo 3. 精确模块更新:
echo    python scripts\collect_data.py --module scripts
echo.
echo 4. 查看完整帮助:
echo    python scripts\collect_data.py --help
echo.
echo %CYAN%🔧 开发工具:%NC%
echo • 代码分析: python scripts\unused_code_analyzer.py
echo • 架构分析: python scripts\analyze_architecture.py
echo • 文档更新: python scripts\update_claude_md.py
echo.
echo %CYAN%📚 更多信息:%NC%
echo • 项目文档: type README.md
echo • 安装指南: type INSTALLATION.md
echo.
echo %GREEN%💡 享受智能交互式项目管理体验！%NC%
echo.

pause
goto :eof