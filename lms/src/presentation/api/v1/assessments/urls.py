"""
Assessment API URLs

Endpoints cho chức năng Quiz:

Giáo viên:
- POST   /assignments/                          - Tạo bài tập
- GET    /assignments/{id}/questions/           - Xem danh sách câu hỏi
- POST   /assignments/{id}/questions/           - Thêm câu hỏi
- PUT    /questions/{id}/                       - Sửa câu hỏi
- DELETE /questions/{id}/                       - Xóa câu hỏi
- POST   /assignments/{id}/import-excel/        - Import từ Excel

Học viên:
- POST   /assignments/{id}/start/               - Bắt đầu làm bài
- POST   /attempts/{id}/submit/                 - Nộp bài
- GET    /attempts/{id}/result/                 - Xem kết quả
"""
from django.urls import path

from .views import (
    CreateAssignmentView,
    AssignmentQuestionsView,
    QuestionDetailView,
    ImportExcelView,
    StartAttemptView,
    SubmitAttemptView,
    AttemptResultView,
    MyAttemptsCountView,
    MyAttemptsListView,
    AssignmentInfoView,
    SubmitFileAssignmentView,
    GradeAttemptView,
)

urlpatterns = [
    # Assignment management
    path('assignments/', CreateAssignmentView.as_view(), name='create_assignment'),
    path('assignments/<int:assignment_id>/questions/', AssignmentQuestionsView.as_view(), name='assignment_questions'),
    path('assignments/<int:assignment_id>/import-excel/', ImportExcelView.as_view(), name='import_excel'),
    
    # Question management
    path('questions/<int:question_id>/', QuestionDetailView.as_view(), name='question_detail'),
    
    # Student actions
    path('assignments/<int:assignment_id>/info/', AssignmentInfoView.as_view(), name='assignment_info'),
    path('assignments/<int:assignment_id>/start/', StartAttemptView.as_view(), name='start_attempt'),
    path('assignments/<int:assignment_id>/submit-file/', SubmitFileAssignmentView.as_view(), name='submit_file'),
    path('attempts/<int:attempt_id>/submit/', SubmitAttemptView.as_view(), name='submit_attempt'),
    path('attempts/<int:attempt_id>/result/', AttemptResultView.as_view(), name='attempt_result'),
    path('attempts/<int:attempt_id>/grade/', GradeAttemptView.as_view(), name='grade_attempt'),
    
    # Stats
    path('my-attempts/count/', MyAttemptsCountView.as_view(), name='my_attempts_count'),
    path('my-attempts/', MyAttemptsListView.as_view(), name='my_attempts_list'),
]




