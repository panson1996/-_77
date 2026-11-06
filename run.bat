@echo off
setlocal
set "PYTHON=C:\Users\p\AppData\Local\Programs\Python\Python314\python.exe"
set "PYTHONW=C:\Users\p\AppData\Local\Programs\Python\Python314\pythonw.exe"
if not exist "%PYTHON%" (
    echo Python 3.14 was not found at "%PYTHON%".
    exit /b 1
)
if not exist "%PYTHONW%" (
    echo Pythonw 3.14 was not found at "%PYTHONW%".
    exit /b 1
)
cd /d "%~dp0"
if "%~1"=="" (
    start "" /D "%~dp0" "%PYTHONW%" main.py
) else (
    "%PYTHON%" main.py %*
)
endlocal
