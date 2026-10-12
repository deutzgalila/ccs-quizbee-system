@echo off
setlocal EnableExtensions EnableDelayedExpansion
title OLFU IT Olympics - Quiz Bee LAN Server
color 0A

:: Force working directory to the folder containing this batch file
cd /d "%~dp0"

echo ========================================================================
echo    OLFU IT OLYMPICS LAN QUIZ BEE MANAGEMENT SYSTEM (ITPM 311)
echo    Windows Automated Quick-Start Launcher
echo ========================================================================
echo.

:: 1. Check Node.js in PATH
where node >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Node.js is not installed or not found in system PATH.
    echo Please install Node.js LTS (64-bit) from: https://nodejs.org/
    echo.
    echo If Node.js was just installed, please close this window and reopen it.
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%v in ('node -v') do set NODE_VER=%%v
echo [OK] Node.js detected: %NODE_VER%

:: 2. Check and Install Dependencies
if not exist "node_modules" (
    echo.
    echo [1/3] Installing dependencies (npm install)...
    call npm install
    if %errorlevel% neq 0 (
        color 0C
        echo.
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
) else (
    REM Check if native module better-sqlite3 loads properly
    node -e "try { require('better-sqlite3'); } catch(e) { process.exit(1); }" >nul 2>nul
    if !errorlevel! neq 0 (
        echo [NOTICE] Native binary mismatch detected (e.g. Linux binaries transferred to Windows).
        echo Reinstalling dependencies for Windows x64...
        call npm install
        if !errorlevel! neq 0 (
            color 0C
            echo [ERROR] Failed to recompile/reinstall native modules.
            pause
            exit /b 1
        )
    )
    echo [OK] Dependencies verified.
)

:: 3. Seed Database if Missing
if not exist "quizbee.db" (
    echo.
    echo [2/3] Initializing SQLite database (npm run seed)...
    call npm run seed
    if %errorlevel% neq 0 (
        color 0C
        echo.
        echo [ERROR] Database seeding failed.
        pause
        exit /b 1
    )
) else (
    echo [OK] Database (quizbee.db) verified.
)

:: 4. Display Host IP Addresses
echo.
echo [3/3] Detected Local IPv4 Addresses on this Host:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set "IP=%%a"
    set "IP=!IP:~1!"
    echo     * http://!IP!:3000/
)
echo.

echo ========================================================================
echo Starting Quiz Bee Server... (Keep this window open during the event)
echo ========================================================================
echo.
call npm start
echo.
echo Server stopped.
pause
