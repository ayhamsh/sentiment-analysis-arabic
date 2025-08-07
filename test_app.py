#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف اختبار التطبيق
Test Application

اختبار وظائف التطبيق الأساسية
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

# إضافة مسار المشروع إلى sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    validate_url, is_video_url, format_size, format_time, 
    sanitize_filename, is_valid_save_path, get_default_download_path
)
from downloader import VideoDownloader

class TestUtils(unittest.TestCase):
    """اختبار الدوال المساعدة"""
    
    def test_validate_url(self):
        """اختبار التحقق من صحة الروابط"""
        # روابط صحيحة
        self.assertTrue(validate_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertTrue(validate_url("http://example.com"))
        
        # روابط غير صحيحة
        self.assertFalse(validate_url(""))
        self.assertFalse(validate_url("not_a_url"))
        self.assertFalse(validate_url("ftp://example.com"))
        self.assertFalse(validate_url(None))
        
    def test_is_video_url(self):
        """اختبار التحقق من روابط الفيديو"""
        # روابط فيديو صحيحة
        self.assertTrue(is_video_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertTrue(is_video_url("https://youtu.be/dQw4w9WgXcQ"))
        self.assertTrue(is_video_url("https://www.facebook.com/video.php?v=123"))
        self.assertTrue(is_video_url("https://vimeo.com/123456"))
        
        # روابط غير فيديو
        self.assertFalse(is_video_url("https://www.google.com"))
        self.assertFalse(is_video_url("https://example.com"))
        
    def test_format_size(self):
        """اختبار تنسيق أحجام الملفات"""
        self.assertEqual(format_size(0), "غير معروف")
        self.assertEqual(format_size(1024), "1.0 KB")
        self.assertEqual(format_size(1024 * 1024), "1.0 MB")
        self.assertEqual(format_size(1024 * 1024 * 1024), "1.0 GB")
        
    def test_format_time(self):
        """اختبار تنسيق الوقت"""
        self.assertEqual(format_time(0), "غير معروف")
        self.assertEqual(format_time(60), "1:00")
        self.assertEqual(format_time(3661), "1:01:01")
        self.assertEqual(format_time(90), "1:30")
        
    def test_sanitize_filename(self):
        """اختبار تنظيف أسماء الملفات"""
        self.assertEqual(sanitize_filename(""), "untitled")
        self.assertEqual(sanitize_filename("test<>file"), "test__file")
        self.assertEqual(sanitize_filename("normal_file.mp4"), "normal_file.mp4")
        
    def test_is_valid_save_path(self):
        """اختبار صحة مسارات الحفظ"""
        # مسار صحيح (مجلد موجود)
        temp_dir = "/tmp"
        if os.path.exists(temp_dir):
            self.assertTrue(is_valid_save_path(temp_dir))
        
        # مسار غير صحيح
        self.assertFalse(is_valid_save_path(""))
        self.assertFalse(is_valid_save_path("/non/existent/path"))
        
    def test_get_default_download_path(self):
        """اختبار الحصول على مسار التحميل الافتراضي"""
        path = get_default_download_path()
        self.assertIsInstance(path, str)
        self.assertTrue(len(path) > 0)

class TestVideoDownloader(unittest.TestCase):
    """اختبار فئة VideoDownloader"""
    
    def setUp(self):
        """إعداد الاختبار"""
        self.progress_callback = Mock()
        self.status_callback = Mock()
        self.downloader = VideoDownloader(self.progress_callback, self.status_callback)
        
    def test_init(self):
        """اختبار تهيئة الكلاس"""
        self.assertIsNotNone(self.downloader)
        self.assertEqual(self.downloader.progress_callback, self.progress_callback)
        self.assertEqual(self.downloader.status_callback, self.status_callback)
        self.assertFalse(self.downloader.is_downloading)
        self.assertFalse(self.downloader.is_paused)
        self.assertFalse(self.downloader.is_cancelled)
        
    def test_get_quality_options(self):
        """اختبار استخراج خيارات الجودة"""
        # تحضير بيانات وهمية للتنسيقات
        mock_formats = [
            {
                'format_id': '1',
                'height': 720,
                'width': 1280,
                'ext': 'mp4',
                'filesize': 50000000,
                'vcodec': 'h264',
                'acodec': 'aac'
            },
            {
                'format_id': '2',
                'height': 1080,
                'width': 1920,
                'ext': 'mp4',
                'filesize': 100000000,
                'vcodec': 'h264',
                'acodec': 'aac'
            }
        ]
        
        options = self.downloader.get_quality_options(mock_formats)
        self.assertIsInstance(options, list)
        self.assertTrue(len(options) > 0)
        
        # التحقق من وجود المفاتيح المطلوبة
        for option in options:
            self.assertIn('format_id', option)
            self.assertIn('label', option)
            self.assertIn('height', option)
            self.assertIn('ext', option)

def run_basic_tests():
    """تشغيل الاختبارات الأساسية"""
    print("بدء الاختبارات الأساسية...")
    
    # اختبار استيراد الوحدات
    try:
        import utils
        import downloader
        print("✓ تم استيراد جميع الوحدات بنجاح")
    except ImportError as e:
        print(f"✗ فشل في استيراد الوحدات: {e}")
        return False
        
    # اختبار الدوال المساعدة
    try:
        assert validate_url("https://www.youtube.com/watch?v=test")
        assert not validate_url("invalid_url")
        assert is_video_url("https://www.youtube.com/watch?v=test")
        assert format_size(1024) == "1.0 KB"
        assert format_time(60) == "1:00"
        print("✓ جميع الدوال المساعدة تعمل بشكل صحيح")
    except AssertionError:
        print("✗ فشل في اختبار الدوال المساعدة")
        return False
        
    # اختبار إنشاء كائن VideoDownloader
    try:
        downloader_obj = VideoDownloader()
        assert downloader_obj is not None
        assert not downloader_obj.is_downloading
        print("✓ تم إنشاء كائن VideoDownloader بنجاح")
    except Exception as e:
        print(f"✗ فشل في إنشاء كائن VideoDownloader: {e}")
        return False
        
    print("✓ جميع الاختبارات الأساسية نجحت!")
    return True

def test_gui_components():
    """اختبار مكونات الواجهة الرسومية (بدون عرض)"""
    print("اختبار مكونات الواجهة الرسومية...")
    
    try:
        # محاولة استيراد tkinter
        import tkinter as tk
        from tkinter import ttk
        print("✓ تم استيراد tkinter بنجاح")
        
        # إنشاء نافذة وهمية للاختبار
        root = tk.Tk()
        root.withdraw()  # إخفاء النافذة
        
        # اختبار إنشاء المكونات الأساسية
        frame = ttk.Frame(root)
        entry = ttk.Entry(frame)
        button = ttk.Button(frame, text="اختبار")
        progress = ttk.Progressbar(frame)
        combo = ttk.Combobox(frame)
        
        print("✓ تم إنشاء جميع مكونات الواجهة بنجاح")
        
        # تنظيف
        root.destroy()
        return True
        
    except ImportError:
        print("✗ tkinter غير متوفر في هذه البيئة")
        return False
    except Exception as e:
        print(f"✗ فشل في اختبار مكونات الواجهة: {e}")
        return False

def main():
    """الدالة الرئيسية للاختبار"""
    print("=" * 50)
    print("اختبار برنامج تحميل الفيديوهات والملفات")
    print("=" * 50)
    
    success = True
    
    # تشغيل الاختبارات الأساسية
    if not run_basic_tests():
        success = False
        
    print()
    
    # اختبار مكونات الواجهة
    if not test_gui_components():
        success = False
        
    print()
    
    # تشغيل اختبارات unittest
    print("تشغيل اختبارات unittest...")
    try:
        # تشغيل الاختبارات بصمت
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(sys.modules[__name__])
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("✓ جميع اختبارات unittest نجحت!")
        else:
            print(f"✗ فشل {len(result.failures + result.errors)} اختبار")
            success = False
            
    except Exception as e:
        print(f"✗ فشل في تشغيل اختبارات unittest: {e}")
        success = False
        
    print()
    print("=" * 50)
    if success:
        print("✓ جميع الاختبارات نجحت! البرنامج جاهز للاستخدام.")
    else:
        print("✗ بعض الاختبارات فشلت. يرجى مراجعة الأخطاء.")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    main()

