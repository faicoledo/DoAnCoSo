"""
Notification API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from .....application.use_cases.notification import (
    ListUserNotificationsUseCase,
    MarkNotificationAsReadUseCase,
    ListNotificationsInput,
)


class NotificationListView(APIView):
    """
    GET /api/v1/notifications/
    
    Lấy danh sách thông báo của user hiện tại.
    
    Query params:
    - is_read: true/false (optional) - Lọc theo trạng thái đã đọc
    - limit: số lượng (optional)
    - offset: vị trí bắt đầu (optional)
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        """Lấy danh sách thông báo"""
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            is_read = is_read.lower() == 'true'
        else:
            is_read = None
        
        limit = request.query_params.get('limit')
        limit = int(limit) if limit else None
        
        offset = request.query_params.get('offset', 0)
        offset = int(offset)
        
        use_case = ListUserNotificationsUseCase()
        notifications = use_case.execute(ListNotificationsInput(
            user_id=request.user.id,
            is_read=is_read,
            limit=limit,
            offset=offset,
        ))
        
        from .serializers import NotificationSerializer
        # Convert DTOs to dict để serialize
        notifications_data = []
        for n in notifications:
            notifications_data.append({
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.type,
                'is_read': n.is_read,
                'related_object_type': n.related_object_type,
                'related_object_id': n.related_object_id,
                'created_at': n.created_at,
            })
        serializer = NotificationSerializer(notifications_data, many=True)
        return Response(serializer.data)


class UnreadCountView(APIView):
    """
    GET /api/v1/notifications/unread-count/
    
    Lấy số lượng thông báo chưa đọc.
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        from .....infrastructure.persistence.models.communication import NotificationModel
        count = NotificationModel.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'count': count})


class MarkNotificationAsReadView(APIView):
    """
    POST /api/v1/notifications/{id}/read/
    
    Đánh dấu thông báo đã đọc.
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def post(self, request, notification_id):
        """Đánh dấu thông báo đã đọc"""
        try:
            use_case = MarkNotificationAsReadUseCase()
            notification = use_case.execute(notification_id, request.user.id)
            
            from .serializers import NotificationSerializer
            notification_data = {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.type,
                'is_read': notification.is_read,
                'related_object_type': notification.related_object_type,
                'related_object_id': notification.related_object_id,
                'created_at': notification.created_at,
            }
            serializer = NotificationSerializer(notification_data)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

