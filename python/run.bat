@echo off
echo ========================================
echo   Ігрофікс ПК - Запуск сервера
echo ========================================
echo.
echo Встановлення залежностей...
py -3.13 -m pip install -r requirements.txt
echo.
echo Запуск сервера...
py -3.13 app.py
pause
