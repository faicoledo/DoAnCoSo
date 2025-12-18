"""
Repository Interfaces (Ports)

These define the contracts that infrastructure repositories must implement.
Following the Dependency Inversion Principle from Clean Architecture.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.user import UserEntity
from ..entities.course import CourseEntity, SubjectEntity, ModuleEntity, LessonEntity
from ..entities.enrollment import EnrollmentEntity
from ..entities.assessment import AssignmentEntity, QuestionEntity, AttemptEntity
from ..entities.progress import (
    CourseProgressEntity, 
    LessonProgressEntity,
    ResourceProgressEntity,
    AssignmentProgressEntity
)


class IRepository(ABC):
    """Base repository interface"""
    
    @abstractmethod
    def save(self, entity) -> None:
        """Persist an entity"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete an entity by ID"""
        pass


class IUserRepository(IRepository):
    """User Repository Interface"""
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[UserEntity]:
        """Find user by ID"""
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[UserEntity]:
        """Find user by email"""
        pass
    
    @abstractmethod
    def find_by_username(self, username: str) -> Optional[UserEntity]:
        """Find user by username"""
        pass
    
    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Check if user with email exists"""
        pass
    
    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[UserEntity]:
        """Get all users with pagination"""
        pass
    
    @abstractmethod
    def find_by_role(self, role: str) -> List[UserEntity]:
        """Find users by role"""
        pass


class ICourseRepository(IRepository):
    """Course Repository Interface"""
    
    @abstractmethod
    def find_by_id(self, course_id: int) -> Optional[CourseEntity]:
        """Find course by ID"""
        pass
    
    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[CourseEntity]:
        """Get all courses with pagination"""
        pass
    
    @abstractmethod
    def find_by_status(self, status: str) -> List[CourseEntity]:
        """Find courses by status"""
        pass
    
    @abstractmethod
    def find_by_subject(self, subject_id: int) -> List[CourseEntity]:
        """Find courses by subject"""
        pass
    
    @abstractmethod
    def find_with_modules(self, course_id: int) -> Optional[CourseEntity]:
        """Find course with all modules and lessons"""
        pass


class ISubjectRepository(IRepository):
    """Subject Repository Interface"""
    
    @abstractmethod
    def find_by_id(self, subject_id: int) -> Optional[SubjectEntity]:
        """Find subject by ID"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[SubjectEntity]:
        """Get all subjects"""
        pass


class IEnrollmentRepository(IRepository):
    """Enrollment Repository Interface"""
    
    @abstractmethod
    def find_by_id(self, enrollment_id: int) -> Optional[EnrollmentEntity]:
        """Find enrollment by ID"""
        pass
    
    @abstractmethod
    def find_by_user_and_course(self, user_id: int, course_id: int) -> Optional[EnrollmentEntity]:
        """Find enrollment by user and course"""
        pass
    
    @abstractmethod
    def find_by_user(self, user_id: int) -> List[EnrollmentEntity]:
        """Find all enrollments for a user"""
        pass
    
    @abstractmethod
    def find_by_course(self, course_id: int) -> List[EnrollmentEntity]:
        """Find all enrollments for a course"""
        pass
    
    @abstractmethod
    def exists(self, user_id: int, course_id: int) -> bool:
        """Check if enrollment exists"""
        pass
    
    @abstractmethod
    def count_by_course(self, course_id: int) -> int:
        """Count enrollments for a course"""
        pass


class IAssignmentRepository(IRepository):
    """Assignment Repository Interface"""
    
    @abstractmethod
    def find_by_id(self, assignment_id: int) -> Optional[AssignmentEntity]:
        """Find assignment by ID"""
        pass
    
    @abstractmethod
    def find_by_lesson(self, lesson_id: int) -> List[AssignmentEntity]:
        """Find assignments for a lesson"""
        pass
    
    @abstractmethod
    def find_with_questions(self, assignment_id: int) -> Optional[AssignmentEntity]:
        """Find assignment with all questions"""
        pass


class IAttemptRepository(IRepository):
    """Attempt Repository Interface"""
    
    @abstractmethod
    def find_by_id(self, attempt_id: int) -> Optional[AttemptEntity]:
        """Find attempt by ID"""
        pass
    
    @abstractmethod
    def find_by_user_and_assignment(self, user_id: int, assignment_id: int) -> List[AttemptEntity]:
        """Find all attempts by user for an assignment"""
        pass
    
    @abstractmethod
    def count_by_user_and_assignment(self, user_id: int, assignment_id: int) -> int:
        """Count attempts by user for an assignment"""
        pass
    
    @abstractmethod
    def find_latest_by_user_and_assignment(self, user_id: int, assignment_id: int) -> Optional[AttemptEntity]:
        """Find the latest attempt"""
        pass


class IProgressRepository(IRepository):
    """Progress Repository Interface"""
    
    @abstractmethod
    def find_course_progress(self, user_id: int, course_id: int) -> Optional[CourseProgressEntity]:
        """Find course progress for user"""
        pass
    
    @abstractmethod
    def find_lesson_progress(self, user_id: int, lesson_id: int) -> Optional[LessonProgressEntity]:
        """Find lesson progress for user"""
        pass
    
    @abstractmethod
    def find_resource_progress(self, user_id: int, resource_id: int) -> Optional[ResourceProgressEntity]:
        """Find resource progress for user"""
        pass
    
    @abstractmethod
    def find_assignment_progress(self, user_id: int, assignment_id: int) -> Optional[AssignmentProgressEntity]:
        """Find assignment progress for user"""
        pass
    
    @abstractmethod
    def find_all_course_progress(self, user_id: int) -> List[CourseProgressEntity]:
        """Find all course progress for user"""
        pass
    
    @abstractmethod
    def save_course_progress(self, progress: CourseProgressEntity) -> None:
        """Save course progress"""
        pass
    
    @abstractmethod
    def save_lesson_progress(self, progress: LessonProgressEntity) -> None:
        """Save lesson progress"""
        pass

