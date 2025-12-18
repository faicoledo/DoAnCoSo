"""
Catalog API Views

API cho nội dung khóa học:
1. Danh sách khóa học của user (my-courses)
2. Chi tiết khóa học với modules và lessons
3. Chi tiết bài học với resources và assignments
"""
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from django.shortcuts import get_object_or_404

from .serializers import (
    MyCourseSerializer,
    CourseDetailSerializer,
    LessonDetailSerializer,
)
from .permissions import IsEnrolledInCourse, IsEnrolledInLessonCourse
from .....infrastructure.persistence.models.enrollment import EnrollmentModel
from .....infrastructure.persistence.models.course import (
    CourseModel, ModuleModel, LessonModel
)
from .....infrastructure.persistence.models.content import ResourceModel
from .....infrastructure.persistence.models.assessment import AssignmentModel
from .....infrastructure.persistence.models.course import SubjectModel


class SubjectListView(APIView):
    """
    GET /api/v1/catalog/subjects/
    
    Lấy danh sách tất cả môn học.
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        subjects = SubjectModel.objects.all().order_by('title')
        results = [
            {
                'id': s.id,
                'name': s.title,
                'description': s.description or ''
            }
            for s in subjects
        ]
        return Response(results)


class CourseListView(APIView):
    """
    GET /api/v1/catalog/courses/
    
    Lấy danh sách tất cả khóa học.
    
    Query params:
    - subject: filter by subject_id
    - search: search by title
    - page: page number
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        courses = CourseModel.objects.select_related('subject').order_by('-created_at')
        
        # Filter by subject
        subject_id = request.query_params.get('subject')
        if subject_id:
            courses = courses.filter(subject_id=subject_id)
        
        # Search by title
        search = request.query_params.get('search')
        if search:
            courses = courses.filter(title__icontains=search)
        
        # Simple pagination
        page = int(request.query_params.get('page', 1))
        page_size = 12
        start = (page - 1) * page_size
        end = start + page_size
        
        total = courses.count()
        courses = courses[start:end]
        
        # Get teacher info
        from .....infrastructure.persistence.models.enrollment import EnrollmentModel
        
        results = []
        for course in courses:
            # Find teacher
            teacher_enrollment = EnrollmentModel.objects.filter(
                course=course,
                role_in_course='TEACHER'
            ).select_related('user').first()
            
            teacher_info = None
            if teacher_enrollment:
                teacher_info = {
                    'id': teacher_enrollment.user.id,
                    'full_name': teacher_enrollment.user.full_name or teacher_enrollment.user.email
                }
            
            results.append({
                'id': course.id,
                'title': course.title,
                'description': course.description or '',
                'thumbnail': None,  # Model không có thumbnail
                'subject': {
                    'id': course.subject.id,
                    'name': course.subject.title
                } if course.subject else None,
                'teacher': teacher_info,
                'is_published': True,  # Mặc định là published
                'created_at': course.created_at,
            })
        
        return Response({
            'count': total,
            'next': f'?page={page + 1}' if end < total else None,
            'previous': f'?page={page - 1}' if page > 1 else None,
            'results': results
        })


