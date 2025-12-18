"""
Comment API URLs
"""
from django.urls import path

from .views import CommentListView, CreateCommentView

urlpatterns = [
    path('', CommentListView.as_view(), name='comment_list'),
    path('create/', CreateCommentView.as_view(), name='create_comment'),
]



