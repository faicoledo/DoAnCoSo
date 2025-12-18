"""
Progress Domain Entities
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal

from .base import Entity


@dataclass
class ResourceProgressEntity(Entity):
    """User's progress on a resource"""
    user_id: int = None
    resource_id: int = None
    viewed: bool = False
    watched_percent: int = 0  # 0-100
    last_watched_at: Optional[datetime] = None
    
    def __str__(self) -> str:
        return f"User {self.user_id} - Resource {self.resource_id} ({self.watched_percent}%)"
    
    def mark_viewed(self) -> None:
        """Mark resource as viewed"""
        self.viewed = True
        self.last_watched_at = datetime.now()
    
    def update_watch_progress(self, percent: int) -> None:
        """Update watch progress"""
        if percent < 0 or percent > 100:
            raise ValueError("Percent must be between 0 and 100")
        
        # Only update if new progress is higher
        if percent > self.watched_percent:
            self.watched_percent = percent
            self.last_watched_at = datetime.now()
        
        if percent >= 90:  # Consider 90% as viewed
            self.viewed = True
    
    def is_completed(self) -> bool:
        """Check if resource is completed"""
        return self.viewed or self.watched_percent >= 90


@dataclass
class AssignmentProgressEntity(Entity):
    """User's progress on an assignment"""
    user_id: int = None
    assignment_id: int = None
    score: Optional[Decimal] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    
    def __str__(self) -> str:
        status = "Hoàn thành" if self.completed else "Chưa hoàn thành"
        return f"User {self.user_id} - Assignment {self.assignment_id} ({status})"
    
    def mark_completed(self, score: Decimal) -> None:
        """Mark assignment as completed with score"""
        self.score = score
        self.completed = True
        self.completed_at = datetime.now()
    
    def is_passed(self, passing_score: Decimal = Decimal('50')) -> bool:
        """Check if passed the assignment"""
        return self.completed and self.score is not None and self.score >= passing_score


@dataclass
class LessonProgressEntity(Entity):
    """User's progress on a lesson"""
    user_id: int = None
    lesson_id: int = None
    percent_complete: int = 0  # 0-100
    
    def __str__(self) -> str:
        return f"User {self.user_id} - Lesson {self.lesson_id} ({self.percent_complete}%)"
    
    def update_progress(self, percent: int) -> None:
        """Update lesson progress"""
        if percent < 0 or percent > 100:
            raise ValueError("Percent must be between 0 and 100")
        self.percent_complete = percent
    
    def is_completed(self) -> bool:
        """Check if lesson is completed"""
        return self.percent_complete >= 100


@dataclass
class CourseProgressEntity(Entity):
    """User's overall progress on a course"""
    user_id: int = None
    course_id: int = None
    percent_complete: int = 0  # 0-100
    completed: bool = False
    last_accessed: Optional[datetime] = None
    
    def __str__(self) -> str:
        return f"User {self.user_id} - Course {self.course_id} ({self.percent_complete}%)"
    
    def update_progress(self, percent: int) -> None:
        """Update course progress"""
        if percent < 0 or percent > 100:
            raise ValueError("Percent must be between 0 and 100")
        
        self.percent_complete = percent
        self.last_accessed = datetime.now()
        
        if percent >= 100:
            self.completed = True
    
    def mark_accessed(self) -> None:
        """Mark course as accessed"""
        self.last_accessed = datetime.now()
    
    def is_completed(self) -> bool:
        """Check if course is completed"""
        return self.completed or self.percent_complete >= 100


@dataclass
class ProgressEntity(Entity):
    """
    Aggregate for tracking overall user progress
    Combines all progress types for convenient access
    """
    user_id: int = None
    course_progress: Optional[CourseProgressEntity] = None
    lesson_progresses: list = None
    resource_progresses: list = None
    assignment_progresses: list = None
    
    def __post_init__(self):
        if self.lesson_progresses is None:
            self.lesson_progresses = []
        if self.resource_progresses is None:
            self.resource_progresses = []
        if self.assignment_progresses is None:
            self.assignment_progresses = []
    
    def get_overall_percent(self) -> int:
        """Calculate overall progress percentage"""
        if self.course_progress:
            return self.course_progress.percent_complete
        return 0
    
    def get_completed_lessons_count(self) -> int:
        """Get count of completed lessons"""
        return sum(1 for p in self.lesson_progresses if p.is_completed())
    
    def get_completed_assignments_count(self) -> int:
        """Get count of completed assignments"""
        return sum(1 for p in self.assignment_progresses if p.completed)

