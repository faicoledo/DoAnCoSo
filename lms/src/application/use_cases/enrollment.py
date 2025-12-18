"""
Enrollment Use Cases
"""
from dataclasses import dataclass
from typing import List

from .base import UseCase
from ..dtos.course import EnrollmentDTO, EnrollmentResponseDTO, StudentListDTO
from ...domain.interfaces import IEnrollmentRepository, ICourseRepository, IUserRepository
from ...domain.entities.enrollment import EnrollmentEntity, CourseRole
from ...domain.entities.course import CourseStatus
from ...domain.exceptions.course import (
    CourseNotFoundException,
    CourseNotAvailableException,
    AlreadyEnrolledException,
    NotEnrolledException,
    CannotUnenrollException,
)
from ...domain.exceptions.user import InsufficientPermissionsException


@dataclass
class EnrollInput:
    """Input for enrollment"""
    user_id: int
    course_id: int


class EnrollInCourseUseCase(UseCase[EnrollInput, EnrollmentResponseDTO]):
    """
    Use case for enrolling a user in a course.
    
    Business Rules:
    1. Course must exist
    2. Course must be in UPCOMING status
    3. User must not be already enrolled
    """
    
    def __init__(
        self,
        enrollment_repository: IEnrollmentRepository,
        course_repository: ICourseRepository,
    ):
        self.enrollment_repository = enrollment_repository
        self.course_repository = course_repository
    
    def execute(self, input_dto: EnrollInput) -> EnrollmentResponseDTO:
        # Get course
        course = self.course_repository.find_by_id(input_dto.course_id)
        if not course:
            raise CourseNotFoundException(input_dto.course_id)
        
        # Check course status
        if not course.can_enroll():
            raise CourseNotAvailableException(
                input_dto.course_id, 
                course.status.display_name
            )
        
        # Check if already enrolled
        if self.enrollment_repository.exists(input_dto.user_id, input_dto.course_id):
            raise AlreadyEnrolledException(input_dto.user_id, input_dto.course_id)
        
        # Create enrollment
        enrollment = EnrollmentEntity(
            user_id=input_dto.user_id,
            course_id=input_dto.course_id,
            role_in_course=CourseRole.STUDENT,
        )
        
        # Save
        self.enrollment_repository.save(enrollment)
        
        return EnrollmentResponseDTO(
            id=enrollment.id,
            user_id=enrollment.user_id,
            course_id=enrollment.course_id,
            course_title=course.title,
            subject_title=course.subject.title if course.subject else "",
            role_in_course=enrollment.role_in_course.value,
            role_display=enrollment.role_in_course.display_name,
            joined_at=enrollment.joined_at,
        )


class UnenrollFromCourseUseCase(UseCase[EnrollInput, bool]):
    """
    Use case for un-enrolling a user from a course.
    
    Business Rules:
    1. User must be enrolled
    2. Course must be in UPCOMING status (cannot unenroll from ongoing/completed)
    """
    
    def __init__(
        self,
        enrollment_repository: IEnrollmentRepository,
        course_repository: ICourseRepository,
    ):
        self.enrollment_repository = enrollment_repository
        self.course_repository = course_repository
    
    def execute(self, input_dto: EnrollInput) -> bool:
        # Get enrollment
        enrollment = self.enrollment_repository.find_by_user_and_course(
            input_dto.user_id, 
            input_dto.course_id
        )
        if not enrollment:
            raise NotEnrolledException(input_dto.user_id, input_dto.course_id)
        
        # Get course
        course = self.course_repository.find_by_id(input_dto.course_id)
        if not course:
            raise CourseNotFoundException(input_dto.course_id)
        
        # Check if can unenroll
        if not course.can_unenroll():
            raise CannotUnenrollException(
                input_dto.course_id,
                f"Course is {course.status.display_name}"
            )
        
        # Delete enrollment
        return self.enrollment_repository.delete(enrollment.id)


@dataclass
class GetMyCoursesInput:
    """Input for getting user's courses"""
    user_id: int


class GetMyCoursesUseCase(UseCase[GetMyCoursesInput, List[EnrollmentResponseDTO]]):
    """
    Use case for getting all courses a user is enrolled in.
    """
    
    def __init__(
        self,
        enrollment_repository: IEnrollmentRepository,
        course_repository: ICourseRepository,
    ):
        self.enrollment_repository = enrollment_repository
        self.course_repository = course_repository
    
    def execute(self, input_dto: GetMyCoursesInput) -> List[EnrollmentResponseDTO]:
        enrollments = self.enrollment_repository.find_by_user(input_dto.user_id)
        
        result = []
        for e in enrollments:
            course = self.course_repository.find_by_id(e.course_id)
            if course:
                result.append(EnrollmentResponseDTO(
                    id=e.id,
                    user_id=e.user_id,
                    course_id=e.course_id,
                    course_title=course.title,
                    subject_title=course.subject.title if course.subject else "",
                    role_in_course=e.role_in_course.value,
                    role_display=e.role_in_course.display_name,
                    joined_at=e.joined_at,
                ))
        
        return result


@dataclass
class GetCourseStudentsInput:
    """Input for getting course students"""
    user_id: int  # Requesting user
    course_id: int


class GetCourseStudentsUseCase(UseCase[GetCourseStudentsInput, List[StudentListDTO]]):
    """
    Use case for getting all students in a course.
    
    Access Control:
    - Only teachers/TAs of the course can view the student list
    """
    
    def __init__(
        self,
        enrollment_repository: IEnrollmentRepository,
        course_repository: ICourseRepository,
        user_repository: IUserRepository,
    ):
        self.enrollment_repository = enrollment_repository
        self.course_repository = course_repository
        self.user_repository = user_repository
    
    def execute(self, input_dto: GetCourseStudentsInput) -> List[StudentListDTO]:
        # Check course exists
        course = self.course_repository.find_by_id(input_dto.course_id)
        if not course:
            raise CourseNotFoundException(input_dto.course_id)
        
        # Check user permission (must be teacher/TA in this course)
        user_enrollment = self.enrollment_repository.find_by_user_and_course(
            input_dto.user_id,
            input_dto.course_id
        )
        
        if not user_enrollment or not user_enrollment.can_view_all_students():
            raise InsufficientPermissionsException("COURSE_TEACHER_OR_TA")
        
        # Get all enrollments
        enrollments = self.enrollment_repository.find_by_course(input_dto.course_id)
        
        result = []
        for e in enrollments:
            user = self.user_repository.find_by_id(e.user_id)
            if user:
                result.append(StudentListDTO(
                    user_id=user.id,
                    email=user.email,
                    full_name=user.full_name,
                    role_in_course=e.role_in_course.value,
                    role_display=e.role_in_course.display_name,
                    joined_at=e.joined_at,
                ))
        
        return result