class MyCoursesView(APIView):
    """
    GET /api/v1/catalog/my-courses/
    
    Lấy danh sách các khóa học mà user hiện tại đã đăng ký.
    Bao gồm cả vai trò học viên, giảng viên và trợ giảng.
    
    Query params:
    - status: UPCOMING, ONGOING, COMPLETED (optional)
    - role: STUDENT, TEACHER, TA (optional)
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        # Base queryset
        enrollments = EnrollmentModel.objects.filter(
            user=request.user
        ).select_related(
            'course',
            'course__subject'
        ).order_by('-joined_at')
        
        # Filter by role if provided
        role_filter = request.query_params.get('role')
        if role_filter:
            enrollments = enrollments.filter(role_in_course=role_filter.upper())
        
        # Build response data
        results = []
        for enrollment in enrollments:
            course = enrollment.course
            
            # Compute status
            computed_status = course.computed_status
            
            # Filter by status if provided
            status_filter = request.query_params.get('status')
            if status_filter and computed_status != status_filter.upper():
                continue
            
            # Get teacher info
            teacher_enrollment = EnrollmentModel.objects.filter(
                course=course,
                role_in_course='TEACHER'
            ).select_related('user').first()
            
            teacher_info = None
            if teacher_enrollment:
                teacher_info = {
                    'id': teacher_enrollment.user.id,
                    'full_name': teacher_enrollment.user.full_name or teacher_enrollment.user.email
                }
            
            results.append({
                'id': course.id,
                'title': course.title,
                'description': course.description or '',
                'thumbnail': None,
                'subject': {
                    'id': course.subject.id,
                    'name': course.subject.title
                } if course.subject else None,
                'teacher': teacher_info,
                'is_published': True,
                'created_at': course.created_at,
                'status': computed_status,
                'status_display': course.computed_status_display,
                'role_in_course': enrollment.role_in_course,
            })
        
        # Sort: ONGOING first, then UPCOMING, then COMPLETED
        status_order = {'ONGOING': 0, 'UPCOMING': 1, 'COMPLETED': 2}
        results.sort(key=lambda x: (status_order.get(x['status'], 3), x['title']))
        
        return Response({
            'count': len(results),
            'next': None,
            'previous': None,
            'results': results
        })


class CourseDetailView(APIView):
    """
    GET /api/v1/catalog/courses/{course_id}/
    
    Lấy chi tiết khóa học kèm danh sách chương và bài học.
    Chỉ user đã enroll mới được xem.
    """
    permission_classes = [IsAuthenticated, IsEnrolledInCourse]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request, course_id):
        # Get course with related data
        course = get_object_or_404(
            CourseModel.objects.select_related('subject'),
            pk=course_id
        )
        
        # Get modules with lessons
        modules = ModuleModel.objects.filter(
            course=course
        ).prefetch_related('lessons').order_by('order')
        
        # Get user's enrollment
        enrollment = EnrollmentModel.objects.filter(
            user=request.user,
            course=course
        ).first()
        
        # Build modules data
        modules_data = []
        total_lessons = 0
        
        for module in modules:
            lessons = list(module.lessons.order_by('order'))
            total_lessons += len(lessons)
            
            lessons_data = []
            for lesson in lessons:
                # Get resources for this lesson
                resources = ResourceModel.objects.filter(lesson=lesson).order_by('order')
                resources_data = [
                    {
                        'id': r.id,
                        'title': r.title,
                        'type': r.type,
                    }
                    for r in resources
                ]
                
                # Get assignments for this lesson
                assignments = AssignmentModel.objects.filter(lesson=lesson).order_by('id')
                assignments_data = [
                    {
                        'id': a.id,
                        'title': a.title,
                        'type': a.type,
                    }
                    for a in assignments
                ]
                
                lessons_data.append({
                    'id': lesson.id,
                    'title': lesson.title,
                    'description': getattr(lesson, 'description', '') or '',
                    'order': lesson.order,
                    'resources': resources_data,
                    'assignments': assignments_data,
                })
            
            modules_data.append({
                'id': module.id,
                'title': module.title,
                'description': getattr(module, 'description', '') or '',
                'order': module.order,
                'lessons': lessons_data,
                'lessons_count': len(lessons),
            })
        
        # Build response
        result = {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'status': course.computed_status,
            'status_display': course.computed_status_display,
            'start_date': course.start_date,
            'end_date': course.end_date,
            'subject': {
                'id': course.subject.id,
                'title': course.subject.title,
            },
            'modules': modules_data,
            'total_modules': len(modules_data),
            'total_lessons': total_lessons,
        }
        
        # Add user's role if enrolled
        if enrollment:
            result['my_role'] = enrollment.role_in_course
            result['my_role_display'] = enrollment.get_role_in_course_display()
        
        serializer = CourseDetailSerializer(result)
        return Response(serializer.data)


class LessonDetailView(APIView):
    """
    GET /api/v1/catalog/lessons/{lesson_id}/
    
    Lấy chi tiết bài học kèm danh sách tài liệu và bài tập.
    Chỉ user đã enroll vào khóa học chứa lesson mới được xem.
    """
    permission_classes = [IsAuthenticated, IsEnrolledInLessonCourse]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request, lesson_id):
        # Get lesson with related data
        lesson = get_object_or_404(
            LessonModel.objects.select_related(
                'module',
                'module__course',
                'module__course__subject'
            ),
            pk=lesson_id
        )
        
        module = lesson.module
        course = module.course
        
        # Get resources
        resources = ResourceModel.objects.filter(
            lesson=lesson
        ).order_by('order')
        
        # Get assignments
        assignments = AssignmentModel.objects.filter(
            lesson=lesson
        ).order_by('start_at')
        
        # Get prev/next lessons for navigation
        all_lessons = LessonModel.objects.filter(
            module__course=course
        ).select_related('module').order_by('module__order', 'order')
        
        lesson_ids = list(all_lessons.values_list('id', flat=True))
        current_index = lesson_ids.index(lesson.id) if lesson.id in lesson_ids else -1
        
        prev_lesson = None
        next_lesson = None
        
        if current_index > 0:
            prev = all_lessons[current_index - 1]
            prev_lesson = {
                'id': prev.id,
                'title': prev.title,
                'order': prev.order,
            }
        
        if current_index < len(lesson_ids) - 1:
            next_l = all_lessons[current_index + 1]
            next_lesson = {
                'id': next_l.id,
                'title': next_l.title,
                'order': next_l.order,
            }
        
        # Build resources data
        resources_data = []
        for resource in resources:
            resource_data = {
                'id': resource.id,
                'type': resource.type,
                'type_display': resource.get_type_display(),
                'title': resource.title,
                'document_url': None,
                'video_url': None,
                'link_url': None,
                'text_content': None,
                'file_size': resource.file_size,
                'file_size_display': resource.file_size_display,
                'duration': resource.duration,
                'duration_display': resource.duration_display,
                'is_uploaded': resource.is_uploaded,
                'order': resource.order,
            }
            
            # Set URL based on type
            if resource.type == 'DOCUMENT' and resource.document_file:
                resource_data['document_url'] = request.build_absolute_uri(resource.document_file.url)
            elif resource.type == 'VIDEO':
                if resource.video_file:
                    resource_data['video_url'] = request.build_absolute_uri(resource.video_file.url)
                elif resource.video_url:
                    resource_data['video_url'] = resource.video_url
            elif resource.type == 'LINK':
                resource_data['link_url'] = resource.external_url
            elif resource.type == 'TEXT':
                resource_data['text_content'] = resource.text_content
            
            resources_data.append(resource_data)
        
        # Build assignments data
        now = timezone.now()
        assignments_data = []
        for assignment in assignments:
            is_available = True
            if assignment.start_at and now < assignment.start_at:
                is_available = False
            if assignment.end_at and now > assignment.end_at:
                is_available = False
            
            assignments_data.append({
                'id': assignment.id,
                'title': assignment.title,
                'type': assignment.type,
                'type_display': assignment.get_type_display(),
                'start_at': assignment.start_at,
                'end_at': assignment.end_at,
                'time_limit': assignment.time_limit,
                'attempts_allowed': assignment.attempts_allowed,
                'is_available': is_available,
            })
        
        # Ghi activity log khi xem bài học
        try:
            from .....application.use_cases.activity_log import LogActivityUseCase, LogActivityInput
            log_use_case = LogActivityUseCase()
            log_use_case.execute(LogActivityInput(
                user_id=request.user.id,
                action_type='VIEW_LESSON',
                target_type='lesson',
                target_id=lesson.id,
                metadata={'course_id': course.id, 'module_id': module.id}
            ))
        except Exception:
            pass  # Bỏ qua lỗi log để không ảnh hưởng đến flow chính
        
        # Build response
        result = {
            'id': lesson.id,
            'title': lesson.title,
            'content': lesson.content,
            'order': lesson.order,
            'module': {
                'id': module.id,
                'title': module.title,
                'order': module.order,
            },
            'course': {
                'id': course.id,
                'title': course.title,
                'status': course.computed_status,
                'status_display': course.computed_status_display,
            },
            'resources': resources_data,
            'assignments': assignments_data,
            'resources_count': len(resources_data),
            'assignments_count': len(assignments_data),
            'prev_lesson': prev_lesson,
            'next_lesson': next_lesson,
        }
        
        serializer = LessonDetailSerializer(result)
        return Response(serializer.data)

