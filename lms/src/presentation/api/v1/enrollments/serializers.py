"""
Enrollments Serializers
"""
from rest_framework import serializers


class EnrollmentOutputSerializer(serializers.Serializer):
    """Output serializer for enrollment"""
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    subject_title = serializers.CharField()
    role_in_course = serializers.CharField()
    role_display = serializers.CharField()
    status = serializers.CharField(required=False, help_text="Trạng thái khóa học (tự động tính)")
    status_display = serializers.CharField(required=False, help_text="Hiển thị trạng thái")
    joined_at = serializers.DateTimeField()


class StudentListOutputSerializer(serializers.Serializer):
    """Output serializer for student list"""
    user_id = serializers.IntegerField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
    role_in_course = serializers.CharField()
    role_display = serializers.CharField()
    joined_at = serializers.DateTimeField()

