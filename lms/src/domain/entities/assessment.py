"""
Assessment Domain Entities (Assignments, Questions, Attempts)
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum
from decimal import Decimal

from .base import Entity, AggregateRoot


class AssignmentType(str, Enum):
    """Type of assignment"""
    QUIZ = "QUIZ"
    FILE_UPLOAD = "FILE_UPLOAD"
    
    @property
    def display_name(self) -> str:
        names = {
            "QUIZ": "Quiz",
            "FILE_UPLOAD": "Nộp file"
        }
        return names.get(self.value, self.value)


class QuestionLevel(str, Enum):
    """Difficulty level of question"""
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    
    @property
    def display_name(self) -> str:
        names = {
            "EASY": "Dễ",
            "MEDIUM": "Trung bình",
            "HARD": "Khó"
        }
        return names.get(self.value, self.value)


class AnswerChoice(str, Enum):
    """Answer choices for multiple choice questions"""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class AttemptStatus(str, Enum):
    """Status of an attempt"""
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    
    @property
    def display_name(self) -> str:
        names = {
            "IN_PROGRESS": "Đang làm",
            "SUBMITTED": "Đã nộp"
        }
        return names.get(self.value, self.value)


@dataclass
class QuestionEntity(Entity):
    """Question Entity"""
    assignment_id: Optional[int] = None
    question_bank_id: Optional[int] = None
    text: str = ""
    option_a: str = ""
    option_b: str = ""
    option_c: str = ""
    option_d: str = ""
    correct_answer: AnswerChoice = AnswerChoice.A
    explanation: str = ""
    level: QuestionLevel = QuestionLevel.MEDIUM
    order: int = 1
    
    def __str__(self) -> str:
        text_preview = self.text[:50] + '...' if len(self.text) > 50 else self.text
        return f"Q: {text_preview}"
    
    def get_option(self, choice: AnswerChoice) -> str:
        """Get option text by choice"""
        options = {
            AnswerChoice.A: self.option_a,
            AnswerChoice.B: self.option_b,
            AnswerChoice.C: self.option_c,
            AnswerChoice.D: self.option_d,
        }
        return options.get(choice, "")
    
    def is_correct_answer(self, answer: AnswerChoice) -> bool:
        """Check if answer is correct"""
        return answer == self.correct_answer
    
    def get_all_options(self) -> dict:
        """Get all options as a dictionary"""
        return {
            "A": self.option_a,
            "B": self.option_b,
            "C": self.option_c,
            "D": self.option_d,
        }


@dataclass
class AttemptDetailEntity(Entity):
    """Detail of an answer in an attempt"""
    attempt_id: int = None
    question_id: int = None
    chosen_answer: Optional[AnswerChoice] = None
    is_correct: bool = False
    time_spent: int = 0  # In seconds
    
    def __str__(self) -> str:
        return f"Attempt {self.attempt_id} - Q{self.question_id} ({'✓' if self.is_correct else '✗'})"


@dataclass
class AttemptEntity(Entity):
    """
    Attempt Entity
    
    Represents a user's attempt at an assignment.
    """
    user_id: int = None
    assignment_id: int = None
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    score: Optional[Decimal] = None
    status: AttemptStatus = AttemptStatus.IN_PROGRESS
    details: List[AttemptDetailEntity] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"User {self.user_id} - Assignment {self.assignment_id} ({self.status.display_name})"
    
    def submit(self) -> None:
        """Submit the attempt"""
        if self.status == AttemptStatus.SUBMITTED:
            raise ValueError("Attempt already submitted")
        self.status = AttemptStatus.SUBMITTED
        self.submitted_at = datetime.now()
    
    def calculate_score(self, total_points: Decimal = None, max_score: Decimal = Decimal('100')) -> Decimal:
        """
        Calculate score based on correct answers and question points
        
        Args:
            total_points: Tổng điểm tất cả câu hỏi
            max_score: Điểm tối đa của bài tập
        
        Formula: (earned_points / total_points) * max_score
        """
        if not self.details:
            return Decimal('0')
        
        # Tính điểm đạt được
        earned_points = sum(
            d.question.points for d in self.details 
            if d.is_correct and d.question
        )
        
        if not total_points or total_points == 0:
            # Fallback: tính từ các câu đã trả lời
            total_points = sum(d.question.points for d in self.details if d.question)
        
        if total_points == 0:
            return Decimal('0')
        
        self.score = (earned_points / total_points * max_score).quantize(Decimal('0.01'))
        return self.score
    
    def get_duration(self) -> Optional[int]:
        """Get attempt duration in seconds"""
        if self.started_at and self.submitted_at:
            delta = self.submitted_at - self.started_at
            return int(delta.total_seconds())
        return None
    
    def is_passed(self, passing_score: Decimal = Decimal('50')) -> bool:
        """Check if attempt passed"""
        return self.score is not None and self.score >= passing_score


@dataclass 
class AssignmentEntity(AggregateRoot):
    """
    Assignment Aggregate Root
    
    Represents an assignment or quiz attached to a lesson.
    """
    lesson_id: int = None
    title: str = ""
    instructions: str = ""
    type: AssignmentType = AssignmentType.QUIZ
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    time_limit: Optional[int] = None  # In minutes
    attempts_allowed: int = 1
    questions: List[QuestionEntity] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.title} ({self.type.display_name})"
    
    # ==================== Question Management ====================
    
    def add_question(self, question: QuestionEntity) -> None:
        """Add a question to the assignment"""
        question.assignment_id = self.id
        if not question.order:
            question.order = len(self.questions) + 1
        self.questions.append(question)
    
    def remove_question(self, question_id: int) -> bool:
        """Remove a question from the assignment"""
        for i, question in enumerate(self.questions):
            if question.id == question_id:
                self.questions.pop(i)
                return True
        return False
    
    def get_question_count(self) -> int:
        """Get total number of questions"""
        return len(self.questions)
    
    # ==================== Availability Checks ====================
    
    def is_available(self) -> bool:
        """Check if assignment is currently available"""
        now = datetime.now()
        
        if self.start_at and now < self.start_at:
            return False
        if self.end_at and now > self.end_at:
            return False
        
        return True
    
    def is_upcoming(self) -> bool:
        """Check if assignment hasn't started yet"""
        if not self.start_at:
            return False
        return datetime.now() < self.start_at
    
    def is_expired(self) -> bool:
        """Check if assignment has ended"""
        if not self.end_at:
            return False
        return datetime.now() > self.end_at
    
    # ==================== Attempt Validation ====================
    
    def can_user_attempt(self, user_attempt_count: int) -> bool:
        """Check if user can make another attempt"""
        if not self.is_available():
            return False
        return user_attempt_count < self.attempts_allowed
    
    def get_time_limit_seconds(self) -> Optional[int]:
        """Get time limit in seconds"""
        if self.time_limit:
            return self.time_limit * 60
        return None


@dataclass
class QuestionBankEntity(Entity):
    """Question Bank Entity - Pool of questions for a course"""
    course_id: int = None
    topic: str = ""
    level: Optional[QuestionLevel] = None
    questions: List[QuestionEntity] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.topic} ({self.level.display_name if self.level else 'Mixed'})"
    
    def add_question(self, question: QuestionEntity) -> None:
        """Add a question to the bank"""
        question.question_bank_id = self.id
        self.questions.append(question)
    
    def get_random_questions(self, count: int) -> List[QuestionEntity]:
        """Get random questions from the bank"""
        import random
        if count >= len(self.questions):
            return self.questions.copy()
        return random.sample(self.questions, count)

