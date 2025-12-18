"""
Management command để gửi thông báo khi khóa học bắt đầu hoặc kết thúc.

Chạy hàng ngày qua cron job:
    python manage.py notify_course_status
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from src.infrastructure.persistence.models.course import CourseModel
from src.infrastructure.persistence.models.enrollment import EnrollmentModel
from src.infrastructure.persistence.models.communication import NotificationModel


class Command(BaseCommand):
    help = 'Gửi thông báo khi khóa học bắt đầu hoặc kết thúc'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Khóa học bắt đầu hôm nay
        starting_courses = CourseModel.objects.filter(start_date=today)
        for course in starting_courses:
            self.notify_course_start(course)
        
        # Khóa học kết thúc hôm nay
        ending_courses = CourseModel.objects.filter(end_date=today)
        for course in ending_courses:
            self.notify_course_end(course)
        
        # Khóa học sắp bắt đầu (trong 1 ngày)
        tomorrow = today + timedelta(days=1)
        upcoming_courses = CourseModel.objects.filter(start_date=tomorrow)
        for course in upcoming_courses:
            self.notify_course_starting_soon(course)
        
        # Khóa học sắp kết thúc (còn 3 ngày)
        ending_soon_date = today + timedelta(days=3)
        ending_soon_courses = CourseModel.objects.filter(end_date=ending_soon_date)
        for course in ending_soon_courses:
            self.notify_course_ending_soon(course)
        
        self.stdout.write(self.style.SUCCESS('Đã gửi thông báo khóa học'))

    def notify_course_start(self, course):
        """Thông báo khóa học đã bắt đầu"""
        enrollments = EnrollmentModel.objects.filter(course=course)
        
        for enrollment in enrollments:
            # Kiểm tra đã gửi thông báo chưa
            exists = NotificationModel.objects.filter(
                user=enrollment.user,
                type='COURSE_START',
                related_object_type='course',
                related_object_id=course.id,
            ).exists()
            
            if not exists:
                role_text = 'giảng dạy' if enrollment.role_in_course == 'TEACHER' else 'tham gia'
                NotificationModel.objects.create(
                    user=enrollment.user,
                    title='Khóa học đã bắt đầu',
                    message=f'Khóa học "{course.title}" mà bạn {role_text} đã bắt đầu. Hãy truy cập ngay!',
                    type='COURSE_START',
                    related_object_type='course',
                    related_object_id=course.id,
                )

    def notify_course_end(self, course):
        """Thông báo khóa học đã kết thúc"""
        enrollments = EnrollmentModel.objects.filter(course=course)
        
        for enrollment in enrollments:
            exists = NotificationModel.objects.filter(
                user=enrollment.user,
                type='COURSE_END',
                related_object_type='course',
                related_object_id=course.id,
            ).exists()
            
            if not exists:
                NotificationModel.objects.create(
                    user=enrollment.user,
                    title='Khóa học đã kết thúc',
                    message=f'Khóa học "{course.title}" đã kết thúc. Cảm ơn bạn đã tham gia!',
                    type='COURSE_END',
                    related_object_type='course',
                    related_object_id=course.id,
                )

    def notify_course_starting_soon(self, course):
        """Thông báo khóa học sắp bắt đầu"""
        enrollments = EnrollmentModel.objects.filter(course=course)
        
        for enrollment in enrollments:
            exists = NotificationModel.objects.filter(
                user=enrollment.user,
                type='COURSE_STARTING_SOON',
                related_object_type='course',
                related_object_id=course.id,
            ).exists()
            
            if not exists:
                NotificationModel.objects.create(
                    user=enrollment.user,
                    title='Khóa học sắp bắt đầu',
                    message=f'Khóa học "{course.title}" sẽ bắt đầu vào ngày mai. Hãy chuẩn bị sẵn sàng!',
                    type='COURSE_STARTING_SOON',
                    related_object_type='course',
                    related_object_id=course.id,
                )

    def notify_course_ending_soon(self, course):
        """Thông báo khóa học sắp kết thúc"""
        enrollments = EnrollmentModel.objects.filter(course=course)
        
        for enrollment in enrollments:
            exists = NotificationModel.objects.filter(
                user=enrollment.user,
                type='COURSE_ENDING_SOON',
                related_object_type='course',
                related_object_id=course.id,
            ).exists()
            
            if not exists:
                NotificationModel.objects.create(
                    user=enrollment.user,
                    title='Khóa học sắp kết thúc',
                    message=f'Khóa học "{course.title}" sẽ kết thúc trong 3 ngày. Hãy hoàn thành các bài tập còn lại!',
                    type='COURSE_ENDING_SOON',
                    related_object_type='course',
                    related_object_id=course.id,
                )

