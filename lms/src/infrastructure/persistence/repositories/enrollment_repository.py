"""
Django Enrollment Repository Implementation
"""
from typing import List, Optional
from django.db import transaction

from ....domain.interfaces.repositories import IEnrollmentRepository
from ....domain.entities.enrollment import EnrollmentEntity, CourseRole
from ..models.enrollment import EnrollmentModel


class DjangoEnrollmentRepository(IEnrollmentRepository):
    """
    Django ORM implementation of IEnrollmentRepository
    """
    
    def _to_entity(self, enrollment: EnrollmentModel) -> EnrollmentEntity:
        """Convert Enrollment model to entity"""
        return EnrollmentEntity(
            id=enrollment.id,
            user_id=enrollment.user_id,
            course_id=enrollment.course_id,
            role_in_course=CourseRole(enrollment.role_in_course),
            joined_at=enrollment.joined_at,
        )
    
    @transaction.atomic
    def save(self, entity: EnrollmentEntity) -> None:
        """Save enrollment entity"""
        if entity.id:
            enrollment = EnrollmentModel.objects.get(pk=entity.id)
        else:
            enrollment = EnrollmentModel()
        
        enrollment.user_id = entity.user_id
        enrollment.course_id = entity.course_id
        enrollment.role_in_course = entity.role_in_course.value
        enrollment.save()
        
        entity.id = enrollment.id
        entity.joined_at = enrollment.joined_at
    
    def delete(self, entity_id: int) -> bool:
        """Delete enrollment by ID"""
        try:
            enrollment = EnrollmentModel.objects.get(pk=entity_id)
            enrollment.delete()
            return True
        except EnrollmentModel.DoesNotExist:
            return False
    
    def find_by_id(self, enrollment_id: int) -> Optional[EnrollmentEntity]:
        """Find enrollment by ID"""
        try:
            enrollment = EnrollmentModel.objects.get(pk=enrollment_id)
            return self._to_entity(enrollment)
        except EnrollmentModel.DoesNotExist:
            return None
    
    def find_by_user_and_course(self, user_id: int, course_id: int) -> Optional[EnrollmentEntity]:
        """Find enrollment by user and course"""
        try:
            enrollment = EnrollmentModel.objects.get(user_id=user_id, course_id=course_id)
            return self._to_entity(enrollment)
        except EnrollmentModel.DoesNotExist:
            return None
    
    def find_by_user(self, user_id: int) -> List[EnrollmentEntity]:
        """Find all enrollments for a user"""
        enrollments = EnrollmentModel.objects.filter(user_id=user_id).select_related('course')
        return [self._to_entity(e) for e in enrollments]
    
    def find_by_course(self, course_id: int) -> List[EnrollmentEntity]:
        """Find all enrollments for a course"""
        enrollments = EnrollmentModel.objects.filter(course_id=course_id).select_related('user')
        return [self._to_entity(e) for e in enrollments]
    
    def exists(self, user_id: int, course_id: int) -> bool:
        """Check if enrollment exists"""
        return EnrollmentModel.objects.filter(user_id=user_id, course_id=course_id).exists()
    
    def count_by_course(self, course_id: int) -> int:
        """Count enrollments for a course"""
        return EnrollmentModel.objects.filter(course_id=course_id).count()

