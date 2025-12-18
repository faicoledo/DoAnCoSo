"""
Django Course Repository Implementation
"""
from typing import List, Optional
from django.db import transaction

from ....domain.interfaces.repositories import ICourseRepository
from ....domain.entities.course import CourseEntity, SubjectEntity, ModuleEntity, LessonEntity, CourseStatus
from ..models.course import CourseModel, SubjectModel, ModuleModel, LessonModel


class DjangoCourseRepository(ICourseRepository):
    """
    Django ORM implementation of ICourseRepository
    """
    
    def _subject_to_entity(self, subject: SubjectModel) -> SubjectEntity:
        """Convert Subject model to entity"""
        return SubjectEntity(
            id=subject.id,
            title=subject.title,
            description=subject.description or "",
            created_at=subject.created_at,
            updated_at=subject.updated_at,
        )
    
    def _lesson_to_entity(self, lesson: LessonModel) -> LessonEntity:
        """Convert Lesson model to entity"""
        return LessonEntity(
            id=lesson.id,
            module_id=lesson.module_id,
            title=lesson.title,
            content=lesson.content or "",
            order=lesson.order,
            created_at=lesson.created_at,
            updated_at=lesson.updated_at,
        )
    
    def _module_to_entity(self, module: ModuleModel, include_lessons: bool = False) -> ModuleEntity:
        """Convert Module model to entity"""
        lessons = []
        if include_lessons:
            lessons = [self._lesson_to_entity(l) for l in module.lessons.all()]
        
        return ModuleEntity(
            id=module.id,
            course_id=module.course_id,
            title=module.title,
            order=module.order,
            lessons=lessons,
            created_at=module.created_at,
            updated_at=module.updated_at,
        )
    
    def _to_entity(self, course: CourseModel, include_modules: bool = False) -> CourseEntity:
        """Convert Course model to entity"""
        subject = None
        if course.subject:
            subject = self._subject_to_entity(course.subject)
        
        modules = []
        if include_modules:
            modules = [
                self._module_to_entity(m, include_lessons=True) 
                for m in course.modules.prefetch_related('lessons').all()
            ]
        
        return CourseEntity(
            id=course.id,
            subject_id=course.subject_id,
            subject=subject,
            title=course.title,
            description=course.description or "",
            start_date=course.start_date,
            end_date=course.end_date,
            status=CourseStatus(course.status),
            modules=modules,
            created_at=course.created_at,
            updated_at=course.updated_at,
        )
    
    @transaction.atomic
    def save(self, entity: CourseEntity) -> None:
        """Save course entity"""
        if entity.id:
            course = CourseModel.objects.get(pk=entity.id)
        else:
            course = CourseModel()
        
        course.subject_id = entity.subject_id
        course.title = entity.title
        course.description = entity.description
        course.start_date = entity.start_date
        course.end_date = entity.end_date
        course.status = entity.status.value
        course.save()
        
        entity.id = course.id
    
    def delete(self, entity_id: int) -> bool:
        """Delete course by ID"""
        try:
            course = CourseModel.objects.get(pk=entity_id)
            course.delete()
            return True
        except CourseModel.DoesNotExist:
            return False
    
    def find_by_id(self, course_id: int) -> Optional[CourseEntity]:
        """Find course by ID"""
        try:
            course = CourseModel.objects.select_related('subject').get(pk=course_id)
            return self._to_entity(course)
        except CourseModel.DoesNotExist:
            return None
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[CourseEntity]:
        """Get all courses"""
        courses = CourseModel.objects.select_related('subject').all()[offset:offset + limit]
        return [self._to_entity(c) for c in courses]
    
    def find_by_status(self, status: str) -> List[CourseEntity]:
        """Find courses by status"""
        courses = CourseModel.objects.select_related('subject').filter(status=status)
        return [self._to_entity(c) for c in courses]
    
    def find_by_subject(self, subject_id: int) -> List[CourseEntity]:
        """Find courses by subject"""
        courses = CourseModel.objects.select_related('subject').filter(subject_id=subject_id)
        return [self._to_entity(c) for c in courses]
    
    def find_with_modules(self, course_id: int) -> Optional[CourseEntity]:
        """Find course with all modules and lessons"""
        try:
            course = CourseModel.objects.select_related('subject').prefetch_related(
                'modules__lessons'
            ).get(pk=course_id)
            return self._to_entity(course, include_modules=True)
        except CourseModel.DoesNotExist:
            return None

