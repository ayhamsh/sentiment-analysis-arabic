#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وحدة الدوال المساعدة
Utility Functions Module

تحتوي على دوال مساعدة للتحقق من الروابط وتنسيق البيانات
"""

import re
import os
import sys
from urllib.parse import urlparse
from pathlib import Path

def validate_url(url):
    """
    التحقق من صحة الرابط
    
    Args:
        url: الرابط المراد التحقق منه
        
    Returns:
        bool: True إذا كان الرابط صحيحاً، False إذا لم يكن
    """
    if not url or not isinstance(url, str):
        return False
        
    url = url.strip()
    if not url:
        return False
        
    # التحقق من وجود بروتوكول
    if not url.startswith(('http://', 'https://')):
        return False
        
    try:
        result = urlparse(url)
        # التحقق من وجود domain صحيح
        return all([result.scheme, result.netloc])
    except:
        return False

def is_video_url(url):
    """
    التحقق من كون الرابط رابط فيديو
    
    Args:
        url: الرابط المراد التحقق منه
        
    Returns:
        bool: True إذا كان رابط فيديو، False إذا لم يكن
    """
    if not validate_url(url):
        return False
        
    # قائمة المواقع المدعومة للفيديو
    video_domains = [
        'youtube.com', 'youtu.be', 'www.youtube.com',
        'facebook.com', 'www.facebook.com', 'fb.watch',
        'instagram.com', 'www.instagram.com',
        'twitter.com', 'www.twitter.com', 'x.com',
        'tiktok.com', 'www.tiktok.com',
        'vimeo.com', 'www.vimeo.com',
        'dailymotion.com', 'www.dailymotion.com',
        'twitch.tv', 'www.twitch.tv',
        'reddit.com', 'www.reddit.com',
        'streamable.com', 'www.streamable.com'
    ]
    
    try:
        domain = urlparse(url).netloc.lower()
        return any(video_domain in domain for video_domain in video_domains)
    except:
        return False

def format_size(size_bytes):
    """
    تنسيق حجم الملف لعرضه بشكل مقروء
    
    Args:
        size_bytes: حجم الملف بالبايت
        
    Returns:
        str: حجم الملف منسق (مثل "1.5 MB")
    """
    if not size_bytes or size_bytes <= 0:
        return "غير معروف"
        
    # وحدات القياس
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
        
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"

def format_time(seconds):
    """
    تنسيق الوقت لعرضه بشكل مقروء
    
    Args:
        seconds: الوقت بالثواني
        
    Returns:
        str: الوقت منسق (مثل "1:30:45")
    """
    if not seconds or seconds <= 0:
        return "غير معروف"
        
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

def format_speed(bytes_per_second):
    """
    تنسيق سرعة التحميل لعرضها بشكل مقروء
    
    Args:
        bytes_per_second: سرعة التحميل بالبايت/ثانية
        
    Returns:
        str: السرعة منسقة (مثل "1.2 MB/s")
    """
    if not bytes_per_second or bytes_per_second <= 0:
        return "غير معروف"
        
    return format_size(bytes_per_second) + "/s"

def sanitize_filename(filename):
    """
    تنظيف اسم الملف من الأحرف غير المسموحة
    
    Args:
        filename: اسم الملف الأصلي
        
    Returns:
        str: اسم الملف منظف
    """
    if not filename:
        return "untitled"
        
    # إزالة الأحرف غير المسموحة في أسماء الملفات
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
        
    # إزالة المسافات الزائدة والنقاط في البداية والنهاية
    filename = filename.strip(' .')
    
    # تحديد طول الاسم (Windows له حد أقصى 255 حرف)
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
        
    return filename or "untitled"

def get_file_extension_from_url(url):
    """
    استخراج امتداد الملف من الرابط
    
    Args:
        url: رابط الملف
        
    Returns:
        str: امتداد الملف (مثل ".mp4") أو سلسلة فارغة
    """
    try:
        parsed = urlparse(url)
        path = parsed.path
        if path:
            return os.path.splitext(path)[1].lower()
    except:
        pass
    return ""

def is_valid_save_path(path):
    """
    التحقق من صحة مسار الحفظ
    
    Args:
        path: مسار المجلد
        
    Returns:
        bool: True إذا كان المسار صحيحاً وقابلاً للكتابة، False إذا لم يكن
    """
    if not path:
        return False
        
    try:
        path_obj = Path(path)
        
        # التحقق من وجود المسار
        if not path_obj.exists():
            return False
            
        # التحقق من كونه مجلد
        if not path_obj.is_dir():
            return False
            
        # التحقق من إمكانية الكتابة
        return os.access(path, os.W_OK)
        
    except:
        return False

def create_directory_if_not_exists(path):
    """
    إنشاء مجلد إذا لم يكن موجوداً
    
    Args:
        path: مسار المجلد
        
    Returns:
        bool: True إذا تم إنشاء المجلد أو كان موجوداً، False في حالة الفشل
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except:
        return False

