"""
Assessment Views

API Views cho chức năng Quiz.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from decimal import Decimal

from .serializers import (
    CreateAssignmentSerializer,
    AssignmentOutputSerializer,
    CreateQuestionSerializer,
    UpdateQuestionSerializer,
    QuestionOutputSerializer,
    ImportExcelResultSerializer,
    StartAttemptOutputSerializer,
    SubmitAttemptSerializer,
    SubmitAttemptOutputSerializer,
    AttemptResultOutputSerializer,
)
from .....application.use_cases.assessment import (
    CreateAssignmentInput,
    CreateAssignmentUseCase,
    CreateQuestionInput,
    CreateQuestionUseCase,
    UpdateQuestionInput,
    UpdateQuestionUseCase,
    DeleteQuestionUseCase,
    ImportQuestionsInput,
    ImportQuestionsFromExcelUseCase,
    StartAttemptInput,
    StartAttemptUseCase,
    SubmitAttemptInput,
    SubmitAttemptUseCase,
    AnswerInput,
    GetAttemptResultUseCase,
    # Exceptions
    AssessmentException,
    NotTeacherException,
    NotEnrolledException,
    AssignmentNotFoundException,
    QuestionNotFoundException,
    AttemptNotFoundException,
    AssignmentNotOpenException,
    MaxAttemptsReachedException,
    AttemptAlreadySubmittedException,
    AttemptInProgressException,
)
from .....infrastructure.persistence.models.assessment import (
    AssignmentModel, QuestionModel
)
from .....infrastructure.services.excel_parser import ExcelQuestionParser, ExcelParseError


class CreateAssignmentView(APIView):
    """
    POST /api/v1/assessments/assignments/
    
    Tạo bài tập Quiz mới. Chỉ giáo viên/TA được tạo.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get_serializer(self, *args, **kwargs):
        return CreateAssignmentSerializer(*args, **kwargs)
    
    def post(self, request):
        serializer = CreateAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            use_case = CreateAssignmentUseCase()
            assignment = use_case.execute(CreateAssignmentInput(
                lesson_id=data['lesson_id'],
                title=data['title'],
                user_id=request.user.id,
                instructions=data.get('instructions'),
                start_at=data.get('start_at'),
                end_at=data.get('end_at'),
                time_limit=data.get('time_limit'),
                attempts_allowed=data.get('attempts_allowed', 1),
                max_score=data.get('max_score', Decimal('100')),
                shuffle_questions=data.get('shuffle_questions', False),
                shuffle_answers=data.get('shuffle_answers', False),
                show_result=data.get('show_result', True),
            ))
            
            output = AssignmentOutputSerializer({
                'id': assignment.id,
                'lesson_id': assignment.lesson_id,
                'title': assignment.title,
                'instructions': assignment.instructions,
                'type': assignment.type,
                'start_at': assignment.start_at,
                'end_at': assignment.end_at,
                'time_limit': assignment.time_limit,
                'attempts_allowed': assignment.attempts_allowed,
                'max_score': assignment.max_score,
                'shuffle_questions': assignment.shuffle_questions,
                'shuffle_answers': assignment.shuffle_answers,
                'show_result': assignment.show_result,
                'question_count': assignment.question_count,
                'is_open': assignment.is_open,
                'created_at': assignment.created_at,
            })
            
            return Response(output.data, status=status.HTTP_201_CREATED)
            
        except NotTeacherException as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except AssignmentNotFoundException as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except AssessmentException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AssignmentQuestionsView(APIView):
    """
    GET /api/v1/assessments/assignments/{id}/questions/
    POST /api/v1/assessments/assignments/{id}/questions/
    
    Lấy danh sách câu hỏi hoặc thêm câu hỏi mới.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get_serializer(self, *args, **kwargs):
        return CreateQuestionSerializer(*args, **kwargs)
    
    def get(self, request, assignment_id):
        """Lấy danh sách câu hỏi của assignment"""
        try:
            assignment = AssignmentModel.objects.get(pk=assignment_id)
        except AssignmentModel.DoesNotExist:
            return Response(
                {'detail': f'Assignment {assignment_id} không tồn tại'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        questions = assignment.questions.order_by('order')
        
        output = QuestionOutputSerializer([{
            'id': q.id,
            'assignment_id': q.assignment_id,
            'text': q.text,
            'option_a': q.option_a,
            'option_b': q.option_b,
            'option_c': q.option_c,
            'option_d': q.option_d,
            'correct_answer': q.correct_answer,
            'explanation': q.explanation,
            'points': q.points,
            'order': q.order,
        } for q in questions], many=True)
        
        return Response({
            'assignment_id': assignment_id,
            'count': len(output.data),
            'questions': output.data,
        })
    
    def post(self, request, assignment_id):
        """Thêm câu hỏi mới"""
        serializer = CreateQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            use_case = CreateQuestionUseCase()
            question = use_case.execute(CreateQuestionInput(
                assignment_id=assignment_id,
                user_id=request.user.id,
                text=data['text'],
                option_a=data['option_a'],
                option_b=data['option_b'],
                option_c=data['option_c'],
                option_d=data['option_d'],
                correct_answer=data['correct_answer'],
                explanation=data.get('explanation'),
                points=data.get('points', Decimal('1')),
                order=data.get('order'),
            ))
            
            output = QuestionOutputSerializer({
                'id': question.id,
                'assignment_id': question.assignment_id,
                'text': question.text,
                'option_a': question.option_a,
                'option_b': question.option_b,
                'option_c': question.option_c,
                'option_d': question.option_d,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'points': question.points,
                'order': question.order,
            })
            
            return Response(output.data, status=status.HTTP_201_CREATED)
            
        except NotTeacherException as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except AssignmentNotFoundException as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except AssessmentException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class QuestionDetailView(APIView):
    """
    PUT /api/v1/assessments/questions/{id}/
    DELETE /api/v1/assessments/questions/{id}/
    
    Cập nhật hoặc xóa câu hỏi.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get_serializer(self, *args, **kwargs):
        return UpdateQuestionSerializer(*args, **kwargs)
    
    def put(self, request, question_id):
        """Cập nhật câu hỏi"""
        serializer = UpdateQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            use_case = UpdateQuestionUseCase()
            question = use_case.execute(UpdateQuestionInput(
                question_id=question_id,
                user_id=request.user.id,
                text=data.get('text'),
                option_a=data.get('option_a'),
                option_b=data.get('option_b'),
                option_c=data.get('option_c'),
                option_d=data.get('option_d'),
                correct_answer=data.get('correct_answer'),
                explanation=data.get('explanation'),
                points=data.get('points'),
                order=data.get('order'),
            ))
            
            output = QuestionOutputSerializer({
                'id': question.id,
                'assignment_id': question.assignment_id,
                'text': question.text,
                'option_a': question.option_a,
                'option_b': question.option_b,
                'option_c': question.option_c,
                'option_d': question.option_d,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'points': question.points,
                'order': question.order,
            })
            
            return Response(output.data)
            
        except NotTeacherException as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except QuestionNotFoundException as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except AssessmentException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, question_id):
        """Xóa câu hỏi"""
        try:
            use_case = DeleteQuestionUseCase()
            use_case.execute(question_id, request.user.id)
            
            return Response({'message': 'Đã xóa câu hỏi'}, status=status.HTTP_200_OK)
            
        except NotTeacherException as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except QuestionNotFoundException as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)


