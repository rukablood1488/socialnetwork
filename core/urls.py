from django.urls import path
from . import views


feed_urls = [
    path('', views.feed, name='feed'),
]

auth_urls = [
    path('auth/register/', views.register, name='register'),

    path('auth/login/', views.login_view, name='login'),

    path('auth/logout/', views.logout_view, name='logout'),
]


profile_urls = [
    path('profile/<str:username>/', views.profile, name='profile'),

    path('profile/<str:username>/edit/', views.profile_edit, name='profile_edit'),

    path('profile/<str:username>/friends/', views.profile_friends, name='profile_friends'),

    path('profile/<str:username>/followers/', views.profile_followers, name='profile_followers'),

    path('profile/<str:username>/following/', views.profile_following, name='profile_following'),
]


post_urls = [
    #path('posts/create/', views.post_create, name='post_create'),

    #path('posts/<int:pk>/', views.post_detail, name='post_detail'),

    #path('posts/<int:pk>/edit/', views.post_edit, name='post_edit'),

    #path('posts/<int:pk>/delete/', views.post_delete, name='post_delete'),

    #path('posts/<int:pk>/like/', views.post_like, name='post_like'),

    #path('posts/<int:pk>/repost/', views.post_repost, name='post_repost'),

    #path('posts/<int:pk>/comment/', views.comment_create, name='comment_create'),

    #path('posts/comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
]


friend_urls = [
    path('friends/', views.friends, name='friends'),

    #path('friends/requests/', views.friend_requests, name='friend_requests'),

    path('friends/request/<int:user_id>/', views.friend_request_send, name='friend_request_send'),

    #path('friends/accept/<int:request_id>/', views.friend_request_accept, name='friend_request_accept'),

    #path('friends/decline/<int:request_id>/', views.friend_request_decline, name='friend_request_decline'),

    path('friends/remove/<int:user_id>/', views.friend_remove, name='friend_remove'),

    path('friends/subscribe/<int:user_id>/', views.subscribe, name='subscribe'),

    path('friends/unsubscribe/<int:user_id>/', views.unsubscribe, name='unsubscribe'),
]


group_urls = [
    path('groups/', views.group_list, name='group_list'),

    #path('groups/create/', views.group_create, name='group_create'),

    #path('groups/<int:pk>/', views.group_detail, name='group_detail'),

    #path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),

    #path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),

    #path('groups/<int:pk>/join/', views.group_join, name='group_join'),

    #path('groups/<int:pk>/leave/', views.group_leave, name='group_leave'),

    #path('groups/<int:pk>/members/', views.group_members, name='group_members'),

    #path('groups/<int:pk>/members/<int:user_id>/kick/', views.group_kick, name='group_kick'),

    #path('groups/<int:pk>/members/<int:user_id>/promote/', views.group_promote, name='group_promote'),
]


chat_urls = [

    path('chat/', views.chat_list, name='chat_list'),

    #path('chat/create/<int:user_id>/', views.chat_create_private, name='chat_create_private'),

    #path('chat/create-group/', views.chat_create_group, name='chat_create_group'),

    #path('chat/<int:pk>/', views.chat_detail, name='chat_detail'),

    #path('chat/<int:pk>/send/', views.message_send, name='message_send'),

    #path('chat/<int:pk>/message/<int:msg_id>/delete/', views.message_delete, name='message_delete'),

    #path('chat/<int:pk>/read/', views.chat_mark_read, name='chat_mark_read'),
]


notification_urls = [
    path('notifications/', views.notifications, name='notifications'),

    #path('notifications/<int:pk>/read/', views.notification_read, name='notification_read'),

    #path('notifications/read-all/', views.notifications_read_all, name='notifications_read_all'),
]


urlpatterns = (
    feed_urls
    + auth_urls
    + profile_urls
    + post_urls
    + friend_urls
    + group_urls
    + chat_urls
    + notification_urls
)