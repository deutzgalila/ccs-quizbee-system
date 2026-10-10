@echo off
title Open Quiz Bee Port 3000 in Windows Firewall
echo ========================================================================
echo   Configuring Windows Firewall for Port 3000 (Inbound TCP)
echo ========================================================================
echo.
netsh advfirewall firewall add rule name="OLFU QuizBee Server" dir=in action=allow protocol=TCP localport=3000
if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Firewall rule "OLFU QuizBee Server" created successfully!
    echo Port 3000 is now accessible to other computers on the lab network.
) else (
    echo.
    echo [FAILED] Administrator privileges required.
    echo Please right-click this file and select "Run as administrator".
)
echo.
pause
