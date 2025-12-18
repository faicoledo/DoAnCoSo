"""
Assessment DTOs
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


@dataclass
class QuestionDTO:
    """DTO for question data"""
    id: int
    text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    level: str
    level_display: str
    order: int
    # Note: correct_answer is not included for security (don't expose to students)


@dataclass
class QuestionWithAnswerDTO(QuestionDTO):
    """DTO for question with answer (for teachers/after submission)"""
    correct_answer: str
    explanation: str = ""


@dataclass
class AssignmentDTO:
    """DTO for assignment data"""
    id: int
    lesson_id: int
    title: str
    instructions: str
    type: str
    type_display: str
    start_at: datetime
    end_at: datetime
    time_limit: Optional[int]  # minutes
    attempts_allowed: int
    questions_count: int = 0
    is_available: bool = True


@dataclass
class AssignmentDetailDTO(AssignmentDTO):
    """DTO for assignment with questions"""
    questions: List[QuestionDTO] = field(default_factory=list)


@dataclass
class SubmitAnswerDTO:
    """DTO for submitting an answer"""
    question_id: int
    chosen_answer: str  # A, B, C, or D


@dataclass
class AttemptDetailDTO:
    """DTO for attempt detail"""
    question_id: int
    question_text: str
    chosen_answer: Optional[str]
    correct_answer: str  # Only shown after submission
    is_correct: bool
    time_spent: int  # seconds


@dataclass
class AttemptDTO:
    """DTO for attempt data"""
    id: int
    assignment_id: int
    assignment_title: str
    user_id: int
    started_at: datetime
    submitted_at: Optional[datetime]
    score: Optional[Decimal]
    status: str
    status_display: str
    details: List[AttemptDetailDTO] = field(default_factory=list)


@dataclass
class AttemptSummaryDTO:
    """DTO for attempt summary (list view)"""
    id: int
    assignment_id: int
    assignment_title: str
    started_at: datetime
    submitted_at: Optional[datetime]
    score: Optional[Decimal]
    status: str


@dataclass
class StartAttemptDTO:
    """DTO for starting an attempt"""
    assignment_id: int


@dataclass
class SubmitAttemptDTO:
    """DTO for submitting an attempt"""
    attempt_id: int
    answers: List[SubmitAnswerDTO] = field(default_factory=list)