class ImportExcelView(APIView):
    """
    POST /api/v1/assessments/assignments/{id}/import-excel/
    
    Import câu hỏi từ file Excel.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def post(self, request, assignment_id):
        """Import câu hỏi từ Excel"""
        # Validate file
        if 'file' not in request.FILES:
            return Response(
                {'detail': 'Vui lòng upload file Excel'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        
        # Check file extension
        if not file.name.endswith(('.xlsx', '.xls')):
            return Response(
                {'detail': 'File phải có định dạng .xlsx hoặc .xls'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Parse Excel
            parser = ExcelQuestionParser()
            questions_data = parser.parse(file, file.name)
            
            if not questions_data:
                return Response(
                    {'detail': 'File Excel không có dữ liệu câu hỏi'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Import questions
            use_case = ImportQuestionsFromExcelUseCase()
            result = use_case.execute(ImportQuestionsInput(
                assignment_id=assignment_id,
                user_id=request.user.id,
                questions_data=questions_data,
            ))
            
            output = ImportExcelResultSerializer({
                'total_rows': result.total_rows,
                'success_count': result.success_count,
                'error_rows': result.error_rows,
            })
            
            return Response(output.data)
            
        except ExcelParseError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except NotTeacherException as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except AssignmentNotFoundException as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except AssessmentException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StartAttemptView(APIView):
    """
    POST /api/v1/assessments/assignments/{id}/start/
    
    Bắt đầu làm bài quiz.
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def post(self, request, assignment_id):
        """Bắt đầu làm bài"""
        try:
            use_case = StartAttemptUseCase()
            result = use_case.execute(StartAttemptInput(
                assignment_id=assignment_id,
                user_id=request.user.id,
            ))
            
            output = StartAttemptOutputSerializer({
                'attempt_id': result.attempt_id,
                'assignment_title': result.assignment_title,
                'time_limit': result.time_limit,
                'started_at': result.started_at,
                'questions': [{
                    'id': q.id,
                    'order': q.order,
                    'text': q.text,
                    'option_a': q.option_a,
                    'option_b': q.option_b,
                    'option_c': q.option_c,
                    'option_d': q.option_d,
                    'points': q.points,
                } for q in result.questions],
            })
            
            return Response(output.data, status=status.HTTP_201_CREATED)
            
        except NotEnrolledException as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except AssignmentNotFoundException as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except (AssignmentNotOpenException, MaxAttemptsReachedException, AttemptInProgressException) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SubmitAttemptView(APIView):
    """
    POST /api/v1/assessments/attempts/{id}/submit/
    
    Nộp bài quiz.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get_serializer(self, *args, **kwargs):
        return SubmitAttemptSerializer(*args, **kwargs)
    
    def post(self, request, attempt_id):
        """Nộp bài"""
        serializer = SubmitAttemptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            use_case = SubmitAttemptUseCase()
            result = use_case.execute(SubmitAttemptInput(
                attempt_id=attempt_id,
                user_id=request.user.id,
                answers=[
                    AnswerInput(
                        question_id=a['question_id'],
                        chosen_answer=a['chosen_answer'],
                    )
                    for a in data['answers']
                ],
            ))
            
            output = SubmitAttemptOutputSerializer({
                'attempt_id': result.attempt_id,
                'submitted_at': result.submitted_at,
                'score': result.score,
                'total_questions': result.total_questions,
                'correct_count': result.correct_count,
            })
            
            return Response(output.data)
            
        except AttemptNotFoundException as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except AttemptAlreadySubmittedException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except AssessmentException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AttemptResultView(APIView):
    """
    GET /api/v1/assessments/attempts/{id}/result/
    
    Xem kết quả bài làm.
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request, attempt_id):
        """Xem kết quả"""
        try:
            use_case = GetAttemptResultUseCase()
            result = use_case.execute(attempt_id, request.user.id)
            
            output = AttemptResultOutputSerializer({
                'attempt_id': result.attempt_id,
                'assignment_title': result.assignment_title,
                'started_at': result.started_at,
                'submitted_at': result.submitted_at,
                'score': result.score,
                'total_questions': result.total_questions,
                'correct_count': result.correct_count,
                'questions': [{
                    'question_id': q.question_id,
                    'order': q.order,
                    'text': q.text,
                    'chosen_answer': q.chosen_answer,
                    'correct_answer': q.correct_answer,
                    'is_correct': q.is_correct,
                    'explanation': q.explanation,
                } for q in result.questions],
            })
            
            return Response(output.data)
            
        except AttemptNotFoundException as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except AssessmentException as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)


