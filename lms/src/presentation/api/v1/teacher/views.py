"""
Teacher API Views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .....infrastructure.persistence.models.course import CourseModel, ModuleModel, LessonModel
from .....infrastructure.persistence.models.enrollment import EnrollmentModel
from .....infrastructure.persistence.models.assessment import AssignmentModel, AttemptModel, QuestionModel, AttemptDetailModel
from .....infrastructure.persistence.models.content import ResourceModel


class IsTeacherOrAdmin:
    """Permission check for teacher or admin"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            profile = request.user.profile
            return profile.role in ['TEACHER', 'ADMIN']
        except:
            return False


class TeacherStatsView(APIView):
    """GET /api/v1/teacher/stats/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        user = request.user
        
        # Get courses where user is teacher (via enrollment)
        teacher_enrollments = EnrollmentModel.objects.filter(
            user=user,
            role_in_course='TEACHER'
        )
        course_ids = teacher_enrollments.values_list('course_id', flat=True)
        
        # Count students enrolled in teacher's courses
        total_students = EnrollmentModel.objects.filter(
            course_id__in=course_ids,
            role_in_course='STUDENT'
        ).values('user').distinct().count()
        
        # Count assignments in teacher's courses
        total_assignments = AssignmentModel.objects.filter(
            lesson__module__course_id__in=course_ids
        ).count()
        
        # Count pending submissions
        pending_submissions = AttemptModel.objects.filter(
            assignment__lesson__module__course_id__in=course_ids,
            status='SUBMITTED'
        ).count()
        
        return Response({
            'total_courses': len(course_ids),
            'total_students': total_students,
            'total_assignments': total_assignments,
            'pending_submissions': pending_submissions
        })


class TeacherCoursesView(APIView):
    """GET /api/v1/teacher/courses/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        # Get courses where user is teacher
        teacher_enrollments = EnrollmentModel.objects.filter(
            user=request.user,
            role_in_course='TEACHER'
        ).select_related('course', 'course__subject')
        
        results = []
        for enrollment in teacher_enrollments:
            course = enrollment.course
            # Count modules
            modules_count = ModuleModel.objects.filter(course=course).count()
            # Count students
            students_count = EnrollmentModel.objects.filter(
                course=course,
                role_in_course='STUDENT'
            ).count()
            
            results.append({
                'id': course.id,
                'title': course.title,
                'description': course.description or '',
                'thumbnail': None,
                'subject': {
                    'id': course.subject.id,
                    'name': course.subject.title
                } if course.subject else None,
                'status': course.computed_status,
                'status_display': course.computed_status_display,
                'start_date': course.start_date,
                'end_date': course.end_date,
                'modules_count': modules_count,
                'students_count': students_count,
            })
        
        return Response(results)


