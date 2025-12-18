"""
Courses Serializers
"""
from rest_framework import serializers


class CourseListOutputSerializer(serializers.Serializer):
    """Output serializer for course list"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    subject_title = serializers.CharField()
    status = serializers.CharField()
    status_display = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    students_count = serializers.IntegerField()


class LessonOutputSerializer(serializers.Serializer):
    """Output serializer for lesson"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField(allow_blank=True)
    order = serializers.IntegerField()
    resources_count = serializers.IntegerField()
    assignments_count = serializers.IntegerField()


class ModuleOutputSerializer(serializers.Serializer):
    """Output serializer for module"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    order = serializers.IntegerField()
    lessons_count = serializers.IntegerField()
    lessons = LessonOutputSerializer(many=True)


class CourseDetailOutputSerializer(serializers.Serializer):
    """Output serializer for course detail"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    subject_id = serializers.IntegerField()
    subject_title = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    status = serializers.CharField()
    status_display = serializers.CharField()
    total_lessons = serializers.IntegerField()
    total_students = serializers.IntegerField()
    modules = ModuleOutputSerializer(many=True)

