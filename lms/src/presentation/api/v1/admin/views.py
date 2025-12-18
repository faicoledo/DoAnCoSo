"""
Admin API Views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from django.contrib.auth import get_user_model
from django.db.models import Count

from .....infrastructure.persistence.models.course import CourseModel, SubjectModel, ModuleModel
from .....infrastructure.persistence.models.enrollment import EnrollmentModel
from .....infrastructure.persistence.models.assessment import AssignmentModel, AttemptModel
from .....infrastructure.persistence.models.user import UserProfileModel

User = get_user_model()


class AdminStatsView(APIView):
    """GET /api/v1/admin/stats/"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        total_users = User.objects.count()
        total_students = UserProfileModel.objects.filter(role='STUDENT').count()
        total_teachers = UserProfileModel.objects.filter(role='TEACHER').count()
        total_courses = CourseModel.objects.count()
        total_subjects = SubjectModel.objects.count()
        total_enrollments = EnrollmentModel.objects.count()
        total_assignments = AssignmentModel.objects.count()
        total_attempts = AttemptModel.objects.count()
        
        return Response({
            'total_users': total_users,
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_courses': total_courses,
            'total_subjects': total_subjects,
            'total_enrollments': total_enrollments,
            'total_assignments': total_assignments,
            'total_attempts': total_attempts,
        })


