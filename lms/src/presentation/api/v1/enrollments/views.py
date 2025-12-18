"""
Enrollments API Views

⚠️ LƯU Ý: 
- Việc đăng ký khóa học (enroll/unenroll) chỉ được thực hiện bởi Admin qua Django Admin.
- Sinh viên và giảng viên KHÔNG TỰ đăng ký trên hệ thống này.
- API chỉ cho phép:
  + Xem danh sách khóa học đã đăng ký (MyCoursesView)
  + Xem danh sách học viên trong khóa học - dành cho giảng viên (CourseStudentsView)
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from .serializers import EnrollmentOutputSerializer, StudentListOutputSerializer
from .....application.use_cases.enrollment import (
    GetMyCoursesUseCase,
    GetCourseStudentsUseCase,
    GetMyCoursesInput,
    GetCourseStudentsInput,
)
from .....infrastructure.persistence.repositories import (
    DjangoEnrollmentRepository,
    DjangoCourseRepository,
    DjangoUserRepository,
)
from .....domain.exceptions.course import CourseNotFoundException
from .....domain.exceptions.user import InsufficientPermissionsException


class MyCoursesView(APIView):
    """
    GET /api/v1/enrollments/my-courses/
    
    Lấy danh sách các khóa học mà user hiện tại đã được đăng ký.
    Bao gồm cả khóa học với vai trò học viên, giảng viên hoặc trợ giảng.
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        # Create input DTO
        input_dto = GetMyCoursesInput(user_id=request.user.id)
        
        # Execute use case
        enrollment_repo = DjangoEnrollmentRepository()
        course_repo = DjangoCourseRepository()
        use_case = GetMyCoursesUseCase(enrollment_repo, course_repo)
        
        results = use_case.execute(input_dto)
        
        # Enrich with computed status
        enriched_results = []
        for r in results:
            data = r.__dict__.copy()
            # Get course to compute status
            course = course_repo.find_by_id(r.course_id)
            if course:
                data['status'] = course.status.value
                data['status_display'] = course.status.display_name
            enriched_results.append(data)
        
        # Serialize output
        serializer = EnrollmentOutputSerializer(enriched_results, many=True)
        return Response({
            'count': len(results),
            'results': serializer.data
        })


class CourseStudentsView(APIView):
    """
    GET /api/v1/enrollments/courses/{course_id}/students/
    
    Lấy danh sách học viên trong một khóa học.
    Chỉ giảng viên hoặc trợ giảng của khóa học mới có quyền xem.
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request, course_id):
        # Create input DTO
        input_dto = GetCourseStudentsInput(
            user_id=request.user.id,
            course_id=course_id,
        )
        
        # Execute use case
        enrollment_repo = DjangoEnrollmentRepository()
        course_repo = DjangoCourseRepository()
        user_repo = DjangoUserRepository()
        use_case = GetCourseStudentsUseCase(enrollment_repo, course_repo, user_repo)
        
        try:
            results = use_case.execute(input_dto)
        except CourseNotFoundException as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except InsufficientPermissionsException as e:
            return Response(
                {'detail': 'Bạn không có quyền xem danh sách học viên của khóa học này.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = StudentListOutputSerializer([r.__dict__ for r in results], many=True)
        return Response({
            'course_id': course_id,
            'count': len(results),
            'results': serializer.data
        })
