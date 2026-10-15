@echo off
setlocal EnableExtensions EnableDelayedExpansion
title OLFU IT Olympics - Reset Quiz Bee Database & Sessions
color 0E

:: Force working directory to the folder containing this batch file
cd /d "%~dp0"

echo ========================================================================
echo    OLFU IT OLYMPICS LAN QUIZ BEE MANAGEMENT SYSTEM (ITPM 311)
echo    Tournament Database ^& Session Reset Utility
echo ========================================================================
echo.
echo  [WARNING] This action will completely reset the tournament database:
echo    * All contestant submissions, points, and scores will be CLEARED (0 PTS).
echo    * All anti-cheat and security logs will be PURGED.
echo    * Workstation terminals (PIN 1001-1060) will be RESET to default state.
echo    * Competition rounds and questions from sample_questions.csv will be RELOADED.
echo.

:: Check for -y / --yes / /y flag for non-interactive automation
if /i "%~1"=="-y" goto proceed
if /i "%~1"=="--yes" goto proceed
if /i "%~1"=="/y" goto proceed

set /p "CONFIRM=Are you sure you want to reset the database and sessions? (Y/N): "
if /i "!CONFIRM!" neq "Y" (
    echo.
    echo Reset cancelled. No changes were made.
    echo.
    pause
    exit /b 0
)

:proceed
echo.
echo ========================================================================
echo [1/3] Checking Node.js runtime environment...
where node >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Node.js is not installed or not found in system PATH.
    echo Please install Node.js LTS from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%v in ('node -v') do set NODE_VER=%%v
echo [OK] Node.js detected: %NODE_VER%

echo.
echo [2/3] Resetting database and seeding fresh tournament data...
call npm run seed
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] Database reset/seed failed.
    echo If the server is currently running, please stop it first and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Verifying database integrity...
if exist "quizbee.db" (
    color 0A
    echo [OK] quizbee.db is tournament-ready!
) else (
    color 0C
    echo [ERROR] quizbee.db was not generated.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo  TOURNAMENT RESET COMPLETE!
echo    - Database:   Freshly seeded from sample_questions.csv
echo    - Terminals:  60 stations (PIN 1001-1060) reset to 0 PTS
echo    - Sessions:   All active submissions and cheat logs cleared
echo ========================================================================
echo.
echo You can now start or restart the server using: start-windows.bat
echo.
pause
