"""
Video Duration Service

Tự động tính thời lượng video từ file upload hoặc URL.
"""
import os
import re
from typing import Optional
from django.core.files.uploadedfile import UploadedFile


def get_video_duration_from_file(file: UploadedFile) -> Optional[int]:
    """
    Lấy thời lượng video từ file upload (giây)
    
    Args:
        file: File object (UploadedFile)
    
    Returns:
        Duration in seconds, hoặc None nếu không lấy được
    """
    if not file:
        return None
    
    try:
        # Thử dùng moviepy (nếu có)
        try:
            from moviepy.editor import VideoFileClip
            import tempfile
            
            # Lưu file tạm để đọc
            file.seek(0)  # Reset file pointer
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp:
                for chunk in file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
            
            try:
                clip = VideoFileClip(tmp_path)
                duration = int(clip.duration)
                clip.close()
                return duration
            finally:
                # Xóa file tạm
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except:
                        pass
        except ImportError:
            # Nếu không có moviepy, thử dùng ffprobe
            try:
                import subprocess
                import tempfile
                
                # Lưu file tạm
                file.seek(0)  # Reset file pointer
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp:
                    for chunk in file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name
                
                try:
                    # Dùng ffprobe để lấy duration
                    cmd = [
                        'ffprobe',
                        '-v', 'error',
                        '-show_entries', 'format=duration',
                        '-of', 'default=noprint_wrappers=1:nokey=1',
                        tmp_path
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        duration = float(result.stdout.strip())
                        return int(duration)
                finally:
                    if os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except:
                            pass
            except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, Exception):
                pass
    except Exception:
        pass
    
    return None


def get_video_duration_from_url(url: str) -> Optional[int]:
    """
    Lấy thời lượng video từ URL (YouTube, Vimeo, etc.)
    
    Args:
        url: Video URL
    
    Returns:
        Duration in seconds, hoặc None nếu không lấy được
    """
    try:
        # YouTube
        youtube_pattern = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
        match = re.search(youtube_pattern, url)
        if match:
            video_id = match.group(1)
            try:
                from pytube import YouTube
                yt = YouTube(url)
                return int(yt.length)
            except:
                # Thử dùng youtube-dl
                try:
                    import yt_dlp
                    ydl_opts = {'quiet': True}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        if 'duration' in info:
                            return int(info['duration'])
                except:
                    pass
        
        # Vimeo
        vimeo_pattern = r'vimeo\.com\/(?:.*\/)?(\d+)'
        match = re.search(vimeo_pattern, url)
        if match:
            video_id = match.group(1)
            try:
                import requests
                response = requests.get(f'https://vimeo.com/api/v2/video/{video_id}.json', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return int(data[0].get('duration', 0))
            except:
                pass
    except Exception:
        pass
    
    return None

