"""
Management command để gửi notification cho học viên khi bài tập sắp đến hạn (trước 1 giờ)

Chạy command này định kỳ (ví dụ mỗi 5 phút) bằng cron job hoặc Celery beat.

Usage:
    python manage.py notify_assignment_deadline
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from ...persistence.models.assessment import AssignmentModel
from ...persistence.models.enrollment import EnrollmentModel
from ...application.use_cases.notification import notify_students_on_assignment_deadline


class Command(BaseCommand):
    help = 'Gửi notification cho học viên khi bài tập sắp đến hạn (trước 1 giờ)'
    
    def handle(self, *args, **options):
        """Tìm các bài tập sắp đến hạn và gửi notification"""
        now = timezone.now()
        # Tìm các bài tập có deadline trong khoảng 55-65 phút nữa (để tránh gửi trùng)
        deadline_start = now + timedelta(minutes=55)
        deadline_end = now + timedelta(minutes=65)
        
        # Lấy các assignment sắp đến hạn
        assignments = AssignmentModel.objects.filter(
            end_at__gte=deadline_start,
            end_at__lte=deadline_end,
        ).select_related('lesson__module__course')
        
        notified_count = 0
        
        for assignment in assignments:
            try:
                course_id = assignment.lesson.module.course_id
                
                # Kiểm tra xem đã gửi notification chưa (tránh gửi trùng)
                # Có thể kiểm tra bằng cách xem notification đã tồn tại chưa
                from ...persistence.models.communication import NotificationModel
                already_notified = NotificationModel.objects.filter(
                    type=NotificationModel.NotificationType.ASSIGNMENT_DEADLINE,
                    related_object_type='assignment',
                    related_object_id=assignment.id,
                    created_at__gte=now - timedelta(hours=1),  # Trong 1 giờ qua
                ).exists()
                
                if not already_notified:
                    notify_students_on_assignment_deadline(
                        assignment_id=assignment.id,
                        course_id=course_id,
                    )
                    notified_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Đã gửi notification cho bài tập: {assignment.title} (ID: {assignment.id})'
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Lỗi khi gửi notification cho bài tập {assignment.id}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Hoàn thành! Đã gửi notification cho {notified_count} bài tập.'
            )
        )



