"""
Assessment Use Cases

Các use case cho chức năng Quiz:
- CreateAssignment: Tạo bài tập (chỉ giáo viên)
- CreateQuestion / UpdateQuestion / DeleteQuestion: Quản lý câu hỏi
- ImportQuestionsFromExcel: Import câu hỏi từ Excel
- StartAttempt: Bắt đầu làm bài
- SubmitAttempt: Nộp bài và chấm điểm
- GetAttemptResult: Xem kết quả
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from ...infrastructure.persistence.models.assessment import (
    AssignmentModel, QuestionModel, AttemptModel, AttemptDetailModel
)
from ...infrastructure.persistence.models.enrollment import EnrollmentModel
from ...infrastructure.persistence.models.course import LessonModel


# ==================== DTOs ====================

@dataclass
class CreateAssignmentInput:
    lesson_id: int
    title: str
    user_id: int
    instructions: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    time_limit: Optional[int] = None
    attempts_allowed: int = 1
    max_score: Decimal = Decimal('100')
    shuffle_questions: bool = False
    shuffle_answers: bool = False
    show_result: bool = True


@dataclass
class CreateQuestionInput:
    assignment_id: int
    user_id: int
    text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str  # A, B, C, D
    explanation: Optional[str] = None
    points: Decimal = Decimal('1')
    order: Optional[int] = None


@dataclass
class UpdateQuestionInput:
    question_id: int
    user_id: int
    text: Optional[str] = None
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points: Optional[Decimal] = None
    order: Optional[int] = None


@dataclass
class ImportQuestionsInput:
    assignment_id: int
    user_id: int
    questions_data: List[Dict[str, Any]]  # Parsed from Excel


@dataclass
class ImportQuestionsResult:
    total_rows: int
    success_count: int
    error_rows: List[Dict[str, Any]]  # [{'row': 1, 'error': 'message'}]


@dataclass
class StartAttemptInput:
    assignment_id: int
    user_id: int


@dataclass
class QuestionForAttempt:
    """Câu hỏi cho học viên làm bài (không có đáp án đúng)"""
    id: int
    order: int
    text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    points: Decimal


@dataclass
class StartAttemptResult:
    attempt_id: int
    assignment_title: str
    time_limit: Optional[int]
    started_at: datetime
    questions: List[QuestionForAttempt]


@dataclass
class AnswerInput:
    question_id: int
    chosen_answer: str  # A, B, C, D


@dataclass
class SubmitAttemptInput:
    attempt_id: int
    user_id: int
    answers: List[AnswerInput]


@dataclass
class SubmitAttemptResult:
    attempt_id: int
    submitted_at: datetime
    score: Decimal
    total_questions: int
    correct_count: int


@dataclass
class QuestionResult:
    """Kết quả từng câu hỏi"""
    question_id: int
    order: int
    text: str
    chosen_answer: Optional[str]
    correct_answer: str
    is_correct: bool
    explanation: Optional[str]


@dataclass
class GetAttemptResultOutput:
    attempt_id: int
    assignment_title: str
    started_at: datetime
    submitted_at: Optional[datetime]
    score: Optional[Decimal]
    total_questions: int
    correct_count: int
    questions: List[QuestionResult]


# ==================== EXCEPTIONS ====================

class AssessmentException(Exception):
    """Base exception for assessment"""
    pass


class NotTeacherException(AssessmentException):
    """User is not a teacher for this course"""
    pass


class NotEnrolledException(AssessmentException):
    """User is not enrolled in the course"""
    pass


class AssignmentNotFoundException(AssessmentException):
    """Assignment not found"""
    pass


class QuestionNotFoundException(AssessmentException):
    """Question not found"""
    pass


class AttemptNotFoundException(AssessmentException):
    """Attempt not found"""
    pass


class AssignmentNotOpenException(AssessmentException):
    """Assignment is not open for attempts"""
    pass


class MaxAttemptsReachedException(AssessmentException):
    """User has reached max attempts allowed"""
    pass


class AttemptAlreadySubmittedException(AssessmentException):
    """Attempt has already been submitted"""
    pass


class AttemptInProgressException(AssessmentException):
    """User already has an attempt in progress"""
    pass


# ==================== HELPER FUNCTIONS ====================

def is_teacher_of_course(user_id: int, course_id: int) -> bool:
    """
    Kiểm tra user có phải giáo viên của khóa học không
    
    Admin (is_staff hoặc is_superuser) có toàn quyền.
    """
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(pk=user_id)
        # Admin có toàn quyền
        if user.is_staff or user.is_superuser:
            return True
    except User.DoesNotExist:
        pass
    
    # Kiểm tra enrollment với vai trò TEACHER/TA
    return EnrollmentModel.objects.filter(
        user_id=user_id,
        course_id=course_id,
        role_in_course__in=['TEACHER', 'TA']
    ).exists()


def is_enrolled_in_course(user_id: int, course_id: int) -> bool:
    """
    Kiểm tra user có enroll trong khóa học không
    
    Admin (is_staff hoặc is_superuser) có toàn quyền.
    """
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(pk=user_id)
        # Admin có toàn quyền
        if user.is_staff or user.is_superuser:
            return True
    except User.DoesNotExist:
        pass
    
    return EnrollmentModel.objects.filter(
        user_id=user_id,
        course_id=course_id
    ).exists()


def get_course_id_from_assignment(assignment_id: int) -> Optional[int]:
    """Lấy course_id từ assignment"""
    try:
        assignment = AssignmentModel.objects.select_related(
            'lesson__module__course'
        ).get(pk=assignment_id)
        return assignment.lesson.module.course_id
    except AssignmentModel.DoesNotExist:
        return None


def get_course_id_from_lesson(lesson_id: int) -> Optional[int]:
    """Lấy course_id từ lesson"""
    try:
        lesson = LessonModel.objects.select_related(
            'module__course'
        ).get(pk=lesson_id)
        return lesson.module.course_id
    except LessonModel.DoesNotExist:
        return None


# ==================== USE CASES ====================

class CreateAssignmentUseCase:
    """
    Tạo bài tập mới
    
    Chỉ giáo viên/TA của khóa học mới được tạo.
    """
    
    def execute(self, input_dto: CreateAssignmentInput) -> AssignmentModel:
        # Kiểm tra lesson tồn tại
        try:
            lesson = LessonModel.objects.select_related(
                'module__course'
            ).get(pk=input_dto.lesson_id)
        except LessonModel.DoesNotExist:
            raise AssignmentNotFoundException(f"Lesson {input_dto.lesson_id} không tồn tại")
        
        course_id = lesson.module.course_id
        
        # Kiểm tra quyền giáo viên
        if not is_teacher_of_course(input_dto.user_id, course_id):
            raise NotTeacherException("Bạn không có quyền tạo bài tập cho khóa học này")
        
        # Tạo assignment
        assignment = AssignmentModel.objects.create(
            lesson=lesson,
            title=input_dto.title,
            instructions=input_dto.instructions,
            type='QUIZ',
            start_at=input_dto.start_at or timezone.now(),
            end_at=input_dto.end_at or (timezone.now() + timezone.timedelta(days=7)),
            time_limit=input_dto.time_limit,
            attempts_allowed=input_dto.attempts_allowed,
            max_score=input_dto.max_score,
            shuffle_questions=input_dto.shuffle_questions,
            shuffle_answers=input_dto.shuffle_answers,
            show_result=input_dto.show_result,
        )
        
        # Gửi notification cho học viên
        try:
            from .notification import notify_students_on_new_assignment
            notify_students_on_new_assignment(
                assignment_id=assignment.id,
                course_id=course_id,
            )
        except Exception:
            pass  # Bỏ qua lỗi notification để không ảnh hưởng đến flow chính
        
        return assignment


class CreateQuestionUseCase:
    """
    Tạo câu hỏi mới cho bài tập
    
    Chỉ giáo viên/TA mới được tạo.
    """
    
    def execute(self, input_dto: CreateQuestionInput) -> QuestionModel:
        # Kiểm tra assignment tồn tại
        course_id = get_course_id_from_assignment(input_dto.assignment_id)
        if course_id is None:
            raise AssignmentNotFoundException(f"Assignment {input_dto.assignment_id} không tồn tại")
        
        # Kiểm tra quyền
        if not is_teacher_of_course(input_dto.user_id, course_id):
            raise NotTeacherException("Bạn không có quyền thêm câu hỏi")
        
        # Validate correct_answer
        if input_dto.correct_answer not in ['A', 'B', 'C', 'D']:
            raise AssessmentException("Đáp án đúng phải là A, B, C hoặc D")
        
        # Tính order nếu không truyền
        order = input_dto.order
        if order is None:
            max_order = QuestionModel.objects.filter(
                assignment_id=input_dto.assignment_id
            ).aggregate(max_order=models.Max('order'))['max_order']
            order = (max_order or 0) + 1
        
        # Tạo question
        question = QuestionModel.objects.create(
            assignment_id=input_dto.assignment_id,
            text=input_dto.text,
            option_a=input_dto.option_a,
            option_b=input_dto.option_b,
            option_c=input_dto.option_c,
            option_d=input_dto.option_d,
            correct_answer=input_dto.correct_answer,
            explanation=input_dto.explanation,
            points=input_dto.points,
            order=order,
        )
        
        return question


class UpdateQuestionUseCase:
    """
    Cập nhật câu hỏi
    """
    
    def execute(self, input_dto: UpdateQuestionInput) -> QuestionModel:
        # Lấy question
        try:
            question = QuestionModel.objects.select_related(
                'assignment__lesson__module__course'
            ).get(pk=input_dto.question_id)
        except QuestionModel.DoesNotExist:
            raise QuestionNotFoundException(f"Question {input_dto.question_id} không tồn tại")
        
        course_id = question.assignment.lesson.module.course_id
        
        # Kiểm tra quyền
        if not is_teacher_of_course(input_dto.user_id, course_id):
            raise NotTeacherException("Bạn không có quyền sửa câu hỏi")
        
        # Cập nhật các field
        if input_dto.text is not None:
            question.text = input_dto.text
        if input_dto.option_a is not None:
            question.option_a = input_dto.option_a
        if input_dto.option_b is not None:
            question.option_b = input_dto.option_b
        if input_dto.option_c is not None:
            question.option_c = input_dto.option_c
        if input_dto.option_d is not None:
            question.option_d = input_dto.option_d
        if input_dto.correct_answer is not None:
            if input_dto.correct_answer not in ['A', 'B', 'C', 'D']:
                raise AssessmentException("Đáp án đúng phải là A, B, C hoặc D")
            question.correct_answer = input_dto.correct_answer
        if input_dto.explanation is not None:
            question.explanation = input_dto.explanation
        if input_dto.points is not None:
            question.points = input_dto.points
        if input_dto.order is not None:
            question.order = input_dto.order
        
        question.save()
        return question


class DeleteQuestionUseCase:
    """
    Xóa câu hỏi
    """
    
    def execute(self, question_id: int, user_id: int) -> bool:
        # Lấy question
        try:
            question = QuestionModel.objects.select_related(
                'assignment__lesson__module__course'
            ).get(pk=question_id)
        except QuestionModel.DoesNotExist:
            raise QuestionNotFoundException(f"Question {question_id} không tồn tại")
        
        course_id = question.assignment.lesson.module.course_id
        
        # Kiểm tra quyền
        if not is_teacher_of_course(user_id, course_id):
            raise NotTeacherException("Bạn không có quyền xóa câu hỏi")
        
        question.delete()
        return True


class ImportQuestionsFromExcelUseCase:
    """
    Import câu hỏi từ dữ liệu Excel đã parse
    
    Mỗi row gồm: text, A, B, C, D, correct, explanation (optional), points (optional)
    """
    
    @transaction.atomic
    def execute(self, input_dto: ImportQuestionsInput) -> ImportQuestionsResult:
        # Kiểm tra assignment
        course_id = get_course_id_from_assignment(input_dto.assignment_id)
        if course_id is None:
            raise AssignmentNotFoundException(f"Assignment {input_dto.assignment_id} không tồn tại")
        
        # Kiểm tra quyền
        if not is_teacher_of_course(input_dto.user_id, course_id):
            raise NotTeacherException("Bạn không có quyền import câu hỏi")
        
        # Lấy max order hiện tại
        max_order = QuestionModel.objects.filter(
            assignment_id=input_dto.assignment_id
        ).aggregate(max_order=models.Max('order'))['max_order'] or 0
        
        total_rows = len(input_dto.questions_data)
        success_count = 0
        error_rows = []
        
        for idx, row_data in enumerate(input_dto.questions_data, start=1):
            try:
                # Validate required fields
                text = row_data.get('text', '').strip()
                option_a = row_data.get('A', '').strip()
                option_b = row_data.get('B', '').strip()
                option_c = row_data.get('C', '').strip()
                option_d = row_data.get('D', '').strip()
                correct = row_data.get('correct', '').strip().upper()
                explanation = row_data.get('explanation', '').strip() or None
                
                # Parse points (optional, mặc định 1)
                points_str = row_data.get('points', '').strip()
                if points_str:
                    try:
                        points = Decimal(str(points_str))
                        if points < 0:
                            raise ValueError("Điểm phải >= 0")
                    except (ValueError, TypeError):
                        # Nếu không parse được, dùng mặc định
                        points = Decimal('1')
                else:
                    points = Decimal('1')
                
                # Validate
                if not text:
                    raise ValueError("Thiếu nội dung câu hỏi")
                if not option_a or not option_b or not option_c or not option_d:
                    raise ValueError("Thiếu đáp án A, B, C hoặc D")
                if correct not in ['A', 'B', 'C', 'D']:
                    raise ValueError(f"Đáp án đúng '{correct}' không hợp lệ (phải là A/B/C/D)")
                
                # Tạo question
                max_order += 1
                QuestionModel.objects.create(
                    assignment_id=input_dto.assignment_id,
                    text=text,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    correct_answer=correct,
                    explanation=explanation,
                    points=points,
                    order=max_order,
                )
                success_count += 1
                
            except Exception as e:
                error_rows.append({
                    'row': idx,
                    'error': str(e),
                    'data': row_data,
                })
        
        return ImportQuestionsResult(
            total_rows=total_rows,
            success_count=success_count,
            error_rows=error_rows,
        )


class StartAttemptUseCase:
    """
    Bắt đầu làm bài
    
    Kiểm tra:
    - User đã enroll trong course
    - Assignment đang mở (trong khoảng start_at - end_at)
    - Chưa đạt số lần làm tối đa
    - Không có attempt đang IN_PROGRESS
    """
    
    def execute(self, input_dto: StartAttemptInput) -> StartAttemptResult:
        # Lấy assignment
        try:
            assignment = AssignmentModel.objects.select_related(
                'lesson__module__course'
            ).get(pk=input_dto.assignment_id)
        except AssignmentModel.DoesNotExist:
            raise AssignmentNotFoundException(f"Assignment {input_dto.assignment_id} không tồn tại")
        
        course_id = assignment.lesson.module.course_id
        
        # Kiểm tra enrollment
        if not is_enrolled_in_course(input_dto.user_id, course_id):
            raise NotEnrolledException("Bạn chưa đăng ký khóa học này")
        
        # Kiểm tra thời gian
        if not assignment.is_open:
            if assignment.is_upcoming:
                raise AssignmentNotOpenException(f"Bài tập chưa mở. Bắt đầu lúc {assignment.start_at}")
            else:
                raise AssignmentNotOpenException(f"Bài tập đã đóng lúc {assignment.end_at}")
        
        # Kiểm tra số lần làm
        attempt_count = AttemptModel.objects.filter(
            user_id=input_dto.user_id,
            assignment_id=input_dto.assignment_id,
        ).count()
        
        if attempt_count >= assignment.attempts_allowed:
            raise MaxAttemptsReachedException(
                f"Bạn đã làm {attempt_count}/{assignment.attempts_allowed} lần cho phép"
            )
        
        # Kiểm tra không có attempt đang IN_PROGRESS
        in_progress = AttemptModel.objects.filter(
            user_id=input_dto.user_id,
            assignment_id=input_dto.assignment_id,
            status='IN_PROGRESS',
        ).first()
        
        if in_progress:
            raise AttemptInProgressException(
                f"Bạn đang có một lần làm bài dở dang (ID: {in_progress.id})"
            )
        
        # Tạo attempt
        attempt = AttemptModel.objects.create(
            user_id=input_dto.user_id,
            assignment_id=input_dto.assignment_id,
            status='IN_PROGRESS',
        )
        
        # Ghi activity log
        try:
            from .activity_log import LogActivityUseCase, LogActivityInput
            log_use_case = LogActivityUseCase()
            log_use_case.execute(LogActivityInput(
                user_id=input_dto.user_id,
                action_type='START_ATTEMPT',
                target_type='assignment',
                target_id=input_dto.assignment_id,
                metadata={'attempt_id': attempt.id}
            ))
        except Exception:
            pass  # Bỏ qua lỗi log để không ảnh hưởng đến flow chính
        
        # Lấy danh sách câu hỏi
        questions = assignment.questions.all().order_by('order')
        
        # Trộn câu hỏi nếu cần
        import random
        if assignment.shuffle_questions:
            questions = list(questions)
            random.shuffle(questions)
        
        questions_for_attempt = []
        answer_mappings = {}  # question_id -> {new_key: original_key}
        
        for q in questions:
            option_a = q.option_a
            option_b = q.option_b
            option_c = q.option_c
            option_d = q.option_d
            
            # Trộn đáp án nếu cần
            if assignment.shuffle_answers:
                # Tạo list các đáp án với key gốc
                options = [
                    ('A', q.option_a),
                    ('B', q.option_b),
                    ('C', q.option_c),
                    ('D', q.option_d),
                ]
                random.shuffle(options)
                
                # Gán lại theo thứ tự mới
                option_a = options[0][1]
                option_b = options[1][1]
                option_c = options[2][1]
                option_d = options[3][1]
                
                # Lưu mapping: key mới -> key gốc
                new_keys = ['A', 'B', 'C', 'D']
                answer_mappings[q.id] = {
                    new_keys[i]: options[i][0] for i in range(4)
                }
            
            questions_for_attempt.append(QuestionForAttempt(
                id=q.id,
                order=q.order,
                text=q.text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                points=q.points,
            ))
        
        # Lưu answer_mappings vào attempt để dùng khi chấm điểm
        if answer_mappings:
            attempt.feedback = str(answer_mappings)  # Tạm dùng field feedback để lưu
            attempt.save(update_fields=['feedback'])
        
        return StartAttemptResult(
            attempt_id=attempt.id,
            assignment_title=assignment.title,
            time_limit=assignment.time_limit,
            started_at=attempt.started_at,
            questions=questions_for_attempt,
        )


class SubmitAttemptUseCase:
    """
    Nộp bài và chấm điểm
    
    - Lưu tất cả câu trả lời
    - Tự động chấm điểm
    - Cập nhật attempt status = SUBMITTED
    """
    
    @transaction.atomic
    def execute(self, input_dto: SubmitAttemptInput) -> SubmitAttemptResult:
        # Lấy attempt
        try:
            attempt = AttemptModel.objects.select_related(
                'assignment'
            ).get(pk=input_dto.attempt_id)
        except AttemptModel.DoesNotExist:
            raise AttemptNotFoundException(f"Attempt {input_dto.attempt_id} không tồn tại")
        
        # Kiểm tra owner
        if attempt.user_id != input_dto.user_id:
            raise AssessmentException("Bạn không có quyền nộp bài này")
        
        # Kiểm tra status
        if attempt.status != 'IN_PROGRESS':
            raise AttemptAlreadySubmittedException("Bài làm đã được nộp trước đó")
        
        # Xóa các answer cũ (nếu có)
        AttemptDetailModel.objects.filter(attempt=attempt).delete()
        
        # Lấy answer_mappings nếu có (khi shuffle_answers = True)
        answer_mappings = {}
        if attempt.feedback:
            try:
                import ast
                answer_mappings = ast.literal_eval(attempt.feedback)
            except:
                pass
        
        # Lưu các câu trả lời
        correct_count = 0
        for answer in input_dto.answers:
            try:
                question = QuestionModel.objects.get(
                    pk=answer.question_id,
                    assignment_id=attempt.assignment_id,
                )
            except QuestionModel.DoesNotExist:
                continue  # Bỏ qua câu hỏi không thuộc assignment
            
            # Map đáp án về key gốc nếu có shuffle
            chosen_answer = answer.chosen_answer
            if answer.question_id in answer_mappings:
                mapping = answer_mappings[answer.question_id]
                chosen_answer = mapping.get(answer.chosen_answer, answer.chosen_answer)
            
            is_correct = (chosen_answer == question.correct_answer)
            if is_correct:
                correct_count += 1
            
            AttemptDetailModel.objects.create(
                attempt=attempt,
                question=question,
                chosen_answer=chosen_answer,  # Lưu đáp án gốc
                is_correct=is_correct,
            )
        
        # Tính điểm
        score = attempt.calculate_score()
        
        # Cập nhật attempt
        attempt.score = Decimal(str(score))
        attempt.status = 'SUBMITTED'
        attempt.submitted_at = timezone.now()
        attempt.save()
        
        # Ghi activity log
        try:
            from .activity_log import LogActivityUseCase, LogActivityInput
            log_use_case = LogActivityUseCase()
            log_use_case.execute(LogActivityInput(
                user_id=input_dto.user_id,
                action_type='SUBMIT_ATTEMPT',
                target_type='attempt',
                target_id=attempt.id,
                metadata={
                    'assignment_id': attempt.assignment_id,
                    'score': float(attempt.score),
                    'max_score': float(attempt.assignment.max_score),
                    'correct_count': correct_count,
                }
            ))
        except Exception:
            pass  # Bỏ qua lỗi log để không ảnh hưởng đến flow chính
        
        # Gửi notification khi có điểm
        try:
            from .notification import notify_student_on_assignment_graded
            notify_student_on_assignment_graded(
                attempt_id=attempt.id,
                user_id=input_dto.user_id,
                score=float(attempt.score),
                max_score=float(attempt.assignment.max_score),
            )
        except Exception:
            pass  # Bỏ qua lỗi notification để không ảnh hưởng đến flow chính
        
        # Thông báo cho giảng viên khi có bài nộp
        try:
            from ...infrastructure.persistence.models.communication import NotificationModel
            from ...infrastructure.persistence.models.enrollment import EnrollmentModel
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            student = User.objects.get(pk=input_dto.user_id)
            course_id = attempt.assignment.lesson.module.course_id
            
            teacher_enrollments = EnrollmentModel.objects.filter(
                course_id=course_id,
                role_in_course='TEACHER'
            )
            for enrollment in teacher_enrollments:
                NotificationModel.objects.create(
                    user=enrollment.user,
                    title='Có bài nộp mới',
                    message=f'{student.full_name} đã nộp bài "{attempt.assignment.title}"',
                    type='SUBMISSION',
                    related_object_type='attempt',
                    related_object_id=attempt.id,
                )
        except Exception:
            pass  # Bỏ qua lỗi notification
        
        return SubmitAttemptResult(
            attempt_id=attempt.id,
            submitted_at=attempt.submitted_at,
            score=attempt.score,
            total_questions=attempt.total_questions,
            correct_count=correct_count,
        )


class GetAttemptResultUseCase:
    """
    Lấy kết quả bài làm
    
    Chỉ hiển thị chi tiết nếu assignment.show_result = True
    """
    
    def execute(self, attempt_id: int, user_id: int) -> GetAttemptResultOutput:
        # Lấy attempt
        try:
            attempt = AttemptModel.objects.select_related(
                'assignment'
            ).get(pk=attempt_id)
        except AttemptModel.DoesNotExist:
            raise AttemptNotFoundException(f"Attempt {attempt_id} không tồn tại")
        
        # Kiểm tra quyền xem
        course_id = get_course_id_from_assignment(attempt.assignment_id)
        is_owner = (attempt.user_id == user_id)
        is_teacher = is_teacher_of_course(user_id, course_id) if course_id else False
        
        if not is_owner and not is_teacher:
            raise AssessmentException("Bạn không có quyền xem kết quả này")
        
        # Lấy chi tiết
        details = attempt.details.select_related('question').order_by('question__order')
        
        questions_result = []
        for detail in details:
            q = detail.question
            questions_result.append(QuestionResult(
                question_id=q.id,
                order=q.order,
                text=q.text,
                chosen_answer=detail.chosen_answer,
                correct_answer=q.correct_answer if attempt.assignment.show_result else None,
                is_correct=detail.is_correct,
                explanation=q.explanation if attempt.assignment.show_result else None,
            ))
        
        # Ghi activity log khi xem kết quả
        try:
            from .activity_log import LogActivityUseCase, LogActivityInput
            log_use_case = LogActivityUseCase()
            log_use_case.execute(LogActivityInput(
                user_id=user_id,
                action_type='VIEW_RESULT',
                target_type='attempt',
                target_id=attempt.id,
                metadata={
                    'assignment_id': attempt.assignment_id,
                    'score': float(attempt.score) if attempt.score else None,
                }
            ))
        except Exception:
            pass  # Bỏ qua lỗi log để không ảnh hưởng đến flow chính
        
        return GetAttemptResultOutput(
            attempt_id=attempt.id,
            assignment_title=attempt.assignment.title,
            started_at=attempt.started_at,
            submitted_at=attempt.submitted_at,
            score=attempt.score,
            total_questions=len(questions_result),
            correct_count=attempt.correct_count,
            questions=questions_result,
        )


# Import models for aggregate
from django.db import models

