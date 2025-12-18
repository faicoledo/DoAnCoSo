"""
Notification API URLs
"""
from django.urls import path

from .views import NotificationListView, UnreadCountView, MarkNotificationAsReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification_list'),
    path('unread-count/', UnreadCountView.as_view(), name='notification_unread_count'),
    path('<int:notification_id>/read/', MarkNotificationAsReadView.as_view(), name='mark_notification_read'),
]



