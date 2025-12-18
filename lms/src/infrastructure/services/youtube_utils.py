"""
YouTube URL Utilities

Hỗ trợ extract video ID từ các định dạng URL YouTube khác nhau.
"""
import re


def extract_youtube_video_id(url: str) -> str:
    """
    Extract video ID từ YouTube URL
    
    Hỗ trợ các định dạng:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID&feature=share
    - https://m.youtube.com/watch?v=VIDEO_ID
    
    Args:
        url: YouTube URL
    
    Returns:
        Video ID hoặc None nếu không phải YouTube URL
    """
    if not url:
        return None
    
    # Pattern cho các định dạng YouTube URL
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def get_youtube_embed_url(video_id: str) -> str:
    """
    Tạo YouTube embed URL từ video ID
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        Embed URL
    """
    if not video_id:
        return None
    
    return f"https://www.youtube.com/embed/{video_id}"


def is_youtube_url(url: str) -> bool:
    """
    Kiểm tra xem URL có phải YouTube không
    
    Args:
        url: URL cần kiểm tra
    
    Returns:
        True nếu là YouTube URL
    """
    if not url:
        return False
    
    youtube_domains = [
        'youtube.com',
        'youtu.be',
        'm.youtube.com',
        'www.youtube.com',
    ]
    
    return any(domain in url.lower() for domain in youtube_domains)




