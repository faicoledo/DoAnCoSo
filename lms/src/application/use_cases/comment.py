"""
Comment Use Cases

Các use case cho chức năng Comment:
- CreateCommentUseCase: Tạo comment vào lesson hoặc assignment
- ListCommentsUseCase: Lấy danh sách comment theo target
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from django.db import transaction

from ...infrastructure.persistence.models.communication import CommentModel
from ...infrastructure.persistence.models.enrollment import EnrollmentModel
from ...infrastructure.persistence.models.course import LessonModel
from ...infrastructure.persistence.models.assessment import AssignmentModel


# ==================== DTOs ====================

@dataclass
class CreateCommentInput:
    """Input DTO cho CreateCommentUseCase"""
    user_id: int
    content: str
    target_type: str  # 'LESSON' hoặc 'ASSIGNMENT'
    target_id: int
    parent_id: Optional[int] = None  # ID của comment cha (nếu là reply)


@dataclass
class CommentDTO:
    """Output DTO cho Comment"""
    id: int
    user_id: int
    user_full_name: str
    user_username: str
    content: str
    target_type: str
    target_id: int
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    replies_count: int = 0
    
    @classmethod
    def from_model(cls, comment: CommentModel) -> 'CommentDTO':
        return cls(
            id=comment.id,
            user_id=comment.user_id,
            user_full_name=comment.user.profile.full_name if hasattr(comment.user, 'profile') else comment.user.username,
            user_username=comment.user.username,
            content=comment.content,
            target_type=comment.target_type,
            target_id=comment.target_id,
            parent_id=comment.parent_id if comment.parent else None,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            replies_count=comment.replies.count() if hasattr(comment, 'replies') else 0,
        )


@dataclass
class ListCommentsInput:
    """Input DTO cho ListCommentsUseCase"""
    target_type: str
    target_id: int
    include_replies: bool = True  # Có bao gồm replies không


# ==================== USE CASES ====================

class CreateCommentUseCase:
    """
    Tạo comment vào lesson hoặc assignment
    
    Học viên và giáo viên đều có thể comment.
    """
    
    @transaction.atomic
    def execute(self, input_dto: CreateCommentInput) -> CommentModel:
        """
        Tạo comment mới
        
        Returns:
            CommentModel đã tạo
        """
        # Validate target_type
        if input_dto.target_type not in [CommentModel.TargetType.LESSON, CommentModel.TargetType.ASSIGNMENT]:
            raise ValueError(f"target_type phải là 'LESSON' hoặc 'ASSIGNMENT', nhận được: {input_dto.target_type}")
        
        # Validate target tồn tại
        if input_dto.target_type == CommentModel.TargetType.LESSON:
            try:
                lesson = LessonModel.objects.select_related('module__course').get(pk=input_dto.target_id)
                course_id = lesson.module.course_id
            except LessonModel.DoesNotExist:
                raise ValueError(f"Lesson {input_dto.target_id} không tồn tại")
        else:  # ASSIGNMENT
            try:
                assignment = AssignmentModel.objects.select_related('lesson__module__course').get(pk=input_dto.target_id)
                course_id = assignment.lesson.module.course_id
            except AssignmentModel.DoesNotExist:
                raise ValueError(f"Assignment {input_dto.target_id} không tồn tại")
        
        # Kiểm tra user có enroll trong khóa học không
        if not EnrollmentModel.objects.filter(
            user_id=input_dto.user_id,
            course_id=course_id
        ).exists():
            # Kiểm tra xem có phải admin không
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(pk=input_dto.user_id)
                if not (user.is_staff or user.is_superuser):
                    raise ValueError("Bạn phải enroll trong khóa học để có thể comment")
            except User.DoesNotExist:
                raise ValueError("User không tồn tại")
        
        # Validate parent comment nếu có
        parent = None
        if input_dto.parent_id:
            try:
                parent = CommentModel.objects.get(pk=input_dto.parent_id)
                # Kiểm tra parent có cùng target không
                if parent.target_type != input_dto.target_type or parent.target_id != input_dto.target_id:
                    raise ValueError("Comment cha phải cùng target với comment con")
            except CommentModel.DoesNotExist:
                raise ValueError(f"Parent comment {input_dto.parent_id} không tồn tại")
        
        # Tạo comment
        comment = CommentModel.objects.create(
            user_id=input_dto.user_id,
            content=input_dto.content,
            target_type=input_dto.target_type,
            target_id=input_dto.target_id,
            parent=parent,
            # Backward compatibility: set lesson nếu target_type là LESSON
            lesson_id=input_dto.target_id if input_dto.target_type == CommentModel.TargetType.LESSON else None,
        )
        
        return comment


class ListCommentsUseCase:
    """
    Lấy danh sách comment theo target (lesson hoặc assignment)
    """
    
    def execute(self, input_dto: ListCommentsInput) -> List[CommentDTO]:
        """
        Lấy danh sách comment
        
        Returns:
            List các CommentDTO (chỉ top-level comments, không bao gồm replies)
        """
        # Validate target_type
        if input_dto.target_type not in [CommentModel.TargetType.LESSON, CommentModel.TargetType.ASSIGNMENT]:
            raise ValueError(f"target_type phải là 'LESSON' hoặc 'ASSIGNMENT', nhận được: {input_dto.target_type}")
        
        # Lấy tất cả comments của target (chỉ top-level, không có parent)
        queryset = CommentModel.objects.filter(
            target_type=input_dto.target_type,
            target_id=input_dto.target_id,
            parent__isnull=True  # Chỉ lấy top-level comments
        ).select_related('user', 'user__profile').prefetch_related('replies').order_by('-created_at')
        
        comments = [CommentDTO.from_model(c) for c in queryset]
        
        # Nếu include_replies, thêm replies vào mỗi comment
        if input_dto.include_replies:
            for comment_dto in comments:
                # Lấy replies của comment này
                replies = CommentModel.objects.filter(
                    parent_id=comment_dto.id
                ).select_related('user', 'user__profile').order_by('created_at')
                comment_dto.replies = [CommentDTO.from_model(r) for r in replies]
        
        return comments



