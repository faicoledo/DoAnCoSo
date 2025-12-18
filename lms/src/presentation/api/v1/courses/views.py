"""
Courses API Views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import CourseListOutputSerializer, CourseDetailOutputSerializer
from .....application.use_cases.course import (
    ListCoursesUseCase,
    GetCourseDetailUseCase,
    ListCoursesInput,
    GetCourseDetailInput,
)
from .....infrastructure.persistence.repositories import DjangoCourseRepository
from .....domain.exceptions.course import CourseNotFoundException


class CourseListView(APIView):
    """
    GET /api/v1/courses/
    List all courses with optional filters
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Extract query params
        status_filter = request.query_params.get('status')
        subject_id = request.query_params.get('subject_id')
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))
        
        # Create input DTO
        input_dto = ListCoursesInput(
            status=status_filter,
            subject_id=int(subject_id) if subject_id else None,
            limit=limit,
            offset=offset,
        )
        
        # Execute use case
        course_repo = DjangoCourseRepository()
        use_case = ListCoursesUseCase(course_repo)
        
        results = use_case.execute(input_dto)
        
        # Serialize output
        serializer = CourseListOutputSerializer([r.__dict__ for r in results], many=True)
        return Response(serializer.data)


class CourseDetailView(APIView):
    """
    GET /api/v1/courses/{id}/
    Get course detail with modules and lessons
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id):
        # Create input DTO
        input_dto = GetCourseDetailInput(
            course_id=course_id,
            include_modules=True,
        )
        
        # Execute use case
        course_repo = DjangoCourseRepository()
        use_case = GetCourseDetailUseCase(course_repo)
        
        try:
            result = use_case.execute(input_dto)
        except CourseNotFoundException as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Serialize output
        serializer = CourseDetailOutputSerializer(result.__dict__)
        return Response(serializer.data)

