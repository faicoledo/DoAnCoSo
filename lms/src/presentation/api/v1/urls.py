"""
API v1 URL Configuration
"""
from django.urls import path, include

urlpatterns = [
    # Authentication
    path('auth/', include('src.presentation.api.v1.auth.urls')),
    
    # Catalog - Nội dung khóa học (cho học viên/giảng viên)
    path('catalog/', include('src.presentation.api.v1.catalog.urls')),
    
    # Courses - Quản lý khóa học (legacy, có thể xóa sau)
    path('courses/', include('src.presentation.api.v1.courses.urls')),
    
    # Enrollments - Xem đăng ký
    path('enrollments/', include('src.presentation.api.v1.enrollments.urls')),
    
    # Assessments - Quiz & Bài tập
    path('assessments/', include('src.presentation.api.v1.assessments.urls')),
    
    # Notifications
    path('notifications/', include('src.presentation.api.v1.notifications.urls')),
    
    # Comments
    path('comments/', include('src.presentation.api.v1.comments.urls')),
    
    # Activity Logs
    path('activity-logs/', include('src.presentation.api.v1.activity_logs.urls')),
    
    # Teacher
    path('teacher/', include('src.presentation.api.v1.teacher.urls')),
    
    # Admin
    path('admin/', include('src.presentation.api.v1.admin.urls')),
]

