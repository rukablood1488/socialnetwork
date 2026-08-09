def unread_notifications_count(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
    else:
        count = 0
    return {'unread_notifications_count': count}


def unread_messages_count(request):
    if request.user.is_authenticated:
        from .models import Message
        count = Message.objects.filter(
            chat__participants=request.user, is_read=False,
        ).exclude(sender=request.user).count()
    else:
        count = 0
    return {'unread_messages_count': count}