def get_available_filename(directory, filename):
    """
    الحصول على اسم ملف متاح (إضافة رقم إذا كان الاسم موجوداً)
    
    Args:
        directory: مسار المجلد
        filename: اسم الملف المطلوب
        
    Returns:
        str: اسم الملف المتاح
    """
    if not os.path.exists(os.path.join(directory, filename)):
        return filename
        
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while True:
        new_filename = f"{name} ({counter}){ext}"
        if not os.path.exists(os.path.join(directory, new_filename)):
            return new_filename
        counter += 1
        
        # تجنب الحلقة اللانهائية
        if counter > 1000:
            import time
            timestamp = int(time.time())
            return f"{name}_{timestamp}{ext}"

def estimate_download_time(total_size, downloaded_size, speed):
    """
    تقدير الوقت المتبقي للتحميل
    
    Args:
        total_size: الحجم الإجمالي بالبايت
        downloaded_size: الحجم المحمل بالبايت
        speed: سرعة التحميل بالبايت/ثانية
        
    Returns:
        int: الوقت المتبقي بالثواني، أو None إذا لم يمكن التقدير
    """
    if not all([total_size, speed]) or speed <= 0:
        return None
        
    remaining_size = total_size - downloaded_size
    if remaining_size <= 0:
        return 0
        
    return int(remaining_size / speed)

def get_system_info():
    """
    الحصول على معلومات النظام
    
    Returns:
        dict: معلومات النظام
    """
    import platform
    
    return {
        'system': platform.system(),
        'version': platform.version(),
        'architecture': platform.architecture()[0],
        'python_version': platform.python_version(),
        'machine': platform.machine()
    }

def check_disk_space(path, required_size):
    """
    التحقق من توفر مساحة كافية على القرص
    
    Args:
        path: مسار المجلد
        required_size: المساحة المطلوبة بالبايت
        
    Returns:
        bool: True إذا كانت المساحة كافية، False إذا لم تكن
    """
    try:
        if sys.platform == 'win32':
            import shutil
            free_space = shutil.disk_usage(path).free
        else:
            statvfs = os.statvfs(path)
            free_space = statvfs.f_frsize * statvfs.f_bavail
            
        return free_space >= required_size
    except:
        return True  # افتراض وجود مساحة كافية في حالة عدم القدرة على التحقق

def log_error(error_message, error_type="ERROR"):
    """
    تسجيل الأخطاء في ملف log
    
    Args:
        error_message: رسالة الخطأ
        error_type: نوع الخطأ
    """
    try:
        from datetime import datetime
        
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "downloader.log"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {error_type}: {error_message}\n"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
    except:
        # في حالة فشل التسجيل، نطبع الخطأ فقط
        print(f"{error_type}: {error_message}")

def get_default_download_path():
    """
    الحصول على مسار التحميل الافتراضي
    
    Returns:
        str: مسار مجلد التحميل الافتراضي
    """
    try:
        # محاولة الحصول على مجلد Downloads
        downloads_path = Path.home() / "Downloads"
        if downloads_path.exists():
            return str(downloads_path)
            
        # إذا لم يوجد، استخدم مجلد المستخدم
        return str(Path.home())
        
    except:
        # في حالة الفشل، استخدم المجلد الحالي
        return os.getcwd()

