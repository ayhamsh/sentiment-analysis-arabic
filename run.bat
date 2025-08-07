@echo off
chcp 65001 > nul
title برنامج تحميل الفيديوهات والملفات

echo بدء تشغيل البرنامج...

REM التحقق من وجود البيئة الافتراضية
if exist venv\Scripts\activate.bat (
    echo تفعيل البيئة الافتراضية...
    call venv\Scripts\activate.bat
    python run.py
) else (
    echo تشغيل البرنامج مباشرة...
    python run.py
)

if errorlevel 1 (
    echo.
    echo خطأ في تشغيل البرنامج!
    echo يرجى التأكد من:
    echo   1. تثبيت Python بشكل صحيح
    echo   2. تشغيل install.bat أولاً
    echo   3. وجود جميع الملفات المطلوبة
    echo.
    pause
)

echo.
echo تم إغلاق البرنامج.
pause

