"""
Activity Log Use Cases

Các use case cho chức năng Activity Log:
- LogActivityUseCase: Ghi log hành động người dùng
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

from django.db import transaction

from ...infrastructure.persistence.models.activity import UserActivityLogModel


# ==================== DTOs ====================

@dataclass
class LogActivityInput:
    """Input DTO cho LogActivityUseCase"""
    user_id: int
    action_type: str  # ActionType
    target_type: Optional[str] = None  # Ví dụ: 'lesson', 'assignment', 'attempt'
    target_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None  # Thông tin bổ sung: điểm số, attempt_id, etc.


@dataclass
class ActivityLogDTO:
    """Output DTO cho ActivityLog"""
    id: int
    user_id: int
    user_full_name: str
    user_username: str
    action_type: str
    target_type: Optional[str]
    target_id: Optional[int]
    metadata: Dict[str, Any]
    timestamp: datetime
    
    @classmethod
    def from_model(cls, log: UserActivityLogModel) -> 'ActivityLogDTO':
        return cls(
            id=log.id,
            user_id=log.user_id,
            user_full_name=log.user.profile.full_name if hasattr(log.user, 'profile') else log.user.username,
            user_username=log.user.username,
            action_type=log.action_type,
            target_type=log.target_type,
            target_id=log.target_id,
            metadata=log.metadata or {},
            timestamp=log.timestamp,
        )


@dataclass
class ListActivityLogsInput:
    """Input DTO cho ListActivityLogsUseCase"""
    user_id: int
    action_type: Optional[str] = None
    target_type: Optional[str] = None
    limit: Optional[int] = None
    offset: int = 0


# ==================== USE CASES ====================

class LogActivityUseCase:
    """
    Ghi log hành động người dùng
    
    Sử dụng để ghi lại các hành động chính:
    - VIEW_LESSON: Xem bài học
    - START_ATTEMPT: Bắt đầu làm bài
    - SUBMIT_ATTEMPT: Nộp bài
    - VIEW_RESULT: Xem kết quả bài làm
    """
    
    @transaction.atomic
    def execute(self, input_dto: LogActivityInput) -> UserActivityLogModel:
        """
        Ghi log hành động
        
        Returns:
            UserActivityLogModel đã tạo
        """
        # Validate action_type
        valid_actions = [choice[0] for choice in UserActivityLogModel.ActionType.choices]
        if input_dto.action_type not in valid_actions:
            raise ValueError(f"action_type không hợp lệ: {input_dto.action_type}")
        
        # Tạo log
        log = UserActivityLogModel.objects.create(
            user_id=input_dto.user_id,
            action_type=input_dto.action_type,
            target_type=input_dto.target_type,
            target_id=input_dto.target_id,
            metadata=input_dto.metadata or {},
        )
        
        return log


class ListActivityLogsUseCase:
    """
    Lấy danh sách activity logs của user
    
    User chỉ xem được log của chính mình (trừ admin).
    """
    
    def execute(self, input_dto: ListActivityLogsInput) -> List[ActivityLogDTO]:
        """
        Lấy danh sách activity logs
        
        Returns:
            List các ActivityLogDTO
        """
        queryset = UserActivityLogModel.objects.filter(user_id=input_dto.user_id)
        
        # Lọc theo action_type nếu có
        if input_dto.action_type:
            queryset = queryset.filter(action_type=input_dto.action_type)
        
        # Lọc theo target_type nếu có
        if input_dto.target_type:
            queryset = queryset.filter(target_type=input_dto.target_type)
        
        # Sắp xếp theo thời gian (mới nhất trước)
        queryset = queryset.select_related('user', 'user__profile').order_by('-timestamp')
        
        # Pagination
        if input_dto.offset:
            queryset = queryset[input_dto.offset:]
        if input_dto.limit:
            queryset = queryset[:input_dto.limit]
        
        return [ActivityLogDTO.from_model(log) for log in queryset]



