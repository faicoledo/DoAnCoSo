"""
Catalog API URLs

Endpoints cho nội dung khóa học:
- /subjects/ - Danh sách môn học
- /courses/ - Danh sách khóa học
- /my-courses/ - Danh sách khóa học của user
- /courses/{id}/ - Chi tiết khóa học
- /lessons/{id}/ - Chi tiết bài học
"""
from django.urls import path

from .views import SubjectListView, CourseListView, MyCoursesView, CourseDetailView, LessonDetailView

urlpatterns = [
    # Danh sách môn học
    path('subjects/', SubjectListView.as_view(), name='subject_list'),
    
    # Danh sách khóa học công khai
    path('courses/', CourseListView.as_view(), name='course_list'),
    
    # Danh sách khóa học của user hiện tại
    path('my-courses/', MyCoursesView.as_view(), name='my_courses'),
    
    # Chi tiết khóa học (kèm modules và lessons)
    path('courses/<int:course_id>/', CourseDetailView.as_view(), name='course_detail'),
    
    # Chi tiết bài học (kèm resources và assignments)
    path('lessons/<int:lesson_id>/', LessonDetailView.as_view(), name='lesson_detail'),
]

