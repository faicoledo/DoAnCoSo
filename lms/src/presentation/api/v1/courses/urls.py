"""
Courses API URLs
"""
from django.urls import path

from .views import CourseListView, CourseDetailView

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('<int:course_id>/', CourseDetailView.as_view(), name='course_detail'),
]

