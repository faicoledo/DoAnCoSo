"""
Enrollments API URLs

⚠️ LƯU Ý: 
- Việc đăng ký khóa học (enroll/unenroll) chỉ được thực hiện bởi Admin qua Django Admin.
- Sinh viên và giảng viên KHÔNG TỰ đăng ký trên hệ thống này.
- API chỉ cho phép xem danh sách khóa học đã đăng ký.
"""
from django.urls import path

from .views import MyCoursesView, CourseStudentsView

urlpatterns = [
    # Xem danh sách khóa học của user hiện tại
    path('my-courses/', MyCoursesView.as_view(), name='my_courses'),
    
    # Xem danh sách học viên trong khóa học (chỉ dành cho giảng viên/TA)
    path('courses/<int:course_id>/students/', CourseStudentsView.as_view(), name='course_students'),
]
