"""
Comment API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from .....application.use_cases.comment import (
    CreateCommentUseCase,
    ListCommentsUseCase,
    CreateCommentInput,
    ListCommentsInput,
)


class CommentListView(APIView):
    """
    GET /api/v1/comments/?target_type=&target_id=
    
    Lấy danh sách comment theo target (lesson hoặc assignment).
    
    Query params:
    - target_type: 'LESSON' hoặc 'ASSIGNMENT' (required)
    - target_id: ID của lesson hoặc assignment (required)
    - include_replies: true/false (optional, default: true)
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def get(self, request):
        """Lấy danh sách comment"""
        target_type = request.query_params.get('target_type')
        target_id = request.query_params.get('target_id')
        
        if not target_type or not target_id:
            return Response(
                {'detail': 'target_type và target_id là bắt buộc'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            target_id = int(target_id)
        except ValueError:
            return Response(
                {'detail': 'target_id phải là số'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        include_replies = request.query_params.get('include_replies', 'true').lower() == 'true'
        
        use_case = ListCommentsUseCase()
        try:
            comments = use_case.execute(ListCommentsInput(
                target_type=target_type,
                target_id=target_id,
                include_replies=include_replies,
            ))
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        from .serializers import CommentSerializer
        # Convert DTOs to dict để serialize
        comments_data = []
        for c in comments:
            comment_dict = {
                'id': c.id,
                'user_id': c.user_id,
                'user_full_name': c.user_full_name,
                'user_username': c.user_username,
                'content': c.content,
                'target_type': c.target_type,
                'target_id': c.target_id,
                'parent_id': c.parent_id,
                'created_at': c.created_at,
                'updated_at': c.updated_at,
                'replies_count': c.replies_count,
            }
            if hasattr(c, 'replies'):
                comment_dict['replies'] = [{
                    'id': r.id,
                    'user_id': r.user_id,
                    'user_full_name': r.user_full_name,
                    'user_username': r.user_username,
                    'content': r.content,
                    'parent_id': r.parent_id,
                    'created_at': r.created_at,
                    'updated_at': r.updated_at,
                } for r in c.replies]
            comments_data.append(comment_dict)
        serializer = CommentSerializer(comments_data, many=True)
        return Response(serializer.data)


class CreateCommentView(APIView):
    """
    POST /api/v1/comments/
    
    Tạo comment mới vào lesson hoặc assignment.
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    def post(self, request):
        """Tạo comment"""
        from .serializers import CreateCommentSerializer
        serializer = CreateCommentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        use_case = CreateCommentUseCase()
        try:
            comment = use_case.execute(CreateCommentInput(
                user_id=request.user.id,
                content=serializer.validated_data['content'],
                target_type=serializer.validated_data['target_type'],
                target_id=serializer.validated_data['target_id'],
                parent_id=serializer.validated_data.get('parent_id'),
            ))
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        from .serializers import CommentSerializer
        from .....application.use_cases.comment import CommentDTO
        comment_dto = CommentDTO.from_model(comment)
        comment_data = {
            'id': comment_dto.id,
            'user_id': comment_dto.user_id,
            'user_full_name': comment_dto.user_full_name,
            'user_username': comment_dto.user_username,
            'content': comment_dto.content,
            'target_type': comment_dto.target_type,
            'target_id': comment_dto.target_id,
            'parent_id': comment_dto.parent_id,
            'created_at': comment_dto.created_at,
            'updated_at': comment_dto.updated_at,
            'replies_count': comment_dto.replies_count,
        }
        serializer = CommentSerializer(comment_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

