@echo off
chcp 65001 > nul
echo ========================================
echo     برنامج تحميل الفيديوهات والملفات
echo        Video Downloader Installer
echo ========================================
echo.

echo [1/4] التحقق من Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo خطأ: Python غير مثبت على النظام
    echo يرجى تحميل وتثبيت Python من: https://python.org
    pause
    exit /b 1
)
echo ✓ Python متوفر

echo.
echo [2/4] إنشاء البيئة الافتراضية...
if exist venv (
    echo البيئة الافتراضية موجودة مسبقاً
) else (
    python -m venv venv
    if errorlevel 1 (
        echo خطأ في إنشاء البيئة الافتراضية
        pause
        exit /b 1
    )
    echo ✓ تم إنشاء البيئة الافتراضية
)

echo.
echo [3/4] تفعيل البيئة الافتراضية وتثبيت المتطلبات...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo خطأ في تفعيل البيئة الافتراضية
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo خطأ في تثبيت المتطلبات
    pause
    exit /b 1
)
echo ✓ تم تثبيت جميع المتطلبات

echo.
echo [4/4] اختبار التثبيت...
python test_app.py
if errorlevel 1 (
    echo تحذير: بعض الاختبارات فشلت، لكن يمكن تشغيل البرنامج
)

echo.
echo ========================================
echo ✓ تم التثبيت بنجاح!
echo.
echo لتشغيل البرنامج:
echo   1. انقر نقراً مزدوجاً على run.bat
echo   أو
echo   2. افتح موجه الأوامر واكتب: python run.py
echo ========================================
echo.
pause

