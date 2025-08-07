#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف إعداد البرنامج لإنشاء ملف تنفيذي
Setup script for creating executable

استخدم هذا الملف مع PyInstaller لإنشاء ملف .exe
"""

import os
import sys
from pathlib import Path

# معلومات البرنامج
APP_NAME = "VideoDownloader"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "برنامج تحميل الفيديوهات والملفات"
APP_AUTHOR = "Video Downloader Team"

def create_spec_file():
    """إنشاء ملف .spec لـ PyInstaller"""
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon='icon.ico'  # إذا كان لديك أيقونة
)
'''
    
    with open('VideoDownloader.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ تم إنشاء ملف VideoDownloader.spec")

def create_version_info():
    """إنشاء ملف معلومات الإصدار"""
    
    version_info = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'{APP_AUTHOR}'),
           StringStruct(u'FileDescription', u'{APP_DESCRIPTION}'),
           StringStruct(u'FileVersion', u'{APP_VERSION}'),
           StringStruct(u'InternalName', u'{APP_NAME}'),
           StringStruct(u'LegalCopyright', u'© 2024 {APP_AUTHOR}'),
           StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
           StringStruct(u'ProductName', u'{APP_DESCRIPTION}'),
           StringStruct(u'ProductVersion', u'{APP_VERSION}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("✓ تم إنشاء ملف version_info.txt")

def create_build_script():
    """إنشاء سكريبت البناء"""
    
    build_script = '''@echo off
chcp 65001 > nul
echo ========================================
echo     بناء ملف تنفيذي للبرنامج
echo     Building Executable File
echo ========================================
echo.

echo [1/3] التحقق من PyInstaller...
pip show pyinstaller > nul 2>&1
if errorlevel 1 (
    echo تثبيت PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo خطأ في تثبيت PyInstaller
        pause
        exit /b 1
    )
)
echo ✓ PyInstaller متوفر

echo.
echo [2/3] بناء الملف التنفيذي...
pyinstaller VideoDownloader.spec
if errorlevel 1 (
    echo خطأ في بناء الملف التنفيذي
    pause
    exit /b 1
)
echo ✓ تم بناء الملف التنفيذي

echo.
echo [3/3] نسخ الملفات الإضافية...
if exist dist\\VideoDownloader (
    copy README.md dist\\VideoDownloader\\
    copy requirements.txt dist\\VideoDownloader\\
    echo ✓ تم نسخ الملفات الإضافية
)

echo.
echo ========================================
echo ✓ تم بناء البرنامج بنجاح!
echo.
echo يمكنك العثور على الملف التنفيذي في:
echo   dist\\VideoDownloader\\VideoDownloader.exe
echo ========================================
echo.
pause
'''
    
    with open('build.bat', 'w', encoding='utf-8') as f:
        f.write(build_script)
    
    print("✓ تم إنشاء ملف build.bat")

def main():
    """الدالة الرئيسية"""
    print("إعداد ملفات البناء...")
    print("=" * 40)
    
    create_spec_file()
    create_version_info()
    create_build_script()
    
    print()
    print("=" * 40)
    print("✓ تم إنشاء جميع ملفات البناء!")
    print()
    print("لإنشاء ملف تنفيذي:")
    print("1. تأكد من تثبيت PyInstaller: pip install pyinstaller")
    print("2. شغل: build.bat")
    print("أو")
    print("3. شغل: pyinstaller VideoDownloader.spec")
    print("=" * 40)

if __name__ == "__main__":
    main()

