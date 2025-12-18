"""
Content Domain Entities (Resources)
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

from .base import Entity


class ResourceType(str, Enum):
    """Type of learning resource"""
    PDF = "PDF"
    VIDEO = "VIDEO"
    LINK = "LINK"
    FILE = "FILE"
    TEXT = "TEXT"
    
    @property
    def display_name(self) -> str:
        return self.value


@dataclass
class ResourceEntity(Entity):
    """
    Resource Entity
    
    Represents learning materials attached to a lesson.
    Can be PDF, Video, Link, File, or Text content.
    """
    lesson_id: int = None
    type: ResourceType = ResourceType.TEXT
    title: str = ""
    file_url: Optional[str] = None
    video_url: Optional[str] = None
    content: Optional[str] = None
    duration: Optional[int] = None  # Duration in seconds (for videos)
    order: int = 1
    
    def __str__(self) -> str:
        return f"{self.title} ({self.type.display_name})"
    
    # ==================== Type Checks ====================
    
    def is_video(self) -> bool:
        return self.type == ResourceType.VIDEO
    
    def is_document(self) -> bool:
        return self.type in [ResourceType.PDF, ResourceType.FILE]
    
    def is_text(self) -> bool:
        return self.type == ResourceType.TEXT
    
    def is_external_link(self) -> bool:
        return self.type == ResourceType.LINK
    
    # ==================== URL Helpers ====================
    
    def get_url(self) -> Optional[str]:
        """Get the appropriate URL based on resource type"""
        if self.type == ResourceType.VIDEO:
            return self.video_url
        elif self.type in [ResourceType.PDF, ResourceType.FILE, ResourceType.LINK]:
            return self.file_url
        return None
    
    # ==================== Duration Helpers ====================
    
    def get_duration_display(self) -> str:
        """Get human readable duration"""
        if not self.duration:
            return ""
        
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
    
    # ==================== Validation ====================
    
    def validate(self) -> list:
        """Validate resource data"""
        errors = []
        
        if not self.title:
            errors.append("Title is required")
        
        if self.type == ResourceType.VIDEO and not self.video_url:
            errors.append("Video URL is required for video resources")
        
        if self.type in [ResourceType.PDF, ResourceType.FILE] and not self.file_url:
            errors.append("File URL is required for document resources")
        
        if self.type == ResourceType.LINK and not self.file_url:
            errors.append("URL is required for link resources")
        
        if self.type == ResourceType.TEXT and not self.content:
            errors.append("Content is required for text resources")
        
        return errors

