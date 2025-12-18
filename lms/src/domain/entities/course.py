"""
Course Domain Entities
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List
from enum import Enum

from .base import Entity, AggregateRoot


class CourseStatus(str, Enum):
    """
    Course status choices
    
    Trạng thái được tính TỰ ĐỘNG dựa trên ngày bắt đầu và kết thúc:
    - UPCOMING: Trước ngày bắt đầu
    - ONGOING: Trong thời gian khóa học  
    - COMPLETED: Sau ngày kết thúc
    """
    UPCOMING = "UPCOMING"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    
    @property
    def display_name(self) -> str:
        names = {
            "UPCOMING": "Sắp diễn ra",
            "ONGOING": "Đang diễn ra",
            "COMPLETED": "Đã hoàn thành"
        }
        return names.get(self.value, self.value)
    
    @staticmethod
    def compute_from_dates(start_date: date, end_date: date) -> 'CourseStatus':
        """Tính trạng thái dựa trên ngày"""
        from datetime import date as date_type
        today = date_type.today()
        
        if today < start_date:
            return CourseStatus.UPCOMING
        elif today > end_date:
            return CourseStatus.COMPLETED
        else:
            return CourseStatus.ONGOING


@dataclass
class SubjectEntity(Entity):
    """Subject Entity - Top level category"""
    title: str = ""
    description: str = ""
    
    def __str__(self) -> str:
        return self.title


@dataclass
class LessonEntity(Entity):
    """Lesson Entity - Belongs to Module"""
    module_id: int = None
    title: str = ""
    content: str = ""
    order: int = 1
    resources: List['ResourceEntity'] = field(default_factory=list)
    assignments: List['AssignmentEntity'] = field(default_factory=list)
    
    def add_resource(self, resource: 'ResourceEntity') -> None:
        """Add a resource to the lesson"""
        resource.lesson_id = self.id
        self.resources.append(resource)
    
    def add_assignment(self, assignment: 'AssignmentEntity') -> None:
        """Add an assignment to the lesson"""
        assignment.lesson_id = self.id
        self.assignments.append(assignment)
    
    def reorder(self, new_order: int) -> None:
        """Change lesson order"""
        if new_order < 1:
            raise ValueError("Order must be at least 1")
        self.order = new_order


@dataclass
class ModuleEntity(Entity):
    """Module Entity - Chapter of a Course"""
    course_id: int = None
    title: str = ""
    order: int = 1
    lessons: List[LessonEntity] = field(default_factory=list)
    
    def add_lesson(self, lesson: LessonEntity) -> None:
        """Add a lesson to the module"""
        lesson.module_id = self.id
        if not lesson.order:
            lesson.order = len(self.lessons) + 1
        self.lessons.append(lesson)
    
    def get_lesson_by_order(self, order: int) -> Optional[LessonEntity]:
        """Get lesson by its order"""
        for lesson in self.lessons:
            if lesson.order == order:
                return lesson
        return None
    
    def reorder(self, new_order: int) -> None:
        """Change module order"""
        if new_order < 1:
            raise ValueError("Order must be at least 1")
        self.order = new_order


@dataclass
class CourseEntity(AggregateRoot):
    """
    Course Aggregate Root
    
    A course belongs to a subject and contains modules.
    This is the main aggregate for course-related operations.
    """
    subject_id: int = None
    subject: Optional[SubjectEntity] = None
    title: str = ""
    description: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: CourseStatus = CourseStatus.UPCOMING
    modules: List[ModuleEntity] = field(default_factory=list)
    enrollments: List['EnrollmentEntity'] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.title} ({self.subject.title if self.subject else 'No Subject'})"
    
    # ==================== Status Management ====================
    
    def can_enroll(self) -> bool:
        """Check if enrollment is allowed"""
        return self.status == CourseStatus.UPCOMING
    
    def can_unenroll(self) -> bool:
        """Check if un-enrollment is allowed"""
        return self.status == CourseStatus.UPCOMING
    
    def start(self) -> None:
        """Start the course"""
        if self.status != CourseStatus.UPCOMING:
            raise ValueError(f"Cannot start course with status {self.status}")
        self.status = CourseStatus.ONGOING
    
    def complete(self) -> None:
        """Complete the course"""
        if self.status != CourseStatus.ONGOING:
            raise ValueError(f"Cannot complete course with status {self.status}")
        self.status = CourseStatus.COMPLETED
    
    # ==================== Module Management ====================
    
    def add_module(self, module: ModuleEntity) -> None:
        """Add a module to the course"""
        module.course_id = self.id
        if not module.order:
            module.order = len(self.modules) + 1
        self.modules.append(module)
    
    def remove_module(self, module_id: int) -> bool:
        """Remove a module from the course"""
        for i, module in enumerate(self.modules):
            if module.id == module_id:
                self.modules.pop(i)
                return True
        return False
    
    def get_module_by_order(self, order: int) -> Optional[ModuleEntity]:
        """Get module by its order"""
        for module in self.modules:
            if module.order == order:
                return module
        return None
    
    def get_total_lessons(self) -> int:
        """Get total number of lessons in the course"""
        return sum(len(module.lessons) for module in self.modules)
    
    # ==================== Enrollment Management ====================
    
    def get_teachers(self) -> List['EnrollmentEntity']:
        """Get all teacher enrollments"""
        from .enrollment import CourseRole
        return [e for e in self.enrollments if e.role_in_course == CourseRole.TEACHER]
    
    def get_students(self) -> List['EnrollmentEntity']:
        """Get all student enrollments"""
        from .enrollment import CourseRole
        return [e for e in self.enrollments if e.role_in_course == CourseRole.STUDENT]
    
    def get_enrollment_count(self) -> int:
        """Get total enrollment count"""
        return len(self.enrollments)
    
    # ==================== Validation ====================
    
    def validate_dates(self) -> bool:
        """Validate course dates"""
        if self.start_date and self.end_date:
            return self.start_date <= self.end_date
        return True

