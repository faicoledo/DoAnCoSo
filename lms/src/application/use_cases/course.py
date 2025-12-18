"""
Course Use Cases
"""
from dataclasses import dataclass
from typing import List, Optional

from .base import UseCase
from ..dtos.course import CourseDTO, CourseListDTO
from ...domain.interfaces import ICourseRepository
from ...domain.exceptions.course import CourseNotFoundException


@dataclass
class GetCourseDetailInput:
    """Input for getting course detail"""
    course_id: int
    include_modules: bool = True


class GetCourseDetailUseCase(UseCase[GetCourseDetailInput, CourseDTO]):
    """
    Use case for getting detailed course information.
    """
    
    def __init__(self, course_repository: ICourseRepository):
        self.course_repository = course_repository
    
    def execute(self, input_dto: GetCourseDetailInput) -> CourseDTO:
        if input_dto.include_modules:
            course = self.course_repository.find_with_modules(input_dto.course_id)
        else:
            course = self.course_repository.find_by_id(input_dto.course_id)
        
        if not course:
            raise CourseNotFoundException(input_dto.course_id)
        
        return CourseDTO.from_entity(course)


@dataclass
class ListCoursesInput:
    """Input for listing courses"""
    status: Optional[str] = None
    subject_id: Optional[int] = None
    limit: int = 20
    offset: int = 0


class ListCoursesUseCase(UseCase[ListCoursesInput, List[CourseListDTO]]):
    """
    Use case for listing courses with optional filters.
    """
    
    def __init__(self, course_repository: ICourseRepository):
        self.course_repository = course_repository
    
    def execute(self, input_dto: ListCoursesInput) -> List[CourseListDTO]:
        # Apply filters
        if input_dto.status:
            courses = self.course_repository.find_by_status(input_dto.status)
        elif input_dto.subject_id:
            courses = self.course_repository.find_by_subject(input_dto.subject_id)
        else:
            courses = self.course_repository.find_all(
                limit=input_dto.limit,
                offset=input_dto.offset
            )
        
        return [
            CourseListDTO(
                id=c.id,
                title=c.title,
                subject_title=c.subject.title if c.subject else "",
                status=c.status.value,
                status_display=c.status.display_name,
                start_date=c.start_date,
                end_date=c.end_date,
                students_count=len(c.get_students()) if c.enrollments else 0,
            )
            for c in courses
        ]

