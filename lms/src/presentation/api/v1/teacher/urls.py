"""
Teacher API URLs
"""
from django.urls import path
from .views import (
    TeacherStatsView,
    TeacherCoursesView,
    TeacherStudentsView,
    TeacherSubmissionsView,
    AssignmentSubmissionsView,
    ModuleCreateView,
    ModuleDetailView,
    LessonCreateView,
    LessonDetailView,
    ResourceCreateView,
    ResourceDetailView,
    AssignmentCreateView,
    AssignmentDetailView,
    UpdateOrderView,
    AssignmentQuestionsView,
    AssignmentSettingsView,
    QuestionCreateView,
    QuestionDetailView,
    ImportQuestionsView,
    CourseStudentsView,
    StudentGradesView,
)

urlpatterns = [
    path('stats/', TeacherStatsView.as_view(), name='teacher_stats'),
    path('courses/', TeacherCoursesView.as_view(), name='teacher_courses'),
    path('students/', TeacherStudentsView.as_view(), name='teacher_students'),
    path('submissions/', TeacherSubmissionsView.as_view(), name='teacher_submissions'),
    path('assignments/<int:assignment_id>/submissions/', AssignmentSubmissionsView.as_view(), name='assignment_submissions'),
    
    # Content management
    path('modules/', ModuleCreateView.as_view(), name='module_create'),
    path('modules/<int:module_id>/', ModuleDetailView.as_view(), name='module_detail'),
    path('lessons/', LessonCreateView.as_view(), name='lesson_create'),
    path('lessons/<int:lesson_id>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('resources/', ResourceCreateView.as_view(), name='resource_create'),
    path('resources/<int:resource_id>/', ResourceDetailView.as_view(), name='resource_detail'),
    path('assignments/', AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignments/<int:assignment_id>/', AssignmentDetailView.as_view(), name='assignment_detail'),
    path('update-order/', UpdateOrderView.as_view(), name='update_order'),
    
    # Question management
    path('assignments/<int:assignment_id>/questions/', AssignmentQuestionsView.as_view(), name='assignment_questions'),
    path('assignments/<int:assignment_id>/settings/', AssignmentSettingsView.as_view(), name='assignment_settings'),
    path('assignments/<int:assignment_id>/import-questions/', ImportQuestionsView.as_view(), name='import_questions'),
    path('questions/', QuestionCreateView.as_view(), name='question_create'),
    path('questions/<int:question_id>/', QuestionDetailView.as_view(), name='question_detail'),
    
    # Student management by course
    path('courses/<int:course_id>/students/', CourseStudentsView.as_view(), name='course_students'),
    path('courses/<int:course_id>/students/<int:student_id>/grades/', StudentGradesView.as_view(), name='student_grades'),
]

