"""
Admin API URLs
"""
from django.urls import path
from .views import (
    AdminStatsView,
    AdminUsersView,
    AdminUserDetailView,
    AdminSubjectsView,
    AdminSubjectDetailView,
    AdminCoursesView,
    AdminCourseDetailView,
    AdminEnrollmentsView,
    AdminEnrollmentDetailView,
)

urlpatterns = [
    path('stats/', AdminStatsView.as_view(), name='admin_stats'),
    
    # Users
    path('users/', AdminUsersView.as_view(), name='admin_users'),
    path('users/<int:user_id>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
    
    # Subjects
    path('subjects/', AdminSubjectsView.as_view(), name='admin_subjects'),
    path('subjects/<int:subject_id>/', AdminSubjectDetailView.as_view(), name='admin_subject_detail'),
    
    # Courses
    path('courses/', AdminCoursesView.as_view(), name='admin_courses'),
    path('courses/<int:course_id>/', AdminCourseDetailView.as_view(), name='admin_course_detail'),
    
    # Enrollments
    path('enrollments/', AdminEnrollmentsView.as_view(), name='admin_enrollments'),
    path('enrollments/<int:enrollment_id>/', AdminEnrollmentDetailView.as_view(), name='admin_enrollment_detail'),
]

