"""
Activity Log API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from .....application.use_cases.activity_log import (
    ListActivityLogsUseCase,
    ListActivityLogsInput,
)


class ActivityLogListView(APIView):
    """
    GET /api/v1/activity-logs/
    
    Lấy danh sách activity logs của user hiện tại.
    
    User chỉ xem được log của chính mình (trừ admin).
    
    Query params:
    - action_type: Loại hành động (optional)
    - target_type: Loại đối tượng (optional)
    - limit: số lượng (optional)
    - offset: vị trí bắt đầu (optional)
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        """Lấy danh sách activity logs"""
        # User chỉ xem được log của chính mình (trừ admin)
        user_id = request.user.id
        if not (request.user.is_staff or request.user.is_superuser):
            # Nếu không phải admin, chỉ cho xem log của chính mình
            if 'user_id' in request.query_params:
                query_user_id = request.query_params.get('user_id')
                try:
                    query_user_id = int(query_user_id)
                    if query_user_id != user_id:
                        return Response(
                            {'detail': 'Bạn chỉ có thể xem log của chính mình'},
                            status=status.HTTP_403_FORBIDDEN
                        )
                except ValueError:
                    pass
        
        action_type = request.query_params.get('action_type')
        target_type = request.query_params.get('target_type')
        
        limit = request.query_params.get('limit')
        limit = int(limit) if limit else None
        
        offset = request.query_params.get('offset', 0)
        offset = int(offset)
        
        use_case = ListActivityLogsUseCase()
        logs = use_case.execute(ListActivityLogsInput(
            user_id=user_id,
            action_type=action_type,
            target_type=target_type,
            limit=limit,
            offset=offset,
        ))
        
        from .serializers import ActivityLogSerializer
        # Convert DTOs to dict để serialize
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'user_id': log.user_id,
                'user_full_name': log.user_full_name,
                'user_username': log.user_username,
                'action_type': log.action_type,
                'target_type': log.target_type,
                'target_id': log.target_id,
                'metadata': log.metadata,
                'timestamp': log.timestamp,
            })
        serializer = ActivityLogSerializer(logs_data, many=True)
        return Response(serializer.data)