class TeacherStudentsView(APIView):
    """GET /api/v1/teacher/students/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        # Get courses where user is teacher
        teacher_course_ids = EnrollmentModel.objects.filter(
            user=request.user,
            role_in_course='TEACHER'
        ).values_list('course_id', flat=True)
        
        # Get all students enrolled in those courses
        enrollments = EnrollmentModel.objects.filter(
            course_id__in=teacher_course_ids,
            role_in_course='STUDENT'
        ).select_related('user', 'user__profile', 'course')
        
        results = []
        for enrollment in enrollments:
            avatar_url = None
            if hasattr(enrollment.user, 'profile') and enrollment.user.profile and enrollment.user.profile.avatar:
                avatar_url = request.build_absolute_uri(enrollment.user.profile.avatar.url)
            results.append({
                'id': enrollment.user.id,
                'full_name': enrollment.user.full_name,
                'email': enrollment.user.email,
                'avatar': avatar_url,
                'course_title': enrollment.course.title,
                'joined_at': enrollment.joined_at,
            })
        
        return Response({'results': results})


class TeacherSubmissionsView(APIView):
    """GET /api/v1/teacher/submissions/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        # Get courses where user is teacher
        teacher_course_ids = EnrollmentModel.objects.filter(
            user=request.user,
            role_in_course='TEACHER'
        ).values_list('course_id', flat=True)
        
        # Filter by type if specified
        assignment_type = request.query_params.get('type')  # QUIZ or SUBMISSION
        
        # Get all submissions for teacher's courses
        attempts = AttemptModel.objects.filter(
            assignment__lesson__module__course_id__in=teacher_course_ids
        ).select_related('user', 'user__profile', 'assignment').order_by('-submitted_at')
        
        if assignment_type:
            attempts = attempts.filter(assignment__type=assignment_type)
        
        results = []
        for attempt in attempts:
            # Auto calculate score for quiz if not graded
            auto_score = None
            if attempt.assignment.type == 'QUIZ':
                auto_score = attempt.calculate_score()
            
            student_avatar = None
            if hasattr(attempt.user, 'profile') and attempt.user.profile and attempt.user.profile.avatar:
                student_avatar = request.build_absolute_uri(attempt.user.profile.avatar.url)
            results.append({
                'id': attempt.id,
                'student': {
                    'id': attempt.user.id,
                    'full_name': attempt.user.full_name,
                    'email': attempt.user.email,
                    'avatar': student_avatar,
                },
                'assignment_id': attempt.assignment.id,
                'assignment_title': attempt.assignment.title,
                'assignment_type': attempt.assignment.type,
                'max_score': float(attempt.assignment.max_score),
                'submitted_at': attempt.submitted_at,
                'score': float(attempt.score) if attempt.score else auto_score,
                'auto_score': auto_score,
                'status': attempt.status,
                'submitted_file': request.build_absolute_uri(attempt.submitted_file.url) if attempt.submitted_file else None,
                'submitted_text': attempt.submitted_text,
                'correct_count': attempt.correct_count if attempt.assignment.type == 'QUIZ' else None,
                'total_questions': attempt.total_questions if attempt.assignment.type == 'QUIZ' else None,
            })
        
        return Response(results)


