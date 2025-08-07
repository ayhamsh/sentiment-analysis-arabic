#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
برنامج تحميل الفيديوهات والملفات
Video and File Downloader

يدعم تحميل الفيديوهات من YouTube, Facebook وغيرها من المواقع
مع إمكانية اختيار الجودة ومتابعة التقدم ودعم الاستئناف
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
from pathlib import Path
import json

# استيراد الوحدات المخصصة
from downloader import VideoDownloader
from utils import format_size, format_time, validate_url

class DownloadApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        self.downloader = VideoDownloader(self.update_progress, self.update_status)
        
    def setup_window(self):
        """إعداد النافذة الرئيسية"""
        self.root.title("برنامج تحميل الفيديوهات والملفات - Video Downloader")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)
        
        # تعيين أيقونة النافذة (إذا كانت متوفرة)
        try:
            icon_path = Path(__file__).parent / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
            
        # تطبيق ثيم حديث
        style = ttk.Style()
        style.theme_use("clam")
        
        # تخصيص الألوان
        style.configure("Title.TLabel", font=("Arial", 14, "bold"), foreground="#2c3e50")
        style.configure("Heading.TLabel", font=("Arial", 10, "bold"), foreground="#34495e")
        style.configure("Status.TLabel", font=("Arial", 9), foreground="#7f8c8d")
        style.configure("Success.TLabel", font=("Arial", 9), foreground="#27ae60")
        style.configure("Error.TLabel", font=("Arial", 9), foreground="#e74c3c")
        
    def setup_variables(self):
        """إعداد المتغيرات"""
        self.url_var = tk.StringVar()
        self.save_path_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.quality_var = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="جاهز للتحميل")
        self.message_var = tk.StringVar()
        
        # متغيرات التحكم
        self.is_downloading = False
        self.is_paused = False
        self.current_download = None
        self.quality_options = []  # لحفظ خيارات الجودة
        
    def setup_ui(self):
        """إنشاء واجهة المستخدم"""
        # إطار رئيسي مع padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # تكوين الشبكة للتوسع
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # العنوان الرئيسي
        title_label = ttk.Label(main_frame, text="برنامج تحميل الفيديوهات والملفات", 
                               style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # قسم الرابط
        ttk.Label(main_frame, text="رابط الفيديو/الملف:", style="Heading.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        url_frame = ttk.Frame(main_frame)
        url_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(0, weight=1)
        
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=("Arial", 10))
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.fetch_btn = ttk.Button(url_frame, text="جلب المعلومات", 
                                   command=self.fetch_info, width=15)
        self.fetch_btn.grid(row=0, column=1)
        
        # قسم الجودة
        ttk.Label(main_frame, text="جودة الفيديو:", style="Heading.TLabel").grid(
            row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        self.quality_combo = ttk.Combobox(main_frame, textvariable=self.quality_var, 
                                         state="readonly", width=50)
        self.quality_combo.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # إضافة قيمة افتراضية
        self.quality_combo["values"] = ["اضغط على 'جلب المعلومات' أولاً لعرض خيارات الجودة"]
        self.quality_combo.current(0)
        
        # قسم مسار الحفظ
        ttk.Label(main_frame, text="مسار الحفظ:", style="Heading.TLabel").grid(
            row=5, column=0, sticky=tk.W, pady=(10, 5))
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        path_frame.columnconfigure(0, weight=1)
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.save_path_var, 
                                   font=("Arial", 10))
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_btn = ttk.Button(path_frame, text="تصفح", 
                                    command=self.browse_folder, width=10)
        self.browse_btn.grid(row=0, column=1)
        
        # أزرار التحكم
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=7, column=0, columnspan=3, pady=(0, 15))
        
        self.download_btn = ttk.Button(control_frame, text="بدء التحميل", 
                                      command=self.start_download, width=15)
        self.download_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.pause_btn = ttk.Button(control_frame, text="إيقاف مؤقت", 
                                   command=self.toggle_pause, width=15, state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.cancel_btn = ttk.Button(control_frame, text="إلغاء", 
                                    command=self.cancel_download, width=15, state="disabled")
        self.cancel_btn.grid(row=0, column=2)
        
        # شريط التقدم
        ttk.Label(main_frame, text="تقدم التحميل:", style="Heading.TLabel").grid(
            row=8, column=0, sticky=tk.W, pady=(15, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # معلومات الحالة
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                     style="Status.TLabel")
        self.status_label.grid(row=10, column=0, columnspan=3, pady=(0, 10))
        
        # منطقة الرسائل
        message_frame = ttk.LabelFrame(main_frame, text="الرسائل", padding="10")
        message_frame.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                          pady=(10, 0))
        message_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(11, weight=1)
        
        self.message_text = tk.Text(message_frame, height=6, wrap=tk.WORD, 
                                   font=("Arial", 9), state="disabled")
        self.message_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # شريط التمرير للرسائل
        message_scrollbar = ttk.Scrollbar(message_frame, orient="vertical", 
                                         command=self.message_text.yview)
        message_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.message_text.configure(yscrollcommand=message_scrollbar.set)
        
    def add_message(self, message, msg_type="info"):
        """إضافة رسالة إلى منطقة الرسائل"""
        self.message_text.configure(state="normal")
        
        # تحديد لون الرسالة حسب النوع
        if msg_type == "error":
            tag = "error"
            self.message_text.tag_configure("error", foreground="#e74c3c")
        elif msg_type == "success":
            tag = "success"
            self.message_text.tag_configure("success", foreground="#27ae60")
        elif msg_type == "warning":
            tag = "warning"
            self.message_text.tag_configure("warning", foreground="#f39c12")
        else:
            tag = "info"
            self.message_text.tag_configure("info", foreground="#2c3e50")
        
        # إضافة الرسالة مع الوقت
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        self.message_text.insert(tk.END, full_message, tag)
        self.message_text.see(tk.END)
        self.message_text.configure(state="disabled")
        
    def fetch_info(self):
        """جلب معلومات الفيديو والجودات المتاحة"""
        url = self.url_var.get().strip()
        if not url:
            self.add_message("يرجى إدخال رابط صحيح", "error")
            return
            
        if not validate_url(url):
            self.add_message("الرابط المدخل غير صحيح", "error")
            return
            
        self.add_message("جاري جلب معلومات الفيديو...")
        self.fetch_btn.configure(state="disabled")
        
        # إعادة تعيين قائمة الجودة
        self.quality_combo["values"] = ["جاري جلب خيارات الجودة..."]
        self.quality_combo.current(0)
        
        # تشغيل جلب المعلومات في خيط منفصل
        thread = threading.Thread(target=self._fetch_info_thread, args=(url,))
        thread.daemon = True
        thread.start()
        
    def _fetch_info_thread(self, url):
        """خيط جلب معلومات الفيديو"""
        try:
            info = self.downloader.get_video_info(url)
            if info:
                # تحديث واجهة المستخدم في الخيط الرئيسي
                self.root.after(0, self._update_video_info, info)
            else:
                self.root.after(0, self.add_message, "فشل في جلب معلومات الفيديو", "error")
                self.root.after(0, self._set_default_quality_options)
        except Exception as e:
            self.root.after(0, self.add_message, f"خطأ: {str(e)}", "error")
            self.root.after(0, self._set_default_quality_options)
        finally:
            self.root.after(0, lambda: self.fetch_btn.configure(state="normal"))
            
    def _update_video_info(self, info):
        """تحديث معلومات الفيديو في الواجهة"""
        title = info.get("title", "غير معروف")
        duration = info.get("duration", 0)
        uploader = info.get("uploader", "غير معروف")
        
        # عرض معلومات الفيديو
        duration_str = format_time(duration) if duration else "غير محدد"
        self.add_message(f"العنوان: {title}", "success")
        self.add_message(f"القناة: {uploader}")
        self.add_message(f"المدة: {duration_str}")
        
        # تحديث قائمة الجودات
        formats = info.get("formats", [])
        self.quality_options = self.downloader.get_quality_options(formats)
        
        if self.quality_options:
            quality_labels = [q["label"] for q in self.quality_options]
            self.quality_combo["values"] = quality_labels
            self.quality_combo.current(0)
            self.add_message(f"تم العثور على {len(self.quality_options)} خيار جودة")
        else:
            self._set_default_quality_options()
            self.add_message("لم يتم العثور على خيارات جودة متاحة", "warning")
            
    def _set_default_quality_options(self):
        """تعيين خيارات جودة افتراضية"""
        default_options = [
            "أفضل جودة متاحة",
            "جودة متوسطة",
            "جودة منخفضة",
            "صوت فقط"
        ]
        self.quality_combo["values"] = default_options
        self.quality_combo.current(0)
        self.quality_options = [
            {"format_id": "best", "label": "أفضل جودة متاحة", "type": "best"},
            {"format_id": "worst", "label": "جودة متوسطة", "type": "medium"},
            {"format_id": "worst", "label": "جودة منخفضة", "type": "worst"},
            {"format_id": "bestaudio", "label": "صوت فقط", "type": "audio"}
        ]
            
    def browse_folder(self):
        """فتح نافذة اختيار المجلد"""
        folder = filedialog.askdirectory(initialdir=self.save_path_var.get())
        if folder:
            self.save_path_var.set(folder)
            
    def start_download(self):
        """بدء عملية التحميل"""
        url = self.url_var.get().strip()
        if not url:
            self.add_message("يرجى إدخال رابط صحيح", "error")
            return
            
        if not self.quality_var.get():
            self.add_message("يرجى اختيار جودة الفيديو أولاً", "error")
            return
            
        save_path = self.save_path_var.get()
        if not os.path.exists(save_path):
            self.add_message("مسار الحفظ غير موجود", "error")
            return
            
        # تحديث حالة الأزرار
        self.download_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.cancel_btn.configure(state="normal")
        self.fetch_btn.configure(state="disabled")
        
        self.is_downloading = True
        self.is_paused = False
        
        # بدء التحميل في خيط منفصل
        selected_quality = self.quality_combo.current()
        thread = threading.Thread(target=self._download_thread, 
                                 args=(url, selected_quality, save_path))
        thread.daemon = True
        thread.start()
        
        self.add_message("بدء التحميل...", "success")
        
    def _download_thread(self, url, quality_index, save_path):
        """خيط التحميل"""
        try:
            # التأكد من وجود خيارات الجودة
            if not self.quality_options:
                # إذا لم تكن متاحة، استخدم الخيارات الافتراضية
                self._set_default_quality_options()
                
            # استخدام format_id مباشرة للخيارات الافتراضية
            if quality_index < len(self.quality_options):
                selected_option = self.quality_options[quality_index]
                if selected_option.get("type") in ["best", "medium", "worst", "audio"]:
                    # استخدام yt-dlp مع format_id مباشرة
                    success = self._download_with_format_id(url, selected_option["format_id"], save_path)
                else:
                    success = self.downloader.download_video(url, quality_index, save_path)
            else:
                success = False
                
            if success:
                self.root.after(0, self.add_message, "تم التحميل بنجاح!", "success")
            else:
                self.root.after(0, self.add_message, "فشل التحميل", "error")
                
        except Exception as e:
            self.root.after(0, self.add_message, f"خطأ في التحميل: {str(e)}", "error")
        finally:
            self.root.after(0, self._download_completed)
            
    def _download_with_format_id(self, url, format_id, save_path):
        """تحميل باستخدام format_id مباشرة"""
        try:
            import subprocess
            
            # تحضير مسار الحفظ
            output_template = os.path.join(save_path, "%(title)s.%(ext)s")
            
            cmd = [
                "yt-dlp",
                "-f", format_id,
                "-o", output_template,
                "--no-playlist",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Download with format_id error: {e}")
            return False
            
    def _download_completed(self):
        """إعادة تعيين الواجهة بعد انتهاء التحميل"""
        self.is_downloading = False
        self.is_paused = False
        
        self.download_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="إيقاف مؤقت")
        self.cancel_btn.configure(state="disabled")
        self.fetch_btn.configure(state="normal")
        
        self.progress_var.set(0)
        self.status_var.set("جاهز للتحميل")
        
    def toggle_pause(self):
        """إيقاف مؤقت أو استئناف التحميل"""
        if self.is_downloading:
            if self.is_paused:
                self.downloader.resume_download()
                self.is_paused = False
                self.pause_btn.configure(text="إيقاف مؤقت")
                self.add_message("تم استئناف التحميل")
            else:
                self.downloader.pause_download()
                self.is_paused = True
                self.pause_btn.configure(text="استئناف")
                self.add_message("تم إيقاف التحميل مؤقتاً")
                
    def cancel_download(self):
        """إلغاء التحميل"""
        if self.is_downloading:
            result = messagebox.askyesno("تأكيد الإلغاء", "هل تريد إلغاء التحميل؟")
            if result:
                self.downloader.cancel_download()
                self.add_message("تم إلغاء التحميل", "warning")
                self._download_completed()
                
    def update_progress(self, percentage):
        """تحديث شريط التقدم"""
        self.progress_var.set(percentage)
        
    def update_status(self, status):
        """تحديث نص الحالة"""
        self.status_var.set(status)

def main():
    """الدالة الرئيسية"""
    root = tk.Tk()
    app = DownloadApp(root)
    
    # التعامل مع إغلاق النافذة
    def on_closing():
        if app.is_downloading:
            result = messagebox.askyesno("تأكيد الإغلاق", 
                                       "يوجد تحميل جاري. هل تريد إغلاق البرنامج؟")
            if result:
                app.downloader.cancel_download()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

