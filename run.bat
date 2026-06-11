@echo off
REM Bansos Netflix - Launcher untuk Windows
REM Fungsi: Setup virtualenv, install dependencies, dan jalankan program

setlocal enabledelayedexpansion

REM Dapatkan directory script
set SCRIPT_DIR=%~dp0
set VENV_PATH=%SCRIPT_DIR%myenv
set PYTHON_BIN=%VENV_PATH%\Scripts\python.exe
set PIP_BIN=%VENV_PATH%\Scripts\pip.exe

REM Warna untuk output (optional)
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set RESET=[0m

echo.
echo ===============================================
echo   Bansos Netflix - Windows Launcher
echo ===============================================
echo.

REM Cek Python terinstall
echo Memeriksa Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python tidak ditemukan!
    echo Silakan install Python dari https://www.python.org/
    echo Pastikan "Add Python to PATH" dicentang saat install.
    echo.
    pause
    exit /b 1
)

REM Cek versi Python
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK - %PYTHON_VERSION% terdeteksi

echo.
echo Menyiapkan virtualenv...

REM Buat virtualenv jika belum ada
if not exist "%VENV_PATH%" (
    echo Membuat virtualenv di: %VENV_PATH%
    python -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo ERROR: Gagal membuat virtualenv!
        echo Pastikan modul venv tersedia untuk Python Anda.
        echo.
        pause
        exit /b 1
    )
    echo OK - Virtualenv berhasil dibuat
) else (
    echo OK - Virtualenv sudah ada
)

echo.
echo Menyiapkan dependencies...

REM Install dependencies
"%PIP_BIN%" install -q requests urllib3 playwright
if errorlevel 1 (
    echo WARNING: Ada masalah saat install dependencies
    echo Mencoba lagi dengan verbose...
    "%PIP_BIN%" install requests urllib3 playwright
    if errorlevel 1 (
        echo ERROR: Gagal install dependencies!
        echo.
        pause
        exit /b 1
    )
)
echo OK - Dependencies berhasil disiapkan

echo.
echo Memulai Bansos Netflix...
echo ===============================================
echo.

REM Jalankan program dengan argument yang dipass
"%PYTHON_BIN%" "%SCRIPT_DIR%nf-token-generator.py" %*

REM Tunggu sebelum menutup window
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Program gagal dijalankan
    pause
    exit /b 1
)

endlocal
