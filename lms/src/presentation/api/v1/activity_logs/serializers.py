"""
Activity Log Serializers
"""
from rest_framework import serializers


class ActivityLogSerializer(serializers.Serializer):
    """Serializer cho ActivityLog"""
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    user_full_name = serializers.CharField(read_only=True)
    user_username = serializers.CharField(read_only=True)
    action_type = serializers.CharField(read_only=True)
    target_type = serializers.CharField(read_only=True, allow_null=True)
    target_id = serializers.IntegerField(read_only=True, allow_null=True)
    metadata = serializers.DictField(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)
    
    def to_representation(self, instance):
        """Custom representation để thêm action_type_display"""
        data = super().to_representation(instance)
        # Lấy action_type_display từ model
        from ......infrastructure.persistence.models.activity import UserActivityLogModel
        if hasattr(instance, 'action_type'):
            for choice in UserActivityLogModel.ActionType.choices:
                if choice[0] == instance.action_type:
                    data['action_type_display'] = choice[1]
                    break
        return data

