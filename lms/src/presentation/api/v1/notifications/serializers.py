"""
Notification Serializers
"""
from rest_framework import serializers
from datetime import datetime


class NotificationSerializer(serializers.Serializer):
    """Serializer cho Notification"""
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)
    is_read = serializers.BooleanField(read_only=True)
    related_object_type = serializers.CharField(read_only=True, allow_null=True)
    related_object_id = serializers.IntegerField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    def to_representation(self, instance):
        """Custom representation để thêm type_display"""
        data = super().to_representation(instance)
        # Lấy type_display từ model
        from .....infrastructure.persistence.models.communication import NotificationModel
        type_value = instance.get('type') if isinstance(instance, dict) else getattr(instance, 'type', None)
        if type_value:
            for choice in NotificationModel.NotificationType.choices:
                if choice[0] == type_value:
                    data['type_display'] = choice[1]
                    break
        return data


class MarkAsReadSerializer(serializers.Serializer):
    """Serializer cho mark as read request"""
    pass  # Không cần input

