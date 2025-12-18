"""
Course DTOs
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date, datetime


@dataclass
class LessonDTO:
    """DTO for lesson data"""
    id: int
    title: str
    content: str
    order: int
    resources_count: int = 0
    assignments_count: int = 0


@dataclass
class ModuleDTO:
    """DTO for module data"""
    id: int
    title: str
    order: int
    lessons: List[LessonDTO] = field(default_factory=list)
    lessons_count: int = 0


@dataclass
class CourseDTO:
    """DTO for full course data"""
    id: int
    title: str
    description: str
    subject_id: int
    subject_title: str
    start_date: date
    end_date: date
    status: str
    status_display: str
    modules: List[ModuleDTO] = field(default_factory=list)
    total_lessons: int = 0
    total_students: int = 0
    
    @classmethod
    def from_entity(cls, course_entity) -> 'CourseDTO':
        """Create DTO from CourseEntity"""
        modules = [
            ModuleDTO(
                id=m.id,
                title=m.title,
                order=m.order,
                lessons=[
                    LessonDTO(
                        id=l.id,
                        title=l.title,
                        content=l.content or "",
                        order=l.order,
                        resources_count=len(l.resources) if l.resources else 0,
                        assignments_count=len(l.assignments) if l.assignments else 0,
                    ) for l in m.lessons
                ],
                lessons_count=len(m.lessons)
            ) for m in course_entity.modules
        ]
        
        return cls(
            id=course_entity.id,
            title=course_entity.title,
            description=course_entity.description or "",
            subject_id=course_entity.subject_id,
            subject_title=course_entity.subject.title if course_entity.subject else "",
            start_date=course_entity.start_date,
            end_date=course_entity.end_date,
            status=course_entity.status.value,
            status_display=course_entity.status.display_name,
            modules=modules,
            total_lessons=course_entity.get_total_lessons(),
            total_students=len(course_entity.get_students()) if course_entity.enrollments else 0,
        )


@dataclass
class CourseListDTO:
    """DTO for course list (summary)"""
    id: int
    title: str
    subject_title: str
    status: str
    status_display: str
    start_date: date
    end_date: date
    students_count: int = 0


@dataclass
class EnrollmentDTO:
    """DTO for enrollment operations"""
    user_id: int
    course_id: int
    role_in_course: str = "STUDENT"


@dataclass
class EnrollmentResponseDTO:
    """DTO for enrollment response"""
    id: int
    user_id: int
    course_id: int
    course_title: str
    subject_title: str
    role_in_course: str
    role_display: str
    joined_at: datetime


@dataclass
class StudentListDTO:
    """DTO for student in course list"""
    user_id: int
    email: str
    full_name: str
    role_in_course: str
    role_display: str
    joined_at: datetime

