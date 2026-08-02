from django.urls import path
from . import views_notifications


notification_urls = [
    path('notifications/', views_notifications.NotificationsView.as_view(), name='notifications'),

    path('notifications/<int:pk>/read/', views_notifications.NotificationReadView.as_view(), name='notification_read'),

    path('notifications/read-all/', views_notifications.NotificationsReadAllView.as_view(), name='notifications_read_all'),
]