"""
Comment Serializers
"""
from rest_framework import serializers
from datetime import datetime


class CommentSerializer(serializers.Serializer):
    """Serializer cho Comment"""
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    user_full_name = serializers.CharField(read_only=True)
    user_username = serializers.CharField(read_only=True)
    content = serializers.CharField()
    target_type = serializers.CharField(read_only=True)
    target_id = serializers.IntegerField(read_only=True)
    parent_id = serializers.IntegerField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    replies_count = serializers.IntegerField(read_only=True)
    replies = serializers.ListField(child=serializers.DictField(), read_only=True, required=False)


class CreateCommentSerializer(serializers.Serializer):
    """Serializer cho tạo comment"""
    content = serializers.CharField(required=True, min_length=1, max_length=5000)
    target_type = serializers.ChoiceField(choices=['LESSON', 'ASSIGNMENT'], required=True)
    target_id = serializers.IntegerField(required=True, min_value=1)
    parent_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)