class AssignmentInfoView(APIView):
    """
    GET /api/v1/assessments/assignments/{id}/info/
    
    Lấy thông tin bài tập trước khi bắt đầu làm.
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request, assignment_id):
        from .....infrastructure.persistence.models.assessment import AssignmentModel, AttemptModel
        
        try:
            assignment = AssignmentModel.objects.get(id=assignment_id)
        except AssignmentModel.DoesNotExist:
            return Response({'detail': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Count user's attempts
        user_attempts = AttemptModel.objects.filter(
            user=request.user,
            assignment=assignment
        ).count()
        
        # Calculate remaining attempts
        attempts_remaining = None
        can_start = True
        message = None
        
        if assignment.attempts_allowed is not None and assignment.attempts_allowed > 0:
            attempts_remaining = max(0, assignment.attempts_allowed - user_attempts)
            if attempts_remaining <= 0:
                can_start = False
                message = 'Bạn đã hết lượt làm bài'
        
        return Response({
            'id': assignment.id,
            'title': assignment.title,
            'time_limit': assignment.time_limit,
            'attempts_allowed': assignment.attempts_allowed,
            'attempts_remaining': attempts_remaining,
            'can_start': can_start,
            'message': message
        })


class MyAttemptsCountView(APIView):
    """
    GET /api/v1/assessments/my-attempts/count/
    
    Lấy số lượng bài tập đã nộp của user hiện tại.
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        from .....infrastructure.persistence.models.assessment import AttemptModel
        count = AttemptModel.objects.filter(
            user=request.user,
            status__in=['SUBMITTED', 'GRADED']
        ).count()
        return Response({'count': count})