class AssignmentSubmissionsView(APIView):
    """GET /api/v1/teacher/assignments/{id}/submissions/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request, assignment_id):
        attempts = AttemptModel.objects.filter(
            assignment_id=assignment_id
        ).select_related('user', 'user__profile').order_by('-submitted_at')
        
        results = []
        for attempt in attempts:
            student_avatar = None
            if hasattr(attempt.user, 'profile') and attempt.user.profile and attempt.user.profile.avatar:
                student_avatar = request.build_absolute_uri(attempt.user.profile.avatar.url)
            results.append({
                'id': attempt.id,
                'student': {
                    'id': attempt.user.id,
                    'full_name': attempt.user.full_name,
                    'email': attempt.user.email,
                    'avatar': student_avatar,
                },
                'submitted_at': attempt.submitted_at,
                'score': attempt.score,
                'status': attempt.status,
                'submitted_file': request.build_absolute_uri(attempt.submitted_file.url) if attempt.submitted_file else None,
                'submitted_text': attempt.submitted_text,
            })
        
        return Response(results)


# Content Management Views

class ModuleCreateView(APIView):
    """POST /api/v1/teacher/modules/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def post(self, request):
        course_id = request.data.get('course')
        title = request.data.get('title')
        description = request.data.get('description', '')
        
        if not course_id or not title:
            return Response({'detail': 'course and title are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get max order
        max_order = ModuleModel.objects.filter(course_id=course_id).count() + 1
        
        module = ModuleModel.objects.create(
            course_id=course_id,
            title=title,
            description=description,
            order=max_order
        )
        
        return Response({'id': module.id, 'title': module.title}, status=status.HTTP_201_CREATED)


class ModuleDetailView(APIView):
    """PATCH/DELETE /api/v1/teacher/modules/{id}/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def patch(self, request, module_id):
        try:
            module = ModuleModel.objects.get(id=module_id)
        except ModuleModel.DoesNotExist:
            return Response({'detail': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'title' in request.data:
            module.title = request.data['title']
        if 'description' in request.data:
            module.description = request.data['description']
        module.save()
        
        return Response({'id': module.id, 'title': module.title})
    
    def delete(self, request, module_id):
        try:
            module = ModuleModel.objects.get(id=module_id)
            module.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ModuleModel.DoesNotExist:
            return Response({'detail': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)


class LessonCreateView(APIView):
    """POST /api/v1/teacher/lessons/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def post(self, request):
        module_id = request.data.get('module')
        title = request.data.get('title')
        description = request.data.get('description', '')
        
        if not module_id or not title:
            return Response({'detail': 'module and title are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        max_order = LessonModel.objects.filter(module_id=module_id).count() + 1
        
        lesson = LessonModel.objects.create(
            module_id=module_id,
            title=title,
            description=description,
            order=max_order
        )
        
        return Response({'id': lesson.id, 'title': lesson.title}, status=status.HTTP_201_CREATED)


class LessonDetailView(APIView):
    """PATCH/DELETE /api/v1/teacher/lessons/{id}/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def patch(self, request, lesson_id):
        try:
            lesson = LessonModel.objects.get(id=lesson_id)
        except LessonModel.DoesNotExist:
            return Response({'detail': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'title' in request.data:
            lesson.title = request.data['title']
        if 'description' in request.data:
            lesson.description = request.data['description']
        lesson.save()
        
        return Response({'id': lesson.id, 'title': lesson.title})
    
    def delete(self, request, lesson_id):
        try:
            lesson = LessonModel.objects.get(id=lesson_id)
            lesson.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except LessonModel.DoesNotExist:
            return Response({'detail': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)


class ResourceCreateView(APIView):
    """POST /api/v1/teacher/resources/"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def post(self, request):
        lesson_id = request.data.get('lesson')
        resource_type = request.data.get('type')
        title = request.data.get('title')
        
        if not lesson_id or not resource_type or not title:
            return Response({'detail': 'lesson, type and title are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        max_order = ResourceModel.objects.filter(lesson_id=lesson_id).count() + 1
        
        resource = ResourceModel(
            lesson_id=lesson_id,
            type=resource_type,
            title=title,
            order=max_order
        )
        
        if resource_type == 'DOCUMENT':
            if 'document_file' in request.FILES:
                resource.document_file = request.FILES['document_file']
        elif resource_type == 'VIDEO':
            video_source = request.data.get('video_source', 'FILE')
            resource.video_source = video_source
            if video_source == 'FILE' and 'video_file' in request.FILES:
                resource.video_file = request.FILES['video_file']
            elif video_source == 'URL':
                resource.video_url = request.data.get('video_url', '')
        elif resource_type == 'LINK':
            resource.link_url = request.data.get('link_url', '')
        elif resource_type == 'TEXT':
            resource.text_content = request.data.get('text_content', '')
        
        resource.save()
        
        return Response({'id': resource.id, 'title': resource.title}, status=status.HTTP_201_CREATED)


class ResourceDetailView(APIView):
    """PATCH/DELETE /api/v1/teacher/resources/{id}/"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def patch(self, request, resource_id):
        try:
            resource = ResourceModel.objects.get(id=resource_id)
        except ResourceModel.DoesNotExist:
            return Response({'detail': 'Resource not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'title' in request.data:
            resource.title = request.data['title']
        if 'order' in request.data:
            resource.order = request.data['order']
        if 'type' in request.data:
            resource.type = request.data['type']
        
        # Handle file updates based on type
        if resource.type == 'DOCUMENT' and 'document_file' in request.FILES:
            resource.document_file = request.FILES['document_file']
        elif resource.type == 'VIDEO':
            if 'video_source' in request.data:
                resource.video_source = request.data['video_source']
            if resource.video_source == 'FILE' and 'video_file' in request.FILES:
                resource.video_file = request.FILES['video_file']
            elif resource.video_source == 'URL' and 'video_url' in request.data:
                resource.video_url = request.data['video_url']
        elif resource.type == 'LINK' and 'link_url' in request.data:
            resource.link_url = request.data['link_url']
        elif resource.type == 'TEXT' and 'text_content' in request.data:
            resource.text_content = request.data['text_content']
        
        resource.save()
        return Response({'id': resource.id, 'title': resource.title})
    
    def delete(self, request, resource_id):
        try:
            resource = ResourceModel.objects.get(id=resource_id)
            resource.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ResourceModel.DoesNotExist:
            return Response({'detail': 'Resource not found'}, status=status.HTTP_404_NOT_FOUND)


class AssignmentCreateView(APIView):
    """POST /api/v1/teacher/assignments/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def post(self, request):
        from django.utils import timezone
        
        lesson_id = request.data.get('lesson')
        assignment_type = request.data.get('type')
        title = request.data.get('title')
        
        if not lesson_id or not assignment_type or not title:
            return Response({'detail': 'lesson, type and title are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Default start_at to now, end_at to 30 days later
        now = timezone.now()
        start_at = request.data.get('start_at') or now
        end_at = request.data.get('end_at') or (now + timezone.timedelta(days=30))
        
        assignment = AssignmentModel.objects.create(
            lesson_id=lesson_id,
            type=assignment_type,
            title=title,
            instructions=request.data.get('description', ''),
            start_at=start_at,
            end_at=end_at,
            time_limit=request.data.get('time_limit') or None,
            attempts_allowed=request.data.get('attempts_allowed') or 1,
            max_score=request.data.get('max_score') or 100,
        )
        
        return Response({'id': assignment.id, 'title': assignment.title}, status=status.HTTP_201_CREATED)


class AssignmentDetailView(APIView):
    """PATCH/DELETE /api/v1/teacher/assignments/{id}/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def patch(self, request, assignment_id):
        try:
            assignment = AssignmentModel.objects.get(id=assignment_id)
        except AssignmentModel.DoesNotExist:
            return Response({'detail': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'title' in request.data:
            assignment.title = request.data['title']
        if 'instructions' in request.data:
            assignment.instructions = request.data['instructions']
        if 'time_limit' in request.data:
            assignment.time_limit = request.data['time_limit']
        if 'attempts_allowed' in request.data:
            assignment.attempts_allowed = request.data['attempts_allowed']
        if 'max_score' in request.data:
            assignment.max_score = request.data['max_score']
        
        assignment.save()
        return Response({'id': assignment.id, 'title': assignment.title})
    
    def delete(self, request, assignment_id):
        try:
            assignment = AssignmentModel.objects.get(id=assignment_id)
            assignment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AssignmentModel.DoesNotExist:
            return Response({'detail': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdateOrderView(APIView):
    """PATCH /api/v1/teacher/update-order/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def patch(self, request):
        """
        Update order of modules, lessons, or resources.
        Request body: { "type": "module|lesson|resource", "items": [{"id": 1, "order": 1}, ...] }
        """
        item_type = request.data.get('type')
        items = request.data.get('items', [])
        
        if not item_type or not items:
            return Response({'detail': 'type and items are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        model_map = {
            'module': ModuleModel,
            'lesson': LessonModel,
            'resource': ResourceModel,
            'question': QuestionModel,
        }
        
        Model = model_map.get(item_type)
        if not Model:
            return Response({'detail': 'Invalid type'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use bulk update to bypass save() method and order_manager
        for item in items:
            Model.objects.filter(id=item['id']).update(order=item['order'])
        
        return Response({'detail': 'Order updated successfully'})


# ==================== QUESTION MANAGEMENT ====================

class AssignmentQuestionsView(APIView):
    """GET /api/v1/teacher/assignments/{id}/questions/ - List questions"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request, assignment_id):
        try:
            assignment = AssignmentModel.objects.get(id=assignment_id)
        except AssignmentModel.DoesNotExist:
            return Response({'detail': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        questions = QuestionModel.objects.filter(assignment=assignment).order_by('order')
        results = []
        for q in questions:
            results.append({
                'id': q.id,
                'question_text': q.text,
                'option_a': q.option_a,
                'option_b': q.option_b,
                'option_c': q.option_c,
                'option_d': q.option_d,
                'correct_answer': q.correct_answer,
                'points': q.points,
                'order': q.order,
            })
        
        return Response({
            'assignment': {
                'id': assignment.id,
                'title': assignment.title,
                'type': assignment.type,
                'shuffle_questions': assignment.shuffle_questions,
                'shuffle_answers': assignment.shuffle_answers,
                'show_result': assignment.show_result,
            },
            'questions': results,
            'total': len(results)
        })


class AssignmentSettingsView(APIView):
    """PATCH /api/v1/teacher/assignments/{id}/settings/ - Update quiz settings"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def patch(self, request, assignment_id):
        try:
            assignment = AssignmentModel.objects.get(id=assignment_id)
        except AssignmentModel.DoesNotExist:
            return Response({'detail': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'shuffle_questions' in request.data:
            assignment.shuffle_questions = request.data['shuffle_questions']
        if 'shuffle_answers' in request.data:
            assignment.shuffle_answers = request.data['shuffle_answers']
        if 'show_result' in request.data:
            assignment.show_result = request.data['show_result']
        if 'time_limit' in request.data:
            assignment.time_limit = request.data['time_limit'] or None
        if 'attempts_allowed' in request.data:
            assignment.attempts_allowed = request.data['attempts_allowed'] or 1
        if 'max_score' in request.data:
            assignment.max_score = request.data['max_score'] or 100
        
        assignment.save()
        
        return Response({
            'id': assignment.id,
            'shuffle_questions': assignment.shuffle_questions,
            'shuffle_answers': assignment.shuffle_answers,
            'show_result': assignment.show_result,
            'time_limit': assignment.time_limit,
            'attempts_allowed': assignment.attempts_allowed,
            'max_score': assignment.max_score,
        })


class QuestionCreateView(APIView):
    """POST /api/v1/teacher/questions/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def post(self, request):
        assignment_id = request.data.get('assignment')
        question_text = request.data.get('question_text')
        
        if not assignment_id or not question_text:
            return Response({'detail': 'assignment and question_text are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get next order
        max_order = QuestionModel.objects.filter(assignment_id=assignment_id).count() + 1
        
        question = QuestionModel.objects.create(
            assignment_id=assignment_id,
            text=question_text,
            option_a=request.data.get('option_a', ''),
            option_b=request.data.get('option_b', ''),
            option_c=request.data.get('option_c', ''),
            option_d=request.data.get('option_d', ''),
            correct_answer=request.data.get('correct_answer', 'A'),
            points=request.data.get('points', 1),
            order=max_order,
        )
        
        return Response({
            'id': question.id,
            'question_text': question.text,
            'order': question.order,
        }, status=status.HTTP_201_CREATED)


class QuestionDetailView(APIView):
    """PATCH/DELETE /api/v1/teacher/questions/{id}/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def patch(self, request, question_id):
        try:
            question = QuestionModel.objects.get(id=question_id)
        except QuestionModel.DoesNotExist:
            return Response({'detail': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'question_text' in request.data:
            question.text = request.data['question_text']
        if 'option_a' in request.data:
            question.option_a = request.data['option_a']
        if 'option_b' in request.data:
            question.option_b = request.data['option_b']
        if 'option_c' in request.data:
            question.option_c = request.data['option_c']
        if 'option_d' in request.data:
            question.option_d = request.data['option_d']
        if 'correct_answer' in request.data:
            question.correct_answer = request.data['correct_answer']
        if 'points' in request.data:
            question.points = request.data['points']
        if 'order' in request.data:
            question.order = request.data['order']
        
        question.save()
        
        return Response({
            'id': question.id,
            'question_text': question.text,
        })
    
    def delete(self, request, question_id):
        try:
            question = QuestionModel.objects.get(id=question_id)
            question.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except QuestionModel.DoesNotExist:
            return Response({'detail': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)


class ImportQuestionsView(APIView):
    """POST /api/v1/teacher/assignments/{id}/import-questions/"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def post(self, request, assignment_id):
        try:
            assignment = AssignmentModel.objects.get(id=assignment_id)
        except AssignmentModel.DoesNotExist:
            return Response({'detail': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'file' not in request.FILES:
            return Response({'detail': 'Excel file is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        excel_file = request.FILES['file']
        
        try:
            from .....infrastructure.services.excel_parser import ExcelQuestionParser
            
            parser = ExcelQuestionParser()
            questions_data = parser.parse(excel_file, excel_file.name)
            
            # Get current max order
            max_order = QuestionModel.objects.filter(assignment=assignment).count()
            
            created_count = 0
            for idx, q_data in enumerate(questions_data, start=1):
                QuestionModel.objects.create(
                    assignment=assignment,
                    text=q_data.get('text', ''),
                    option_a=q_data.get('A', ''),
                    option_b=q_data.get('B', ''),
                    option_c=q_data.get('C', ''),
                    option_d=q_data.get('D', ''),
                    correct_answer=q_data.get('correct', 'A').upper(),
                    points=int(float(q_data.get('points', 1) or 1)),
                    order=max_order + idx,
                )
                created_count += 1
            
            return Response({
                'detail': f'Đã import {created_count} câu hỏi thành công',
                'created': created_count
            })
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CourseStudentsView(APIView):
    """GET /api/v1/teacher/courses/{course_id}/students/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request, course_id):
        # Check if user is teacher of this course
        is_teacher = EnrollmentModel.objects.filter(
            user=request.user,
            course_id=course_id,
            role_in_course='TEACHER'
        ).exists()
        
        if not is_teacher and not request.user.is_staff:
            return Response({'detail': 'Bạn không có quyền xem'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            course = CourseModel.objects.get(id=course_id)
        except CourseModel.DoesNotExist:
            return Response({'detail': 'Khóa học không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        
        enrollments = EnrollmentModel.objects.filter(
            course_id=course_id,
            role_in_course='STUDENT'
        ).select_related('user', 'user__profile')
        
        students = []
        for enrollment in enrollments:
            avatar_url = None
            if hasattr(enrollment.user, 'profile') and enrollment.user.profile and enrollment.user.profile.avatar:
                avatar_url = request.build_absolute_uri(enrollment.user.profile.avatar.url)
            students.append({
                'id': enrollment.user.id,
                'full_name': enrollment.user.full_name,
                'email': enrollment.user.email,
                'avatar': avatar_url,
                'joined_at': enrollment.joined_at,
            })
        
        return Response({
            'course_title': course.title,
            'students': students
        })


class StudentGradesView(APIView):
    """GET /api/v1/teacher/courses/{course_id}/students/{student_id}/grades/"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request, course_id, student_id):
        # Check if user is teacher of this course
        is_teacher = EnrollmentModel.objects.filter(
            user=request.user,
            course_id=course_id,
            role_in_course='TEACHER'
        ).exists()
        
        if not is_teacher and not request.user.is_staff:
            return Response({'detail': 'Bạn không có quyền xem'}, status=status.HTTP_403_FORBIDDEN)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            student = User.objects.select_related('profile').get(id=student_id)
        except User.DoesNotExist:
            return Response({'detail': 'Học viên không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get all assignments in this course
        assignment_ids = AssignmentModel.objects.filter(
            lesson__module__course_id=course_id
        ).values_list('id', flat=True)
        
        # Get attempts by this student for those assignments
        attempts = AttemptModel.objects.filter(
            user_id=student_id,
            assignment_id__in=assignment_ids
        ).select_related('assignment').order_by('-submitted_at')
        
        status_display_map = {
            'IN_PROGRESS': 'Đang làm',
            'SUBMITTED': 'Đã nộp',
            'GRADED': 'Đã chấm điểm'
        }
        
        attempts_data = []
        for attempt in attempts:
            attempts_data.append({
                'id': attempt.id,
                'assignment_id': attempt.assignment.id,
                'assignment_title': attempt.assignment.title,
                'assignment_type': attempt.assignment.type,
                'score': attempt.score,
                'max_score': attempt.assignment.max_score,
                'status': attempt.status,
                'status_display': status_display_map.get(attempt.status, attempt.status),
                'submitted_at': attempt.submitted_at,
                'feedback': attempt.feedback or '',
            })
        
        avatar_url = None
        if hasattr(student, 'profile') and student.profile and student.profile.avatar:
            avatar_url = request.build_absolute_uri(student.profile.avatar.url)
        
        return Response({
            'student': {
                'id': student.id,
                'full_name': student.full_name,
                'email': student.email,
                'avatar': avatar_url,
            },
            'attempts': attempts_data
        })

