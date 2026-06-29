from django.urls import path
from django.http import HttpResponse
from django.shortcuts import redirect



feed_urls = [
    path(
        '',
        lambda request: HttpResponse('TODO: стрічка новин'),
        name='feed',
    ),
]


auth_urls = [
    path(
        'auth/register/',
        lambda request: HttpResponse('TODO: реєстрація'),
        name='register',
    ),

    path(
        'auth/login/',
        lambda request: HttpResponse('TODO: вхід'),
        name='login',
    ),

    path(
        'auth/logout/',
        lambda request: redirect('feed'),
        name='logout',
    ),
]


profile_urls = [
    path(
        'profile/<str:username>/',
        lambda request, username: HttpResponse(f'TODO: профіль {username}'),
        name='profile',
    ),

    path(
        'profile/<str:username>/edit/',
        lambda request, username: HttpResponse(f'TODO: редагування профілю {username}'),
        name='profile_edit',
    ),

    path(
        'profile/<str:username>/friends/',
        lambda request, username: HttpResponse(f'TODO: друзі {username}'),
        name='profile_friends',
    ),

    path(
        'profile/<str:username>/followers/',
        lambda request, username: HttpResponse(f'TODO: підписники {username}'),
        name='profile_followers',
    ),

    path(
        'profile/<str:username>/following/',
        lambda request, username: HttpResponse(f'TODO: підписки {username}'),
        name='profile_following',
    ),
]


post_urls = [
    path(
        'posts/create/',
        lambda request: HttpResponse('TODO: створення поста'),
        name='post_create',
    ),

    path(
        'posts/<int:pk>/',
        lambda request, pk: HttpResponse(f'TODO: деталі поста {pk}'),
        name='post_detail',
    ),

    path(
        'posts/<int:pk>/edit/',
        lambda request, pk: HttpResponse(f'TODO: редагування поста {pk}'),
        name='post_edit',
    ),

    path(
        'posts/<int:pk>/delete/',
        lambda request, pk: redirect('feed'),
        name='post_delete',
    ),

    path(
        'posts/<int:pk>/like/',
        lambda request, pk: redirect('post_detail', pk=pk),
        name='post_like',
    ),

    path(
        'posts/<int:pk>/repost/',
        lambda request, pk: redirect('post_detail', pk=pk),
        name='post_repost',
    ),

    path(
        'posts/<int:pk>/comment/',
        lambda request, pk: redirect('post_detail', pk=pk),
        name='comment_create',
    ),

    path(
        'posts/comment/<int:pk>/delete/',
        lambda request, pk: redirect('feed'),
        name='comment_delete',
    ),
]


friend_urls = [
    path(
        'friends/',
        lambda request: HttpResponse('TODO: список друзів'),
        name='friends',
    ),

    path(
        'friends/requests/',
        lambda request: HttpResponse('TODO: вхідні запити у друзі'),
        name='friend_requests',
    ),

    path(
        'friends/request/<int:user_id>/',
        lambda request, user_id: redirect('friends'),
        name='friend_request_send',
    ),

    path(
        'friends/accept/<int:request_id>/',
        lambda request, request_id: redirect('friend_requests'),
        name='friend_request_accept',
    ),

    path(
        'friends/decline/<int:request_id>/',
        lambda request, request_id: redirect('friend_requests'),
        name='friend_request_decline',
    ),

    path(
        'friends/remove/<int:user_id>/',
        lambda request, user_id: redirect('friends'),
        name='friend_remove',
    ),

    path(
        'friends/subscribe/<int:user_id>/',
        lambda request, user_id: redirect('friends'),
        name='subscribe',
    ),

    path(
        'friends/unsubscribe/<int:user_id>/',
        lambda request, user_id: redirect('friends'),
        name='unsubscribe',
    ),
]


group_urls = [
    path(
        'groups/',
        lambda request: HttpResponse('TODO: каталог груп'),
        name='group_list',
    ),

    path(
        'groups/create/',
        lambda request: HttpResponse('TODO: створення групи'),
        name='group_create',
    ),

    path(
        'groups/<int:pk>/',
        lambda request, pk: HttpResponse(f'TODO: сторінка групи {pk}'),
        name='group_detail',
    ),

    path(
        'groups/<int:pk>/edit/',
        lambda request, pk: HttpResponse(f'TODO: редагування групи {pk}'),
        name='group_edit',
    ),

    path(
        'groups/<int:pk>/delete/',
        lambda request, pk: redirect('group_list'),
        name='group_delete',
    ),

    path(
        'groups/<int:pk>/join/',
        lambda request, pk: redirect('group_detail', pk=pk),
        name='group_join',
    ),

    path(
        'groups/<int:pk>/leave/',
        lambda request, pk: redirect('group_detail', pk=pk),
        name='group_leave',
    ),

    path(
        'groups/<int:pk>/members/',
        lambda request, pk: HttpResponse(f'TODO: учасники групи {pk}'),
        name='group_members',
    ),

    path(
        'groups/<int:pk>/members/<int:user_id>/kick/',
        lambda request, pk, user_id: redirect('group_members', pk=pk),
        name='group_kick',
    ),

    path(
        'groups/<int:pk>/members/<int:user_id>/promote/',
        lambda request, pk, user_id: redirect('group_members', pk=pk),
        name='group_promote',
    ),
]


chat_urls = [
    path(
        'chat/',
        lambda request: HttpResponse('TODO: список чатів'),
        name='chat_list',
    ),

    path(
        'chat/create/<int:user_id>/',
        lambda request, user_id: redirect('chat_list'),
        name='chat_create_private',
    ),

    path(
        'chat/create-group/',
        lambda request: HttpResponse('TODO: створення групового чату'),
        name='chat_create_group',
    ),

    path(
        'chat/<int:pk>/',
        lambda request, pk: HttpResponse(f'TODO: чат {pk}'),
        name='chat_detail',
    ),

    path(
        'chat/<int:pk>/send/',
        lambda request, pk: redirect('chat_detail', pk=pk),
        name='message_send',
    ),

    path(
        'chat/<int:pk>/message/<int:msg_id>/delete/',
        lambda request, pk, msg_id: redirect('chat_detail', pk=pk),
        name='message_delete',
    ),

    path(
        'chat/<int:pk>/read/',
        lambda request, pk: redirect('chat_detail', pk=pk),
        name='chat_mark_read',
    ),
]


notification_urls = [
    path(
        'notifications/',
        lambda request: HttpResponse('TODO: список сповіщень'),
        name='notifications',
    ),

    path(
        'notifications/<int:pk>/read/',
        lambda request, pk: redirect('notifications'),
        name='notification_read',
    ),

    path(
        'notifications/read-all/',
        lambda request: redirect('notifications'),
        name='notifications_read_all',
    ),
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