class MyAttemptsListView(APIView):
    """
    GET /api/v1/assessments/my-attempts/
    
    Lấy danh sách bài tập đã làm của user hiện tại.
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        from .....infrastructure.persistence.models.assessment import AttemptModel
        
        attempts = AttemptModel.objects.filter(
            user=request.user
        ).select_related('assignment', 'assignment__lesson', 'assignment__lesson__module', 'assignment__lesson__module__course').order_by('-started_at')
        
        status_display_map = {
            'IN_PROGRESS': 'Đang làm',
            'SUBMITTED': 'Đã nộp',
            'GRADED': 'Đã chấm điểm'
        }
        
        results = []
        for attempt in attempts:
            course_title = 'N/A'
            try:
                if attempt.assignment and attempt.assignment.lesson and attempt.assignment.lesson.module and attempt.assignment.lesson.module.course:
                    course_title = attempt.assignment.lesson.module.course.title
            except Exception:
                pass
            
            # max_score from assignment
            max_score = None
            if attempt.assignment:
                max_score = attempt.assignment.max_score if hasattr(attempt.assignment, 'max_score') else None
            
            results.append({
                'id': attempt.id,
                'assignment_title': attempt.assignment.title if attempt.assignment else 'N/A',
                'assignment_type': attempt.assignment.type if attempt.assignment else 'N/A',
                'course_title': course_title,
                'status': attempt.status,
                'status_display': status_display_map.get(attempt.status, attempt.status),
                'score': attempt.score,
                'max_score': max_score,
                'feedback': attempt.feedback or '',
                'submitted_at': attempt.submitted_at,
                'started_at': attempt.started_at,
            })
        
        return Response({'results': results})


class SubmitFileAssignmentView(APIView):
    """
    POST /api/v1/assessments/assignments/{id}/submit-file/
    
    Nộp bài tập dạng file (không phải quiz).
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def post(self, request, assignment_id):
        from .....infrastructure.persistence.models.assessment import AssignmentModel, AttemptModel
        from .....infrastructure.persistence.models.enrollment import EnrollmentModel
        
        # Get assignment
        try:
            assignment = AssignmentModel.objects.select_related(
                'lesson__module__course'
            ).get(pk=assignment_id)
        except AssignmentModel.DoesNotExist:
            return Response({'detail': 'Bài tập không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check enrollment
        course_id = assignment.lesson.module.course_id
        is_enrolled = EnrollmentModel.objects.filter(
            user=request.user,
            course_id=course_id,
            role_in_course='STUDENT'
        ).exists()
        
        if not is_enrolled:
            return Response({'detail': 'Bạn chưa đăng ký khóa học này'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if assignment is open
        if not assignment.is_open:
            return Response({'detail': 'Bài tập không trong thời gian nộp'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check attempts
        attempt_count = AttemptModel.objects.filter(
            user=request.user,
            assignment=assignment,
        ).count()
        
        if attempt_count >= assignment.attempts_allowed:
            return Response({'detail': f'Bạn đã nộp {attempt_count}/{assignment.attempts_allowed} lần'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get file and text
        submitted_file = request.FILES.get('file')
        submitted_text = request.data.get('text', '')
        
        if not submitted_file and not submitted_text:
            return Response({'detail': 'Vui lòng nộp file hoặc nhập nội dung'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create attempt
        from django.utils import timezone
        attempt = AttemptModel.objects.create(
            user=request.user,
            assignment=assignment,
            status='SUBMITTED',
            submitted_at=timezone.now(),
            submitted_file=submitted_file,
            submitted_text=submitted_text,
        )
        
        # Thông báo cho giảng viên
        from .....infrastructure.persistence.models.communication import NotificationModel
        from .....infrastructure.persistence.models.enrollment import EnrollmentModel
        
        teacher_enrollments = EnrollmentModel.objects.filter(
            course_id=course_id,
            role_in_course='TEACHER'
        )
        for enrollment in teacher_enrollments:
            NotificationModel.objects.create(
                user=enrollment.user,
                title='Có bài nộp mới',
                message=f'{request.user.full_name} đã nộp bài "{assignment.title}"',
                type='SUBMISSION',
                related_object_type='attempt',
                related_object_id=attempt.id,
            )
        
        return Response({
            'id': attempt.id,
            'message': 'Nộp bài thành công',
            'submitted_at': attempt.submitted_at,
        }, status=status.HTTP_201_CREATED)


class GradeAttemptView(APIView):
    """
    POST /api/v1/assessments/attempts/{id}/grade/
    
    Giảng viên chấm điểm bài nộp.
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def post(self, request, attempt_id):
        from .....infrastructure.persistence.models.assessment import AttemptModel
        from .....infrastructure.persistence.models.enrollment import EnrollmentModel
        
        # Get attempt
        try:
            attempt = AttemptModel.objects.select_related(
                'assignment__lesson__module__course'
            ).get(pk=attempt_id)
        except AttemptModel.DoesNotExist:
            return Response({'detail': 'Bài nộp không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user is teacher of this course
        course_id = attempt.assignment.lesson.module.course_id
        is_teacher = EnrollmentModel.objects.filter(
            user=request.user,
            course_id=course_id,
            role_in_course='TEACHER'
        ).exists()
        
        if not is_teacher and not request.user.is_staff:
            return Response({'detail': 'Bạn không có quyền chấm điểm'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get score and feedback
        score = request.data.get('score')
        feedback = request.data.get('feedback', '')
        
        if score is None:
            return Response({'detail': 'Vui lòng nhập điểm'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            score = Decimal(str(score))
            if score < 0 or score > attempt.assignment.max_score:
                return Response({
                    'detail': f'Điểm phải từ 0 đến {attempt.assignment.max_score}'
                }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Điểm không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update attempt
        attempt.score = score
        attempt.feedback = feedback
        attempt.status = 'GRADED'
        attempt.save(update_fields=['score', 'feedback', 'status'])
        
        # Gửi thông báo cho học viên
        from .....infrastructure.persistence.models.communication import NotificationModel
        NotificationModel.objects.create(
            user=attempt.user,
            title='Bài tập đã được chấm điểm',
            message=f'Bài tập "{attempt.assignment.title}" đã được chấm điểm: {score}/{attempt.assignment.max_score}',
            type='GRADE',
            related_object_type='attempt',
            related_object_id=attempt.id,
        )
        
        return Response({
            'id': attempt.id,
            'score': float(attempt.score),
            'feedback': attempt.feedback,
            'status': attempt.status,
            'message': 'Chấm điểm thành công',
        })
