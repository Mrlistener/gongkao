@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

rem ============================================================
rem  Windows 双击启动：本地练习服务
rem  需要 Python 3（python.org 安装时勾选 Add python.exe to PATH）
rem  macOS 用户请双击 启动练习.command
rem ============================================================

set "SERVER=%~dp099_工具\serve.py"
set "PY="

rem 1) DSH 自带的 Python（装了才有）
set "DSHPY=%USERPROFILE%\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
if exist "%DSHPY%" set "PY=%DSHPY%"

rem 2) Windows 官方的 py 启动器
if not defined PY (
  where py >nul 2>nul
  if not errorlevel 1 set "PY=py -3"
)

rem 3) PATH 里的 python / python3
if not defined PY (
  where python >nul 2>nul
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  where python3 >nul 2>nul
  if not errorlevel 1 set "PY=python3"
)

if not defined PY (
  echo.
  echo   没有找到 Python 3。
  echo   请到 https://www.python.org/downloads/ 下载安装，
  echo   安装第一页记得勾选 "Add python.exe to PATH"。
  echo.
  pause
  exit /b 1
)

if not exist "%SERVER%" (
  echo.
  echo   找不到 %SERVER%
  echo   请确认仓库目录完整（99_工具\serve.py 要在）。
  echo.
  pause
  exit /b 1
)

%PY% "%SERVER%"

if errorlevel 1 (
  echo.
  echo   服务异常退出，上面是错误信息。
  echo.
  pause
)
endlocal
