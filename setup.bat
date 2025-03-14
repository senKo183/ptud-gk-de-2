@echo off
echo ===== TASK MANAGER SETUP =====
echo.

REM Kiểm tra Python đã được cài đặt chưa
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python chua duoc cai dat. Vui long cai dat Python truoc khi chay setup.
    exit /b 1
)

echo [INFO] Dang tao moi truong ao Python...
python -m venv venv
if errorlevel 1 (
    echo [ERRO] Khong the tao moi truong ao. Vui long thu lai.
    exit /b 1
)

echo [INFO] Dang kich hoat moi truong ao...
call venv\Scripts\activate.bat

echo [INFO] Dang nang cap pip...
python -m pip install --upgrade pip

echo [INFO] Dang cai dat cac goi phu thuoc...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Khong the cai dat cac goi phu thuoc. Vui long thu lai.
    exit /b 1
)

echo [INFO] Dang tao cac thu muc can thiet...
mkdir task_manager\static\images 2>nul
mkdir task_manager\database 2>nul

echo.
echo ===== CAI DAT HOAN TAT =====
echo.
echo Huong dan su dung:
echo 1. Kich hoat moi truong ao:
echo    call venv\Scripts\activate.bat
echo.
echo 2. Chay ung dung:
echo    python task_manager\app.py
echo.
echo 3. Truy cap ung dung:
echo    http://localhost:5000
echo.
echo Tai khoan mac dinh:
echo - Admin: 
echo   + Username: admin
echo   + Password: admin123
echo.
pause 