#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف تشغيل البرنامج
Run Script

ملف مبسط لتشغيل البرنامج مع معالجة الأخطاء
"""

import sys
import os
from pathlib import Path

def check_requirements():
    """التحقق من المتطلبات الأساسية"""
    print("التحقق من المتطلبات...")
    
    # التحقق من إصدار Python
    if sys.version_info < (3, 7):
        print("خطأ: يتطلب البرنامج Python 3.7 أو أحدث")
        return False
        
    # التحقق من وجود المكتبات المطلوبة
    required_modules = ['requests']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
            
    if missing_modules:
        print(f"خطأ: المكتبات التالية مفقودة: {', '.join(missing_modules)}")
        print("يرجى تثبيتها باستخدام: pip install -r requirements.txt")
        return False
        
    # التحقق من وجود yt-dlp
    try:
        import subprocess
        result = subprocess.run(['yt-dlp', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("تحذير: yt-dlp غير متوفر. سيتم محاولة تثبيته تلقائياً.")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("تحذير: yt-dlp غير متوفر. سيتم محاولة تثبيته تلقائياً.")
        
    print("✓ تم التحقق من المتطلبات")
    return True

def run_gui():
    """تشغيل الواجهة الرسومية"""
    try:
        # محاولة استيراد tkinter
        import tkinter as tk
        from tkinter import messagebox
        
        # استيراد التطبيق الرئيسي
        from main import DownloadApp
        
        print("بدء تشغيل الواجهة الرسومية...")
        
        # إنشاء النافذة الرئيسية
        root = tk.Tk()
        app = DownloadApp(root)
        
        # تشغيل التطبيق
        root.mainloop()
        
    except ImportError as e:
        if 'tkinter' in str(e).lower():
            print("خطأ: tkinter غير متوفر في هذا النظام")
            print("في أنظمة Linux، يمكن تثبيته باستخدام:")
            print("sudo apt-get install python3-tk")
            return False
        else:
            print(f"خطأ في الاستيراد: {e}")
            return False
    except Exception as e:
        print(f"خطأ في تشغيل الواجهة الرسومية: {e}")
        return False
        
    return True

def run_console():
    """تشغيل إصدار وحدة التحكم (للأنظمة التي لا تدعم GUI)"""
    print("تشغيل إصدار وحدة التحكم...")
    
    try:
        from downloader import VideoDownloader
        from utils import validate_url, get_default_download_path
        
        downloader = VideoDownloader()
        
        print("=" * 50)
        print("برنامج تحميل الفيديوهات والملفات - إصدار وحدة التحكم")
        print("=" * 50)
        
        while True:
            print("\nالخيارات المتاحة:")
            print("1. تحميل فيديو")
            print("2. عرض معلومات فيديو")
            print("3. الخروج")
            
            choice = input("\nاختر رقم الخيار: ").strip()
            
            if choice == "1":
                url = input("أدخل رابط الفيديو: ").strip()
                if not validate_url(url):
                    print("رابط غير صحيح!")
                    continue
                    
                print("جاري جلب معلومات الفيديو...")
                info = downloader.get_video_info(url)
                
                if not info:
                    print("فشل في جلب معلومات الفيديو!")
                    continue
                    
                print(f"العنوان: {info.get('title', 'غير معروف')}")
                print(f"القناة: {info.get('uploader', 'غير معروف')}")
                
                # عرض خيارات الجودة
                formats = info.get('formats', [])
                quality_options = downloader.get_quality_options(formats)
                
                if not quality_options:
                    print("لا توجد خيارات جودة متاحة!")
                    continue
                    
                print("\nخيارات الجودة المتاحة:")
                for i, option in enumerate(quality_options):
                    print(f"{i + 1}. {option['label']}")
                    
                try:
                    quality_choice = int(input("اختر رقم الجودة: ")) - 1
                    if quality_choice < 0 or quality_choice >= len(quality_options):
                        print("اختيار غير صحيح!")
                        continue
                except ValueError:
                    print("يرجى إدخال رقم صحيح!")
                    continue
                    
                save_path = input(f"مسار الحفظ (اتركه فارغاً للمسار الافتراضي): ").strip()
                if not save_path:
                    save_path = get_default_download_path()
                    
                print(f"بدء التحميل إلى: {save_path}")
                success = downloader.download_video(url, quality_choice, save_path)
                
                if success:
                    print("✓ تم التحميل بنجاح!")
                else:
                    print("✗ فشل التحميل!")
                    
            elif choice == "2":
                url = input("أدخل رابط الفيديو: ").strip()
                if not validate_url(url):
                    print("رابط غير صحيح!")
                    continue
                    
                print("جاري جلب معلومات الفيديو...")
                info = downloader.get_video_info(url)
                
                if info:
                    print(f"\nالعنوان: {info.get('title', 'غير معروف')}")
                    print(f"القناة: {info.get('uploader', 'غير معروف')}")
                    print(f"المدة: {info.get('duration', 'غير معروف')} ثانية")
                    print(f"الوصف: {info.get('description', 'غير متوفر')[:100]}...")
                else:
                    print("فشل في جلب معلومات الفيديو!")
                    
            elif choice == "3":
                print("شكراً لاستخدام البرنامج!")
                break
            else:
                print("اختيار غير صحيح!")
                
    except KeyboardInterrupt:
        print("\n\nتم إيقاف البرنامج بواسطة المستخدم.")
    except Exception as e:
        print(f"خطأ في تشغيل وحدة التحكم: {e}")
        return False
        
    return True

def main():
    """الدالة الرئيسية"""
    print("برنامج تحميل الفيديوهات والملفات")
    print("=" * 40)
    
    # التحقق من المتطلبات
    if not check_requirements():
        input("اضغط Enter للخروج...")
        return 1
        
    # محاولة تشغيل الواجهة الرسومية أولاً
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        # تشغيل وحدة التحكم مباشرة إذا تم تمرير المعامل
        success = run_console()
    else:
        # محاولة تشغيل الواجهة الرسومية
        success = run_gui()
        
        # إذا فشلت الواجهة الرسومية، جرب وحدة التحكم
        if not success:
            print("\nفشل في تشغيل الواجهة الرسومية. التبديل إلى وحدة التحكم...")
            success = run_console()
            
    if success:
        return 0
    else:
        input("اضغط Enter للخروج...")
        return 1

if __name__ == "__main__":
    sys.exit(main())

