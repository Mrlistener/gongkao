@echo off
chcp 65001 >nul
setlocal
set PYBUNDLED=C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe
if exist "%PYBUNDLED%" (
  "%PYBUNDLED%" "%~dp099_工具\serve.py"
) else (
  python "%~dp099_工具\serve.py"
)
pause