@echo off
chcp 65001 >nul 2>&1
title HFSS MCP Server

echo ============================================
echo   HFSS MCP Server - 一键启动
echo ============================================
echo.

:: 切换到脚本所在目录
cd /d "%~dp0"

:: 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 未找到虚拟环境，请先执行：
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -e .
    pause
    exit /b 1
)

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 默认参数
set TRANSPORT=http
set HOST=0.0.0.0
set PORT=8765

:: 解析命令行参数
if not "%1"=="" set TRANSPORT=%1
if not "%2"=="" set HOST=%2
if not "%3"=="" set PORT=%3

echo [启动] 传输模式: %TRANSPORT%
echo [启动] 监听地址: %HOST%:%PORT%
echo [启动] MCP 端点: http://%%COMPUTERNAME%%:%PORT%/mcp
echo.
echo 按 Ctrl+C 停止服务器
echo ============================================
echo.

python -m src.server --transport %TRANSPORT% --host %HOST% --port %PORT%

pause