class AdminUsersView(APIView):
    """
    GET /api/v1/admin/users/ - List users
    POST /api/v1/admin/users/ - Create user
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        users = User.objects.select_related('profile').all().order_by('-date_joined')
        
        results = []
        for user in users:
            avatar_url = None
            role = 'STUDENT'
            role_display = 'Học viên'
            
            if hasattr(user, 'profile') and user.profile:
                if user.profile.avatar:
                    avatar_url = request.build_absolute_uri(user.profile.avatar.url)
                role = user.profile.role
                role_display = {
                    'STUDENT': 'Học viên',
                    'TEACHER': 'Giảng viên',
                    'ADMIN': 'Quản trị viên'
                }.get(role, role)
            
            results.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': role,
                'role_display': role_display,
                'avatar': avatar_url,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'date_joined': user.date_joined,
            })
        
        return Response(results)
    
    def post(self, request):
        data = request.data
        
        # Validate required fields
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return Response({'detail': 'Username, email và password là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if username exists
        if User.objects.filter(username=data['username']).exists():
            return Response({'detail': 'Username đã tồn tại'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email exists
        if User.objects.filter(email=data['email']).exists():
            return Response({'detail': 'Email đã tồn tại'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
        )
        
        # Update or create profile
        profile, _ = UserProfileModel.objects.get_or_create(user=user)
        profile.full_name = data.get('full_name', '')
        profile.role = data.get('role', 'STUDENT')
        profile.save()
        
        # Set staff status for admin
        if data.get('role') == 'ADMIN':
            user.is_staff = True
            user.save()
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'Tạo người dùng thành công'
        }, status=status.HTTP_201_CREATED)


class AdminUserDetailView(APIView):
    """
    GET /api/v1/admin/users/{id}/ - Get user detail
    PATCH /api/v1/admin/users/{id}/ - Update user
    DELETE /api/v1/admin/users/{id}/ - Delete user
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request, user_id):
        try:
            user = User.objects.select_related('profile').get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'Người dùng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        
        avatar_url = None
        role = 'STUDENT'
        if hasattr(user, 'profile') and user.profile:
            if user.profile.avatar:
                avatar_url = request.build_absolute_uri(user.profile.avatar.url)
            role = user.profile.role
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': role,
            'avatar': avatar_url,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'date_joined': user.date_joined,
            'phone': user.profile.phone if hasattr(user, 'profile') and user.profile else '',
            'bio': user.profile.bio if hasattr(user, 'profile') and user.profile else '',
        })
    
    def patch(self, request, user_id):
        try:
            user = User.objects.select_related('profile').get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'Người dùng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        
        # Update user fields
        if 'email' in data:
            if User.objects.filter(email=data['email']).exclude(pk=user_id).exists():
                return Response({'detail': 'Email đã tồn tại'}, status=status.HTTP_400_BAD_REQUEST)
            user.email = data['email']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        user.save()
        
        # Update profile
        profile, _ = UserProfileModel.objects.get_or_create(user=user)
        if 'full_name' in data:
            profile.full_name = data['full_name']
        if 'role' in data:
            profile.role = data['role']
            user.is_staff = data['role'] == 'ADMIN'
            user.save()
        if 'phone' in data:
            profile.phone = data['phone']
        if 'bio' in data:
            profile.bio = data['bio']
        profile.save()
        
        return Response({'message': 'Cập nhật thành công'})
    
    def delete(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'Người dùng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.id == request.user.id:
            return Response({'detail': 'Không thể xóa chính mình'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminSubjectsView(APIView):
    """
    GET /api/v1/admin/subjects/ - List subjects
    POST /api/v1/admin/subjects/ - Create subject
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        subjects = SubjectModel.objects.annotate(
            courses_count=Count('courses')
        ).order_by('title')
        
        results = []
        for subject in subjects:
            results.append({
                'id': subject.id,
                'title': subject.title,
                'description': subject.description or '',
                'courses_count': subject.courses_count,
            })
        
        return Response(results)
    
    def post(self, request):
        data = request.data
        
        if not data.get('title'):
            return Response({'detail': 'Tên môn học là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)
        
        subject = SubjectModel.objects.create(
            title=data['title'],
            description=data.get('description', ''),
        )
        
        return Response({
            'id': subject.id,
            'title': subject.title,
            'message': 'Tạo môn học thành công'
        }, status=status.HTTP_201_CREATED)


class AdminSubjectDetailView(APIView):
    """
    PATCH /api/v1/admin/subjects/{id}/ - Update subject
    DELETE /api/v1/admin/subjects/{id}/ - Delete subject
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def patch(self, request, subject_id):
        try:
            subject = SubjectModel.objects.get(pk=subject_id)
        except SubjectModel.DoesNotExist:
            return Response({'detail': 'Môn học không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        if 'title' in data:
            subject.title = data['title']
        if 'description' in data:
            subject.description = data['description']
        subject.save()
        
        return Response({'message': 'Cập nhật thành công'})
    
    def delete(self, request, subject_id):
        try:
            subject = SubjectModel.objects.get(pk=subject_id)
        except SubjectModel.DoesNotExist:
            return Response({'detail': 'Môn học không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        
        if subject.courses.exists():
            return Response({'detail': 'Không thể xóa môn học đã có khóa học'}, status=status.HTTP_400_BAD_REQUEST)
        
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminCoursesView(APIView):
    """
    GET /api/v1/admin/courses/ - List courses
    POST /api/v1/admin/courses/ - Create course
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        from django.db.models import Q
        courses = CourseModel.objects.select_related('subject').order_by('-created_at')
        
        results = []
        for course in courses:
            results.append({
                'id': course.id,
                'title': course.title,
                'description': course.description or '',
                'subject': {
                    'id': course.subject.id,
                    'title': course.subject.title
                } if course.subject else None,
                'status': course.computed_status,
                'status_display': course.computed_status_display,
                'start_date': course.start_date,
                'end_date': course.end_date,
                'total_students': EnrollmentModel.objects.filter(course=course, role_in_course='STUDENT').count(),
                'total_modules': course.modules.count(),
            })
        
        return Response(results)
    
    def post(self, request):
        data = request.data
        
        if not data.get('title'):
            return Response({'detail': 'Tên khóa học là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)
        
        course = CourseModel.objects.create(
            title=data['title'],
            description=data.get('description', ''),
            subject_id=data.get('subject_id'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
        )
        
        return Response({
            'id': course.id,
            'title': course.title,
            'message': 'Tạo khóa học thành công'
        }, status=status.HTTP_201_CREATED)


class AdminCourseDetailView(APIView):
    """
    GET /api/v1/admin/courses/{id}/ - Get course detail
    PATCH /api/v1/admin/courses/{id}/ - Update course
    DELETE /api/v1/admin/courses/{id}/ - Delete course
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request, course_id):
        try:
            course = CourseModel.objects.select_related('subject').get(pk=course_id)
        except CourseModel.DoesNotExist:
            return Response({'detail': 'Khóa học không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'id': course.id,
            'title': course.title,
            'description': course.description or '',
            'subject': {
                'id': course.subject.id,
                'title': course.subject.title
            } if course.subject else None,
            'status': course.computed_status,
            'status_display': course.computed_status_display,
            'start_date': course.start_date,
            'end_date': course.end_date,
        })
    
    def patch(self, request, course_id):
        try:
            course = CourseModel.objects.get(pk=course_id)
        except CourseModel.DoesNotExist:
            return Response({'detail': 'Khóa học không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        if 'title' in data:
            course.title = data['title']
        if 'description' in data:
            course.description = data['description']
        if 'subject_id' in data:
            course.subject_id = data['subject_id']
        if 'start_date' in data:
            course.start_date = data['start_date']
        if 'end_date' in data:
            course.end_date = data['end_date']
        course.save()
        
        return Response({'message': 'Cập nhật thành công'})
    
    def delete(self, request, course_id):
        try:
            course = CourseModel.objects.get(pk=course_id)
        except CourseModel.DoesNotExist:
            return Response({'detail': 'Khóa học không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminEnrollmentsView(APIView):
    """
    GET /api/v1/admin/enrollments/ - List enrollments
    POST /api/v1/admin/enrollments/ - Create enrollment
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        course_id = request.query_params.get('course')
        
        enrollments = EnrollmentModel.objects.select_related('user', 'user__profile', 'course')
        if course_id:
            enrollments = enrollments.filter(course_id=course_id)
        enrollments = enrollments.order_by('-joined_at')
        
        results = []
        for enrollment in enrollments:
            avatar_url = None
            if hasattr(enrollment.user, 'profile') and enrollment.user.profile and enrollment.user.profile.avatar:
                avatar_url = request.build_absolute_uri(enrollment.user.profile.avatar.url)
            
            results.append({
                'id': enrollment.id,
                'user': {
                    'id': enrollment.user.id,
                    'full_name': enrollment.user.full_name,
                    'email': enrollment.user.email,
                    'avatar': avatar_url,
                },
                'course': {
                    'id': enrollment.course.id,
                    'title': enrollment.course.title,
                },
                'role_in_course': enrollment.role_in_course,
                'role_display': 'Giảng viên' if enrollment.role_in_course == 'TEACHER' else 'Học viên',
                'joined_at': enrollment.joined_at,
            })
        
        return Response(results)
    
    def post(self, request):
        data = request.data
        
        if not data.get('user_id') or not data.get('course_id'):
            return Response({'detail': 'User và Course là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if enrollment exists
        if EnrollmentModel.objects.filter(user_id=data['user_id'], course_id=data['course_id']).exists():
            return Response({'detail': 'Người dùng đã được đăng ký vào khóa học này'}, status=status.HTTP_400_BAD_REQUEST)
        
        enrollment = EnrollmentModel.objects.create(
            user_id=data['user_id'],
            course_id=data['course_id'],
            role_in_course=data.get('role_in_course', 'STUDENT'),
        )
        
        return Response({
            'id': enrollment.id,
            'message': 'Đăng ký thành công'
        }, status=status.HTTP_201_CREATED)


class AdminEnrollmentDetailView(APIView):
    """DELETE /api/v1/admin/enrollments/{id}/ - Delete enrollment"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def delete(self, request, enrollment_id):
        try:
            enrollment = EnrollmentModel.objects.get(pk=enrollment_id)
        except EnrollmentModel.DoesNotExist:
            return Response({'detail': 'Đăng ký không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        
        enrollment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

