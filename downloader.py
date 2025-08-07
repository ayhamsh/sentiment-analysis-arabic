#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وحدة التحميل الرئيسية
Video Downloader Module

تحتوي على منطق التحميل باستخدام yt-dlp مع دعم الإيقاف المؤقت والاستئناف
"""

import os
import sys
import json
import time
import threading
import subprocess
from pathlib import Path
import requests
from urllib.parse import urlparse

class VideoDownloader:
    def __init__(self, progress_callback=None, status_callback=None):
        """
        تهيئة منزل الفيديوهات
        
        Args:
            progress_callback: دالة لتحديث التقدم (تستقبل نسبة مئوية)
            status_callback: دالة لتحديث الحالة (تستقبل نص الحالة)
        """
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        
        # متغيرات التحكم في التحميل
        self.is_downloading = False
        self.is_paused = False
        self.is_cancelled = False
        self.current_process = None
        self.download_thread = None
        
        # معلومات التحميل الحالي
        self.current_info = None
        self.download_path = None
        self.temp_path = None
        
        # التحقق من وجود yt-dlp
        self._check_ytdlp()
        
    def _check_ytdlp(self):
        """التحقق من وجود yt-dlp وتثبيته إذا لزم الأمر"""
        try:
            result = subprocess.run(["yt-dlp", "--version"],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"yt-dlp version: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        # محاولة تثبيت yt-dlp
        try:
            print("Installing yt-dlp...")
            subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"],
                          check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install yt-dlp: {e}")
            return False
            
    def get_video_info(self, url):
        """
        جلب معلومات الفيديو من الرابط
        
        Args:
            url: رابط الفيديو
            
        Returns:
            dict: معلومات الفيديو أو None في حالة الفشل
        """
        try:
            cmd = [
                "yt-dlp",
                "--dump-json",
                "--no-playlist",
                url
            ]
            
            # زيادة المهلة إلى 60 ثانية
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                self.current_info = info
                return info
            else:
                print(f"yt-dlp error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("Timeout while fetching video info")
            return None
        except json.JSONDecodeError:
            print("Failed to parse video info JSON")
            return None
        except Exception as e:
            print(f"Error fetching video info: {e}")
            return None
            
    def get_quality_options(self, formats):
        """
        استخراج خيارات الجودة المتاحة من معلومات الفيديو
        
        Args:
            formats: قائمة التنسيقات من معلومات الفيديو
            
        Returns:
            list: قائمة خيارات الجودة
        """
        quality_options = []
        seen_qualities = set()
        
        # تصفية التنسيقات غير الصالحة (بدون URL أو حجم)
        valid_formats = [f for f in formats if f.get("url") and (f.get("filesize") or f.get("filesize_approx"))]
        
        # ترتيب التنسيقات حسب الجودة (من الأعلى للأقل)
        # الأولوية: فيديو+صوت مدمج -> فيديو فقط -> صوت فقط
        
        # 1. تنسيقات مدمجة (فيديو + صوت)
        for fmt in valid_formats:
            if fmt.get("vcodec", "none") != "none" and fmt.get("acodec", "none") != "none":
                height = fmt.get("height", 0)
                ext = fmt.get("ext", "mp4")
                filesize = fmt.get("filesize") or fmt.get("filesize_approx", 0)
                
                quality_label = f"{height}p"
                if fmt.get("width"): quality_label += " ({0}x{1})".format(fmt.get("width"), height)
                if filesize > 0: quality_label += f" - {filesize / (1024 * 1024):.1f} MB"
                quality_label += f" [{ext}]"
                
                quality_key = f"combined_{height}_{ext}"
                if quality_key not in seen_qualities:
                    quality_options.append({
                        "format_id": fmt.get("format_id"),
                        "label": quality_label,
                        "height": height,
                        "ext": ext,
                        "filesize": filesize,
                        "type": "combined"
                    })
                    seen_qualities.add(quality_key)
                    
        # 2. تنسيقات فيديو فقط + أفضل صوت (لدمجها لاحقاً)
        video_only_formats = sorted([f for f in valid_formats if f.get("vcodec", "none") != "none" and f.get("acodec", "none") == "none"], key=lambda x: x.get("height", 0), reverse=True)
        audio_only_formats = sorted([f for f in valid_formats if f.get("acodec", "none") != "none" and f.get("vcodec", "none") == "none"], key=lambda x: x.get("abr", 0), reverse=True)
        
        if video_only_formats and audio_only_formats:
            best_audio_format = audio_only_formats[0]
            for fmt in video_only_formats:
                height = fmt.get("height", 0)
                ext = fmt.get("ext", "mp4")
                filesize = (fmt.get("filesize") or fmt.get("filesize_approx", 0)) + (best_audio_format.get("filesize") or best_audio_format.get("filesize_approx", 0))
                
                quality_label = f"{height}p (فيديو + صوت)"
                if fmt.get("width"): quality_label += " ({0}x{1})".format(fmt.get("width"), height)
                quality_label += " [{0} + {1}]".format(ext, best_audio_format.get("ext", "mp3"))
                if filesize > 0: quality_label += f" - {filesize / (1024 * 1024):.1f} MB"
                
                quality_key = f"separate_{height}_{ext}"
                if quality_key not in seen_qualities:
                    quality_options.append({
                        "format_id": "{0}+{1}".format(fmt.get("format_id"), best_audio_format.get("format_id")),
                        "label": quality_label,
                        "height": height,
                        "ext": ext,
                        "filesize": filesize,
                        "type": "separate"
                    })
                    seen_qualities.add(quality_key)
                    
        # 3. تنسيقات صوت فقط
        for fmt in audio_only_formats:
            ext = fmt.get("ext", "mp3")
            filesize = fmt.get("filesize") or fmt.get("filesize_approx", 0)
            
            quality_label = f"صوت فقط"
            if fmt.get("abr"): quality_label += " ({0:.0f}kbps)".format(fmt.get("abr"))
            if filesize > 0: quality_label += f" - {filesize / (1024 * 1024):.1f} MB"
            quality_label += f" [{ext}]"
            
            # تم إصلاح هذا السطر
            quality_key = "audio_{}_{}".format(ext, fmt.get("abr", 0))
            if quality_key not in seen_qualities:
                quality_options.append({
                    "format_id": fmt.get("format_id"),
                    "label": quality_label,
                    "height": 0,
                    "ext": ext,
                    "filesize": filesize,
                    "type": "audio"
                })
                seen_qualities.add(quality_key)
                
        # ترتيب نهائي حسب الارتفاع (الجودة) ثم الحجم
        quality_options.sort(key=lambda x: (x["height"], x["filesize"]), reverse=True)
        
        return quality_options
        
    def download_video(self, url, quality_index, save_path):
        """
        تحميل الفيديو
        
        Args:
            url: رابط الفيديو
            quality_index: فهرس الجودة المختارة
            save_path: مسار الحفظ
            
        Returns:
            bool: True إذا نجح التحميل، False إذا فشل
        """
        if not self.current_info:
            # حاول جلب المعلومات مرة أخرى إذا لم تكن متاحة
            if not self.get_video_info(url):
                return False
                
        formats = self.current_info.get("formats", [])
        quality_options = self.get_quality_options(formats)
        
        if not quality_options or quality_index >= len(quality_options):
            print("لا توجد خيارات جودة متاحة أو الفهرس غير صالح.")
            return False
            
        selected_quality = quality_options[quality_index]
        format_id = selected_quality["format_id"]
        
        # تحضير مسار الحفظ
        title = self.current_info.get("title", "video")
        # تنظيف اسم الملف من الأحرف غير المسموحة
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).rstrip()
        safe_title = safe_title[:100]  # تحديد طول الاسم
        
        output_template = os.path.join(save_path, f"{safe_title}.%(ext)s")
        
        # بناء أمر yt-dlp
        cmd = [
            "yt-dlp",
            "-f", format_id,
            "-o", output_template,
            "--no-playlist",
            "--newline",  # لتسهيل تتبع التقدم
            url
        ]
        
        # إضافة خيارات إضافية للجودة
        if selected_quality["type"] == "separate":
            cmd.extend(["--merge-output-format", "mp4"])
            
        self.is_downloading = True
        self.is_cancelled = False
        self.is_paused = False
        
        try:
            # تشغيل عملية التحميل
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            # تتبع التقدم
            self._monitor_progress()
            
            # انتظار انتهاء العملية
            return_code = self.current_process.wait()
            
            if return_code == 0 and not self.is_cancelled:
                if self.status_callback:
                    self.status_callback("تم التحميل بنجاح")
                return True
            else:
                if self.status_callback:
                    self.status_callback("فشل التحميل أو تم إلغاؤه")
                return False
                
        except Exception as e:
            print(f"Download error: {e}")
            if self.status_callback:
                self.status_callback(f"خطأ في التحميل: {str(e)}")
            return False
        finally:
            self.is_downloading = False
            self.current_process = None
            
    def _monitor_progress(self):
        """مراقبة تقدم التحميل"""
        if not self.current_process:
            return
            
        try:
            for line in self.current_process.stdout:
                if self.is_cancelled:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                    
                # تحليل خط التقدم من yt-dlp
                if "[download]" in line and "%" in line:
                    try:
                        # استخراج النسبة المئوية
                        parts = line.split()
                        for part in parts:
                            if "%" in part:
                                percentage_str = part.replace("%", "")
                                percentage = float(percentage_str)
                                
                                if self.progress_callback:
                                    self.progress_callback(percentage)
                                    
                                # استخراج معلومات إضافية (السرعة، الوقت المتبقي)
                                status_parts = []
                                for i, p in enumerate(parts):
                                    if "iB/s" in p or "B/s" in p:  # السرعة
                                        status_parts.append(f"السرعة: {p}")
                                    elif "ETA" in p and i + 1 < len(parts):  # الوقت المتبقي
                                        eta = parts[i + 1]
                                        status_parts.append(f"الوقت المتبقي: {eta}")
                                        
                                status_text = f"{percentage:.1f}%"
                                if status_parts:
                                    status_text += " - " + " | ".join(status_parts)
                                    
                                if self.status_callback:
                                    self.status_callback(status_text)
                                break
                    except (ValueError, IndexError):
                        continue
                        
        except Exception as e:
            print(f"Progress monitoring error: {e}")
            
    def pause_download(self):
        """إيقاف التحميل مؤقتاً"""
        if self.current_process and self.is_downloading:
            self.is_paused = True
            try:
                # إرسال إشارة SIGSTOP (Linux/Mac) أو محاولة إيقاف العملية
                if hasattr(self.current_process, "suspend"):
                    self.current_process.suspend()
                else:
                    # في Windows، نحتاج لطريقة مختلفة
                    import signal
                    os.kill(self.current_process.pid, signal.SIGSTOP)
            except:
                # إذا فشل الإيقاف المؤقت، نلغي التحميل
                self.cancel_download()
                
    def resume_download(self):
        """استئناف التحميل"""
        if self.current_process and self.is_paused:
            self.is_paused = False
            try:
                # إرسال إشارة SIGCONT (Linux/Mac) أو استئناف العملية
                if hasattr(self.current_process, "resume"):
                    self.current_process.resume()
                else:
                    import signal
                    os.kill(self.current_process.pid, signal.SIGCONT)
            except:
                pass
                
    def cancel_download(self):
        """إلغاء التحميل"""
        self.is_cancelled = True
        if self.current_process:
            try:
                self.current_process.terminate()
                # انتظار قصير ثم القتل القسري إذا لزم الأمر
                try:
                    self.current_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.current_process.kill()
            except:
                pass
            finally:
                self.current_process = None
                
        self.is_downloading = False
        self.is_paused = False
        
    def download_file(self, url, save_path, filename=None):
        """
        تحميل ملف عادي (غير فيديو) باستخدام requests
        
        Args:
            url: رابط الملف
            save_path: مسار الحفظ
            filename: اسم الملف (اختياري)
            
        Returns:
            bool: True إذا نجح التحميل، False إذا فشل
        """
        try:
            # تحديد اسم الملف
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename:
                    filename = "downloaded_file"
                    
            file_path = os.path.join(save_path, filename)
            
            # بدء التحميل
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0
            
            self.is_downloading = True
            self.is_cancelled = False
            
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.is_cancelled:
                        break
                        
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # تحديث التقدم
                        if total_size > 0:
                            percentage = (downloaded_size / total_size) * 100
                            if self.progress_callback:
                                self.progress_callback(percentage)
                                
                            # تحديث الحالة
                            size_mb = downloaded_size / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)
                            status = f"{percentage:.1f}% - {size_mb:.1f}/{total_mb:.1f} MB"
                            if self.status_callback:
                                self.status_callback(status)
                                
            if self.is_cancelled:
                # حذف الملف المؤقت في حالة الإلغاء
                try:
                    os.remove(file_path)
                except:
                    pass
                return False
                
            return True
            
        except Exception as e:
            print(f"File download error: {e}")
            if self.status_callback:
                self.status_callback(f"خطأ في تحميل الملف: {str(e)}")
            return False
        finally:
            self.is_downloading = False

