from django.urls import path
from . import views_chat


chat_urls = [
    path('chat/', views_chat.ChatListView.as_view(), name='chat_list'),

    path('chat/popup/', views_chat.ChatPopupView.as_view(), name='chat_popup'),

    path('chat/popup/<int:pk>/', views_chat.ChatPopupConversationView.as_view(), name='chat_popup_conversation'),

    path('chat/create/<int:user_id>/', views_chat.ChatCreatePrivateView.as_view(), name='chat_create_private'),

    path('chat/create-group/', views_chat.ChatCreateGroupView.as_view(), name='chat_create_group'),

    path('chat/<int:pk>/', views_chat.ChatDetailView.as_view(), name='chat_detail'),

    path('chat/<int:pk>/messages/', views_chat.ChatMessagesPollView.as_view(), name='chat_messages_poll'),

    path('chat/<int:pk>/send/', views_chat.MessageSendView.as_view(), name='message_send'),

    path('chat/<int:pk>/message/<int:msg_id>/delete/', views_chat.MessageDeleteView.as_view(), name='message_delete'),

    path('chat/<int:pk>/read/', views_chat.ChatMarkReadView.as_view(), name='chat_mark_read'),

    path('chat/<int:pk>/leave/', views_chat.ChatLeaveView.as_view(), name='chat_leave'),

    path('chat/<int:pk>/delete/', views_chat.ChatDeleteView.as_view(), name='chat_delete'),

    path('posts/<int:pk>/share/<int:chat_id>/', views_chat.PostShareView.as_view(), name='post_share'),
]